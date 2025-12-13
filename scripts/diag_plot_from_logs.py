import math
import runpy
from pathlib import Path

# Load functions directly from the script file (no package import required)
mod = runpy.run_path(str(Path(__file__).with_name("plot_from_logs.py")))
parse_log = mod["parse_log"]
select_beans = mod["select_beans"]

logfile = Path("DUMP.small.txt")
bs, ts, dr = parse_log(logfile)
print(f"Found {len(bs)} beans, {len(ts)} timeseries, {len(dr)} death entries")
selected = select_beans(bs, per_sex=3, seed=42)
print("Selected:", selected)

for b in selected:
    rows = ts.get(b, [])
    print(f"\nBean {b}: samples={len(rows)}")
    if not rows:
        continue
    ages = [r.get("age", math.nan) for r in rows]
    energies = [r.get("energy", math.nan) for r in rows]
    sizes = [r.get("size", math.nan) for r in rows]
    speeds = [r.get("speed", math.nan) for r in rows]
    ts_vals = [r.get("target_size", math.nan) for r in rows]
    print(f"  age first/last: {ages[0]} / {ages[-1]}")
    # monotonicity check
    monotonic = all((ages[i] <= ages[i+1] for i in range(len(ages)-1)))
    print(f"  age monotonic: {monotonic}")
    print(f"  energy min/max: {min(energies):.3f} / {max(energies):.3f}")
    print(f"  size min/max: {min(sizes):.3f} / {max(sizes):.3f}")
    print(f"  speed min/max: {min(speeds):.3f} / {max(speeds):.3f}")
    print(f"  target_size min/max: {min(ts_vals):.3f} / {max(ts_vals):.3f}")
    # check NaNs
    n_nans = sum(1 for v in ages if v!=v)
    print(f"  NaN ages: {n_nans}")

print("\nDeath reasons sample (first 10):")
for i,(k,v) in enumerate(dr.items()):
    print(f"  Bean {k}: {v}")
    if i>9:
        break
