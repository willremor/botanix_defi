from __future__ import annotations
from pathlib import Path
import pandas as pd

# Support running both as a module (python -m src.grid_runner) and as a script (python src/grid_runner.py)
try:  # relative imports when part of package
    from .sim_core import load_all_configs, run_single_scenario_group
    from .utils_io import ensure_dir, timestamp_slug
    from .mlflow_utils import set_tracking, start_run, log_run_config, log_artifacts_dir
except ImportError:
    # Fallback: add repo root to sys.path and import via namespace package 'src'
    import sys as _sys
    from pathlib import Path as _Path
    _root = str(_Path(__file__).resolve().parents[1])
    if _root not in _sys.path:
        _sys.path.insert(0, _root)
    from src.sim_core import load_all_configs, run_single_scenario_group
    from src.utils_io import ensure_dir, timestamp_slug
    from src.mlflow_utils import set_tracking, start_run, log_run_config, log_artifacts_dir

def run_grid():
    cfg = load_all_configs()
    ts = timestamp_slug(cfg.run.get("timestamp_utc", True))
    root = Path(cfg.run["output_root"]) / "comparisons"
    ensure_dir(root)

    parent = None
    if cfg.tracking.get("enabled", False):
        set_tracking(cfg.tracking.get("tracking_uri"), cfg.tracking["experiment_name"])
        parent = start_run(f"grid_{ts}", tags={"run_kind": "grid_parent"})

    index_rows = []
    summary_rows = []

    for sg in cfg.run["scenario_groups"]:
        # child run
        child = None
        if cfg.tracking.get("enabled", False):
            child = start_run(f"sg{sg}_{cfg.run['preset_name']}_{ts}", tags={"scenario_group_id": str(sg), "preset": cfg.run["preset_name"], "run_kind": "grid_child"}, nested=True)

        res = run_single_scenario_group(cfg, sg, Path("."))

        # quick end-state summary
        last = res["summary"].iloc[-1]
        summary_rows.append({
            "scenario_group_id": sg,
            "final_exchange_rate": last["exchange_rate_btc_per_stbtc"],
            "final_apy": last["stbtc_apy_annualized"],
            "cum_fees_btc": res["summary"]["fees_total_btc"].sum(),
            "mean_weighted_gas": res["summary"]["weighted_gas_score"].mean()
        })

        if child is not None:
            # log tables as MLflow artifacts (optional)
            import mlflow
            mlflow.log_table(res["summary"], artifact_file=f"sg{sg}_summary.json")
            mlflow.log_table(res["fees_by_primitive"], artifact_file=f"sg{sg}_fees_by_primitive.json")
            mlflow.end_run()

        index_rows.append({"scenario_group_id": sg, "preset": cfg.run["preset_name"], "timestamp": ts})

    df_index = pd.DataFrame(index_rows)
    df_grid  = pd.DataFrame(summary_rows)
    df_index.to_csv(root / "grid_index.csv", index=False)
    df_grid.to_csv(root / "grid_summary.csv", index=False)

    if parent is not None:
        log_artifacts_dir(str(root))
        import mlflow; mlflow.end_run()

if __name__ == "__main__":
    run_grid()
