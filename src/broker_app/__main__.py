#!/usr/bin/env python3
"""
Data Broker Opt-Out Automation — Web Interface entry point.

Run:
    python -m broker_app          # start web UI (from the src/ directory)
    python -m broker_app --help   # show options
"""
from __future__ import annotations

import json
import logging
import os
import secrets
import threading
import time
from dataclasses import asdict
from pathlib import Path
from typing import Dict

import schedule
from flask import Flask, jsonify, redirect, render_template, request, url_for

from .bot import OptOutBot
from .database import DatabaseManager
from .models import BrokerSite, PersonalInfo


# ---------------------------------------------------------------------------
# Configuration path
# ---------------------------------------------------------------------------

# Defaults to config.json in the repo root (two levels up from this file).
# Override with the BROKER_CONFIG environment variable.
_DEFAULT_CONFIG = str(
    Path(__file__).resolve().parent.parent.parent / "config.json"
)
CONFIG_PATH = os.environ.get("BROKER_CONFIG", _DEFAULT_CONFIG)

# ---------------------------------------------------------------------------
# Flask application
# ---------------------------------------------------------------------------

app = Flask(__name__)
# Use an env-var secret in production; fall back to a random token per restart.
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# ---------------------------------------------------------------------------
# Shared bot instance (lazy, thread-safe)
# ---------------------------------------------------------------------------
_bot: "OptOutBot | None" = None
_bot_lock = threading.Lock()


def get_bot() -> OptOutBot:
    global _bot
    if _bot is None:
        with _bot_lock:
            if _bot is None:
                _bot = OptOutBot(config_path=CONFIG_PATH)
    return _bot


# ---------------------------------------------------------------------------
# Real-time run-state — updated by the background thread, read by /api/status
# ---------------------------------------------------------------------------
_run_state: Dict = {
    "running":        False,
    "processed":      0,
    "total":          0,
    "current_broker": "",
}
_run_lock = threading.Lock()


def _update_run_state(**kwargs) -> None:
    with _run_lock:
        _run_state.update(kwargs)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    bot = get_bot()
    return render_template(
        "dashboard.html",
        summary=bot.get_status_summary(),
        brokers=bot.db.get_broker_sites(),
    )


@app.route("/config")
def config():
    bot = get_bot()
    # Convert dataclass → plain dict so template bracket access works
    return render_template("config.html", personal_info=asdict(bot.personal_info))


@app.route("/update_config", methods=["POST"])
def update_config():
    """Persist updated personal information and reload the bot."""
    try:
        fields = [
            "first_name", "last_name", "email", "phone",
            "address", "city", "state", "zip_code",
            "date_of_birth", "middle_name",
        ]
        new_info = {f: request.form.get(f, "") for f in fields}

        cfg_path = Path(CONFIG_PATH)
        existing: Dict = {}
        if cfg_path.exists():
            with open(cfg_path) as fh:
                existing = json.load(fh)
        existing["personal_info"] = new_info
        with open(cfg_path, "w") as fh:
            json.dump(existing, fh, indent=2)

        # Force bot reload on next request
        global _bot
        with _bot_lock:
            _bot = None

        return jsonify({"status": "success", "message": "Configuration updated"})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/run_optout", methods=["POST"])
def run_optout():
    """Start a background opt-out batch; returns immediately."""
    with _run_lock:
        if _run_state["running"]:
            return jsonify({
                "status": "already_running",
                "message": "A batch is already in progress",
            }), 409

    broker_names = (request.json or {}).get("brokers") or None

    def _run() -> None:
        _update_run_state(running=True, processed=0, total=0, current_broker="")
        try:
            bot = get_bot()
            brokers = bot.db.get_broker_sites()
            if broker_names:
                brokers = [b for b in brokers if b.name in broker_names]
            _update_run_state(total=len(brokers))

            def _progress(processed: int, total: int, current: str) -> None:
                _update_run_state(processed=processed, total=total,
                                  current_broker=current)

            bot.run_opt_out_batch(
                broker_names=broker_names,
                progress_callback=_progress,
            )
        except Exception as exc:
            logging.exception("Batch run error: %s", exc)
        finally:
            _update_run_state(running=False, current_broker="")

    threading.Thread(target=_run, daemon=True).start()
    return jsonify({"status": "started",
                    "message": "Opt-out process started in background"})


@app.route("/api/status")
def api_status():
    """
    Returns cumulative stats merged with live run-state so the dashboard
    and the progress modal both get what they need in a single call.
    """
    bot = get_bot()
    summary = bot.get_status_summary()
    with _run_lock:
        live = dict(_run_state)
    summary.update(live)
    return jsonify(summary)


@app.route("/history")
def history():
    bot = get_bot()
    return render_template("history.html", attempts=bot.db.get_attempts_history())


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

def setup_scheduler() -> None:
    """Re-run all opt-outs automatically every 90 days."""
    def _job() -> None:
        try:
            logging.info("Running scheduled opt-out batch")
            results = get_bot().run_opt_out_batch()
            logging.info("Scheduled run done: %d brokers", len(results))
        except Exception as exc:
            logging.error("Scheduled run failed: %s", exc)

    schedule.every(90).days.do(_job)

    def _runner() -> None:
        while True:
            schedule.run_pending()
            time.sleep(3600)

    threading.Thread(target=_runner, daemon=True).start()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Data Broker Opt-Out Bot")
    parser.add_argument("--port",  type=int, default=5000,
                        help="Port to listen on (default: 5000)")
    parser.add_argument("--host",  default="127.0.0.1",
                        help="Bind address (default: 127.0.0.1 = localhost only)")
    parser.add_argument("--debug", action="store_true",
                        help="Enable Flask debug mode (development only)")
    args = parser.parse_args()

    debug = args.debug or os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true")

    setup_scheduler()

    print("Data Broker Opt-Out Bot")
    print(f"  Web UI  →  http://{args.host}:{args.port}")
    print("  Press Ctrl+C to stop\n")

    app.run(host=args.host, port=args.port, debug=debug, use_reloader=False)


if __name__ == "__main__":
    main()
