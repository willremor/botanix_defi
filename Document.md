# Botanix DeFi Flywheel Simulations

## A mathematically driven model for chain growth and sustainability via stBTC

## Overview

This document specifies a configurable simulation framework that quantifies how on-chain activity translates into (i) BTC-denominated fee revenue and (ii) value accrual to stBTC, a non-rebasing token that receives 50% of all on-chain fees. The model:

- (1) forecasts transaction counts by EVM-style type
- (2) maps activity to DeFi primitives and strategy paths
- (3) prices fees in BTC with an EIP-1559-like process
- (4) scores “quality of activity” via multipliers and primitive criticality, and
- (5) updates stBTC’s exchange rate based on fee inflows and net protocol flows.

It produces per-period and cumulative observables, scenario comparisons, and decision-oriented diagnostics to steer policy toward Botanix’s goals: maximize sustainable utilization and stBTC accrual.

---

## 1) Purpose & Scope

**Purpose.** Provide an auditable, configurable and composable simulation that links transaction activity, fee generation (in BTC), and stBTC value accrual.
**Scope.** Cover the modeling of (a) transaction growth, (b) gas consumption and pricing, (c) DeFi primitives and strategy “flywheels”, (d) policy multipliers that bias the mix toward sustainable actions, and (e) stBTC accounting (non-rebasing, price-per-share).

---

## 2) Goals

1. **Growth.** Increase total transactions and gas consumption such that BTC fees grow, lifting value accruing to stBTC holders.
2. **Optimization.** Bias activity toward **repeatable**, **compute-intensive**, and **composable** DeFi actions (closed-loop strategies) via multipliers and primitive criticality, improving durability of utilization.

---

## 3) Modeling Assumptions (concise)

* **Chain & fees.** EVM-compatible; fees are paid in BTC.
* **Transaction types.** `native_transfer`, `erc_transfer`, `contract_creation`, `contract_call`.
* **Primitives.** Payments, Stablecoins (CDP stablecoin), Lending, AMM, DEX Aggregator, Perpetuals, Options, Interest-Tokenisation (PT/YT), Liquid Staking, Bridges/Oracles, Routers/Zaps.
* **stBTC.** Non-rebasing; value-per-token (exchange rate) rises as protocol BTC assets grow relative to supply; 50% of on-chain fees are added to protocol BTC assets.
* **Uncertainty.** Truncated-normal shocks for gas intensity, tx growth, and stBTC asset/supply flows; GBM for BTC/USD (context only).
* **Design intent.** Keep formulas simple, explainable, and parameterized for governance.

---

## 4) Methodology Overview

1. **Input configs** define: transaction growth, primitive gas bands, multipliers, criticality, scenario groups (sets of strategy paths), fee pricing, and stBTC rules.
2. **Per period** the simulator:
   a) generates transaction counts by type;
   b) allocates counts to (primitive, tx\_type) via strategy path mixes;
   c) draws gas per call (global stochastic adjustment) and fee-per-gas (BTC);
   d) computes BTC fees and the **Weighted Gas Score** (quality);
   e) updates stBTC state and derives per-period returns/APY.
3. **Outputs** include time series and aggregates for fees, stBTC exchange rate and APY, weighted gas, and fees by primitive, plus scenario comparisons.

---

## 5) Mathematical Framework

### 5.1 Notation

* Period index: $t = 1,\dots,T$ (e.g., weeks). Period-to-year factor $N_y$ (e.g., 52).
* Transaction types $\mathcal{X} = \{\text{native}, \text{erc}, \text{create}, \text{call}\}$.
* Primitives $\mathcal{P}$ as listed above.
* Strategy path set $\mathcal{K}$; each path $k$ is a sequence of on-chain steps $(\text{primitive}, \text{tx\_type})$.
* Scenario group $G$ is a subset of paths $\mathcal{K}_G \subseteq \mathcal{K}$.

### 5.2 Transaction counts and growth

Baseline total transactions evolve via a single global growth shock:

$$
\text{TotalTx}(t) = \text{TotalTx}(0)\,(1+g_t)^t,
$$

with $g_t \sim \text{TruncNorm}(\mu_g,\sigma_g; [g_{\min},g_{\max}])$.
Split by tx-type shares $s_x$, $\sum_x s_x = 1$:

$$
T_x(t) = s_x \cdot \text{TotalTx}(t), \quad x \in \mathcal{X}.
$$

### 5.3 From strategy paths to (primitive, tx)-mix

Given a scenario group $G$, compute an empirical **step mix** over its selected paths:

$$
w_{p,x}^G = \frac{\# \text{steps with } (p,x) \text{ in } \mathcal{K}_G}{\sum_{(p',x')} \# \text{steps with } (p',x') }.
$$

Normalize within each tx-type when distributing counts:

$$
\widehat{w}_{p|x}^G = \frac{w_{p,x}^G}{\sum_{p'} w_{p',x}^G}.
$$

Then the count mapped to $(p,x)$ is:

$$
N_{p,x}(t) = T_x(t)\,\widehat{w}_{p|x}^G.
$$

### 5.4 Gas per call (primitive-level) with global stochastic adjustment

Each primitive $p$ has a gas band $[g^{\min}_p, g^{\max}_p]$. Draw one global adjustment $\epsilon_g \sim \text{TruncNorm}(\mu,\sigma;[\epsilon_{\min},\epsilon_{\max}])$.
Per-call gas:

$$
\tilde{g}_p = \text{clip}\big(g^{\max}_p(1+\epsilon_g),\, g^{\min}_p,\, g^{\max}_p\big).
$$

### 5.5 Fee-per-gas series (BTC)

EIP-1559-like effective price:

$$
\pi_t = \text{BaseFee}_t + \text{Tip},
$$

with $\text{BaseFee}_t$ evolving lognormally:

$$
\text{BaseFee}_t = \text{BaseFee}_{t-1}\,\exp\big(\mu_{\text{bf}} - \tfrac{1}{2}\sigma_{\text{bf}}^2 + \sigma_{\text{bf}}\,Z_t\big),\quad Z_t \sim \mathcal{N}(0,1).
$$

### 5.6 Fee revenue (BTC) and decomposition

Fees from $(p,x)$ at $t$:

$$
\text{Fees}_{p,x}(t) = N_{p,x}(t)\,\tilde{g}_p\,\pi_t.
$$

Total fees and by-primitive:

$$
\text{Fees}(t) = \sum_{p,x} \text{Fees}_{p,x}(t), \qquad \text{Fees}_p(t) = \sum_{x} \text{Fees}_{p,x}(t).
$$

### 5.7 Activity quality: Weighted Gas Score (WGS)

Primitive base multiplier $m_p$, policy multiplier $q_p$, criticality $c_p \in \{0,\dots,5\}$, and a small scaler $\kappa$ (e.g., 0.05):

$$
M_p = m_p \cdot q_p \cdot (1+\kappa c_p).
$$

Then:

$$
\text{WGS}(t) = \sum_{p,x} N_{p,x}(t)\,\tilde{g}_p \, M_p .
$$

Interpretation: larger WGS implies more compute-intensive and policy-preferred activity.

### 5.8 stBTC accounting (non-rebasing)

State variables: protocol BTC assets $A_t$, stBTC supply $S_t$, exchange rate $E_t = A_t/S_t$.
Stochastic percentage changes in assets and supply (exclusive of fee accrual):

$$
\Delta A_t^{\text{flow}} = A_{t-1}\,\alpha_t,\quad \alpha_t \sim \text{TruncNorm}(\mu_A,\sigma_A;[a_{\min},a_{\max}]),
$$

$$
\Delta S_t^{\text{flow}} = S_{t-1}\,\sigma_t,\quad \sigma_t \sim \text{TruncNorm}(\mu_S,\sigma_S;[s_{\min},s_{\max}]).
$$

Fee share to stBTC (fixed at 50%):

$$
\Delta A_t^{\text{fees}} = 0.5 \cdot \text{Fees}(t).
$$

State update:

$$
A_t = A_{t-1} + \Delta A_t^{\text{flow}} + \Delta A_t^{\text{fees}}, \qquad S_t = S_{t-1} + \Delta S_t^{\text{flow}}.
$$

Exchange rate and returns:

$$
E_t = \frac{A_t}{\max(S_t,\,\varepsilon)},\qquad r_t = \frac{E_t}{E_{t-1}} - 1.
$$

Annualised APY for period cadence $N_y$:

$$
\text{APY}_t = (1 + r_t)^{N_y} - 1.
$$

### 5.9 Strategy path scoring (optional diagnostic)

For path $k$ with constituent $(p,x)$ steps, define:

$$
\text{PathScore}_k(t) = \sum_{(p,x)\in k} N_{p,x}(t)\,\tilde{g}_p\,M_p,
$$

useful to rank which closed-loop behaviors drive WGS.

### 5.10 BTC price path (context)

For reporting in USD, simulate $P^{\text{BTC}}_t$ via GBM:

$$
P_t = P_{t-1}\,\exp\big(\mu_P - \tfrac{1}{2}\sigma_P^2 + \sigma_P \varepsilon_t\big), \quad \varepsilon_t\sim\mathcal{N}(0,1).
$$

(Independent of fee mechanics; used only for USD context if needed.)

---

## 6) Simulation Architecture (concise)

* **Configs (YAML).** `run_config`, `strategies`, `scenarios`, `primitives`, `tx_types`, `gas_policy`, `tx_counts`, `btc_price`, `stbtc`, `policy_multipliers`, `tracking`.
* **Validation.** JSON-Schema on load.
* **Engines.**

  * *Path/Counts:* strategy step-mix → (primitive, tx) distribution.
  * *Gas & Fees:* stochastic gas adjustment at band top; EIP-1559-like BTC/gas series.
  * *stBTC:* state transition with flows + fee share.
* **Runners.** Single-scenario and grid.
* **Tracking.** MLflow (params flattened; per-period metrics with `step`; artifacts logged).
* **Outputs.** CSVs + charts per run; grid summaries for cross-scenario comparison.

---

## 7) Inputs & Parameters

_For illustration only_

* **Tx growth:** $\mu_g, \sigma_g, [g_{\min}, g_{\max}]$.
* **Primitive gas bands:** $g^{\min}_p, g^{\max}_p$.
* **Gas adjustment:** single global $\epsilon_g \sim \text{TruncNorm}$.
* **EIP-1559 fees:** base fee start, $\mu_{\text{bf}}, \sigma_{\text{bf}}$, priority tip.
* **Multipliers & criticality:** $m_p, q_p, c_p$.
* **stBTC:** initial $A_0, S_0, E_0$, 50% fee share, asset/supply flow parameters.
* **Strategy paths & scenarios:** lists of steps and groupings.

All parameters are configurable for policy experiments and sensitivity analysis.

---

## 8) Observables & Diagnostics

Per period $t$ and cumulatives:

* **Fees (BTC):** $\text{Fees}(t)$, $\text{Fees}_p(t)$ by primitive.
* **Weighted Gas Score:** $\text{WGS}(t)$.
* **stBTC state:** $E_t$ (BTC/stBTC), $r_t$, $\text{APY}_t$, $A_t$, $S_t$.
* **Counts:** $T_x(t)$, $N_{p,x}(t)$.
* **Path diagnostics:** $\text{PathScore}_k(t)$ as needed.
  Core charts: APY over time, ER over time, total fees, fees by primitive, WGS over time, scatterplots of Fees vs WGS, and contract-call counts vs stBTC returns.

---

## 9) Policy Experiments & Sensitivity Levers

* **Activity steering.** Adjust $q_p$ (policy multipliers) to reward compute-heavy, composable paths (e.g., Routers/Zaps, Lending+Perps).
* **Criticality.** Vary $c_p$ to reflect evolving stack importance (e.g., stablecoin/CDP and lending during bootstrap).
* **Gas environment.** Change $\mu,\sigma$ of $\epsilon_g$ and fee pricing volatilities to stress test.
* **Growth regime.** Sweep $\mu_g$ and $\sigma_g$ to evaluate scale-up scenarios.
* **Strategy composition.** Change scenario groups (which paths are “on”) to see which bundles maximize stBTC APY and cumulative fees at acceptable risk.

---

## 10) Interpreting Results (decision rules)

* **Primary objective.** Prefer scenario groups with higher **cumulative fees (BTC)** and **higher final $E_T$/APY**, *provided* WGS is not dominated by one-off, low-quality actions.
* **Quality screen.** Higher **WGS** with diversified primitive contributions is healthier than the same WGS concentrated in a single low-depth primitive.
* **Path efficiency.** Compare path-level scores; scale those producing high WGS per unit count with recurring use (e.g., lending-AMM-perps loops).
* **Stress checks.** Under adverse growth or fee-price scenarios, prefer groups whose APY/ER curves remain monotonic and whose fees by primitive are not overly concentrated.

---

## 11) How this achieves Botanix goals

* **Chain utilization (Growth).** By modeling and rewarding compute-intensive, aggregator-routed, composable actions, total gas and BTC fees rise; 50% funnels to stBTC assets.
* **stBTC value accrual (Optimization).** Returns are higher when fees grow and when flows (assets vs supply) are balanced; multipliers push the mix toward actions that tend to repeat and compose (closed loops), stabilizing utilization and APY.
* **Sustainability.** WGS and fees-by-primitive reveal whether growth comes from robust DeFi activity rather than transient bursts, enabling governance to adjust $q_p$ and scenario composition proactively.

---

## 12) Limitations & Extensions

* **Abstractions.** Real EIP-1559 depends on block fullness; we approximate with a stochastic base-fee process.
* **Capacity & ceilings.** Liquidity/TVL ceilings are not enforced in the base spec; they can be added as scaling factors $0\le\lambda_p(t)\le1$ applied to $N_{p,x}(t)$ when depth constraints bind.
* **Risk & defaults.** Liquidation cascades, oracle lags, and bridge downtime are not explicitly modeled; these can be integrated through shock scenarios and path-availability toggles.
* **Behavioral feedback.** Users adapting to incentives can be approximated by changing tx-type shares or path selections over time.

---

## 13) Validation Plan

* **Back-testing.** Fit tx growth and fee-per-gas volatility to historical chain data (where available).
* **Sanity checks.** Unit tests on conservation (counts allocation), fee arithmetic, and stBTC state transitions.
* **Sensitivity sweeps.** Vary $\mu_g$, $\mu_{\text{bf}}$, multipliers $q_p$ to confirm qualitative behavior aligns with expectations (e.g., increasing $q_p$ for Routers/Zaps raises WGS and fees routed through complex paths).

---

## 14) Execution Summary (operational)

1. Configure horizons, scenario groups, and parameters in YAML files.
2. Run single scenarios and grids; MLflow records params, step-wise metrics, and artifacts.
3. Inspect outputs: APY/ER, fees (total/by primitive), WGS, and path diagnostics.
4. Select the policy setting (multipliers, scenario composition) that delivers the best mix of **high fees + high stBTC APY** with sustainable WGS composition.
5. Iterate: update parameters, rerun grids, and monitor deltas.

---

## Appendix A — Symbol Glossary

* $T_x(t)$: tx counts for type $x$ at $t$.
* $N_{p,x}(t)$: counts attributable to (primitive $p$, tx $x$).
* $\tilde{g}_p$: gas per call for primitive $p$ after stochastic adjustment.
* $\pi_t$: BTC/gas effective fee.
* $\text{Fees}(t)$: total fees in BTC; $\text{Fees}_p(t)$: by primitive.
* $M_p$: composite multiplier for primitive $p$.
* $\text{WGS}(t)$: Weighted Gas Score.
* $A_t, S_t, E_t$: stBTC assets (BTC), supply, exchange rate (BTC/stBTC).
* $r_t, \text{APY}_t$: stBTC per-period return, annualized yield.
* $N_y$: periods per year for annualization.

---

### Closing

This framework is deliberately **modular**, **explainable**, and **policy-controllable**. It connects the levers Botanix controls (strategy composition, multipliers, primitive prioritization) to the outcomes Botanix wants (fee growth, repeatable utilization, and stBTC value accrual), while remaining simple enough to audit and extend as the stack evolves.
