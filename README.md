# $z$- and $\tilde{z}$-Index Calculation Guide

## Preparation

Download the latest `retraction_watch.csv` file from the Retraction Watch GitLab:

<https://gitlab.com/crossref/retraction-watch-data>

## Requirements

- Python 3.9 or later
- pandas

Install the required package using:

```bash
pip install pandas
```

## Notes

Only records with `RetractionNature = Retraction` (column Q in
`retraction_watch.csv`) are included in the calculation; records classified as
Expression of concern, Correction, or any other category are excluded.

## Calculating Author $z$- and $\tilde{z}$-Indices

### Step 1: Create an Author-Specific Retraction List

Run:

```bash
python ret-author.py retraction_watch.csv "John Smith" > "John Smith.csv"
```

This script will create a file named `John Smith.csv` containing all retracted
papers associated with the matched author found in the Retraction Watch
Database.

#### Notes

- Check `John Smith.csv` to exclude authors with the same name. Delete entire
  lines, not just text, as blank lines may cause errors.
- Special care is required for names containing umlauts. For example, `Schön`
  and `Schon` may return different search results. In such cases, running the
  script with a partial name (e.g., `Jan Hendrik`) and checking the resulting
  CSV file may be helpful.

### Step 2: Calculate the $z$- and $\tilde{z}$-Indices

```bash
python calc-za.py ifdb.csv "John Smith.csv"
```

#### Notes

- If `WARNING: journal not found: xxx` is displayed, the journal is not yet
  included in `ifdb.csv`. In that case, search for the journal in Clarivate
  Journal Citation Reports:

  <https://jcr.clarivate.com/jcr/home>

  and add its impact factor data to `ifdb.csv`.

- If the journal is included in `ifdb.csv` but still not detected, add a journal
  name mapping to `dict.csv`.

## Calculating Journal $z$- and $\tilde{z}$-Indices

### Step 1: Create a Journal-Specific Retraction List

Run:

```bash
python ret-journal.py retraction_watch.csv "Journal Name" > "Journal Name.csv"
```

This will create a file named `Journal Name.csv` containing all retracted papers
associated with that journal.

#### Notes

- Use the full journal name whenever possible.
- Check `Journal Name.csv` to exclude entries from similarly named journals.
  Delete entire lines, not just text, as blank lines may cause errors.
- If no records are returned, the journal may be stored under a different name
  in the Retraction Watch Database. Search the journal name (column E in
  `retraction_watch.csv`) and check for alternative names (e.g., "The Journal
  of ...").
- If necessary, add the mapping to `dict.csv`. Leave the `retraction_watch`
  entry in column A unchanged. In column B, add abbreviations or alternative
  journal names separated by semicolons.

### Step 2: Calculate the $z$- and $\tilde{z}$-Indices

```bash
python calc-zj.py ifdb.csv "Journal Name.csv"
```

#### Notes

- If `WARNING: year not found` is displayed, this is not an error. It simply
  indicates that `ifdb.csv` does not contain impact factor data for years
  earlier than 1997.
- This warning may disappear if additional historical Journal Impact Factor data
  are added to `ifdb.csv`.

## Code Availability

The Python scripts used to calculate the $z$- and $\tilde{z}$-indices, together
with the processed datasets, are available in this repository for research and
educational purposes.

## License

This repository is released under a modified BSD 3-Clause license with an
additional non-commercial restriction.

Redistribution and use in source and binary forms, with or without modification,
are permitted for non-commercial purposes only, subject to the terms described
in the LICENSE file.
