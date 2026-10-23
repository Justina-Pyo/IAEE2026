"""Editable SVG and high-resolution PNG figures from computed CSV outputs."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Serif','font.size':10,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False})
rows=list(csv.DictReader((ROOT/'results/scenarios.csv').open()))
fig,ax=plt.subplots(figsize=(7,3.5))
labels=['60 km/day','80 km/day','110 km/day','Combined adverse']
for i,(a,label,color) in enumerate([('EV_BaaS_financed','Financed EV + BaaS','#246583'),('EV_BaaS_rental','Continuous rental + BaaS','#ae5736')]):
 vals=[float(next(r['saving_pct'] for r in rows if r['scenario']==n and r['arrangement']==a)) for n in ['km_60','baseline','km_110','combined_adverse']]
 bars=ax.bar([j+(i-.5)*.34 for j in range(4)],vals,width=.34,label=label,color=color)
 for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+(1 if v>=0 else -2),f'{v:.1f}',ha='center',va='bottom' if v>=0 else 'top',fontsize=9)
ax.axhline(0,color='black',lw=.7);ax.set_xticks(range(4),labels);ax.set_ylabel('Saving versus financed ICE (%)');ax.set_ylim(-35,75);ax.legend(frameon=False,loc='upper right');fig.tight_layout()
for ext in ['svg','png']:fig.savefig(ROOT/f'results/figure1_savings.{ext}',dpi=300)
plt.close(fig)
grid=list(csv.DictReader((ROOT/'results/thresholds.csv').open()));fig,ax=plt.subplots(figsize=(7,3.5))
for a,label,color in [('EV_BaaS_financed','Financed EV + BaaS','#246583'),('EV_BaaS_rental','Continuous rental + BaaS','#ae5736')]:
 r=[r for r in grid if r['arrangement']==a];ax.plot([float(x['km_day']) for x in r],[float(x['parity_swap_kes_km']) for x in r],label=label,color=color,lw=2)
ax.axhline(290/95,color='#555555',ls='--',label='Assumed swap price 3.05 KES/km');ax.set_xlabel('Distance per operating day (km)');ax.set_ylabel('TCO parity swap price (KES/km)');ax.set_xlim(10,200);ax.set_ylim(0,13);ax.legend(frameon=False,fontsize=9);fig.tight_layout()
for ext in ['svg','png']:fig.savefig(ROOT/f'results/figure2_thresholds.{ext}',dpi=300)
plt.close(fig)
