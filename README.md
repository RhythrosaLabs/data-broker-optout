<div align="center">

# 🛡️ data-broker-optout

**Automate opt-out requests across 20+ data broker sites — and keep them out every 90 days**

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask&logoColor=white)
![Selenium](https://img.shields.io/badge/Selenium-4-43B02A?style=flat&logo=selenium&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

</div>

---

Data brokers collect and sell your personal info — name, address, phone, relatives, employment — without your consent. This tool automates opt-out submissions to 20+ of them, logs every attempt, and auto-reschedules every 90 days because brokers re-add your data periodically.

**All your personal info stays on your machine.** SQLite + local config, never sent anywhere.

## ✨ Features

- **20+ data brokers** — Spokeo, WhitePages, BeenVerified, Intelius, TruePeopleSearch, Acxiom, Epsilon, LexisNexis, InstantCheckmate, and more
- **Web dashboard** — start batch runs, watch live per-broker progress, review full history
- **Headless Chrome** — Selenium runs Chrome invisibly in the background via auto-downloaded ChromeDriver
- **Auto-reschedule** — reruns every 90 days automatically
- **Local-only** — SQLite DB + local config file; nothing leaves your machine
- **Configurable via UI** — update personal info in the browser, no file editing needed
- **CLI mode** — headless batch jobs and status checks from the terminal

## 🚀 Quick Start

```bash
git clone https://github.com/RhythrosaLabs/data-broker-optout.git
cd data-broker-optout
pip install -r requirements.txt
python app.py
```

Open `http://localhost:5000`, enter your info, and click **Run Opt-Out Batch**.

## 🛠️ Tech Stack

- **Python 3.9+** — core automation logic
- **Flask** — local web dashboard
- **Selenium 4** — browser automation with headless Chrome
- **SQLite** — local attempt history and scheduling

## 📸 Screenshots

| Dashboard | Configuration | History |
|---|---|---|
| ![Dashboard](docs/screenshots/dashboard.png) | ![Config](docs/screenshots/config.png) | ![History](docs/screenshots/history.png) |

## 🤝 Contributing

PRs welcome. Open an issue first for new broker additions.

## 📄 License

MIT

## 💛 Support

If this tool reclaims your privacy, consider supporting development:

👉 [Donate via PayPal](https://paypal.me/noodlebake) — @noodlebake

---
<div align="center">Made with ❤️ by <a href="https://github.com/RhythrosaLabs">RhythrosaLabs</a></div>
