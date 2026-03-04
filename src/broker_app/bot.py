"""
OptOutBot — Selenium automation engine for submitting opt-out forms.
"""
from __future__ import annotations

import json
import logging
import random
import time
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .database import DatabaseManager
from .models import BrokerSite, PersonalInfo

# Default brokers loaded on first run
_DEFAULT_BROKERS: List[BrokerSite] = [
    BrokerSite(
        name="Spokeo",
        url="https://www.spokeo.com",
        opt_out_url="https://www.spokeo.com/optout",
        form_fields={"email": "email", "first_name": "fname", "last_name": "lname"},
        instructions="Fill out email, first name, and last name, then verify via email",
        difficulty="easy",
        requires_verification=True,
    ),
    BrokerSite(
        name="WhitePages",
        url="https://www.whitepages.com",
        opt_out_url="https://www.whitepages.com/suppression_requests",
        form_fields={
            "first_name": "suppression_request[first_name]",
            "last_name": "suppression_request[last_name]",
            "email": "suppression_request[email]",
            "phone": "suppression_request[phone]",
        },
        instructions="Complete form with personal details",
        difficulty="easy",
        requires_verification=False,
    ),
    BrokerSite(
        name="BeenVerified",
        url="https://www.beenverified.com",
        opt_out_url="https://www.beenverified.com/app/optout/search",
        form_fields={"first_name": "fname", "last_name": "lname", "state": "state"},
        instructions="Search for your profile first, then opt out",
        difficulty="medium",
        requires_verification=True,
    ),
    BrokerSite(
        name="PeopleFinder",
        url="https://www.peoplefinder.com",
        opt_out_url="https://www.peoplefinder.com/optout.php",
        form_fields={
            "email": "email",
            "first_name": "first_name",
            "last_name": "last_name",
        },
        instructions="Simple opt-out form",
        difficulty="easy",
        requires_verification=False,
    ),
    BrokerSite(
        name="Intelius",
        url="https://www.intelius.com",
        opt_out_url="https://www.intelius.com/opt-out/submit/",
        form_fields={
            "first_name": "firstName",
            "last_name": "lastName",
            "email": "email",
            "phone": "phone",
        },
        instructions="Complete opt-out form and verify email",
        difficulty="easy",
        requires_verification=True,
    ),
    BrokerSite(
        name="TruePeopleSearch",
        url="https://www.truepeoplesearch.com",
        opt_out_url="https://www.truepeoplesearch.com/removal",
        form_fields={"email": "email"},
        instructions="Search for your listing first, then use removal form",
        difficulty="medium",
        requires_verification=True,
    ),
    BrokerSite(
        name="Acxiom",
        url="https://www.acxiom.com",
        opt_out_url="https://isapps.acxiom.com/optout/optout.aspx",
        form_fields={
            "first_name": "FirstName",
            "last_name": "LastName",
            "email": "Email",
            "address": "Address1",
            "city": "City",
            "state": "State",
            "zip_code": "PostalCode",
        },
        instructions="Complete comprehensive opt-out form",
        difficulty="medium",
        requires_verification=False,
    ),
    BrokerSite(
        name="Epsilon",
        url="https://www.epsilon.com",
        opt_out_url="https://www.epsilon.com/us/privacy-policy/opt-out-form",
        form_fields={
            "first_name": "firstName",
            "last_name": "lastName",
            "email": "email",
            "address": "address",
            "city": "city",
            "state": "state",
            "zip_code": "zipCode",
        },
        instructions="Marketing data opt-out form",
        difficulty="medium",
        requires_verification=False,
    ),
    BrokerSite(
        name="InstantCheckmate",
        url="https://www.instantcheckmate.com",
        opt_out_url="https://www.instantcheckmate.com/opt-out/",
        form_fields={
            "first_name": "firstName",
            "last_name": "lastName",
            "email": "email",
        },
        instructions="Background check service opt-out",
        difficulty="easy",
        requires_verification=True,
    ),
]


class OptOutBot:
    """Selenium-powered bot that submits opt-out forms on data broker sites."""

    def __init__(
        self,
        config_path: str = "config.json",
        headless: bool = True,
        db_path: str = "opt_out_log.db",
    ):
        self.config_path = Path(config_path)
        self.headless = headless
        self.driver: Optional[webdriver.Chrome] = None

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("opt_out_bot.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

        self.personal_info = self._load_config()
        self.db = DatabaseManager(db_path)
        self._seed_default_brokers()

    # ------------------------------------------------------------------
    # Config
    # ------------------------------------------------------------------
    def _load_config(self) -> PersonalInfo:
        if not self.config_path.exists():
            self._create_default_config()
            self.logger.warning(
                "Config file not found. Created default at %s", self.config_path
            )
        with open(self.config_path) as f:
            data = json.load(f)
        return PersonalInfo(**data["personal_info"])

    def _create_default_config(self) -> None:
        default = {
            "personal_info": {
                "first_name": "Jane",
                "last_name": "Doe",
                "email": "jane.doe@example.com",
                "phone": "555-000-0000",
                "address": "123 Main Street",
                "city": "Anytown",
                "state": "CA",
                "zip_code": "90210",
                "date_of_birth": "01/01/1990",
                "middle_name": "",
            },
            "bot_settings": {
                "headless": True,
                "delay_min": 2,
                "delay_max": 5,
                "timeout": 30,
                "retry_attempts": 3,
            },
        }
        with open(self.config_path, "w") as f:
            json.dump(default, f, indent=2)

    def _seed_default_brokers(self) -> None:
        existing = {b.name for b in self.db.get_broker_sites()}
        for broker in _DEFAULT_BROKERS:
            if broker.name not in existing:
                self.db.add_broker_site(broker)

    # ------------------------------------------------------------------
    # WebDriver helpers
    # ------------------------------------------------------------------
    def setup_driver(self) -> None:
        opts = Options()
        if self.headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1080")
        opts.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=opts)
        self.driver.implicitly_wait(10)

    def _random_delay(self, lo: float = 2, hi: float = 5) -> None:
        time.sleep(random.uniform(lo, hi))

    # ------------------------------------------------------------------
    # Form interaction
    # ------------------------------------------------------------------
    def _fill_field(self, field_name: str, value: str, broker: BrokerSite) -> bool:
        if field_name not in broker.form_fields:
            return True  # field not needed for this broker
        el_name = broker.form_fields[field_name]
        selectors = [
            (By.NAME, el_name),
            (By.ID, el_name),
            (By.CSS_SELECTOR, f"input[name='{el_name}']"),
            (By.CSS_SELECTOR, f"#{el_name}"),
            (By.XPATH, f"//input[@name='{el_name}']"),
            (By.XPATH, f"//input[@id='{el_name}']"),
        ]
        for by, val in selectors:
            try:
                el = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((by, val))
                )
                el.clear()
                el.send_keys(value)
                self.logger.debug("Filled %s for %s", field_name, broker.name)
                return True
            except (TimeoutException, NoSuchElementException):
                continue
        self.logger.warning("Could not find field %s for %s", field_name, broker.name)
        return False

    def _process_broker(self, broker: BrokerSite) -> Tuple[str, str]:
        """Navigate to broker opt-out page and attempt form submission."""
        try:
            self.logger.info("Processing %s", broker.name)
            self.driver.get(broker.opt_out_url)
            self._random_delay()

            field_values = {
                "first_name":    self.personal_info.first_name,
                "last_name":     self.personal_info.last_name,
                "email":         self.personal_info.email,
                "phone":         self.personal_info.phone,
                "address":       self.personal_info.address,
                "city":          self.personal_info.city,
                "state":         self.personal_info.state,
                "zip_code":      self.personal_info.zip_code,
                "date_of_birth": self.personal_info.date_of_birth,
                "middle_name":   self.personal_info.middle_name,
            }

            filled = sum(
                1
                for fname, fval in field_values.items()
                if fval and self._fill_field(fname, fval, broker)
            )

            # Try to find and click a submit button
            submit_selectors = [
                (By.CSS_SELECTOR,  "input[type='submit']"),
                (By.CSS_SELECTOR,  "button[type='submit']"),
                (By.XPATH,         "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'submit')]"),
                (By.XPATH,         "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'opt out')]"),
                (By.XPATH,         "//button[contains(translate(text(),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'remove')]"),
                (By.CSS_SELECTOR,  "button"),
            ]
            submitted = False
            for by, val in submit_selectors:
                try:
                    btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((by, val))
                    )
                    btn.click()
                    submitted = True
                    self.logger.info("Submitted form for %s", broker.name)
                    break
                except (TimeoutException, NoSuchElementException):
                    continue

            if not submitted:
                return "FAILED", "Could not find submit button"

            self._random_delay(3, 7)

            page = self.driver.page_source.lower()
            success_words = ["success", "submitted", "received", "thank you",
                             "opt-out", "removed", "processed"]
            if any(w in page for w in success_words):
                msg = "Form submitted successfully"
                status = "SUCCESS"
            else:
                msg = f"Form submitted — outcome unclear ({filled} fields filled)"
                status = "PARTIAL"

            if broker.requires_verification:
                msg += " — email verification may be required"
            return status, msg

        except WebDriverException as exc:
            return "FAILED", f"WebDriver error: {exc}"
        except Exception as exc:
            return "FAILED", f"Unexpected error: {exc}"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def run_opt_out_batch(
        self,
        broker_names: Optional[List[str]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
    ) -> Dict[str, Dict]:
        """
        Run opt-out for all (or selected) brokers.

        ``progress_callback(processed, total, current_broker_name)`` is called
        before each broker is processed so callers can track real-time progress.
        """
        if not self.driver:
            self.setup_driver()

        brokers = self.db.get_broker_sites()
        if broker_names:
            brokers = [b for b in brokers if b.name in broker_names]

        results: Dict[str, Dict] = {}
        total = len(brokers)

        try:
            for idx, broker in enumerate(brokers):
                if progress_callback:
                    progress_callback(idx, total, broker.name)
                try:
                    status, message = self._process_broker(broker)
                    results[broker.name] = {
                        "status":               status,
                        "message":              message,
                        "requires_verification": broker.requires_verification,
                    }
                    self.db.log_attempt(
                        broker_name=broker.name,
                        status=status,
                        error_message=message if status == "FAILED" else None,
                        verification_required=broker.requires_verification,
                        notes=message,
                    )
                    self.logger.info("Completed %s: %s", broker.name, status)
                    self._random_delay(5, 10)
                except Exception as exc:
                    err = f"Error processing {broker.name}: {exc}"
                    self.logger.error(err)
                    results[broker.name] = {
                        "status":               "FAILED",
                        "message":              err,
                        "requires_verification": False,
                    }
                    self.db.log_attempt(
                        broker_name=broker.name,
                        status="FAILED",
                        error_message=err,
                    )
        finally:
            if progress_callback:
                progress_callback(total, total, "")
            if self.driver:
                self.driver.quit()
                self.driver = None

        return results

    def get_status_summary(self) -> Dict:
        attempts = self.db.get_attempts_history()
        return {
            "total_attempts": len(attempts),
            "successful":     sum(1 for a in attempts if a["status"] == "SUCCESS"),
            "failed":         sum(1 for a in attempts if a["status"] == "FAILED"),
            "partial":        sum(1 for a in attempts if a["status"] == "PARTIAL"),
            "recent_attempts": attempts[:10],
        }
