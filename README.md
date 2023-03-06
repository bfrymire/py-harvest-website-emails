# Harvest Website Emails

A Python CLI that steps through links of a website and scrapes email addresses.

Harvest Website Emails uses BeautifulSoup to scrape websites. As a small caveat, websites that populate its elements using JavaScript after render are not scrapable. You would have to use a browser simulator otherwise.

## Installation

1. Clone the repo
2. Install requirements:

```bash
pip install -r requirements.txt
```

## Usage

To get started, create a CSV file that has a column header `websites` and include URLs you want to scrape to the column.

When running the CLI, the `--input` option must be provided pointing to the location of the CSV file.

### CLI Options

| Option | Description | Type | Default |
| -- | -- | -- | -- |
| `--input`, `--i` | CSV file that holds list of websites to harvest from. | `str` | _N/A_ |
| `--max-pages`, `--p` | Maximum number of pages to walk. | `int` | 300 |
| `--max-emails`, `--e` | Maximum number email addresses to harvest. | `int` | 20 |
| `--max-time`, `--t` | Maximum amount of time to harvest each website in seconds. | `int` | -1 _(no time limit)_ |
| `--verbosity`, `--v` | Verbosity of output. | `int` | 2 |

## Tests

Run unit tests:

```py
python -m unittest --v
```

## License

[MIT License](https://github.com/bfrymire/py-harvest-website-emails/blob/master/LICENSE)
