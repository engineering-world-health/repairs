# EWH Repairs Database

[Engineering World Health](http://www.ewh.org/)
has been collecting reports of equipment repairs by participants of the
[Summer Institute](http://www.ewh.org/summer-institute/program)
for several years.

This project aims to parse the repair reports and allow easy exploration of the data
though a data exploration framework (TBD).

The
[original description](https://share.ewh.org/forum/innovation-and-design/bmet-library-development/programming-projects/109-equipment-repair-database)
for this project gives some additional details.

## Parsing
The parsing script (`parse.py`) expects the following format of work summary forms:
```
raw/
 +- 2011/
 |  +- form 1
 |  +- form 2
 |     ...
 +- 2012/
 |  ...
```

The config file `meta.json` contains information on how to parse each work summary form.
e.g. which cell is the county name, which row do repairs start on, the labels for binary columns,
and which fields are necessary to include the row as a repair.

The parsing script always parses all forms in a folder (`raw/`) and generates a single CSV file:
`repairs.csv`.

## Data Exploration
TBD
