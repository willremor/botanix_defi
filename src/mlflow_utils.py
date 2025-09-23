from __future__ import annotations
import mlflow
from typing import Any, Dict, Optional
import yaml

def set_tracking(tracking_uri: Optional[str], experiment_name: str) -> None:
    if tracking_uri:
        mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)

def start_run(run_name: str, tags: Dict[str, str] | None = None, nested: bool = False):
    ctx = mlflow.start_run(run_name=run_name, nested=nested)
    if tags:
        mlflow.set_tags(tags)
    return ctx

def _flatten(prefix: str, d: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    def _walk(kp, v):
        if isinstance(v, dict):
            for k2, v2 in v.items():
                _walk(f"{kp}.{k2}" if kp else str(k2), v2)
        elif isinstance(v, (list, tuple)):
            for i, v2 in enumerate(v):
                _walk(f"{kp}[{i}]", v2)
        else:
            key = f"{prefix}.{kp}" if prefix and kp else (kp or prefix)
            out[key] = str(v)[:250]
    _walk("", d)
    return out

def log_params_from_dict(d: Dict[str, Any], prefix: str = "") -> None:
    flat = _flatten(prefix, d) if prefix else _flatten("", d)
    items = list(flat.items())
    for i in range(0, len(items), 100):
        mlflow.log_params(dict(items[i:i+100]))

def log_metrics_step(metrics: Dict[str, float], step: int) -> None:
    for k, v in metrics.items():
        mlflow.log_metric(k, float(v), step=step)  # stepped series shows in UI

def log_artifacts_dir(local_dir: str, artifact_path: Optional[str] = None) -> None:
    mlflow.log_artifacts(local_dir, artifact_path=artifact_path)

def flatten_run_config(run_cfg: Dict[str, Any], prefix: str = "run") -> Dict[str, Any]:
    return _flatten(prefix, run_cfg)

def log_run_config(run_cfg: Dict[str, Any], prefix: str = "run") -> None:
    log_params_from_dict(run_cfg, prefix)

def log_run_config_artifact(run_cfg: Dict[str, Any], artifact_file: str = "run_config.yaml") -> None:
    s = yaml.safe_dump(run_cfg, sort_keys=True)
    mlflow.log_text(s, artifact_file)
