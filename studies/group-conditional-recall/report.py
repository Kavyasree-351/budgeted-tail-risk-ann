"""All-condition summaries, predefined gates, tables and scientific plots."""
import os,csv,json
from collections import defaultdict
import numpy as np
from data import ROOT,save,digest
os.environ.setdefault('MPLCONFIGDIR',str(ROOT.parents[1]/'work'/'mpl-cache'))
def write_csv(path,rows):
    with open(path,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
def stats(values):
    v=np.array([x for x in values if x is not None],dtype=float)
    return (float(v.mean()),float(v.std(ddof=1)) if len(v)>1 else None) if len(v) else (None,None)
def main():
    rows=[];paired=[];policies=[];timing=[]
    for path in sorted((ROOT/'results').glob('*_metrics.json')):
        obj=json.loads(path.read_text());rows+=obj['rows'];paired+=obj['paired'];policies+=obj['policies']
        d,s=path.name.split('_')[:2];timing.append(dict(dataset=d,seed=int(s),**obj['timing']))
    assert rows
    write_csv(ROOT/'results.csv',rows);write_csv(ROOT/'paired_work.csv',paired);write_csv(ROOT/'policies.csv',policies)
    groups=defaultdict(list)
    for r in rows:groups[(r['dataset'],r['scenario'],r['method'],r['scope'])].append(r)
    summary=[]
    for key,rr in sorted(groups.items()):
        s=dict(zip(['dataset','scenario','method','scope'],key));s['seeds']=len(rr)
        for field in ['fnr','corpus_distances','total_distances','n','mean_nprobe']:
            s[field+'_mean'],s[field+'_sd']=stats([r[field] for r in rr])
        summary.append(s)
    write_csv(ROOT/'summary.csv',summary)
    gate={};opportunity={}
    def row(d,seed,sc,m,scope):return next(r for r in rows if (r['dataset'],r['seed'],r['scenario'],r['method'],r['scope'])==(d,seed,sc,m,scope))
    for d in ['glove','fashion']:
        seeds=sorted({r['seed'] for r in rows if r['dataset']==d});ok=[];secondary=[];work=[];hard=[];allgroups=[];joint=[]
        for seed in seeds:
            global_r=row(d,seed,'iid','global_crc','marginal');h=row(d,seed,'iid','global_crc','hard_9_10')
            if global_r['fnr']<=.1 and h['fnr']>=.18 and h['ci_low']>.1:ok.append(seed)
            if global_r['fnr']<=.1 and h['fnr']>=.15:secondary.append(seed)
            p=next(p for p in paired if (p['dataset'],p['seed'],p['scenario'],p['method'])==(d,seed,'iid','group_crc10'))
            hnew=row(d,seed,'iid','group_crc10','hard_9_10')
            if p['total_distance_ratio']<=1:work.append(seed)
            if hnew['fnr']<=.1:hard.append(seed)
            if p['empirical_decile_violation_fraction']==0:allgroups.append(seed)
            if p['total_distance_ratio']<=1 and p['empirical_decile_violation_fraction']==0:joint.append(seed)
        gate[d]=dict(seeds=seeds,primary_18_percent_pass_seeds=ok,secondary_15_percent_pass_seeds=secondary,primary_pass=len(seeds)==5 and len(ok)>=4)
        opportunity[d]=dict(no_compute_inflation_seeds=work,hard_mean_target_seeds=hard,all_deciles_empirical_target_seeds=allgroups,
            joint_empirical_target_and_no_inflation_seeds=joint)
    save(ROOT/'gate.json',dict(failure=gate,engineering_checks=opportunity,replicated_primary_failure=all(v['primary_pass'] for v in gate.values()),
        novelty_established=False,full_stage_passed=False,reserved_queries_evaluated=False))
    def avg(d,sc,m,scope,field='fnr_mean'):return next(s[field] for s in summary if (s['dataset'],s['scenario'],s['method'],s['scope'])==(d,sc,m,scope))
    lines=['# Direction B — verified exploratory findings','',
        '**A subgroup gap is observed on GloVe, but the predefined >=18% primary failure gate is not met. Groupwise CRC is useful engineering here; a novel publishable method is not established.**','',
        f'Completed {len(timing)} dataset/seed runs, two calibration scenarios, ten methods and {len(rows)} subgroup/method conditions. All use the previously explored public query bank. Reserved final queries remain unevaluated. No paper or full benchmark has been generated.','',
        '## Primary result: unchanged query mixture','',
        '| Dataset | Global marginal FNR | Global top-two-decile FNR | Group CRC top-two-decile FNR | G-CRC/global total-work ratio | Primary passing seeds |',
        '|---|---:|---:|---:|---:|---|']
    for d in ['glove','fashion']:
        ratios=[p['total_distance_ratio'] for p in paired if p['dataset']==d and p['scenario']=='iid' and p['method']=='group_crc10']
        lines.append(f'| {d} | {avg(d,"iid","global_crc","marginal"):.4f} | {avg(d,"iid","global_crc","hard_9_10"):.4f} | {avg(d,"iid","group_crc10","hard_9_10"):.4f} | {np.mean(ratios):.3f} | {gate[d]["primary_18_percent_pass_seeds"]} |')
    lines+=['','Means above average five fitted runs, not independent production datasets. Seed SD and conditional query-bootstrap intervals are in summary.csv/results.csv. A pooled top-two-decile mean is not an individual decile guarantee. The lower 15% secondary criterion was prespecified and is reported in gate.json; it does not replace the failed 18% primary criterion.','',
        '## Matched-query method and ablation comparison','',
        'Total query distance work includes the common 64 centroid comparisons; exact search does not need centroids. Work ratio is relative to global CRC on the same seed, pilot and scenario. Empirical violating-decile fraction counts observed decile mean FNR>.10 and is NOT a formal violation probability.','',
        '| Dataset | Scenario | Method | Marginal FNR mean ± SD | Hard-pair FNR mean ± SD | Work ratio mean ± SD | Empirical violating-decile fraction |',
        '|---|---|---|---:|---:|---:|---:|']
    table_files=[]
    for d in ['glove','fashion']:
        for sc in ['iid','heldout_cells']:
            tex=[f'% {d}, {sc}. Exploratory means, not final evaluation.','\\begin{tabular}{lrrr}','\\hline','Method & Marginal FNR & Hard FNR & Work ratio \\\\','\\hline']
            for method in sorted({r['method'] for r in rows}):
                rr=[p for p in paired if p['dataset']==d and p['scenario']==sc and p['method']==method]
                ratio,rsd=stats([p['total_distance_ratio'] for p in rr]);violation,_=stats([p['empirical_decile_violation_fraction'] for p in rr])
                m=avg(d,sc,method,'marginal');ms=avg(d,sc,method,'marginal','fnr_sd');h=avg(d,sc,method,'hard_9_10');hs=avg(d,sc,method,'hard_9_10','fnr_sd')
                lines.append(f'| {d} | {sc} | {method} | {m:.4f} ± {(ms or 0):.4f} | {h:.4f} ± {(hs or 0):.4f} | {ratio:.3f} ± {(rsd or 0):.3f} | {violation:.2f} |')
                label=method.replace('_',r'\_');tex.append(f'{label} & {m:.4f} & {h:.4f} & {ratio:.3f} \\\\')
            tex+=['\\hline','\\end{tabular}'];file=f'table_{d}_{sc}.tex';table_files.append(file);(ROOT/file).write_text('\n'.join(tex)+'\n')
    (ROOT/'tables.tex').write_text('\n'.join(r'\input{'+f+'}' for f in table_files)+'\n')
    lines+=['','## Per-seed efficiency and residual risk','',
        '| Dataset | Seed | G-CRC/global work ratio | Paired mean work difference [95% bootstrap interval] | Observed violating-decile fraction |',
        '|---|---:|---:|---:|---:|']
    for p in paired:
        if p['scenario']=='iid' and p['method']=='group_crc10':lines.append(f'| {p["dataset"]} | {p["seed"]} | {p["total_distance_ratio"]:.3f} | {p["paired_work_difference"]:.1f} [{p["paired_work_ci_low"]:.1f}, {p["paired_work_ci_high"]:.1f}] | {p["empirical_decile_violation_fraction"]:.2f} |')
    lines+=['','The GloVe mean work ratio is slightly below one, but individual seeds include increases: an averaged saving is not evidence of no inflation for each run. Group CRC also leaves some realized pilot deciles above .10; its theorem is expected mean-risk control over calibration randomness, not a simultaneous certificate for every realized decile. The KL control is the simultaneous-confidence alternative and incurs much larger work.','',
        '## Held-out coarse-cell diagnostic','',
        '| Dataset | Method | Held-cell FNR mean | Seen-cell FNR mean |','|---|---|---:|---:|']
    for d in ['glove','fashion']:
        for m in ['global_crc','group_crc10','group_kl10','ood_exact_fallback']:
            lines.append(f'| {d} | {m} | {avg(d,"heldout_cells",m,"held_cells"):.4f} | {avg(d,"heldout_cells",m,"seen_cells"):.4f} |')
    lines+=['','Held cells are geometric exclusions, not semantic domain/OOD labels. Group CRC calibrated on other cells does not gain an unseen-support guarantee merely by sharing ambiguity bins. OOD exact fallback is explicitly conservative. These already explored query IDs are not fresh OOD confirmation.','',
        '## Feature and fitting overhead','',
        '| Dataset | Seed | Median feature/bin time per query (microseconds, 600-query batch) | Shared exact calibration-truth/curve time (seconds) |',
        '|---|---:|---:|---:|']
    for t in timing:lines.append(f'| {t["dataset"]} | {t["seed"]} | {t["feature_lookup_600_queries_seconds"]/600*1e6:.3f} | {t["calibration_truth_curve_seconds"]:.3f} |')
    lines+=['','All methods reuse identical calibration labels. Feature timing reuses existing centroid distances; it is not complete serving latency. Selection is O(nlist) CPU plus O(log 10) lookup, with zero extra corpus distances, not literal O(1) in index size. Fit times for both scenarios are in each metrics JSON.','',
        '## Novelty and limits','',
        '- The numerical assumption of 25–35% hard/OOD risk was not established. A marginal/subgroup gap is not a defect in the original marginal CRC theorem or proof of broken exchangeability.',
        '- Groupwise/Mondrian calibration and conditional risk control already exist, including the closely related HG-CRC preprint. Applying them to this ANN prototype is not a defensible new algorithm or theorem.',
        '- Ten calibration deciles have roughly 100 queries each. Do not claim simultaneous high-probability group safety from ordinary CRC, merge cells and claim leaf safety, or manufacture calibration examples for absent groups.',
        '- Raw Fashion pixels and GloVe-25 subsamples are not modern production multimodal/MS-MARCO embeddings. This is fixed-probe IVF, not faithful adaptive ConANN, Quake, DARTH+, HNSW or RAG task evaluation.',
        '- Data/group definitions and thresholds were frozen before pilot outcomes. No features, seeds or buckets were selected to force the gate. All individual D9/D10 rows, OOD controls, grouping ablations and unfavorable results are retained.',
        '- Final queries remain untouched. A positive paper would require distinct capability beyond known groupwise calibration, reproducible effect under faithful strong baselines, matched-risk compute comparison, fresh queries and independent index/dataset replication.','',
        'See PROTOCOL.md and THEORY_AND_PRIOR_WORK.md for assumptions, primary-source links and the elementary counterexample showing that subgroup safety cannot universally be free in compute.']
    (ROOT/'FINDINGS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    overview=lines[:12]+['','The complete report includes all seed uncertainty, calibration counts, known groupwise baselines, grouping/monotonicity/shuffled-feature ablations, confidence-bound comparison, held-out-cell tests and post-routing feature timings.','',
        '**Decision:** no full/fresh-query run or paper. The primary >=18% replicated failure gate failed on both datasets; G-CRC does not establish all-decile realized safety or consistently free compute. Its observed engineering benefit is useful but uses established methods.']
    (ROOT/'OVERVIEW.md').write_text('\n'.join(overview)+'\n',encoding='utf-8')
    plots(summary,paired)
    print(json.dumps(dict(conditions=len(rows),failure=gate,engineering_checks=opportunity)),flush=True)
def plots(summary,paired):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,2,figsize=(10,3.8),sharey=True)
    for ax,d in zip(axes,['glove','fashion']):
        for m in ['global_crc','group_crc10','monotone_crc10','worst_uniform','shuffled_crc10']:
            rr=[next(s for s in summary if (s['dataset'],s['scenario'],s['method'],s['scope'])==(d,'iid',m,f'decile_{g}')) for g in range(1,11)]
            ax.errorbar(range(1,11),[s['fnr_mean'] for s in rr],yerr=[s['fnr_sd'] or 0 for s in rr],label=m,marker='.',capsize=2)
        ax.axhline(.1,color='black',ls='--');ax.set_title(d);ax.set_ylim(bottom=0);ax.set_xlabel('Design-defined ambiguity decile')
    axes[0].set_ylabel('FNR mean ± seed SD');axes[1].legend(fontsize=6);fig.tight_layout();fig.savefig(ROOT/'decile_risk.png',dpi=180);fig.savefig(ROOT/'decile_risk.pdf');plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(10,3.8),sharey=True)
    methods=['global_crc','group_crc10','monotone_crc10','worst_uniform','group_crc5','group_crc2','shuffled_crc10']
    for ax,d in zip(axes,['glove','fashion']):
        vals=[[p['total_distance_ratio'] for p in paired if p['dataset']==d and p['scenario']=='iid' and p['method']==m] for m in methods]
        ax.bar(range(len(methods)),[np.mean(v) for v in vals],yerr=[np.std(v,ddof=1) for v in vals],capsize=2)
        ax.set_xticks(range(len(methods)),methods,rotation=65,ha='right',fontsize=7);ax.axhline(1,color='black',ls='--');ax.set_title(d)
    axes[0].set_ylabel('Total distance ratio to global CRC');fig.tight_layout();fig.savefig(ROOT/'work_tradeoff.png',dpi=180);fig.savefig(ROOT/'work_tradeoff.pdf');plt.close(fig)
if __name__=='__main__':main()
