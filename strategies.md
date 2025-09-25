# Strategy Paths

Below are some example strategy paths that can be implemented using Botanix primitives. Each strategy combines different primitives to achieve specific financial goals such as yield generation, liquidity provision, leverage, and risk management.

1. **Strategy name:** stBTC + Stablecoin + Lending

    **Description:** Mint stablecoin using stBTC and earn interest via lending

    **Path:** Deposit BTC → Mint stBTC → Use stBTC as Collateral → Mint Stablecoin → Supply Stablecoin into Lending → Receive interest rewards (by supply)

    **Tags:** \[Income, Yield, Liquidity]

2. **Strategy name:** stBTC + Stablecoin + LP Provision

    **Description:** Use stablecoin to form LP pair and earn trading fees

    **Path:** Deposit BTC → Mint stBTC → Use stBTC as Collateral → Mint Stablecoin → Provide LP pair stBTC/Stablecoin on AMM

    **Tags:** \[Fees, Liquidity, Trading]

3. **Strategy name:** Recursive stBTC Leverage

    **Description:** Looping stBTC collateral and borrowing to increase stake

    **Path:** Use stBTC as Collateral → Borrow Stablecoin → Swap Stablecoin → Buy More stBTC → Restake stBTC as Collateral → Repeat

    **Tags:** \[Leverage, Growth, Risk]

4. **Strategy name:** Contract Call Yield Loop

    **Description:** Repeated router swaps + lending calls to compound return

    **Path:** Contract Call Swap → Contract Call Supply into Lending → Borrow Stablecoin → Contract Call Swap → Supply Back into LP

    **Tags:** \[Composable, Yield Farming, Complexity]

5. **Strategy name:** AMM LP + Farming + Lending

    **Description:** LP tokens used to collateralise lending then re-LPed

    **Path:** Provide LP stBTC/Stablecoin on AMM → Stake LP tokens → Use LP tokens as Collateral → Borrow Stablecoin → Use borrowed Stablecoin to re-provide LP

    **Tags:** \[Leverage, LP, Compounding]

6. **Strategy name:** Perps Hedge + Yield + Stablecoin

    **Description:** Earn perps funding rates while hedging via stablecoin lending

    **Path:** Use stBTC as Collateral → Borrow Stablecoin → Enter Perpetuals Position → Earn Funding → Lend Stablecoin back into Lending

    **Tags:** \[Hedge, Yield, Derivatives]

7. **Strategy name:** Options Premium + Stablecoin Support

    **Description:** Sell covered calls using stBTC while using stablecoin for collateral

    **Path:** Hold stBTC → Use stBTC as Underlying for Options Selling → Receive Premium (active txn) → Use Premium + Stablecoin to Supply Lending → Reinvest

    **Tags:** \[Options, Premium, Stablecoin]

8. **Strategy name:** Liquid Staking + Lending + LP

    **Description:** Stake BTC -> receive LST -> use LST in lending or LP

    **Path:** Stake BTC → Receive LST → Use LST as Collateral in Lending → Borrow Stablecoin → Use Borrowed Stablecoin + LST to Provide LP

    **Tags:** \[LST, Yield, Liquidity]

9. **Strategy name:** Bridge + Stablecoin Yield Cycle

    **Description:** Bridge external stablecoins in, supply in stablecoin markets, LP usage

    **Path:** Bridge Stablecoin asset → Mint stablecoin on Botanix → Supply into Lending or AMM LP → Earn interest / Fees

    **Tags:** \[Onboarding, Yield, Liquidity]

10. **Strategy name:** DEX Aggregator Swap Loop

    **Description:** Frequent swaps via aggregator with stablecoin + LP rebalancing

    **Path:** Swap Stablecoin A → Stablecoin B via Aggregator → Provide LP in Stablecoin Pair → Rebalance LP via Swap → Repeat

    **Tags:** \[Fees, Trading volume, Stability]

11. **Strategy name:** Options + Perpetuals Dual Yield

    **Description:** Combine options premium with perpetuals funding rates

    **Path:** Use Stablecoin collateral → Sell Options → Borrow Stablecoin → Enter Perps Position → Reinvest returns

    **Tags:** \[Derivatives, Yield, Volatility]

12. **Strategy name:** AMM Concentrated Liquidity + Lending Boost

    **Description:** Use concentrated liquidity, earn fees, then boost via lending

    **Path:** Provide concentrated LP stBTC/Stablecoin → Earn trade fees → Stake LP tokens → Use LP tokens as Collateral in Lending → Borrow stablecoin → RE-LP

    **Tags:** \[LP Efficiency, Leverage, Compounding]

13. **Strategy name:** Composable Router Strategy

    **Description:** Use router to chain multiple steps (swap + borrow + LP) in one transaction

    **Path:** Contract Call via Router → Swap → Borrow Stablecoin → Provide LP → Restake LP

    **Tags:** \[Composability, UX, Efficiency]

14. **Strategy name:** Nested Yield via Interest Tokenisation

    **Description:** Create PT/YT from lending then trade/hedge YT token

    **Path:** Supply Stablecoin into Lending → Mint PT/YT → Sell or Hedge YT → Use proceeds to provide LP or reuse for further lending

    **Tags:** \[Tokenisation, Yield, Risk]

15. **Strategy name:** Perps Carry + LP Overlay

    **Description:** Combine perps funding + LP fees

    **Path:** Use stBTC as Collateral → Borrow Stablecoin → Enter Perps Position → Provide LP with perps gains + stablecoin → Reinvest LP fees

    **Tags:** \[Derivatives, Income, Liquidity]

16. **Strategy name:** Liquidity Mining + Stablecoin Reinvestment

    **Description:** Use stablecoin LP rewards reinvested into stablecoin lending

    **Path:** Provide LP in Stablecoin Pair → Earn LP rewards (active) → Convert rewards to stablecoin → Supply into Lending → Reinvest returns

    **Tags:** \[Income, Compound, Stability]

17. **Strategy name:** Recursive LP Leverage

    **Description:** Use LP tokens as collateral to borrow more, LPing recursively

    **Path:** Provide LP stBTC/Stablecoin → Stake LP → Use LP tokens as Collateral → Borrow Stablecoin → Add to LP → Repeat

    **Tags:** \[Leverage, LP, Depth]

18. **Strategy name:** Cross-primitive Derivative Hedge Loop

    **Description:** Use derivatives to hedge LP exposure, earning stable yields in parallel

    **Path:** Provide LP stBTC/Stablecoin → Enter Perps short to hedge price exposure → Use stablecoin from lending to support margin → Reinvest yield from LP and perps

    **Tags:** \[Hedge, Combined Yield, Risk Management]

19. **Strategy name:** Liquid Staking + Contract Calls Yield

    **Description:** Use stBTC or LST in contract calls to yield strategies

    **Path:** Stake BTC → Receive LST → Use LST in Contract Call (e.g. yield strategy) → Earn yield → Reinvest into LST or stablecoin lending

    **Tags:** \[LST, Yield, Composability]

20. **Strategy name:** Stablecoin Collateral + Options Vault + LP

    **Description:** Stablecoin used to back option vaults and then deposits into LP for fees

    **Path:** Supply Stablecoin into Lending → Use stablecoin collateral to open Options Vault → Earn options premium (active) → Use stablecoin + premium to provide LP → Reinvest

    **Tags:** \[Options, Yield, Liquidity]
