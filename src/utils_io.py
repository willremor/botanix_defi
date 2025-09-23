from __future__ import annotations
import json, os, time
from pathlib import Path
from typing import Any, Dict
import yaml

try:
    from jsonschema import validate
except Exception:
    validate = None  # optional

SCHEMA_DIR = Path(__file__).resolve().parents[1] / "schemas"
CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"

def load_yaml(name: str) -> Dict[str, Any]:
    with open(CONFIG_DIR / name, "r") as f:
        return yaml.safe_load(f)

def load_schema(name: str) -> Dict[str, Any]:
    with open(SCHEMA_DIR / name, "r") as f:
        return json.load(f)

def validate_config(doc: Dict[str, Any], schema_name: str) -> None:
    if validate is None:
        return
    schema = load_schema(schema_name)
    validate(instance=doc, schema=schema)

def timestamp_slug(enable: bool) -> str:
    return time.strftime("%Y-%m-%dT%H-%M-%SZ") if enable else "no-ts"

def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)
