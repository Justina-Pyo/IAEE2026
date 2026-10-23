"""Rider expenditure model, KES, monthly cash flows. Python 3.10+; no dependencies."""
from dataclasses import dataclass, replace, asdict
import math

@dataclass(frozen=True)
class Assumptions:
    months: int = 60
    discount_nominal_annual: float = .10
    operating_days: float = 30
    payment_days: float = 30
    km_day: float = 80
    ice_price: float = 195960
    ev_vehicle_price: float = 130000
    down_fraction: float = .20
    apr: float = .25
    term: int = 24
    rental_day: float = 270
    petrol: float = 214
    litres_km: float = .029396694454647956
    ice_maint_km: float = 1.6919394201354927
    ev_maint_km: float = .31395399945999913
    kwh_km: float = .04676378339401287
    tariff: float = 22
    swap_fee: float = 290
    swap_range: float = 95
    ice_downtime: float = 0
    ev_downtime: float = 0
    ev_subsidy: float = 0
    rental_support_total: float = 0
    ice_extra_upfront: float = 0
    ev_extra_upfront: float = 0
    ice_annual_fixed: float = 0
    ev_annual_fixed: float = 0
    ice_residual: float = 0
    ev_residual: float = 0
    maintenance_calendar: bool = False

ARRANGEMENTS=('ICE_financed','EV_BaaS_financed','EV_BaaS_cash','EV_BaaS_rental')

def pmt(principal, apr, term):
    if principal < 0 or apr < 0 or not isinstance(term,int) or term <= 0:
        raise ValueError('Invalid loan inputs')
    r=apr/12
    return principal/term if r==0 else principal*r/(1-(1+r)**(-term))

def validate(p):
    for k,v in asdict(p).items():
        if isinstance(v,bool): continue
        if not math.isfinite(v) or v < 0: raise ValueError('Invalid '+k)
    for k in ('months','term'):
        if not isinstance(getattr(p,k),int) or getattr(p,k)<=0: raise ValueError(k)
    if p.term>p.months: raise ValueError('Loan beyond horizon requires outstanding debt treatment')
    if min(p.km_day,p.operating_days,p.payment_days,p.swap_range)<=0: raise ValueError('Positive service inputs required')
    if max(p.ice_downtime,p.ev_downtime,p.down_fraction)>1: raise ValueError('Fractions exceed 1')
    if p.ev_subsidy>p.ev_vehicle_price: raise ValueError('Subsidy exceeds price')
    if p.rental_support_total>p.rental_day*p.payment_days*p.months: raise ValueError('Support exceeds rent')

def cashflows(p, arrangement, swap_kes_km=None):
    validate(p)
    if arrangement not in ARRANGEMENTS: raise ValueError('Unknown arrangement')
    ice=arrangement=='ICE_financed'; rental=arrangement=='EV_BaaS_rental'; cash=arrangement=='EV_BaaS_cash'
    price=p.ice_price if ice else p.ev_vehicle_price-p.ev_subsidy
    upfront=0 if rental else (price if cash else p.down_fraction*price)
    upfront+=p.ice_extra_upfront if ice else p.ev_extra_upfront
    payment=(p.rental_day*p.payment_days-p.rental_support_total/p.months if rental else
             0 if cash else pmt(price*(1-p.down_fraction),p.apr,p.term))
    days=p.operating_days*(1-(p.ice_downtime if ice else p.ev_downtime))
    km=p.km_day*days
    energy_km=p.petrol*p.litres_km if ice else (p.swap_fee/p.swap_range if swap_kes_km is None else swap_kes_km)
    maint=p.ice_maint_km if ice else p.ev_maint_km
    maint_km=p.km_day*p.operating_days if p.maintenance_calendar else km
    for m in range(p.months+1):
        acquisition=upfront if m==0 else 0
        financing=payment if m>0 and (rental or m<=p.term) else 0
        energy=energy_km*km if m else 0
        maintenance=maint*maint_km if m else 0
        fixed=(p.ice_annual_fixed if ice else p.ev_annual_fixed) if m>0 and m%12==0 else 0
        # Rental grants no terminal vehicle asset.
        residual=(p.ice_residual if ice else 0 if rental else p.ev_residual) if m==p.months else 0
        total=acquisition+financing+energy+maintenance+fixed-residual
        factor=(1+p.discount_nominal_annual/12)**(-m)
        yield dict(arrangement=arrangement,month=m,acquisition=acquisition,payment=financing,energy=energy,maintenance=maintenance,fixed=fixed,residual=residual,total=total,pv=total*factor,km=km if m else 0,pv_km=km*factor if m else 0)

def evaluate(p, arrangement, swap_kes_km=None):
    f=list(cashflows(p,arrangement,swap_kes_km)); pv=sum(x['pv'] for x in f); distance=sum(x['km'] for x in f)
    return dict(arrangement=arrangement,pv_tco=pv,nominal_tco=sum(x['total'] for x in f),km=distance,
                levelized_kes_km=pv/sum(x['pv_km'] for x in f) if distance else None,
                first_month_payment=f[1]['payment'],first_month_outflow=f[1]['total'],upfront=f[0]['acquisition'])

def threshold(p, arrangement):
    """Rider TCO parity tariff; meaningful only at equal positive service."""
    if not math.isclose(p.ice_downtime,p.ev_downtime): return None
    ice=evaluate(p,'ICE_financed')['pv_tco']; zero=list(cashflows(p,arrangement,0))
    denom=sum(x['pv_km'] for x in zero)
    return (ice-sum(x['pv'] for x in zero))/denom if denom else None

def battery_budget(p, life):
    """Hypothetical cash self-charge vs cash BaaS; identical nonbattery costs.
    Maximum uniform initial/replacement pack price if all other extra costs zero.
    This is a budget identity, not a quote or proof of self-charge availability.
    """
    if not isinstance(life,int) or life<=0: raise ValueError('Positive battery life required')
    flow=list(cashflows(p,'EV_BaaS_cash'))
    pvkm=sum(x['pv_km'] for x in flow)
    avoided=pvkm*(p.swap_fee/p.swap_range-p.kwh_km*p.tariff)
    replacement_months=list(range(life,p.months,life))
    weight=1+sum((1+p.discount_nominal_annual/12)**(-m) for m in replacement_months)
    return {'battery_life_months':life,'replacement_months':','.join(map(str,replacement_months)),
            'pv_budget_all_extra_selfcharge_costs':avoided,'max_uniform_pack_price_if_no_other_extras':avoided/weight}
