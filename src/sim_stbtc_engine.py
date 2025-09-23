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
    ar = trunc_normal(rngA, **{k: cfg["flows"]["assets_rate"][k] for k in ["mu","sigma","min","max"]})
    sr = trunc_normal(rngS, **{k: cfg["flows"]["supply_rate"][k] for k in ["mu","sigma","min","max"]})

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
