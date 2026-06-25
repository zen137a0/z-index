#!/usr/bin/env python3
import pandas as pd
import sys

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} input.csv keyword")
    sys.exit(1)

csvfile = sys.argv[1]
keyword = sys.argv[2].lower()

df = pd.read_csv(csvfile, dtype=str).fillna("")

TITLE_COL = 1
JOURNAL_COL = 4
AUTHOR_COL = 7
RETRACTION_DATE_COL = 10
DATE_COL = 13
TYPE_COL = 16

# "Retraction" ONLY
df = df[df.iloc[:, TYPE_COL].str.lower().str.strip() == "retraction"]

terms = keyword.split()

def contains_all_terms(author_text):
    author_text = author_text.lower()
    return all(term in author_text for term in terms)


df = df[df.iloc[:, AUTHOR_COL].apply(contains_all_terms)]

df["_date"] = pd.to_datetime(df.iloc[:, DATE_COL], errors="coerce")
df = df.sort_values("_date")

for _, row in df.iterrows():
    journal = row.iloc[JOURNAL_COL]

    title = row.iloc[TITLE_COL]
    words = title.split()
    short_title = " ".join(words[:5])
    if len(words) > 5:
        short_title += " ..."

    author_text = row.iloc[AUTHOR_COL]

    matched = []
    for author in author_text.split(";"):
        author = author.strip()
        if all(term in author.lower() for term in terms):
            matched.append(author)

    matched_author = "; ".join(matched)

    # Exclude if the name is not listed
    if matched_author == "":
        continue

    pub_date = pd.to_datetime(row.iloc[DATE_COL], errors="coerce")
    ret_date = pd.to_datetime(row.iloc[RETRACTION_DATE_COL], errors="coerce")

    pub_date_str = pub_date.strftime("%Y-%m-%d")
    ret_date_str = ret_date.strftime("%Y-%m-%d")

    months = (
        (ret_date.year - pub_date.year) * 12
        + (ret_date.month - pub_date.month)
    )

    print(
        f"{pub_date_str} | {journal} | {short_title} | "
        f"{matched_author} | {ret_date_str} ({months} months)"
    )
