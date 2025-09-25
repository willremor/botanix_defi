from __future__ import annotations
import numpy as np
from typing import Dict, Tuple

def trunc_normal(rng, mu, sigma, lo, hi):
    while True:
        x = rng.normal(mu, sigma)
        if lo <= x <= hi:
            return x

def run_stbtc_step(state: Dict, fees_btc: float, cfg: Dict, period_fraction_year: float) -> Tuple[Dict, Dict]:
    """
    state: {'assets_btc','supply','exch_rate'}
    cfg: stbtc config with flows and fee_share_to_stbtc
    """
    rngA = np.random.default_rng(cfg["flows"]["assets_rate"]["seed"])
    rngS = np.random.default_rng(cfg["flows"]["supply_rate"]["seed"])

    # percentage changes (Gaussian with truncation)
    # ar = trunc_normal(rngA, **{k: cfg["flows"]["assets_rate"][k] for k in ["mu","sigma","min","max"]})
        # ...existing code...
    # Original (failing) line:
    # ar = trunc_normal(rngA, **{k: cfg["flows"]["assets_rate"][k] for k in ["mu","sigma","min","max"]})
    
    # Fix: map config keys 'min'/'max' to trunc_normal's expected parameter names (assumed min_v/max_v)
    # rates_cfg = cfg["flows"]["assets_rate"]
# ...existing code above...
    # Assets rate (fix: use positional args; trunc_normal does not accept keyword names tried earlier)
    rates_cfg = cfg["flows"]["assets_rate"]
    ar = trunc_normal(
        rngA,
        rates_cfg["mu"],
        rates_cfg["sigma"],
        rates_cfg["min"],
        rates_cfg["max"],
    )
# ...existing code continues...
    
    # Support both possible function signatures defensively
    # try:
    #     ar = trunc_normal(
    #         rngA,
    #         mu=rates_cfg["mu"],
    #         sigma=rates_cfg["sigma"],
    #         min_v=rates_cfg["min"],
    #         max_v=rates_cfg["max"],
    #     )
    # except TypeError:
    #     # Fallback if function actually expects 'low'/'high' or 'a'/'b'
    #     try:
    #         ar = trunc_normal(
    #             rngA,
    #             mu=rates_cfg["mu"],
    #             sigma=rates_cfg["sigma"],
    #             low=rates_cfg["min"],
    #             high=rates_cfg["max"],
    #         )
    #     except TypeError:
    #         ar = trunc_normal(
    #             rngA,
    #             mu=rates_cfg["mu"],
    #             sigma=rates_cfg["sigma"],
    #             a=rates_cfg["min"],
    #             b=rates_cfg["max"],
    #         )
    # # ...existing code...

    # sr = trunc_normal(rngS, **{k: cfg["flows"]["supply_rate"][k] for k in ["mu","sigma","min","max"]})
    sr_cfg = cfg["flows"]["supply_rate"]
    sr = trunc_normal(
        rngS,
        sr_cfg["mu"],
        sr_cfg["sigma"],
        sr_cfg["min"],
        sr_cfg["max"],
    )
    assets_next = state["assets_btc"] * (1 + ar) + cfg["fee_share_to_stbtc"] * fees_btc
    supply_next = state["supply"] * (1 + sr)

    exch_prev = state["exch_rate"]
    exch_next = assets_next / max(1e-9, supply_next)

    period_return = (exch_next / exch_prev) - 1.0
    annualized = (1.0 + period_return) ** (1.0 / period_fraction_year) - 1.0

    next_state = {"assets_btc": assets_next, "supply": supply_next, "exch_rate": exch_next}
    obs = {"stbtc_return_period": period_return, "stbtc_apy_annualized": annualized}
    return next_state, obs

def init_stbtc(cfg: Dict) -> Dict:
    assets_btc = cfg["supply_start"] * cfg["exch_rate_start_btc"]
    return {"assets_btc": assets_btc, "supply": cfg["supply_start"], "exch_rate": cfg["exch_rate_start_btc"]}
