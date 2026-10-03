#!/usr/bin/env python3
"""Check a declared measurement contract; optional narrow SciPy paired cluster-mean CI.

Does not verify declaration truth, choose experimental units, or launch experiments.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import statistics
import warnings


def load(path):
    def unique(pairs):
        d = {}
        for k, v in pairs:
            if k in d:
                raise ValueError('duplicate JSON key: ' + k)
            d[k] = v
        return d
    def invalid(s):
        raise ValueError('nonfinite JSON constant: ' + s)
    return json.loads(Path(path).read_text(), object_pairs_hook=unique, parse_constant=invalid)


def finite(v):
    try:
        return type(v) in (int, float) and math.isfinite(v)
    except OverflowError:
        return False


def review(packet, analyze=False):
    if type(packet) is not dict:
        raise ValueError('packet must be an object')
    d = packet.get('design', {})
    if type(d) is not dict:
        raise ValueError('design must be an object')
    rows = packet.get('rows', [])
    if type(rows) is not list or len(rows) > 20000:
        raise ValueError('rows must be a list of at most 20000 paired records')
    grouped = defaultdict(list)
    seen = set()
    for row in rows:
        if type(row) is not dict or set(row) != {'id', 'cluster', 'baseline', 'candidate'}:
            raise ValueError('each row needs id, cluster, baseline, candidate')
        if any(type(row[k]) is not str or not row[k] or len(row[k]) > 200 for k in ('id', 'cluster')):
            raise ValueError('nonempty bounded id and cluster required')
        if row['id'] in seen or not all(finite(row[k]) for k in ('baseline', 'candidate')):
            raise ValueError('duplicate id or nonfinite/boolean measurement')
        seen.add(row['id'])
        delta = row['candidate'] - row['baseline']
        if not finite(delta):
            raise ValueError('nonfinite paired difference')
        grouped[row['cluster']].append(delta)
    if len(grouped) > 1000:
        raise ValueError('at most 1000 clusters in portable analysis')
    issues = []
    def need(ok, code, requirement):
        if not ok:
            issues.append({'code': code, 'needed': requirement})
    for key in ('claim_id', 'unit'):
        need(type(packet.get(key)) is str and bool(packet[key].strip()), key, 'record ' + key)
    need(packet.get('direction') in ('higher', 'lower'), 'direction', 'declare whether higher or lower is beneficial')
    need(d.get('kind') in ('accuracy', 'performance'), 'kind', 'choose accuracy or performance and its experimental unit')
    need(d.get('estimand') == 'equal_cluster_mean_paired_difference', 'estimand', 'justify equally weighted independent cluster means; other estimands need a dedicated analysis')
    need(bool(rows), 'raw_data', 'recover paired raw outputs/timings and sample/session IDs; summaries cannot produce CI')
    need(3 <= len(grouped), 'independent_units', 'collect multiple independent clusters/sessions; repeated timers are not model trials; 3 is a numerical floor, not adequate power')
    for key in ('cluster_unit', 'independence_evidence', 'noise_sources', 'precision_plan', 'protocol_reference', 'outlier_rule'):
        need(type(d.get(key)) is str and bool(d[key].strip()), key, 'supply justified ' + key)
    for key in ('paired', 'protocol_matched', 'threshold_prespecified', 'no_test_tuning'):
        need(d.get(key) is True, key, 'establish ' + key + '; a declaration is not execution evidence')
    need(d.get('stopping_rule') == 'fixed_before_collection', 'stopping_rule', 'use a prespecified fixed sampling rule; optional stopping/sequential designs need a dedicated analysis')
    need(type(d.get('planned_clusters')) is int and d['planned_clusters'] == len(grouped), 'planned_clusters', 'verify the frozen independent-unit sample count and missingness; do not revise the planned count after observing results')
    need(finite(d.get('target_halfwidth')) and d['target_halfwidth'] > 0, 'target_halfwidth', 'prespecify desired interval halfwidth in the stated unit; establish feasibility from an independent pilot')
    need(d.get('family') == 'single_prespecified_primary', 'multiplicity', 'declare full comparison family/selection history; use a dedicated correction or fresh confirmatory set')
    need(d.get('criterion') in ('superiority', 'noninferiority', 'equivalence'), 'criterion', 'prespecify a claim criterion, not a post-hoc p-value threshold')
    need(finite(d.get('margin')) and d['margin'] > 0, 'margin', 'prespecify a positive practical/noninferiority/equivalence margin in the stated unit')
    if d.get('kind') == 'performance':
        for key in ('hardware_software_shapes_precision', 'warmup_compile_autotune', 'synchronization', 'cold_or_steady', 'exclusion_evidence', 'session_sampling'):
            need(type(d.get(key)) is str and bool(d[key].strip()), key, 'record ' + key)
        need(d.get('order') in ('randomized_paired', 'interleaved_paired'), 'order', 'counter order/drift with randomized or interleaved paired comparisons')
    if d.get('kind') == 'accuracy':
        for key in ('dataset_sampling', 'seed_decoding_scorer'):
            need(type(d.get(key)) is str and bool(d[key].strip()), key, 'record ' + key)
    effect = statistics.mean(statistics.mean(v) for v in grouped.values()) if grouped else None
    if effect is not None and not finite(effect):
        raise ValueError('nonfinite aggregate difference')
    out = {'schema': 'measurement-review/v1', 'claim_id': packet.get('claim_id'),
           'input_sha256': hashlib.sha256(json.dumps(packet, sort_keys=True, allow_nan=False).encode()).hexdigest(),
           'status': 'needs_redesign' if issues else 'contract_ready_not_verified',
           'rows': len(rows), 'independent_clusters_declared': len(grouped),
           'effect_candidate_minus_baseline': effect, 'unit': packet.get('unit'),
           'issues': issues, 'ci': None, 'criterion_met': None, 'precision_met': None,
           'limits': ['Declarations and cluster independence require reviewer verification.',
                      'No p-value; no automatic claim of model improvement or equivalence.',
                      'A finite deterministic benchmark delta need not generalize.',
                      'Marginal CI overlap is not a paired difference test.']}
    if analyze and not issues:
        try:
            import numpy as np
            import scipy
            from scipy.stats import bootstrap
        except ImportError:
            out['status'] = 'blocked_dependency'
            out['issues'].append({'code': 'scipy', 'needed': 'use an approved environment with NumPy and SciPy supporting bootstrap rng (>=1.15); no auto-install'})
        else:
            deltas = np.asarray([statistics.mean(v) for v in grouped.values()])
            if packet['direction'] == 'lower':
                deltas = -deltas
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter('error')
                    result = bootstrap((deltas,), np.mean, method='BCa', confidence_level=.95,
                                       n_resamples=9999, batch=64, rng=np.random.default_rng(42))
                lo, hi = map(float, result.confidence_interval)
                if not math.isfinite(lo) or not math.isfinite(hi) or lo > hi:
                    raise ValueError('nonfinite or reversed interval')
            except (Warning, ValueError, TypeError) as exc:
                out['status'] = 'needs_redesign'
                out['issues'].append({'code':'unsupported_or_degenerate_ci', 'needed':'inspect cluster variation and library compatibility; no zero-width certainty from repeated identical values', 'detail':str(exc)})
            else:
                margin = d['margin']
                met = {'superiority': lo > margin, 'noninferiority': lo > -margin,
                       'equivalence': lo > -margin and hi < margin}[d['criterion']]
                out.update(status='conditional_interval_only', ci={'low':lo,'high':hi,'confidence':.95,
                           'orientation':'positive favors candidate', 'unit':packet['unit'], 'method':'SciPy BCa mean of paired cluster means',
                           'alternative':'two-sided', 'resamples':9999,'rng_seed':42,'scipy_version':scipy.__version__},
                           criterion_met=bool(met), precision_met=bool((hi-lo)/2 <= d['target_halfwidth']))
    out['redesign_tasks'] = [{'owner':'research-implement-optimize', 'issue':i['code'], 'required_data':i['needed'],
                             'analysis_plan':'freeze estimand, independent unit, paired protocol, comparison family and precision target before confirmatory sampling',
                             'cost_config':'estimate from pilot cost per independent unit and authorized resource budget; do not infer budget from this packet',
                             'script_task':'collect immutable paired rows and config/seed/session/scorer/resource receipts; rerun measurement_review.py --analyze only when design fits',
                             'acceptance':'reviewer confirms evidence and preregistered criterion/precision; otherwise narrow claim, retain inconclusive outcome',
                             'execution':'requires existing resource authorization; this command runs no experiment'} for i in out['issues']]
    if out['ci'] is not None and not (out['criterion_met'] and out['precision_met']):
        out['redesign_tasks'].append({'owner':'research-review', 'issue':'criterion_or_precision_not_established',
             'required_data':'independent pilot variance/cost and scope of intended claim',
             'analysis_plan':'plan a separate fixed-size confirmation or validated sequential design with a precision/power target; never rerun until significant',
             'cost_config':'bounded new independent sessions/examples/seeds; authorize resources before collection',
             'script_task':'new frozen run namespace; preserve this result and all failed comparisons',
             'acceptance':'predeclared interval/margin and precision conditions or explicitly inconclusive; non-significant is not equivalent',
             'execution':'not run'})
    return out


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('packet', type=Path)
    p.add_argument('--analyze', action='store_true', help='optional narrow CPU SciPy BCa analysis; never launch workloads')
    p.add_argument('--output', type=Path, help='create a new result; refuse overwrite')
    args = p.parse_args()
    result = review(load(args.packet), args.analyze)
    text = json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    if args.output:
        with args.output.open('x') as f:
            f.write(text)
    else:
        print(text, end='')


if __name__ == '__main__':
    main()
