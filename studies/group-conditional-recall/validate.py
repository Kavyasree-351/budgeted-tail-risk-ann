"""Saved-outcome and certificate checks; no new query evaluation."""
import json
import numpy as np
from data import ROOT,save
def main():
    seen=set();conditions=0
    for path in sorted((ROOT/'results').glob('*_metrics.json')):
        prefix=path.name.replace('_metrics.json','');obj=json.loads(path.read_text())
        prov=json.loads((ROOT/'results'/(prefix+'_provenance.json')).read_text());seen.add((prov['dataset'],prov['seed']))
        split=[set(prov[k]) for k in ['design_ids','calibration_ids','pilot_ids','reserved_unevaluated_ids']]
        assert [len(s) for s in split[:3]]==[400,1000,600]
        assert all(not(a&b) for i,a in enumerate(split) for b in split[i+1:])
        raw=np.load(ROOT/'results'/(prefix+'_raw.npz'));pg=raw['pilot_deciles'];ch=raw['calibration_held_cells'];ph=raw['pilot_held_cells'];cg=raw['calibration_deciles']
        assert len(pg)==600 and np.all((pg>=0)&(pg<10))
        assert np.all(np.diff(raw['calibration_loss_curves'],axis=1)<=1e-12)
        assert np.all(raw['pilot_loss_curves'][:,-1]==0)
        assert len(obj['rows'])==280 and len(obj['paired'])==20 and len(obj['policies'])==20
        for policy in obj['policies']:
            which=np.ones(1000,dtype=bool) if policy['scenario']=='iid' else ~ch
            assert policy['calibration_ids_used']==np.asarray(prov['calibration_ids'])[which].tolist()
            assert policy['calibration_counts']==np.bincount(cg[which],minlength=10).tolist()
            if policy['method']=='group_crc10':
                for g,p in enumerate(policy['budgets']):
                    loss=raw['calibration_loss_curves'][which&(cg==g),p-1]
                    assert p==64 or (loss.sum()+1)/(len(loss)+1)<=.1+1e-12
        for r in obj['rows']:
            key=r['scenario']+'__'+r['method'];v=raw[key+'__loss'];w=raw[key+'__corpus_distances'];p=raw[key+'__nprobe']
            assert np.allclose(v,raw['pilot_loss_curves'][np.arange(600),p-1])
            assert np.array_equal(w,raw['pilot_work_curves'][np.arange(600),p-1])
            if r['scope'].startswith('decile_'):mask=pg==int(r['scope'].split('_')[1])-1
            else:mask={'marginal':np.ones(600,dtype=bool),'hard_9_10':pg>=8,'held_cells':ph,'seen_cells':~ph}[r['scope']]
            assert r['n']==int(mask.sum())
            if r['n']:
                assert abs(v[mask].mean()-r['fnr'])<1e-12
                assert abs(w[mask].mean()-r['corpus_distances'])<1e-9
            else:assert r['fnr'] is None
            if r['method']=='exact':assert np.all(v==0) and np.all(w==prov['base_size'])
            if r['method']=='ood_exact_fallback' and r['scenario']=='heldout_cells':assert np.all(v[ph]==0)
            if r['method'] in ['monotone_crc10','worst_uniform']:
                base=raw[r['scenario']+'__group_crc10__loss'];bw=raw[r['scenario']+'__group_crc10__corpus_distances']
                assert np.all(v<=base+1e-12) and np.all(w>=bw)
            conditions+=1
    assert seen=={(d,s) for d in ['glove','fashion'] for s in range(5)}
    assert conditions==2800
    save(ROOT/'validation.json',dict(passed=True,dataset_seed_runs=len(seen),conditions=conditions,
        checks=['all seeds retained','exploratory/reserved split separation','raw/summary agreement',
                'group calibration criteria and correct group counts','OOD calibration exclusion',
                'monotone and uniform policy dominance','exact and unseen-cell fallback safety']))
    print('Validated',conditions,'conditions; reserved queries not accessed.')
if __name__=='__main__':main()
