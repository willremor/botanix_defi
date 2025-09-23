from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Any
from .sim_core import load_all_configs, run_single_scenario_group
from .utils_io import ensure_dir, timestamp_slug, load_yaml
from .mlflow_utils import set_tracking, start_run, log_params_from_dict, log_run_config, log_run_config_artifact, log_artifacts_dir

def write_charts(outdir: Path, df: pd.DataFrame, df_fees: pd.DataFrame):
    # APY over time
    plt.figure(figsize=(7,4))
    plt.plot(df["period_num"], df["stbtc_apy_annualized"], marker="o")
    plt.xlabel("Period"); plt.ylabel("stBTC APY (annualized)"); plt.title("APY Over Time")
    plt.tight_layout(); plt.savefig(outdir / "chart_apy_over_time.png"); plt.close()

    # ER over time
    plt.figure(figsize=(7,4))
    plt.plot(df["period_num"], df["exchange_rate_btc_per_stbtc"], marker="o")
    plt.xlabel("Period"); plt.ylabel("ER (BTC/stBTC)"); plt.title("Exchange Rate Over Time")
    plt.tight_layout(); plt.savefig(outdir / "chart_exchange_rate_over_time.png"); plt.close()

    # Fees total over time
    plt.figure(figsize=(7,4))
    plt.plot(df["period_num"], df["fees_total_btc"], marker="o")
    plt.xlabel("Period"); plt.ylabel("Fees (BTC)"); plt.title("Total Fees Over Time")
    plt.tight_layout(); plt.savefig(outdir / "chart_fees_total_over_time.png"); plt.close()

    # Fees by primitive (stacked)
    if len(df_fees.columns) > 1:
        prim_cols = [c for c in df_fees.columns if c != "period_num"]
        df_fees.set_index("period_num")[prim_cols].plot(kind="area", figsize=(8,5))
        plt.xlabel("Period"); plt.ylabel("Fees (BTC)"); plt.title("Fees by Primitive (stacked)")
        plt.tight_layout(); plt.savefig(outdir / "chart_fees_by_primitive_stacked.png"); plt.close()

def run_single():
    cfg = load_all_configs()
    ts = timestamp_slug(cfg.run.get("timestamp_utc", True))
    root = Path(cfg.run["output_root"]) / "runs"
    ensure_dir(root)

    # MLflow
    if cfg.tracking.get("enabled", False):
        set_tracking(cfg.tracking.get("tracking_uri"), cfg.tracking["experiment_name"])

    for sg in cfg.run["scenario_groups"]:
        outdir = root / f"{ts}_sg{sg}_{cfg.run['preset_name']}"
        ensure_dir(outdir)

        # Single run MLflow child (or standalone if only one)
        run_name = f"sg{sg}_{cfg.run['preset_name']}_{ts}"
        ctx = None
        if cfg.tracking.get("enabled", False):
            ctx = start_run(run_name, tags={"scenario_group_id": str(sg), "preset": cfg.run["preset_name"]})
            # Log flattened params + raw run_config
            log_run_config({"run": cfg.run}, prefix="run")
            log_params_from_dict({"tracking": cfg.tracking, "policy_multipliers": cfg.policy_multipliers}, prefix="config")
            log_run_config_artifact({"run": cfg.run}, artifact_file="run_config.yaml")

        res = run_single_scenario_group(cfg, sg, outdir)

        # Write CSVs
        res["summary"].to_csv(outdir / "summary_run.csv", index=False)
        res["fees_by_primitive"].to_csv(outdir / "fees_breakdown_by_primitive.csv", index=False)

        # Charts
        write_charts(outdir, res["summary"], res["fees_by_primitive"])

        if ctx is not None:
            # Log entire run folder as artifacts
            log_artifacts_dir(str(outdir))
            import mlflow; mlflow.end_run()

if __name__ == "__main__":
    run_single()
