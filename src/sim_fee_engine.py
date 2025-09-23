from __future__ import annotations
import numpy as np
from typing import Dict

def trunc_normal(rng, mu, sigma, lo, hi, size=1):
    # simple rejection sampler
    vals = []
    while len(vals) < size:
        x = rng.normal(mu, sigma)
        if lo <= x <= hi:
            vals.append(x)
    return np.array(vals) if size > 1 else vals[0]

def gas_adjustment_draw(cfg: Dict) -> float:
    g = cfg["gas_adjustment"]
    rng = np.random.default_rng(g["seed"])
    if cfg["mode"] == "deterministic":
        return 0.0
    return float(trunc_normal(rng, g["mu"], g["sigma"], g["min"], g["max"], 1))

def eip1559_price_series(cfg: Dict, periods: int) -> np.ndarray:
    e = cfg["eip1559"]
    rng = np.random.default_rng(e["seed"])
    base = e["base_fee_btc_start"]
    mu, sigma = e["mu_bf"], e["sigma_bf"]
    out = []
    for _ in range(periods):
        # lognormal drift for base fee (proxy)
        shock = rng.normal(mu - 0.5*sigma**2, sigma)
        base = base * np.exp(shock)
        out.append(base + e["priority_tip_btc"])
    return np.array(out)
