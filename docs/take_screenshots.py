"""Take screenshots of the running web UI for the README."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import time
from pathlib import Path

opts = Options()
opts.add_argument("--headless=new")
opts.add_argument("--no-sandbox")
opts.add_argument("--disable-dev-shm-usage")
opts.add_argument("--window-size=1280,900")
opts.add_argument("--hide-scrollbars")
opts.add_argument("--force-device-scale-factor=2")

CHROMEDRIVER = "/Users/sheils/.wdm/drivers/chromedriver/mac64/145.0.7632.117/chromedriver-mac-arm64/chromedriver"
driver = webdriver.Chrome(service=Service(CHROMEDRIVER), options=opts)
out = Path(__file__).parent / "screenshots"
out.mkdir(exist_ok=True)

pages = [
    ("dashboard", "/"),
    ("config",    "/config"),
    ("history",   "/history"),
]

for name, path in pages:
    driver.get(f"http://127.0.0.1:5000{path}")
    time.sleep(2)
    driver.save_screenshot(str(out / f"{name}.png"))
    print(f"  saved {name}.png  ({driver.title})")

driver.quit()
print("Done")
