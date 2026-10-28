"""Consistency checks of saved runs; no new evaluation queries accessed."""
import json
import numpy as np
import research as r
count=0
for d in ['glove','fashion']:
    provenance=json.loads((r.ROOT/'results'/f'{d}_provenance.json').read_text())
    sets=[set(provenance[k]) for k in ['design_ids','calibration_ids','pilot_ids','reserved_unevaluated_ids']]
    assert [len(x) for x in sets[:3]]==[400,1000,600]
    assert all(not(a&b) for i,a in enumerate(sets) for b in sets[i+1:])
    for seed in range(5):
        obj=json.loads((r.ROOT/'results'/f'{d}_{seed}_metrics.json').read_text())
        assert len(obj['rows'])==48
        raw=np.load(r.ROOT/'results'/f'{d}_{seed}_pilot.npz')
        for row in obj['rows']:
            key=row['selector']+'__'+row['method']
            loss=raw[key+'__loss'];work=raw[key+'__work']
            assert loss.shape==work.shape==(600,)
            assert np.all((loss>=0)&(loss<=1)) and np.all((work>=0)&(work<=provenance['base_size']))
            assert abs(float(loss.mean())-row['fnr'])<1e-7
            assert abs(float(work.mean())-row['distances'])<1e-7
            assert sum(row['k_histogram'])==600
            if row['method']=='exact':assert np.all(loss==0) and np.all(work==provenance['base_size'])
            count+=1
assert count==480
r.save(r.ROOT/'validation.json',dict(passed=True,conditions=count,checks=['query split disjointness including reserved IDs',
    'all five seeds retained','600 paired observations per condition','raw/summary agreement','loss and cost bounds','exact fallback zero loss']))
print('Validated',count,'conditions; no fresh queries evaluated.')
