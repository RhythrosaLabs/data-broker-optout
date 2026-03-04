#!/usr/bin/env python3
"""
Configuration management utilities.
"""
from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

from .models import PersonalInfo

@dataclass
class BotSettings:
    """Bot configuration settings"""
    headless: bool = True
    delay_min: int = 2
    delay_max: int = 5
    timeout: int = 30
    retry_attempts: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

class ConfigManager:
    """Handles configuration file operations"""
    
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self.personal_info = None
        self.bot_settings = None
        self.load_config()
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                
                # Load personal info
                personal_data = config_data.get('personal_info', {})
                self.personal_info = PersonalInfo(**personal_data)
                
                # Load bot settings
                bot_data = config_data.get('bot_settings', {})
                self.bot_settings = BotSettings(**bot_data)
            else:
                # Create default configuration
                self.create_default_config()
                
        except Exception as e:
            raise Exception(f"Error loading configuration: {e}")
    
    def create_default_config(self):
        """Create default configuration"""
        self.personal_info = PersonalInfo(
            first_name="John",
            last_name="Doe", 
            email="john.doe@example.com",
            phone="555-123-4567",
            address="123 Main St",
            city="Anytown",
            state="CA",
            zip_code="12345"
        )
        self.bot_settings = BotSettings()
        self.save_config()
    
    def save_config(self):
        """Save configuration to file"""
        config_data = {
            "personal_info": asdict(self.personal_info),
            "bot_settings": asdict(self.bot_settings)
        }
        
        with open(self.config_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def update_personal_info(self, **kwargs):
        """Update personal information"""
        for key, value in kwargs.items():
            if hasattr(self.personal_info, key):
                setattr(self.personal_info, key, value)
        self.save_config()
    
    def update_bot_settings(self, **kwargs):
        """Update bot settings"""
        for key, value in kwargs.items():
            if hasattr(self.bot_settings, key):
                setattr(self.bot_settings, key, value)
        self.save_config()
    
    def validate_config(self) -> List[str]:
        """Validate configuration and return list of issues"""
        issues = []
        
        # Check required personal info
        if not self.personal_info.first_name:
            issues.append("First name is required")
        if not self.personal_info.last_name:
            issues.append("Last name is required")
        if not self.personal_info.email:
            issues.append("Email is required")
        elif "@" not in self.personal_info.email:
            issues.append("Email format appears invalid")
        
        # Check bot settings
        if self.bot_settings.delay_min >= self.bot_settings.delay_max:
            issues.append("Minimum delay must be less than maximum delay")
        if self.bot_settings.timeout <= 0:
            issues.append("Timeout must be positive")
        if self.bot_settings.retry_attempts < 0:
            issues.append("Retry attempts cannot be negative")
        
        return issues
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        return {
            "personal_info": {
                "name": f"{self.personal_info.first_name} {self.personal_info.last_name}",
                "email": self.personal_info.email,
                "phone": self.personal_info.phone or "Not provided",
                "location": f"{self.personal_info.city}, {self.personal_info.state}" if self.personal_info.city else "Not provided"
            },
            "bot_settings": asdict(self.bot_settings),
            "validation_issues": self.validate_config()
        }

# Enhanced main.py integration
def create_enhanced_main():
    """
    Enhanced version of main.py with CLI integration
    Add this to the end of your main.py file
    """
    enhanced_code = '''
def main():
    """Enhanced main function with CLI support"""
    import sys
    
    if len(sys.argv) > 1:
        # Use CLI interface
        from cli import main as cli_main
        cli_main()
    else:
        # Default to web interface
        print("🌐 Starting Data Broker Opt-Out Bot Web Interface")
        print("=" * 50)
        print("📋 Access the interface at: http://localhost:5000")
        print("⏹️  Press Ctrl+C to stop the server")
        print("💡 Use --help for command-line options")
        print()
        
        # Setup scheduler
        setup_scheduler()
        
        # Run Flask app
        try:
            app.run(debug=False, host='0.0.0.0', port=5000, use_reloader=False)
        except KeyboardInterrupt:
            print("\\n⏹️  Web interface stopped")

if __name__ == "__main__":
    main()
'''
    return enhanced_code