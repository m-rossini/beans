r"""Parse debug log file and plot bean phenotype evolution and death causes.

Features:
- Parse `Bean X created` lines to get bean sex and IDs
- Parse `Bean X after update: phenotype=...` lines to collect time series
- Pick N beans (defaults 6) with specified per-sex count (defaults 3 each) deterministically using a seed
- Plot properties `energy`, `size`, `age`, `speed`, `target_size` (one plot per property, all selected beans)
- Create a pie chart of death causes (if any found in the logs)

Usage (PowerShell):
$env:PYTHONPATH='src'; python .\scripts\plot_from_logs.py --logfile DUMP.small.txt --out plots_from_logs --seed 42

"""
from __future__ import annotations

import argparse
import ast
import math
import random
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

CREATION_RE = re.compile(r"Bean\s+(\d+)\s+created:.*sex=(male|female)")
UPDATE_RE = re.compile(r"Bean\s+(\d+)\s+after update: phenotype\s*[:=]\s*(\{.*?\})")


def parse_log(path: Path):
    beans_sex: Dict[int, str] = {}
    timeseries: Dict[int, List[Dict[str, float]]] = defaultdict(list)
    death_reasons: Dict[int, str] = {}

    text = path.read_text()
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue

        # creation
        m = CREATION_RE.search(line)
        if m:
            bean_id = int(m.group(1))
            sex = m.group(2)
            beans_sex[bean_id] = sex
            continue

        # update phenotype
        m = UPDATE_RE.search(line)
        if m:
            bean_id = int(m.group(1))
            phen_str = m.group(2)
            # Try to parse phenotype dict; may already be valid Python
            try:
                phen = ast.literal_eval(phen_str)
            except Exception:
                # Fallback: try to add quotes to keys (simple heuristic)
                fixed = re.sub(r"([a-zA-Z_]+)\s*:\s", r"'\1': ", phen_str)
                try:
                    phen = ast.literal_eval(fixed)
                except Exception:
                    continue

            # Normalize fields we care about
            entry = {
                "age": float(phen.get("age", math.nan)),
                "energy": float(phen.get("energy", math.nan)),
                "size": float(phen.get("size", math.nan)),
                "speed": float(phen.get("speed", math.nan)),
                "target_size": float(phen.get("target_size", math.nan)),
            }
            timeseries[bean_id].append(entry)
            continue

        # death / survival lines — capture simple keywords and the line as reason
        if re.search(r"\bdie(d|s)?\b|\bdeath\b|energy_deplet|energy_deplete|max_age_reached|max_age", line, re.IGNORECASE):
            id_match = re.search(r"Bean\s+(\d+)", line)
            if id_match:
                bean_id = int(id_match.group(1))
                death_reasons[bean_id] = line

    return beans_sex, timeseries, death_reasons


def select_beans(beans_sex: Dict[int, str], per_sex: int = 3, seed: Optional[int] = None):
    males = sorted([i for i, s in beans_sex.items() if s == "male"])
    females = sorted([i for i, s in beans_sex.items() if s == "female"])
    rng = random.Random(seed)

    sel_m = rng.sample(males, min(per_sex, len(males))) if males else []
    sel_f = rng.sample(females, min(per_sex, len(females))) if females else []
    return sel_m + sel_f


def plot_timeseries(timeseries: Dict[int, List[Dict[str, float]]], selected: List[int], props: List[str], out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    for prop in props:
        plt.figure(figsize=(10, 5))
        for bean_id in selected:
            rows = timeseries.get(bean_id, [])
            if not rows:
                continue
            # Ensure rows are sorted by age (logs may be slightly out of order)
            rows_sorted = sorted(rows, key=lambda r: (r.get("age", math.nan)))
            xs = [float(r.get("age", math.nan)) for r in rows_sorted]
            # Normalize tiny values (avoid negative-zero artifacts) and pull prop values
            ys_raw = [r.get(prop, math.nan) for r in rows_sorted]
            ys = [0.0 if (isinstance(v, (int, float)) and abs(v) < 1e-12) else v for v in ys_raw]
            plt.plot(xs, ys, marker="o", label=f"bean {bean_id}")

        plt.title(f"{prop} over age for selected beans")
        plt.xlabel("age")
        plt.ylabel(prop)
        plt.grid(alpha=0.3, linestyle="--")
        plt.legend(loc="best")
        plt.tight_layout()
        out = out_dir / f"timeseries_{prop}.png"
        plt.savefig(out)
        plt.close()
        print(f"Wrote {out}")


def plot_death_pie(death_reasons: Dict[int, str], out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    if not death_reasons:
        print("No death reasons found in logs; skipping pie chart.")
        return None

    # Simplify reasons by extracting keywords
    simplified = []
    for r in death_reasons.values():
        # try to find specific tokens
        if "energy_deplet" in r.lower() or "energy_deplet" in r.lower():
            simplified.append("energy_depleted")
        elif "max_age_reached" in r.lower() or "max_age" in r.lower():
            simplified.append("max_age")
        elif "obesity" in r.lower() or "health" in r.lower():
            simplified.append("obesity")
        else:
            simplified.append("other")

    counts = Counter(simplified)
    labels = list(counts.keys())
    sizes = [counts[k] for k in labels]

    plt.figure(figsize=(6, 6))
    plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.title("Death causes (simplified)")
    out = out_dir / "death_causes_pie.png"
    plt.tight_layout()
    plt.savefig(out)
    plt.close()
    print(f"Wrote {out}")
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--logfile", "-l", required=True, help="Path to debug log file")
    p.add_argument("--out", "-o", default="plots_from_logs", help="Output directory")
    p.add_argument("--per-sex", type=int, default=3, help="Number of beans per sex to select")
    p.add_argument("--seed", type=int, default=42, help="Random seed for selection")
    args = p.parse_args()

    log_path = Path(args.logfile)
    if not log_path.exists():
        raise SystemExit(f"Log file not found: {log_path}")

    beans_sex, timeseries, death_reasons = parse_log(log_path)

    if not beans_sex:
        print("No beans found in log file.")
        return

    selected = select_beans(beans_sex, per_sex=args.per_sex, seed=args.seed)
    print(f"Selected beans: {selected}")

    props = ["energy", "size", "age", "speed", "target_size"]
    out_dir = Path(args.out)
    plot_timeseries(timeseries, selected, props, out_dir)
    plot_death_pie(death_reasons, out_dir)


if __name__ == "__main__":
    main()
