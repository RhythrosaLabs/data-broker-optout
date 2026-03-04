# systemd_service.py
#!/usr/bin/env python3
"""
Create systemd service files for Linux systems
"""

import os
import sys
from pathlib import Path

def create_systemd_service():
    """Create systemd service file"""
    
    script_dir = Path(__file__).parent.absolute()
    user = os.getenv('USER', 'optout-user')
    
    service_content = f"""[Unit]
Description=Data Broker Opt-Out Bot
After=network.target
Wants=network.target

[Service]
Type=simple
User={user}
WorkingDirectory={script_dir}
ExecStart=/usr/bin/python3 {script_dir}/main.py --web
Restart=always
RestartSec=10
Environment=PATH=/usr/bin:/usr/local/bin
Environment=DISPLAY=:0

[Install]  
WantedBy=multi-user.target
"""

    timer_content = f"""[Unit]
Description=Data Broker Opt-Out Bot Timer
Requires=optout-bot.service

[Timer]
OnCalendar=monthly
Persistent=true

[Install]
WantedBy=timers.target
"""

    batch_service_content = f"""[Unit]
Description=Data Broker Opt-Out Bot Batch Run
After=network.target

[Service]
Type=oneshot
User={user}
WorkingDirectory={script_dir}
ExecStart=/usr/bin/python3 {script_dir}/main.py --run-batch --headless
"""

    print("🐧 Creating systemd service files...")
    
    # Create service files
    service_file = Path("/tmp/optout-bot.service")
    timer_file = Path("/tmp/optout-bot.timer") 
    batch_file = Path("/tmp/optout-bot-batch.service")
    
    with open(service_file, 'w') as f:
        f.write(service_content)
    
    with open(timer_file, 'w') as f:
        f.write(timer_content)
        
    with open(batch_file, 'w') as f:
        f.write(batch_service_content)
    
    print(f"✅ Service files created in /tmp/")
    print("\nTo install:")
    print(f"sudo cp {service_file} /etc/systemd/system/")
    print(f"sudo cp {timer_file} /etc/systemd/system/")
    print(f"sudo cp {batch_file} /etc/systemd/system/")
    print("sudo systemctl daemon-reload")
    print("sudo systemctl enable optout-bot.service")
    print("sudo systemctl enable optout-bot.timer")
    print("sudo systemctl start optout-bot.service")
    print("sudo systemctl start optout-bot.timer")

if __name__ == "__main__":
    create_systemd_service()