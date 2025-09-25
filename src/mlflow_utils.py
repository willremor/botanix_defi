from __future__ import annotations
import mlflow
from typing import Any, Dict, Optional
import yaml
import re

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

def _sanitize_param_key(key: str) -> str:
    """
    Sanitize key for MLflow:
      - Convert [number] to .number
      - Remove disallowed chars (keep alnum, _ - . space : /)
      - Collapse duplicate separators
    """
    key = re.sub(r'\[(\d+)\]', r'.\1', key)
    key = re.sub(r'[^A-Za-z0-9_\-\. :/]', '_', key)
    key = re.sub(r'\.{2,}', '.', key).strip(" .")
    if not key:
        key = "param"
    return key[:250]

def _dedupe_param_keys(pairs):
    seen = {}
    out = []
    for k, v in pairs:
        if k not in seen:
            seen[k] = 1
            out.append((k, v))
        else:
            i = seen[k]
            while True:
                cand = f"{k}.{i}"
                if cand not in seen:
                    seen[k] = i + 1
                    seen[cand] = 1
                    out.append((cand, v))
                    break
                i += 1
    return out

def log_params_from_dict(d, prefix=""):
    """
    Flatten nested dict/list/tuple and log params to MLflow.
    Ensures keys meet MLflow naming rules (no [] etc).
    """
    import mlflow

    def flatten(obj, base=""):
        if isinstance(obj, dict):
            for k, v in obj.items():
                nk = f"{base}.{k}" if base else str(k)
                yield from flatten(v, nk)
        elif isinstance(obj, (list, tuple)):
            for i, v in enumerate(obj):
                nk = f"{base}.{i}" if base else str(i)
                yield from flatten(v, nk)
        else:
            yield base, obj

    items = list(flatten(d))

    # Apply external prefix only if provided and not already present
    if prefix:
        prefixed = []
        for k, v in items:
            if k.startswith(prefix + ".") or k == prefix:
                prefixed.append((k, v))
            else:
                pk = f"{prefix}.{k}" if k else prefix
                prefixed.append((pk, v))
        items = prefixed

    sanitized = [(_sanitize_param_key(k), v) for k, v in items if k]

    sanitized = _dedupe_param_keys(sanitized)

    norm = []
    for k, v in sanitized:
        if isinstance(v, (dict, list, tuple, set)):
            v = str(v)
        norm.append((k, v))

    for i in range(0, len(norm), 100):
        batch = dict(norm[i:i+100])
        if batch:
            mlflow.log_params(batch)

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
