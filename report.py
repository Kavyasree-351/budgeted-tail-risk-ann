"""Aggregate the frozen cap problem, retaining infeasible/unknown outcomes."""
import os,csv,json
from collections import defaultdict
import numpy as np
from data import ROOT,save
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'work'/'mpl-cache'))
METHODS=['overlap_repair','uniform_ltt','cell_shift_ltt','no_overlap','no_tail','cap_max','group_crc_capped','group_crc_uncapped']
def csv_file(path,rows):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def average(x):
    a=[v for v in x if v is not None]
    return (float(np.mean(a)),float(np.std(a,ddof=1)) if len(a)>1 else 0.) if a else (None,None)
def main():
    metrics=[];risks=[];paired=[];sample=[];timings=[]
    for path in sorted((ROOT/'results').glob('*_metrics.json')):
        obj=json.loads(path.read_text());metrics+=obj['metrics'];risks+=obj['risks'];paired+=obj['paired'];sample+=obj['sample_ablation']
        timings.append(dict(run=path.stem,**obj['timing']))
    csv_file(ROOT/'policy_metrics.csv',metrics);csv_file(ROOT/'group_risks.csv',risks);csv_file(ROOT/'paired_comparisons.csv',paired);csv_file(ROOT/'sample_size_ablation.csv',sample);csv_file(ROOT/'timings.csv',timings)
    groups=defaultdict(list)
    for m in metrics:groups[(m['dataset'],m['cap_fraction'],m['method'])].append(m)
    summary=[]
    for key,rr in sorted(groups.items()):
        s=dict(zip(['dataset','cap_fraction','method'],key));s['seeds']=len(rr)
        for status in ['nominal_certified','nominal_infeasible','uncertified','uncertified_reference']:s[status]=sum(r['status']==status for r in rr)
        issued=[r for r in rr if r['nominal_issued']]
        for field in ['mean_fnr','mean_distances','max_distances','cvar90','empirical_constraint_violations']:
            s[field+'_issued_mean'],s[field+'_issued_sd']=average([r[field] for r in issued])
            s[field+'_diagnostic_mean'],_=average([r[field] for r in rr])
        s['cap_violations_sum']=sum(r['cap_violation_count'] for r in rr)
        s['finite_pilot_infeasible_runs']=sum(r['finite_pilot_infeasible'] for r in rr)
        summary.append(s)
    csv_file(ROOT/'summary.csv',summary)
    gate={};components={}
    for dataset in ['glove','fashion']:
        eligible=[];safe=[];passes=[];comparisons=[];comp={m:[] for m in ['no_overlap','no_tail']}
        for seed in range(5):
            rr={r['method']:r for r in metrics if r['dataset']==dataset and r['seed']==seed and r['cap_fraction']==.25}
            if 'overlap_repair' not in rr:continue
            candidate=rr['overlap_repair']
            if candidate['nominal_issued']:eligible.append(seed)
            safety=candidate['nominal_issued'] and candidate['cap_violation_count']==0 and candidate['empirical_constraint_violations']==0
            if safety:safe.append(seed)
            baselines=[rr[m] for m in ['uniform_ltt','cell_shift_ltt'] if m in rr and rr[m]['nominal_issued']]
            if len(baselines)==2:
                best=min(baselines,key=lambda r:r['mean_distances'])
                p=next(p for p in paired if (p['dataset'],p['seed'],p['cap_fraction'],p['comparison'])==(dataset,seed,.25,best['method']))
                ratio=candidate['mean_distances']/best['mean_distances']
                comparisons.append(dict(seed=seed,best_baseline=best['method'],work_ratio=ratio,paired_ci_high=p['ci_high']))
                if safety and ratio<=.90 and p['ci_high']<0:passes.append(seed)
            for ablation in comp:
                p=next(p for p in paired if (p['dataset'],p['seed'],p['cap_fraction'],p['comparison'])==(dataset,seed,.25,ablation))
                if p['both_nominally_issued'] and p['ci_high']<0:comp[ablation].append(seed)
        gate[dataset]=dict(issued_seeds=eligible,empirical_all_target_and_cap_pass_seeds=safe,
            ten_percent_strong_baseline_improvement_seeds=passes,strong_baseline_comparisons=comparisons,opportunity_pass=len(passes)>=4)
        components[dataset]=comp
    save(ROOT/'gate.json',dict(primary_cap_fraction=.25,datasets=gate,component_evidence_counts=components,
        replicated_opportunity=all(g['opportunity_pass'] for g in gate.values()),novelty_established=False,
        full_stage_complete=False,final_test_queries_touched=0))
    lines=['# Cap-constrained simultaneous mean/tail control — findings','',
        '**New setup tested:** a hard per-query distance cap, fifteen overlapping groups, three mean/severity risks, and feasible/infeasible/unknown decisions. This does not reuse the old subgroup-FNR failure gate. No publication novelty is established.','',
        f'Completed {len(timings)} dataset/seed runs, {len(metrics)} policy/cap conditions and {len(risks)} group rows (three risks each). Calibration uses 5,000 fresh TRAIN vectors excluded from the index; all methods share labels. The old 400-design/600-pilot queries remain exploratory. The final 8,000 official query IDs remain unopened.','',
        '## Targets and theorem scope','',
        'For every declared group: mean FNR<=.10, Pr(FNR>.20)<=.10 and Pr(FNR>.50)<=.05. These imply 90th/95th-percentile bounds, not CVaR control. THEORY.md proves deterministic cap compliance and the prefix-class floor; selected-policy and infeasibility properties specialize existing LTT/Chernoff machinery. Fresh calibration can certify its finite source-bank risk under uniform sampling; certificates remain labeled nominal for official-test deployment because the pilot was previously inspected and arbitrary production/OOD shift is outside the theorem.','',
        '## Feasibility profile (candidate; all five seeds retained)','',
        '| Dataset | Corpus-work cap +64 centroids | Nominally issued | Infeasibility witnesses | Insufficient evidence | Empirically infeasible finite pilot workloads |',
        '|---|---:|---:|---:|---:|---:|']
    for s in summary:
        if s['method']=='overlap_repair':lines.append(f'| {s["dataset"]} | {s["cap_fraction"]:.0%} | {s["nominal_certified"]}/5 | {s["nominal_infeasible"]}/5 | {s["uncertified"]}/5 | {s["finite_pilot_infeasible_runs"]}/5 |')
    lines+=['','Concrete witness example: GloVe seed 0, 10% cap, upper-ambiguity/far intersection had a calibration floor exceedance rate Pr(FNR>.20)=0.3312 versus target .10 (n=1739; one-sided p≈2.47e-150). Even the largest permitted prefix has that source-bank risk estimate. This is a prefix-class feasibility issue, not merely a bad fitted threshold. Full witness records for every case are retained in policy_metrics.csv/JSON.']
    lines+=['','Infeasibility concerns exact-within-list PREFIX IVF under this distance counter; it is not an impossibility theorem for arbitrary ANN methods. Unknown is not rejected feasibility. When no policy is issued, diagnostic loss/work fields describe the maximum feasible prefix, NOT a deployed/certified output. Guarantees are pointwise per cap/method; choosing among all displayed caps using this calibration is not covered. A heuristic profile is not a proven optimal Pareto frontier.','',
        '## Primary 25% cap: matched-guarantee comparisons','',
        '| Dataset | Method | Issued | Mean FNR ± seed SD (issued only) | Mean total distances ± SD (issued only) | Maximum observed query distances | Empirical target-violation runs |',
        '|---|---|---:|---:|---:|---:|---:|']
    for dataset in ['glove','fashion']:
        tex=[f'% {dataset}, primary 25%-corpus distance cap; exploratory data.','\\begin{tabular}{lrrr}','\\hline','Method & Issued & Mean FNR & Mean distances \\\\','\\hline']
        for method in METHODS:
            rr=[r for r in metrics if r['dataset']==dataset and r['cap_fraction']==.25 and r['method']==method]
            actual=[r for r in rr if r['nominal_issued']];v,vs=average([r['mean_fnr'] for r in actual]);w,ws=average([r['mean_distances'] for r in actual])
            maxw=max([r['max_distances'] for r in actual],default=None);viol=sum(r['empirical_constraint_violations']>0 for r in actual)
            if actual:description=f'{v:.4f} ± {vs:.4f}';cost=f'{w:.1f} ± {ws:.1f}'
            else:description='not issued';cost='not issued'
            lines.append(f'| {dataset} | {method} | {len(actual)}/5 | {description} | {cost} | {maxw} | {viol}/{len(actual)} |')
            label=method.replace('_',r'\_');tex.append(f'{label} & {len(actual)}/5 & '+(f'{v:.4f} & {w:.0f}' if actual else '-- & --')+' \\\\')
        tex+=['\\hline','\\end{tabular}'];(ROOT/f'table_{dataset}.tex').write_text('\n'.join(tex)+'\n')
    lines+=['','Ordinary Group CRC references are deliberately unissued for this stronger objective; their real diagnostic outcomes and cap violations remain in policy_metrics.csv/group_risks.csv. Do not compare their cheaper work as if they supplied the same tail/confidence/cap guarantee. Issued-policy empirical group violations remain possible from finite pilot variation even when a population-risk confidence theorem applies.','',
        '## Candidate versus strongest simple path, seed by seed','',
        '| Dataset | Seed | Better uniform/template baseline | Candidate/baseline work ratio | Paired work-difference upper 95% endpoint |',
        '|---|---:|---|---:|---:|']
    for d,g in gate.items():
        for p in g['strong_baseline_comparisons']:lines.append(f'| {d} | {p["seed"]} | {p["best_baseline"]} | {p["work_ratio"]:.3f} | {p["paired_ci_high"]:.1f} |')
    lines+=['','Primary gate (>=10% saving, paired upper endpoint<0, observed targets and cap all met, >=4/5 seeds on BOTH datasets): '+str(all(g['opportunity_pass'] for g in gate.values()))+'. No threshold was relaxed after inspection. Ablation evidence counts are descriptive in gate.json; a match or loss against an ablation is retained, not hidden.','',
        '## Calibration-size ablation at primary cap','',
        '| Dataset | Method | Fresh calibration count | Nominally issued | Infeasible | Unknown |','|---|---|---:|---:|---:|---:|']
    for d in ['glove','fashion']:
        for m in ['overlap_repair','uniform_ltt','cell_shift_ltt']:
            for n in [1000,5000]:
                ss=[x for x in sample if x['dataset']==d and x['method']==m and x['ncal']==n and x['cap_fraction']==.25]
                lines.append(f'| {d} | {m} | {n} | {sum(x["status"]=="nominal_certified" for x in ss)}/5 | {sum(x["status"]=="nominal_infeasible" for x in ss)}/5 | {sum(x["status"]=="uncertified" for x in ss)}/5 |')
    lines+=['','5,000 calibration examples are additional supervision, not a free algorithmic cure for fragmentation. At 5% tail risk and .025 test level, a zero-exceedance count requires at least 72 examples in a group. The 1,000-example ablation uses a prefix of the same fresh pool; it never retunes group definitions.','',
        '## Cost, uncertainty and limits','',
        '- Every comparison uses the same corpus, labels, groups, targets, cap and confidence procedure. The calibration family is learned only on 400 design queries. Fresh calibration source rows are excluded from corpus IDs; shared train/test query-law assumptions are explicit, not guaranteed by a filename.',
        '- Exact labeling computes distances for 400 design + 5000 calibration + 600 pilot queries. This supervision cost is shared by all methods, but is substantially larger than prior 1000-query studies. Stored truth_curve_seconds times the combined preparation, NOT calibration alone.',
        '- path_learning_seconds covers all three design-repair variants at that cap. The recorded calibration_selection_seconds includes the 1000-prefix calibration ablation and metadata construction for path methods; it is diagnostic rather than a clean deployment-only timing.',
        '- Query counts bound vector-distance evaluations, not wall-clock latency, memory, GPU operations or all CPU instructions. Group/cell routing and cap-prefix lookup have additional small CPU work. Zero-prefix queries incur FNR=1; no abstention is scored as success.',
        '- Bootstrap CIs are conditional exploratory query resamples. Seed SD is descriptive; seed runs share public datasets and can share source queries. Pilot queries were seen in earlier research. No fresh official TEST confirmation is claimed.',
        '- The maximum-p/FST multiple-risk theorem is established LTT, quantile CRC already exists, and the basic feasibility lemma is elementary monotonicity. Greedy overlap-aware allocation is a candidate heuristic without global optimality. Better numbers alone would not establish novelty.',
        '- Full publication claims require a distinctive capability beyond known cost-aware LTT/Pareto testing, stronger ANN systems and larger/modern embedding workloads, a frozen independent confirmation run, and actual latency/memory measurements. No paper/full experiment was produced.','',
        'One empirical target crossing at the primary cap was Fashion seed 4, ambiguity D8: Pr(FNR>.20)=6/54=.1111 versus .10; its bootstrap interval [.0370,.2037] includes the target. This fails the preregistered strict empirical gate, but is not by itself a contradiction of a population-risk confidence guarantee.','',
        '## Attempt ledger','',
        '1. Defined a new hard-cap and mean/tail problem plus proofs BEFORE running its pilot; did not lower the old 18% threshold.',
        '2. Before pilot outcomes, amended calibration to 5000 fresh non-corpus TRAIN queries after deriving the small-group sample threshold. Added a 1000-prefix ablation; kept all risk/confidence/cost gates unchanged.',
        '3. Initial process failed before the first result due memory allocation pressure. Replaced full HDF5/image/corpus float64 reads with bounded-memory streaming and verified blocked top-k against direct sorting. Archived only an old public download cache with decompressed SHA verification; previous experiment outputs were retained.',
        '4. An intermediate process accumulated bootstrap matrices and failed before Fashion runs. Cleared the cache per seed and stored compact exact multinomial bootstrap counts; reran ALL seeds. Scientific losses, policies and targets were unchanged.',
        '5. Retained infeasible, unknown, bad baselines, work increases and missing component improvements. Final test-query touch count remains zero.']
    (ROOT/'FINDINGS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    overview=[lines[0],lines[1],lines[2],lines[3],lines[4],'','## Feasibility at tight caps','']
    for d in ['glove','fashion']:
        for cap in [.10,.25]:
            s=next(s for s in summary if s['dataset']==d and s['method']=='overlap_repair' and s['cap_fraction']==cap)
            overview.append(f'- {d}, {cap:.0%} corpus-work allowance (+64 centroid comparisons): issued {s["nominal_certified"]}/5, infeasibility evidence {s["nominal_infeasible"]}/5, unknown {s["uncertified"]}/5.')
    overview+=['','## Primary candidate and strongest baseline','']
    for d,g in gate.items():
        candidate=next(s for s in summary if s['dataset']==d and s['cap_fraction']==.25 and s['method']=='overlap_repair')
        uniform=next(s for s in summary if s['dataset']==d and s['cap_fraction']==.25 and s['method']=='uniform_ltt')
        template=next(s for s in summary if s['dataset']==d and s['cap_fraction']==.25 and s['method']=='cell_shift_ltt')
        overview.append(f'- {d}: issued {len(g["issued_seeds"])}/5; mean distance work candidate={candidate["mean_distances_issued_mean"]}, uniform LTT={uniform["mean_distances_issued_mean"]}, template LTT={template["mean_distances_issued_mean"]}. >=10% improvement against the stronger baseline with all gates: seeds {g["ten_percent_strong_baseline_improvement_seeds"]}.')
    overview+=['','**Decision:** novelty remains unestablished; no paper or final-query run. The candidate must beat the best matched-guarantee baseline and demonstrate both components, not merely beat ordinary mean-risk CRC or a conservative union bound. See FINDINGS.md for all conditions, uncertainty, label costs, ablations and negative outcomes; THEORY.md contains the precise propositions and their established prior-work basis.']
    (ROOT/'OVERVIEW.md').write_text('\n'.join(overview)+'\n',encoding='utf-8')
    plots(summary,metrics)
    print(json.dumps(dict(runs=len(timings),policy_conditions=len(metrics),group_rows=len(risks),gate=gate)),flush=True)
def plots(summary,metrics):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,3.8),sharey=True);caps=[.1,.25,.5,1.]
    for ax,d in zip(axes,['glove','fashion']):
        bottom=np.zeros(4)
        for status,color in [('nominal_certified','#228833'),('nominal_infeasible','#cc6677'),('uncertified','#ddaa33')]:
            v=[next(s[status] for s in summary if s['dataset']==d and s['method']=='overlap_repair' and s['cap_fraction']==c) for c in caps]
            ax.bar(range(4),v,bottom=bottom,color=color,label=status);bottom+=v
        ax.set_xticks(range(4),['10%','25%','50%','100%']);ax.set_title(d);ax.set_xlabel('Corpus-distance allowance (+64 centroids)');ax.set_ylim(0,5.5)
    axes[0].set_ylabel('Seed outcomes (all five retained)');axes[1].legend(fontsize=7);fig.tight_layout();fig.savefig(ROOT/'feasibility.png',dpi=180);fig.savefig(ROOT/'feasibility.pdf');plt.close(fig)
    methods=['overlap_repair','uniform_ltt','cell_shift_ltt','no_overlap','no_tail']
    fig,axes=plt.subplots(1,2,figsize=(10,3.8))
    for ax,d in zip(axes,['glove','fashion']):
        rr=[next(s for s in summary if s['dataset']==d and s['cap_fraction']==.25 and s['method']==m) for m in methods]
        ax.bar(range(5),[s['mean_distances_issued_mean'] or 0 for s in rr],yerr=[s['mean_distances_issued_sd'] or 0 for s in rr],capsize=2)
        ax.set_xticks(range(5),[m+' ('+str(s['nominal_certified'])+'/5)' for m,s in zip(methods,rr)],rotation=55,ha='right',fontsize=7);ax.set_title(d);ax.set_ylabel('Mean total query distances, issued only')
    fig.tight_layout();fig.savefig(ROOT/'primary_work.png',dpi=180);fig.savefig(ROOT/'primary_work.pdf');plt.close(fig)
if __name__=='__main__':main()
