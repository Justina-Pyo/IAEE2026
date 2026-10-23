"""Rebuild anonymous aggregate calibration from the original dataset ZIP."""
import argparse,csv,hashlib,io,json,math,statistics as st,zipfile
from collections import defaultdict
from pathlib import Path

def quantile(v,p):
    v=sorted(v);i=(len(v)-1)*p;j=int(i)
    return v[j]+(v[min(j+1,len(v)-1)]-v[j])*(i-j)

def calibrate(path):
    out={}
    with zipfile.ZipFile(path) as z:
        for group,suffix in [('ice','transition-control-fuel-motorcycle-daily-data.csv'),('ev','transition-treatment-electric-motorcycle-daily-data.csv')]:
            matches=[n for n in z.namelist() if n.endswith('/daily_data/'+suffix)]
            if len(matches)!=1:raise ValueError('Expected exactly one '+suffix)
            raw=z.read(matches[0]);rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
            keys=[(r['user_id'],r['date']) for r in rows]
            if len(set(keys))!=len(keys):raise ValueError('Duplicate rider-day')
            dist=defaultdict(list)
            for r in rows:
                if not r['user_id'] or not r['date']:raise ValueError('Missing key')
                km=float(r['distance_km'])
                if not math.isfinite(km) or km<0:raise ValueError('Invalid distance')
                dist[r['user_id']].append(km)
            vals=[st.mean(v) for v in dist.values()]
            d={'rows':len(rows),'riders':len(dist),'sha256':hashlib.sha256(raw).hexdigest(),'distance_rider_quantiles':{str(p):quantile(vals,p) for p in [.1,.25,.5,.75,.9]},'distance_mean':st.mean(float(r['distance_km']) for r in rows)}
            for col in ['fuel_amount_l','fuel_cost_kes','maintenance_kes','kwh_charging','battery_swap_cost_kes']:
                if col not in rows[0]:continue
                pairs=[(r['user_id'],float(r[col]),float(r['distance_km'])) for r in rows if r[col].strip() and float(r['distance_km'])>0]
                if any(not math.isfinite(v) or v<0 for _,v,_ in pairs):raise ValueError('Invalid '+col)
                if not pairs:raise ValueError('No paired records '+col)
                g=defaultdict(list)
                for uid,v,km in pairs:g[uid].append((v,km))
                ratios=[sum(v for v,km in a)/sum(km for v,km in a) for a in g.values()]
                dailymeans=[st.mean(v/km for v,km in a) for a in g.values()]
                loo=[sum(v for u,v,km in pairs if u!=uid)/sum(km for u,v,km in pairs if u!=uid) for uid in g] if len(g)>1 else []
                d[col]={'paired_rows':len(pairs),'paired_riders':len(g),'pooled':sum(v for u,v,km in pairs)/sum(km for u,v,km in pairs),'equal_rider':st.mean(ratios),'daily_ratio_mean':st.mean(v/km for u,v,km in pairs),'equal_rider_daily_ratio':st.mean(dailymeans),'loo_pooled_min':min(loo) if loo else None,'loo_pooled_max':max(loo) if loo else None,'rider_ratio_p25':quantile(ratios,.25),'rider_ratio_p75':quantile(ratios,.75)}
            out[group]=d
    out['provenance']={'dataset_doi':'10.17632/nv3rkn24zv.1','method':'Each cost/intensity uses its own nonmissing measurement matched to positive distance on the same rider-day; pooled sum(value)/sum(distance). Missing values are not zero. Quantiles use linear interpolation. Raw identifiers omitted.'}
    return out
if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--data-zip',required=True,type=Path);a.add_argument('--out',type=Path,default=Path(__file__).parent/'data/calibration.json');p=a.parse_args();p.out.parent.mkdir(parents=True,exist_ok=True);p.out.write_text(json.dumps(calibrate(p.data_zip),indent=2));print(p.out)
