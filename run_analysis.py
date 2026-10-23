"""Reproduce every manuscript number from versioned aggregate inputs."""
import argparse,csv,json,hashlib,platform
from pathlib import Path
from dataclasses import replace,asdict
from model import Assumptions,ARRANGEMENTS,evaluate,cashflows,threshold,battery_budget
ROOT=Path(__file__).resolve().parent

def write(path,rows):
    with path.open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def load_base(cal):
    return Assumptions(litres_km=cal['ice']['fuel_amount_l']['pooled'],ice_maint_km=cal['ice']['maintenance_kes']['pooled'],ev_maint_km=cal['ev']['maintenance_kes']['pooled'],kwh_km=cal['ev']['kwh_charging']['pooled'])

def cases(p,c):
    yield 'baseline','reference',p
    for km in [60,110]:yield f'km_{km}','utilization',replace(p,km_day=km)
    for km in [c['ice']['distance_rider_quantiles']['0.1'],c['ice']['distance_rider_quantiles']['0.9']]:yield f'outer_km_{km:.2f}','utilization_outer',replace(p,km_day=km)
    for d in [22,26]:yield f'operating_days_{d}','access',replace(p,operating_days=d)
    for q in [.25,.4]:yield f'discount_{q}','discount',replace(p,discount_nominal_annual=q)
    for q in [.0,.15,.4]:yield f'apr_{q}','finance',replace(p,apr=q)
    for t in [12,36]:yield f'term_{t}','hypothetical_finance',replace(p,term=t)
    for m in [36,84]:yield f'horizon_{m}','horizon',replace(p,months=m)
    for side in ['ice','ev']:
        for q in ['rider_ratio_p25','rider_ratio_p75','loo_pooled_min','loo_pooled_max']:
            yield side+'_maintenance_'+q,'empirical_maintenance',replace(p,**{side+'_maint_km':c[side]['maintenance_kes'][q]})
        for factor in [.5,2]:yield f'{side}_maintenance_x{factor}','exploratory_maintenance',replace(p,**{side+'_maint_km':getattr(p,side+'_maint_km')*factor})
    yield 'calendar_maintenance','maintenance_basis',replace(p,maintenance_calendar=True,ev_downtime=.10)
    yield 'manufacturer_petrol_45km_l','alternative_transfer',replace(p,litres_km=1/45)
    yield 'calculator_ev_maintenance','alternative_transfer',replace(p,ev_maint_km=4002/(80*365/12))
    for factor in [.8,1.2]:
        yield f'transfer_fuel_x{factor}','temporal_transfer',replace(p,litres_km=p.litres_km*factor)
        yield f'transfer_ev_energy_x{factor}','temporal_transfer',replace(p,swap_range=p.swap_range/factor,kwh_km=p.kwh_km*factor)
    yield 'observed_2023_fuel_expenditure','temporal_transfer',replace(p,petrol=c['ice']['fuel_cost_kes']['pooled']/p.litres_km)
    for method in ['equal_rider','daily_ratio_mean']:
        yield 'estimator_'+method,'estimator',replace(p,litres_km=c['ice']['fuel_amount_l'][method],ice_maint_km=c['ice']['maintenance_kes'][method],ev_maint_km=c['ev']['maintenance_kes'][method],kwh_km=c['ev']['kwh_charging'][method])
    for d in [.05,.10,.15]:yield f'ev_downtime_{d}','unequal_service',replace(p,ev_downtime=d)
    for r in [80,100]:yield f'swap_range_{r}','range',replace(p,swap_range=r)
    for mult in [.8,1.2]:yield f'swap_fee_x{mult}','tariff',replace(p,swap_fee=p.swap_fee*mult)
    for frac in [.5,1]:yield f'policy_10000_pass_{frac}','hypothetical_policy',replace(p,ev_subsidy=10000*frac,rental_support_total=10000*frac)
    for extra in [10000,30000]:yield f'ev_extra_cost_{extra}','unobserved_cost',replace(p,ev_extra_upfront=extra)
    yield 'residual_20pct','residual',replace(p,ice_residual=.2*p.ice_price,ev_residual=.2*p.ev_vehicle_price)
    yield 'combined_adverse','combined_equal_service',replace(p,km_day=60,operating_days=22,litres_km=p.litres_km*.8,ev_maint_km=p.ev_maint_km*2,ice_maint_km=p.ice_maint_km*.5,swap_range=80,swap_fee=p.swap_fee*1.2,ev_extra_upfront=30000)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,default=ROOT/'results');ap.add_argument('--config',type=Path,help='JSON object overriding Assumptions after calibration');args=ap.parse_args();args.out.mkdir(exist_ok=True,parents=True)
    c=json.loads((ROOT/'data/calibration.json').read_text());p=load_base(c)
    if args.config:p=replace(p,**json.loads(args.config.read_text()))
    rows=[];flows=[];configs=[]
    for name,kind,x in cases(p,c):
        configs.append({'scenario':name,'kind':kind,**asdict(x)})
        ice=evaluate(x,'ICE_financed')
        for a in ARRANGEMENTS:
            r=evaluate(x,a);equal=abs(r['km']-ice['km'])<1e-6
            r.update(scenario=name,kind=kind,equal_service=equal,km_day=x.km_day,
                     pv_saving_vs_ice=ice['pv_tco']-r['pv_tco'] if equal else None,
                     saving_pct=100*(1-r['pv_tco']/ice['pv_tco']) if equal else None,
                     parity_swap_kes_km=threshold(x,a) if a!='ICE_financed' else None)
            rows.append(r)
            flows.extend(dict(scenario=name,**f) for f in cashflows(x,a))
    write(args.out/'scenarios.csv',rows);write(args.out/'cashflows.csv',flows)
    grid=[]
    for km in range(10,201,5):
        x=replace(p,km_day=km)
        for a in ARRANGEMENTS[1:]:grid.append(dict(km_day=km,arrangement=a,parity_swap_kes_km=threshold(x,a),assumed_swap_kes_km=p.swap_fee/p.swap_range))
    write(args.out/'thresholds.csv',grid)
    budgets=[]
    for km in [60,80,110]:
        for life in [24,36,60]:budgets.append(dict(km_day=km,**battery_budget(replace(p,km_day=km),life)))
    write(args.out/'battery_budgets.csv',budgets)
    bench=[]
    for method in ['pooled','equal_rider','daily_ratio_mean']:
        for tariff in [15,22,35,50]:
            b=c['ev']['kwh_charging'][method]*tariff
            for pricebasis,price in [('observed_2023_pooled_or_reweighted',c['ev']['battery_swap_cost_kes'][method]),('scenario_290_per_95km',p.swap_fee/p.swap_range)]:
                bench.append(dict(estimator=method,tariff=tariff,price_basis=pricebasis,swap_kes_km=price,electricity_benchmark=b,gap=price-b,gap_share_pct=100*(price-b)/price))
    write(args.out/'benchmarks.csv',bench)
    hashes={str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest() for f in [ROOT/'model.py',ROOT/'run_analysis.py',ROOT/'data/calibration.json']}
    (args.out/'manifest.json').write_text(json.dumps(dict(python=platform.python_version(),source_hashes=hashes,configurations=configs,interpretation='Deterministic conditional scenarios, not population estimates or causal effects. All money is constant scenario-price KES; discount is nominal annual compounding convention, not a forecast of nominal cash escalation.'),indent=2))
    print('Scenarios:',len(configs),'Summary rows:',len(rows))
    for r in rows:
        if r['scenario'] in ['baseline','combined_adverse','km_60','km_110']:print(r)
if __name__=='__main__':main()
