from __future__ import annotations
from typing import Dict, List, Tuple
from collections import Counter

# Expand scenario -> effective step mix -> implied primitive/tx shares among 'contract_call' & 'native_transfer'
def step_mix_for_scenario(scenario_strategy_ids: List[int], strategies: Dict, primitives: Dict) -> Dict[Tuple[str,str], float]:
    # returns share for (primitive, tx_type)
    steps = []
    map_by_id = {s["id"]: s for s in strategies["strategies"]}
    for sid in scenario_strategy_ids:
        st = map_by_id[sid]
        steps.extend([(stp["primitive"], stp["tx_type"]) for stp in st["steps"]])
    c = Counter(steps)
    tot = sum(c.values())
    return {k: v / tot for k, v in c.items()} if tot > 0 else {}

def distribute_tx_counts(base_counts: Dict[str, float], mix: Dict[Tuple[str,str], float]) -> Dict[Tuple[str,str], float]:
    """
    base_counts: tx counts by tx_type (after growth)
    mix: share per (primitive, tx_type)
    -> counts per (primitive, tx_type)
    We scale each (primitive, tx) using the proportion of that tx_type available.
    """
    # Sum mix shares per tx_type
    per_tx_share = {}
    for (primitive, tx), share in mix.items():
        per_tx_share[tx] = per_tx_share.get(tx, 0.0) + share

    out = {}
    for (primitive, tx), share in mix.items():
        if per_tx_share.get(tx, 0) > 0:
            out[(primitive, tx)] = base_counts.get(tx, 0) * (share / per_tx_share[tx])
    return out
