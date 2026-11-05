# Amazon Price Tracker

This script monitors an Amazon product price during the configured hours and
sends an email when the price changes or the product cannot be read.

## Requirements

- Python 3.9 or newer
- An SMTP-enabled email account

Install the Python dependencies:

```bash
pip install requests beautifulsoup4
```

Create a local `details.py` file in the project directory. It must define the
following values:

```python
my_email = "sender@example.com"
password = "smtp-password-or-app-password"
target = "recipient@example.com"
```

For Gmail, use an app password rather than your regular account password.
Keep `details.py` private and do not commit it.

## Usage

Run the tracker with:

```bash
python main.py
```

The default schedule is 06:00 to 21:00, with a price check every 10 seconds.
Update `PRODUCT_URL`, `START_TIME`, `END_TIME`, or `TIMESPACE` in `main.py` to
change the product or monitoring schedule.

Price history is written to `logs.json`. Request and parsing errors are written
to `errors.json`, and invalid JSON files are moved into `backups/` before a new
file is created.

## Notes

Amazon may return a CAPTCHA or bot-check page instead of the product page. The
script records that event and sends an error notification. Scraping behavior
may also be affected by Amazon's terms, regional availability, and markup
changes.
