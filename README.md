# data-broker-optout

Automated opt-out submissions for 20+ data broker and people-search websites.  
A Flask web UI lets you monitor progress, view history, and update your personal information — all stored locally, never sent anywhere except to the broker opt-out forms themselves.

## Features

- **Web dashboard** — start batch runs, watch live progress, review history
- **20+ brokers** — Spokeo, WhitePages, BeenVerified, Acxiom, Epsilon, LexisNexis, and more
- **Scheduled reruns** — automatically retries every 90 days
- **Headless Selenium** — Chrome runs in the background, no window required
- **All data stays local** — SQLite database, config file on your machine only

## Quick start

```bash
# 1. Clone and enter the repo
git clone https://github.com/RhythrosaLabs/data-broker-optout.git
cd data-broker-optout

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy the example config and fill in your details
cp config.json.example config.json
# Edit config.json — your info stays local, never committed

# 5. Start the web UI
cd src
python -m broker_app
```

Then open **http://127.0.0.1:5000** in your browser.

## Configuration

Edit `config.json` (gitignored — never committed):

```json
{
  "personal_info": {
    "first_name": "Jane",
    "last_name":  "Doe",
    "email":      "jane@example.com",
    "phone":      "555-000-0000",
    "address":    "123 Main St",
    "city":       "Anytown",
    "state":      "CA",
    "zip_code":   "90210",
    "date_of_birth": "01/01/1990",
    "middle_name": ""
  },
  "bot_settings": {
    "headless":       true,
    "delay_min":      2,
    "delay_max":      5,
    "timeout":        30,
    "retry_attempts": 3
  }
}
```

You can also update all fields through the **Configuration** page in the web UI.

## CLI usage

```bash
cd src
python -m broker_app --help          # all options
python -m broker_app --port 8080     # custom port
python -m broker_app --debug         # dev mode
```

## Project layout

```
.
├── config.json.example      # safe template — copy to config.json
├── requirements.txt
└── src/broker_app/
    ├── __main__.py          # Flask app + entry point
    ├── bot.py               # Selenium automation engine
    ├── database.py          # SQLite persistence
    ├── models.py            # shared dataclasses
    ├── brokers.py           # full broker definitions list
    ├── cli.py               # CLI helper commands
    ├── config.py            # config manager utilities
    ├── static/app.js        # frontend JS
    └── templates/           # Jinja2 HTML templates
```

## Privacy & security

- `config.json` is in `.gitignore` — your personal details are **never committed**
- The Flask server binds to `127.0.0.1` (localhost) only by default
- No external accounts, APIs, or cloud services required
- Set `SECRET_KEY` env-var for a stable session secret in long-running deployments

## Requirements

- Python 3.9+
- Google Chrome (ChromeDriver is installed automatically via `webdriver-manager`)

## License

MIT
