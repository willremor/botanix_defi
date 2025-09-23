from __future__ import annotations
import numpy as np

def gbm_path(start_price: float, mu: float, sigma: float, periods: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    # log-returns: r_t ~ N((mu - 0.5*sigma^2), sigma^2)
    shocks = rng.normal(loc=(mu - 0.5*sigma**2), scale=sigma, size=periods)
    prices = [start_price]
    for z in shocks:
        prices.append(prices[-1] * np.exp(z))
    return np.array(prices[1:])  # length = periods
