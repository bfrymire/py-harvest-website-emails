# Harvest Website Emails

A Python CLI that steps through links of a website and scrapes email addresses.

## Usage

To get started, create a CSV file that has a column header `website` and include URLs you want to scrape to the column.

When running the CLI, the `--input` option must be provided pointing to the location of the CSV file.

### CLI Options

**--input, --i** - CSV file that holds list of websites to harvest.

Type: `str`

**--max-pages, --p** - Maximum number of pages to walk.

Type: `int`

Default: `300`

**--max-emails, --e** - Maximum number email addresses to harvest.

Type: `int`

Default: `20`

**--max-time, --t** - Maximum amount of time to harvest each website in seconds.

Type: `int`

Default: `-1`, no time limit

**--verbosity, --v** - Verbosity of output.

Type: `int`

Default: `2`

## Tests

Run unit tests:

```py
python -m unittests --v
```

## License

View the [`LICENSE`](https://github.com/bfrymire/py-harvest-website-emails/blob/master/LICENSE) file.
