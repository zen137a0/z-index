#!/usr/bin/env python3
import pandas as pd
import sys

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} input.csv journal_keyword")
    sys.exit(1)

csvfile = sys.argv[1]
keyword = sys.argv[2].lower()

df = pd.read_csv(csvfile, dtype=str).fillna("")

# B,C,D,...
TITLE_COL = 1
JOURNAL_COL = 4
RETRACTION_DATE_COL = 10
DATE_COL = 13
TYPE_COL = 16

# "Retraction" ONLY
df = df[
    df.iloc[:, TYPE_COL]
      .str.lower()
      .str.strip()
      == "retraction"
]

# Journal name match using dict.csv
# Journal name match using dict.csv
journal_map = {}
try:
    m = pd.read_csv("dict.csv", dtype=str).fillna("")

    for _, row in m.iterrows():
        rw = row["retraction_watch"].strip().lower()

        targets = [
            x.strip().lower()
            for x in row["ifdb"].split(";")
            if x.strip()
        ]

        journal_map[rw] = targets

except FileNotFoundError:
    pass

def normalize_journal(s):
    s = s.strip().lower()
    return journal_map.get(s, [s])

query_norms = normalize_journal(sys.argv[2])
df = df[
    df.iloc[:, JOURNAL_COL]
      .apply(
          lambda x: any(
              q in normalize_journal(x)
              for q in query_norms
          )
      )
]

# Original paper date: old to new
df["_date"] = pd.to_datetime(
    df.iloc[:, DATE_COL],
    errors="coerce"
)

df = df.sort_values("_date")

for _, row in df.iterrows():

    journal = row.iloc[JOURNAL_COL]

    title = row.iloc[TITLE_COL]
    words = title.split()

    short_title = " ".join(words[:5])

    if len(words) > 5:
        short_title += " ..."

    pub_date = pd.to_datetime(
        row.iloc[DATE_COL],
        errors="coerce"
    )

    ret_date = pd.to_datetime(
        row.iloc[RETRACTION_DATE_COL],
        errors="coerce"
    )

    pub_date_str = (
        pub_date.strftime("%Y-%m-%d")
        if not pd.isna(pub_date)
        else "?"
    )

    ret_date_str = (
        ret_date.strftime("%Y-%m-%d")
        if not pd.isna(ret_date)
        else "?"
    )

    if pd.isna(pub_date) or pd.isna(ret_date):
        months = "?"
    else:
        months = (
            (ret_date.year - pub_date.year) * 12
            + (ret_date.month - pub_date.month)
        )

    print(
        f"{pub_date_str}"
        f" | {journal}"
        f" | {short_title}"
        f" | {ret_date_str} ({months} months)"
    )

