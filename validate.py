"""Check saved safety predicates, source separation and pointwise bounds."""
import json
import numpy as np
from data import ROOT,save
from control import TARGET,DELTA_PLUS,DELTA_MINUS,risks,max_prefix,apply,test_values,infeasibility
def main():
    seen=set();conditions=0;group_rows=0
    for path in sorted((ROOT/'results').glob('*_metrics.json')):
        prefix=path.name.replace('_metrics.json','');obj=json.loads(path.read_text());prov=json.loads((ROOT/'results'/(prefix+'_provenance.json')).read_text())
        seen.add((prov['dataset'],prov['seed']))
        core=set(prov['corpus_ids']);cal=set(prov['calibration_training_ids'])
        assert len(cal)==5000 and not(core&cal)
        old=[set(prov[k]) for k in ['design_ids','previous_calibration_ids_not_used','pilot_ids','reserved_unevaluated_ids']]
        assert [len(s) for s in old[:3]]==[400,1000,600]
        assert all(not(a&b) for i,a in enumerate(old) for b in old[i+1:])
        raw=np.load(ROOT/'results'/(prefix+'_raw.npz'))
        cl=raw['calibration_loss'];cw=raw['calibration_work'];cg=raw['calibration_groups'];cs=raw['calibration_cells']
        pl=raw['pilot_loss'];pw=raw['pilot_work'];pg=raw['pilot_groups'];ps=raw['pilot_cells'];dec=raw['pilot_deciles']
        assert cl.shape==(5000,65) and pl.shape==(600,65) and cg.shape==(5000,15)
        assert np.all(cl[:,0]==1) and np.all(pl[:,0]==1) and np.all(cl[:,-1]==0) and np.all(pl[:,-1]==0)
        assert np.all(np.diff(cl,axis=1)<=1e-12) and np.all(np.diff(pw,axis=1)>=0)
        assert len(obj['metrics'])==32 and len(obj['risks'])==480 and len(obj['sample_ablation'])==48
        for p in obj['paths']:
            family=np.array(p['path']);assert np.all(np.diff(family,axis=0)>=0) and np.all(family[-1]==64)
        for m in obj['metrics']:
            key=f'{m["cap_fraction"]}__{m["method"]}';v=raw[key+'__loss'];w=raw[key+'__work'];p=raw[key+'__prefix'];cap=m['cap']
            assert np.allclose(v,pl[np.arange(600),p]) and np.array_equal(w,pw[np.arange(600),p])
            assert abs(v.mean()-m['mean_fnr'])<1e-12 and abs(w.mean()-m['mean_distances'])<1e-9
            assert int((w>cap).sum())==m['cap_violation_count']
            if m['method']!='group_crc_uncapped':
                assert np.all(w<=cap)
                pp=max_prefix(pw,cap);floor=pl[np.arange(600),pp];assert np.all(v>=floor-1e-12)
            z,n=risks(v,pg);assert int(((z>TARGET+1e-12)&(n[:,None]>0)).sum())==m['empirical_constraint_violations']
            if m['nominal_issued']:
                policy=np.array(obj['policies'][key]);cp=apply(policy,cs,max_prefix(cw,cap));cv=cl[np.arange(5000),cp]
                structural=cap>=prov['base_size']+64 and np.all(policy==64)
                assert structural or test_values(cv,cg)[0].max()<=DELTA_PLUS+1e-12
            if m['status']=='nominal_infeasible':assert infeasibility(cl,cw,cg,cap)['rejected']
            conditions+=1
        for r in obj['risks']:
            g=prov['group_names'].index(r['group']);take=pg[:,g];v=raw[f'{r["cap_fraction"]}__{r["method"]}__loss'][take]
            assert r['n']==len(v)
            if len(v):
                assert abs(v.mean()-r['mean_fnr'])<1e-12
                assert abs(np.mean(v>.2+1e-12)-r['tail20'])<1e-12
                assert abs(np.mean(v>.5+1e-12)-r['tail50'])<1e-12
            else:assert r['mean_fnr'] is None
            group_rows+=1
    assert seen=={(d,s) for d in ['glove','fashion'] for s in range(5)}
    save(ROOT/'validation.json',dict(passed=True,runs=len(seen),policy_conditions=conditions,group_rows=group_rows,
        checks=['fresh TRAIN calibration excludes corpus','original reserved TEST bank untouched',
                'all seeds/caps/methods retained','raw-summary and severity predicates agree',
                'no capped-policy overruns','prefix lower-envelope domination','issued calibration criteria',
                'infeasibility witness criteria','nested design-only path metadata']))
    print('Validated',conditions,'policy cases and',group_rows,'group rows.')
if __name__=='__main__':main()
