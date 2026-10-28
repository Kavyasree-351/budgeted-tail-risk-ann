"""Exact structural check, NOT an ANN experiment or a new theorem.

Each fixed k has mean false-negative fraction .1. A selector using a visible
category can have mean .2. This illustrates a known selection issue, without
claiming that any existing ANN implementation actually behaves this way.
"""
import json
from pathlib import Path
from fractions import Fraction as F

weights=[F(1,10),F(2,10),F(7,10)]
losses=[[F(1),F(0)],[F(0),F(1,2)],[F(0),F(0)]]
selected=[0,1,0]
fixed=[sum(w*row[k] for w,row in zip(weights,losses)) for k in [0,1]]
adaptive=sum(w*row[k] for w,row,k in zip(weights,losses,selected))
assert fixed==[F(1,10),F(1,10)]
assert adaptive==F(1,5)
assert adaptive>max(fixed)
result={'fixed_k_mean_fnr':[str(x) for x in fixed],'selected_policy_mean_fnr':str(adaptive),
 'selector_information':'visible category only; no runtime labels',
 'scope':'Exact abstract loss-table counterexample, not a realizability proof for ConANN, not an empirical retrieval result and not claimed original.'}
target=Path(__file__).resolve().parent/'logic_check.json'
target.write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
