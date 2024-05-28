# Query Builder

> Python tool to help building queries for scientific literature reviews

## About

*Query Builder* allows to create search query strings for various databases from
one single CSV file. The idea is to create a CSV file and list all keywords
grouped by their core concept. Using checkboxes one can enable or disable
certain keywords for specific databases. Upon running this script, it will go
over all keywords and create a query string according to the CSV that can be
copied and pasted into the search engines of the desired databases.

* **TODO**: fill this README with content about the CSV make and the tool usage

## Notes

* [keywords.csv](./keywords.csv) is an example file
* [queries.md](./queries.md) is this tool's output if the example csv is used
* [query_builder.py](./query_builder.py) is the main script
