from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List
import numpy as np
import pandas as pd
import yaml

from .utils_io import load_yaml, validate_config, timestamp_slug, ensure_dir
from .sim_price_engine import gbm_path
from .sim_fee_engine import gas_adjustment_draw, eip1559_price_series
from .sim_stbtc_engine import init_stbtc, run_stbtc_step
from .sim_paths import step_mix_for_scenario, distribute_tx_counts

@dataclass
class SimConfig:
    run: Dict[str, Any]
    strategies: Dict[str, Any]
    scenarios: Dict[str, Any]
    primitives: Dict[str, Any]
    tx_types: Dict[str, Any]
    gas_policy: Dict[str, Any]
    tx_counts: Dict[str, Any]
    btc_price: Dict[str, Any]
    stbtc: Dict[str, Any]
    policy_multipliers: Dict[str, Any]
    tracking: Dict[str, Any]

def load_all_configs() -> SimConfig:
    # load + validate
    cfgs = {}
    for name, schema in [
        ("strategies.yaml","strategies.schema.json"),
        ("scenarios.yaml","scenarios.schema.json"),
        ("primitives.yaml","primitives.schema.json"),
        ("tx_types.yaml","tx_types.schema.json"),
        ("gas_policy.yaml","gas_policy.schema.json"),
        ("tx_counts.yaml","tx_counts.schema.json"),
        ("btc_price.yaml","btc_price.schema.json"),
        ("stbtc.yaml","stbtc.schema.json"),
        ("policy_multipliers.yaml","policy_multipliers.schema.json"),
        ("run_config.yaml","run_config.schema.json"),
        ("tracking.yaml", None),
    ]:
        doc = load_yaml(name)
        if schema:
            validate_config(doc, schema)
        key = name.split(".")[0]
        cfgs[key] = doc

    return SimConfig(
        run=cfgs["run_config"]["run"],
        strategies=cfgs["strategies"],
        scenarios=cfgs["scenarios"],
        primitives=cfgs["primitives"]["primitives"],
        tx_types=cfgs["tx_types"]["tx_types"],
        gas_policy=cfgs["gas_policy"],
        tx_counts=cfgs["tx_counts"],
        btc_price=cfgs["btc_price"],
        stbtc=cfgs["stbtc"],
        policy_multipliers=cfgs["policy_multipliers"]["policy"],
        tracking=cfgs["tracking"]
    )

def base_tx_counts_per_type(tx_counts_cfg: Dict[str, Any], period: int) -> Dict[str, float]:
    rng = np.random.default_rng(tx_counts_cfg["growth"]["seed"] + period)
    g = tx_counts_cfg["growth"]
    if g["mode"] == "deterministic":
        growth = g["mu"]
    else:
        # truncnorm draw
        while True:
            x = rng.normal(g["mu"], g["sigma"])
            if g["min"] <= x <= g["max"]:
                growth = x
                break
    total = tx_counts_cfg["base_total_txs"] * ((1 + growth) ** period)
    return {tx: total * share for tx, share in tx_counts_cfg["shares"].items()}

def gas_per_call_for_primitive(primitive: str, primitives_cfg: Dict[str, Any], gas_policy_cfg: Dict[str, Any]) -> int:
    band_high = primitives_cfg[primitive]["gas_high"]
    band_low  = primitives_cfg[primitive]["gas_low"]
    adj = gas_adjustment_draw(gas_policy_cfg)
    g = int(max(band_low, min(band_high, band_high * (1.0 + adj))))
    return g

def weighted_gas_multiplier(primitive: str, primitives_cfg: Dict[str, Any], policy_cfg: Dict[str, Any]) -> float:
    base_m = primitives_cfg[primitive]["multiplier"]
    pol_m = policy_cfg.get(primitive, 1.0)
    crit  = primitives_cfg[primitive]["criticality"]
    return base_m * pol_m * (1 + 0.05 * crit)  # simple criticality kicker

def period_fraction_year(period_label: str) -> float:
    return {"day":1/365, "week":1/52, "month":1/12}.get(period_label, 1/52)

def scenario_by_id(scen_cfg: Dict[str, Any], sid: int) -> Dict[str, Any]:
    for s in scen_cfg["scenarios"]:
        if s["id"] == sid:
            return s
    raise KeyError(sid)

def run_single_scenario_group(cfg: SimConfig, scenario_id: int, output_dir: Path) -> Dict[str, Any]:
    horizon = cfg.run["horizon_periods"]
    per_y   = period_fraction_year(cfg.run.get("period_label","week"))

    # Derived series
    btc_series = gbm_path(cfg.btc_price["start_usd"], cfg.btc_price["gbm"]["mu"], cfg.btc_price["gbm"]["sigma"], horizon, cfg.btc_price["gbm"]["seed"])
    eff_price_btc = eip1559_price_series(cfg.gas_policy, horizon)

    # Init stBTC state
    st_state = init_stbtc(cfg.stbtc)

    # Scenario step mix
    scen = scenario_by_id(cfg.scenarios, scenario_id)
    mix = step_mix_for_scenario(scen["strategies"], cfg.strategies, cfg.primitives)

    # Records
    rows = []
    fees_by_primitive = []
    wgas_list = []

    for t in range(1, horizon+1):
        base_counts = base_tx_counts_per_type(cfg.tx_counts, t)
        counts_by_pair = distribute_tx_counts(base_counts, mix)

        # fees and weighted gas
        total_fees_btc = 0.0
        wg_score = 0.0
        fee_prim = {}

        for (primitive, tx_type), n_tx in counts_by_pair.items():
            gas_per_tx = gas_per_call_for_primitive(primitive, cfg.primitives, cfg.gas_policy)
            fees = n_tx * gas_per_tx * eff_price_btc[t-1]
            total_fees_btc += fees
            fee_prim[primitive] = fee_prim.get(primitive, 0.0) + fees

            wg = gas_per_tx * n_tx * weighted_gas_multiplier(primitive, cfg.primitives, cfg.policy_multipliers)
            wg_score += wg

        # stBTC update
        st_state, st_obs = run_stbtc_step(st_state, total_fees_btc, cfg.stbtc, per_y)

        rows.append({
            "period_num": t,
            "btc_price_usd": btc_series[t-1],
            "exchange_rate_btc_per_stbtc": st_state["exch_rate"],
            "stbtc_assets_btc": st_state["assets_btc"],
            "stbtc_supply": st_state["supply"],
            "fees_total_btc": total_fees_btc,
            "weighted_gas_score": wg_score,
            **st_obs
        })
        fees_by_primitive.append({"period_num": t, **fee_prim})
        wgas_list.append({"period_num": t, "weighted_gas_score": wg_score})

    # DataFrames
    df = pd.DataFrame(rows)
    df_fees = pd.DataFrame(fees_by_primitive).fillna(0.0)
    return {
        "summary": df,
        "fees_by_primitive": df_fees,
        "mix": mix
    }
