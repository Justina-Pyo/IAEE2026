import sys,unittest,math,json,tempfile,zipfile
from pathlib import Path
from dataclasses import replace
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from model import *
from calibrate import calibrate
from run_analysis import load_base,cases

class Tests(unittest.TestCase):
    def test_zero_interest(self):self.assertEqual(pmt(120000,0,24),5000)
    def test_cashflow_reconciliation(self):
        for a in ARRANGEMENTS:
            p=Assumptions();f=list(cashflows(p,a));r=evaluate(p,a)
            self.assertAlmostEqual(r['pv_tco'],sum(x['pv'] for x in f));self.assertEqual(r['km'],144000)
            self.assertAlmostEqual(evaluate(replace(p,discount_nominal_annual=0),a)['pv_tco'],r['nominal_tco'])
    def test_independent_loan_annuity(self):
        p=Assumptions(discount_nominal_annual=0);r=evaluate(p,'ICE_financed')
        expected=p.ice_price*p.down_fraction+pmt(p.ice_price*(1-p.down_fraction),p.apr,p.term)*p.term+(p.petrol*p.litres_km+p.ice_maint_km)*p.km_day*p.operating_days*p.months
        self.assertAlmostEqual(r['nominal_tco'],expected)
    def test_parity_identity(self):
        for km in [60,80,110]:
            p=replace(Assumptions(),km_day=km)
            for a in ARRANGEMENTS[1:]:self.assertAlmostEqual(evaluate(p,a,threshold(p,a))['pv_tco'],evaluate(p,'ICE_financed')['pv_tco'],places=6)
    def test_downtime_keeps_payment(self):
        p=Assumptions();q=replace(p,ev_downtime=.15)
        self.assertEqual(evaluate(p,'EV_BaaS_rental')['first_month_payment'],evaluate(q,'EV_BaaS_rental')['first_month_payment'])
        self.assertAlmostEqual(evaluate(q,'EV_BaaS_rental')['km'],.85*evaluate(p,'EV_BaaS_rental')['km']);self.assertIsNone(threshold(q,'EV_BaaS_rental'))
    def test_no_double_counting(self):
        p=Assumptions()
        self.assertEqual(sum(x['payment'] for x in cashflows(p,'EV_BaaS_cash')),0)
        self.assertEqual(sum(x['acquisition'] for x in cashflows(p,'EV_BaaS_cash')),p.ev_vehicle_price)
        self.assertEqual(sum(x['payment'] for x in cashflows(p,'EV_BaaS_rental')),270*30*60)
    def test_term_changes_payment(self):self.assertGreater(pmt(100000,.25,12),pmt(100000,.25,36))
    def test_battery_boundary_and_budget(self):
        p=Assumptions()
        self.assertEqual(battery_budget(p,24)['replacement_months'],'24,48')
        self.assertEqual(battery_budget(p,60)['replacement_months'],'')
        self.assertGreater(battery_budget(p,60)['max_uniform_pack_price_if_no_other_extras'],battery_budget(p,24)['max_uniform_pack_price_if_no_other_extras'])
        b=battery_budget(p,24);v=b['max_uniform_pack_price_if_no_other_extras']
        self.assertAlmostEqual(v*(1+(1+.1/12)**-24+(1+.1/12)**-48),b['pv_budget_all_extra_selfcharge_costs'])
    def test_invalid_inputs(self):
        for p in [Assumptions(swap_range=0),Assumptions(ev_downtime=1.1),Assumptions(term=90),Assumptions(petrol=float('nan'))]:
            with self.assertRaises(ValueError):evaluate(p,'ICE_financed')
    def test_residual_not_rental_asset(self):
        p=Assumptions(ev_residual=20000)
        self.assertEqual(evaluate(p,'EV_BaaS_rental'),evaluate(Assumptions(),'EV_BaaS_rental'))
    def test_every_scenario_valid(self):
        c=json.loads((Path(__file__).parents[1]/'data/calibration.json').read_text());p=load_base(c)
        for _,_,q in cases(p,c):
            for a in ARRANGEMENTS:self.assertTrue(math.isfinite(evaluate(q,a)['pv_tco']))
    def test_missing_not_zero_and_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            path=Path(t)/'fixture.zip'
            def write(dup=False):
                with zipfile.ZipFile(path,'w') as z:
                    head='user_id,date,distance_km,maintenance_kes,fuel_amount_l,fuel_cost_kes,kwh_charging,battery_swap_cost_kes\n'
                    lines='a,1,10,5,1,200,1,50\na,2,100,,,,,\nb,1,20,10,2,400,2,100\n'
                    for name in ['transition-control-fuel-motorcycle-daily-data.csv','transition-treatment-electric-motorcycle-daily-data.csv']:z.writestr('root/daily_data/'+name,head+lines+('a,1,10,5,1,200,1,50\n' if dup else ''))
            write();c=calibrate(path);self.assertAlmostEqual(c['ice']['fuel_amount_l']['pooled'],.1)
            write(True)
            with self.assertRaises(ValueError):calibrate(path)
if __name__=='__main__':unittest.main()
