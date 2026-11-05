# Amazon Price Monitor

A small Python script that checks multiple Amazon product pages, records prices, and sends email notifications when a price changes or a scraping error occurs.

## Features

- Monitors every URL in `PRODUCT_URLS`.
- Checks products during the configured time window.
- Stores prices in `logs.json`.
- Stores scraping errors in `errors.json`.
- Sends Gmail notifications for price changes and errors.
- Uses a request timeout and checks for common Amazon CAPTCHA and robot-check pages.

## Requirements

- Python 3.10 or newer
- `requests`
- `beautifulsoup4`

Install the dependencies in a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install requests beautifulsoup4
```

On Windows, activate the environment with:

```powershell
.venv\Scripts\activate
```

## Configuration

Add the products to `PRODUCT_URLS` in `main.py`:

```python
PRODUCT_URLS = [
	"https://www.amazon.in/example-product-1/dp/PRODUCT_ID_1",
	"https://www.amazon.in/example-product-2/dp/PRODUCT_ID_2",
]
```

The monitor currently runs between `START_TIME` and `END_TIME` and waits `TIMESPACE` seconds between monitoring cycles.

Email settings are currently imported from `details.py`:

```python
my_email = "your-email@gmail.com"
password = "xxxx xxxx xxxx xxxx"
target = "recipient@example.com"
```

Use a Gmail app password, not your normal Gmail password. Never commit `details.py` or share its contents. The existing `.gitignore` excludes it. If credentials have ever been exposed, revoke the app password and create a new one.

For PythonAnywhere, keep credentials out of the repository and configure them using environment variables or a private `details.py` file created only on the server. A safer long-term change is to read `BOT_EMAIL`, `BOT_EMAIL_PASSWORD`, and `BOT_TARGET` with `os.environ`.

## Run

```bash
source .venv/bin/activate
python main.py
```

Stop the monitor with `Ctrl+C`.

Before running, verify the code parses:

```bash
python -m py_compile main.py test.py
```

## Log format

Each monitoring cycle uses one timestamp for all products:

```json
{
	"05/11/2026-19:30:12": {
		"https://www.amazon.in/product-one": "2468.00",
		"https://www.amazon.in/product-two": "58.00"
	}
}
```

The product URL is the key and the normalized price is stored as a string. `errors.json` uses timestamp keys for scraper and request errors.

## PythonAnywhere

1. Create a PythonAnywhere account and open a Bash console.
2. Clone the repository and enter its directory.
3. Create a virtual environment and install the dependencies.
4. Add credentials securely on the server.
5. Test the script manually.
6. Add a Scheduled Task using the virtual-environment interpreter:

```bash
/home/yourusername/web-scraper/.venv/bin/python /home/yourusername/web-scraper/main.py
```

The task should run during the period configured by `START_TIME` and `END_TIME`. Do not commit `logs.json`, `errors.json`, `.venv`, or credentials.

## Troubleshooting

### `ModuleNotFoundError`

Activate the virtual environment and install the dependencies:

```bash
source .venv/bin/activate
pip install requests beautifulsoup4
```

Make sure the command uses the same Python environment where the packages were installed.

### The program starts but sends no email

Check that:

- `details.py` contains the correct sender, app password, and recipient.
- The current price differs from the previous saved price.
- The current time is between `START_TIME` and `END_TIME`.
- The terminal is not only showing `No Send`, which means the monitor is outside its configured time window.

Use a Gmail app password and verify that SMTP access is allowed for the account.

### SMTP login or sending errors

Confirm that the sender address and Gmail app password are correct. Do not use the normal Gmail account password. Check that the SMTP server is `smtp.gmail.com` and that port `587` with TLS is available.

### The same price is saved repeatedly

The monitor saves once per polling cycle. This is expected with the current implementation. To save only changes, compare the fetched price with the latest saved price before calling `add_to_json()`.

### Products have different timestamps

Create the cycle timestamp before the `for product in PRODUCT_URLS` loop. Pass that same timestamp to `add_to_json()` for every product in the cycle. Do not create a new timestamp inside the product loop.

### Timestamps show `01/01/00`

Use `datetime.now()`, not `datetime.now().time()`, when formatting a date and time:

```python
datetime.now().strftime("%d/%m/%Y-%H:%M:%S")
```

Calling `.time()` removes the date before formatting.

### Amazon returns no price or sends an error email

Amazon may have returned a CAPTCHA, robot-check page, or changed HTML. Check `errors.json`, confirm the product URL works in a browser, and avoid polling too frequently. The parser may need updating if Amazon changed its markup.

### `logs.json` cannot be decoded

Check that the file contains valid JSON:

```bash
python -m json.tool logs.json
```

If the file is corrupted, stop the monitor, back up the file, and create a new empty `logs.json` containing `{}`.

### The program exits immediately

Run it from the project directory with the intended interpreter:

```bash
/home/yourusername/web-scraper/.venv/bin/python main.py
```

Also confirm that `main.py` ends with:

```python
if __name__ == "__main__":
	monitor()
```

## Important limitations

- Amazon may return CAPTCHA, robot-check, or changed HTML instead of a product page.
- Amazon can change its HTML structure, which may require updating the parser.
- HTML scraping should respect Amazon's terms and applicable rate limits.
- The current notification logic can send repeated error or price-change emails if the remote page changes repeatedly.