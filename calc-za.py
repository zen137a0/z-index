#!/usr/bin/env python3
import math
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

# Logistic time-weighting parameters for the base function f(t):
# f(0)=0, f(12)=0.5, f(24)=2, f(infinity)=4
#
# For the author zt-index, use fa(t)=min(f(t), 1).
# This preserves the early-retraction discount but prevents
# any additional time-dependent penalty above 1.
L = 4.0
K = 0.149313289102338      # month^-1
T0 = 23.6171913820693      # months

def s(t):
    return 1.0 / (1.0 + math.exp(-K * (t - T0)))

S0 = s(0.0)


def f_weight(t):
    """Base logistic delay weight f(t)."""
    return L * (s(t) - S0) / (1.0 - S0)


def fa_weight(t):
    """Author delay weight fa(t)=min(f(t), 1)."""
    return min(f_weight(t), 1.0)


def round_half_up(x):
    return int(
        Decimal(str(x)).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )


if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} ifdb.csv author-hogehoge.csv")
    sys.exit(1)

ifdb_file = sys.argv[1]
hoge_file = sys.argv[2]

journal_map = {}
try:
    m = pd.read_csv("dict.csv", dtype=str).fillna("")
    for _, row in m.iterrows():
        targets = [
            x.strip().upper()
            for x in row["ifdb"].split(";")
            if x.strip()
        ]

        journal_map[
            row["retraction_watch"].strip().upper()
        ] = targets

except FileNotFoundError:
    pass


def normalize_journal(s):
    s = s.strip().upper()
    return journal_map.get(s, [s])


def parse_date(s):
    try:
        return pd.to_datetime(s, errors="raise")
    except Exception:
        return None


def choose_date_and_journal(parts):
    """
    Supports both formats:
      1) Original Paper Date | Journal | ... | Retraction Date (NN months)
      2) Title | Journal | Original Paper Date | ... | Retraction Date (NN months)
    """
    if len(parts) >= 2 and parse_date(parts[0]) is not None:
        return parts[0], parts[1]

    if len(parts) >= 3 and parse_date(parts[2]) is not None:
        return parts[2], parts[1]

    return None, None


def extract_delay_months(line, publication_date):
    # Preferred: use explicit "NN months" if ret-author.py already wrote it.
    m = re.search(r"\((\d+(?:\.\d+)?)\s*months?\)", line, re.IGNORECASE)
    if m:
        return float(m.group(1))

    # Fallback: compute from first and last ISO-like dates in the line.
    dates = re.findall(r"\d{4}-\d{1,2}-\d{1,2}", line)
    if len(dates) >= 2:
        d0 = pd.to_datetime(publication_date)
        d1 = pd.to_datetime(dates[-1])
        return max(0.0, (d1 - d0).days / 30.4375)

    return None


ifdb = pd.read_csv(ifdb_file, dtype=str).fillna("")
ifdb = ifdb.set_index(ifdb.columns[0])

ifs = []
weighted_ifs = []
weights = []
delays = []
paper_count = 0

with open(hoge_file, encoding="utf-8") as f:
    for line in f:
        line = line.strip()

        if not line:
            continue

        parts = [p.strip() for p in line.split("|")]

        date_str, journal = choose_date_and_journal(parts)
        if date_str is None or journal is None:
            print(f"Warning: bad line: {line}", file=sys.stderr)
            continue

        paper_count += 1

        delay_months = extract_delay_months(line, date_str)
        if delay_months is None:
            print(f"Warning: retraction delay not found: {line}", file=sys.stderr)
            continue

        year = str(pd.to_datetime(date_str).year)
        year_col = f"{year}IF"

        journal_norms = normalize_journal(journal)

        matches = [
            idx for idx in ifdb.index
            if any(
                    n in normalize_journal(idx)
                    for n in journal_norms
            )
        ]

        if len(matches) == 0:
            print(f"WARNING: journal not found: {journal}", file=sys.stderr)
            continue

        if year_col not in ifdb.columns:
            print(f"Warning: year not found: {journal} {year_col}", file=sys.stderr)
            continue

        value = ifdb.loc[matches[0], year_col]

        if value == "":
            print(f"Warning: IF missing: {journal} {year}", file=sys.stderr)
            continue

        value = float(value)
        weight = fa_weight(delay_months)
        weighted_value = value * weight

        ifs.append(value)
        delays.append(delay_months)
        weights.append(weight)
        weighted_ifs.append(weighted_value)

if not weighted_ifs:
    print(f"{paper_count} papers found")
    print("0 IF values collected")
    print("z = 0")
    print("zt = 0")
    sys.exit(0)

z_total = sum(ifs)
zt_total = sum(weighted_ifs)

z = round_half_up(z_total)
zt = round_half_up(zt_total)

expr_z = "+".join(f"{x:g}" for x in ifs)
expr_zt = "+".join(
    f"({x:g}*{w:.3f})" for w, x in zip(weights, ifs)
)

print(f"{paper_count} papers found")
print(f"{len(ifs)} IF values collected")
#print("author time weighting: fa(t)=min(f(t), 1)")
#print(f"parameters: L={L:g}, k={K:.12g} month^-1, t0={T0:.12g} months")
print(f"z  = {expr_z}")
print(f"   = {z}")
print(f"zt = {expr_zt}")
print(f"   = {zt}")
