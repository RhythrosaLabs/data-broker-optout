#!/usr/bin/env python3
"""
Command-line interface for the Data Broker Opt-Out Bot.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .bot import OptOutBot
from .database import DatabaseManager

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Data Broker Opt-Out Bot - Automate your privacy protection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --web                           # Start web interface
  %(prog)s --run-batch                     # Run all brokers
  %(prog)s --run-batch --headless          # Run headlessly
  %(prog)s --brokers "Spokeo,WhitePages"   # Run specific brokers
  %(prog)s --list-brokers                  # Show available brokers
  %(prog)s --status                        # Show status summary
  %(prog)s --config                        # Show current configuration
        """
    )
    
    # Main action groups
    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        '--web', 
        action='store_true',
        help='Start the web interface (default)'
    )
    action_group.add_argument(
        '--run-batch', 
        action='store_true',
        help='Run opt-out batch process'
    )
    action_group.add_argument(
        '--status', 
        action='store_true',
        help='Show status summary'
    )
    action_group.add_argument(
        '--list-brokers', 
        action='store_true',
        help='List all available data brokers'
    )
    action_group.add_argument(
        '--config', 
        action='store_true',
        help='Show current configuration'
    )
    
    # Options for batch run
    parser.add_argument(
        '--brokers',
        type=str,
        help='Comma-separated list of specific brokers to process'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run in headless mode (no browser window)'
    )
    parser.add_argument(
        '--config-file',
        type=str,
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Timeout in seconds for web operations (default: 30)'
    )
    parser.add_argument(
        '--retry-attempts',
        type=int,
        default=3,
        help='Number of retry attempts for failed operations (default: 3)'
    )
    parser.add_argument(
        '--delay-min',
        type=int,
        default=2,
        help='Minimum delay between operations in seconds (default: 2)'
    )
    parser.add_argument(
        '--delay-max',
        type=int,
        default=5,
        help='Maximum delay between operations in seconds (default: 5)'
    )
    
    # Logging options
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress output except errors'
    )
    parser.add_argument(
        '--log-file',
        type=str,
        help='Custom log file path'
    )
    
    # Development options
    parser.add_argument(
        '--test',
        action='store_true',
        help='Test mode - don\'t actually submit forms'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    args = parser.parse_args()
    
    # Default to web interface if no action specified
    if not any([args.run_batch, args.status, args.list_brokers, args.config]):
        args.web = True
    
    try:
        # Handle different actions
        if args.config:
            show_config(args.config_file)
        elif args.list_brokers:
            list_brokers(args.config_file)
        elif args.status:
            show_status(args.config_file)
        elif args.run_batch:
            run_batch(args)
        elif args.web:
            start_web_interface(args)
            
    except KeyboardInterrupt:
        print("\n⏹️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

def show_config(config_file):
    """Show current configuration"""
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        print("📋 Current Configuration")
        print("=" * 25)
        
        personal_info = config.get('personal_info', {})
        print(f"Name: {personal_info.get('first_name', 'N/A')} {personal_info.get('last_name', 'N/A')}")
        print(f"Email: {personal_info.get('email', 'N/A')}")
        print(f"Phone: {personal_info.get('phone', 'N/A')}")
        print(f"Address: {personal_info.get('address', 'N/A')}")
        print(f"City, State ZIP: {personal_info.get('city', 'N/A')}, {personal_info.get('state', 'N/A')} {personal_info.get('zip_code', 'N/A')}")
        
        bot_settings = config.get('bot_settings', {})
        print(f"\nBot Settings:")
        print(f"Headless Mode: {bot_settings.get('headless', 'N/A')}")
        print(f"Timeout: {bot_settings.get('timeout', 'N/A')}s")
        print(f"Retry Attempts: {bot_settings.get('retry_attempts', 'N/A')}")
        print(f"Delay Range: {bot_settings.get('delay_min', 'N/A')}-{bot_settings.get('delay_max', 'N/A')}s")
        
    except FileNotFoundError:
        print(f"❌ Configuration file not found: {config_file}")
        print("Run the installer first: python install.py")
    except json.JSONDecodeError:
        print(f"❌ Invalid JSON in configuration file: {config_file}")

def list_brokers(config_file):
    """List all available brokers"""
    try:
        bot = OptOutBot(config_file)
        brokers = bot.db.get_broker_sites()
        
        print("🏢 Available Data Brokers")
        print("=" * 25)
        
        for broker in brokers:
            difficulty_emoji = {"easy": "🟢", "medium": "🟡", "hard": "🔴"}.get(broker.difficulty, "⚪")
            verification_emoji = "📧" if broker.requires_verification else "✅"
            
            print(f"{difficulty_emoji} {verification_emoji} {broker.name}")
            print(f"   URL: {broker.opt_out_url}")
            print(f"   Difficulty: {broker.difficulty.title()}")
            if broker.instructions:
                print(f"   Instructions: {broker.instructions}")
            print()
        
        print("Legend:")
        print("🟢 Easy  🟡 Medium  🔴 Hard")
        print("✅ No verification required  📧 Email verification required")
        
    except Exception as e:
        print(f"❌ Error loading brokers: {e}")

def show_status(config_file):
    """Show status summary"""
    try:
        bot = OptOutBot(config_file)
        summary = bot.get_status_summary()
        
        print("📊 Opt-Out Status Summary")
        print("=" * 25)
        print(f"Total Attempts: {summary['total_attempts']}")
        print(f"Successful: {summary['successful']} ✅")
        print(f"Partial: {summary['partial']} ⚠️")
        print(f"Failed: {summary['failed']} ❌")
        
        if summary['recent_attempts']:
            print(f"\n🕒 Recent Activity:")
            for attempt in summary['recent_attempts'][:5]:
                status_emoji = {"SUCCESS": "✅", "PARTIAL": "⚠️", "FAILED": "❌"}.get(attempt['status'], "❓")
                print(f"   {status_emoji} {attempt['broker_name']} - {attempt['attempt_date'][:19]}")
        
    except Exception as e:
        print(f"❌ Error getting status: {e}")

def run_batch(args):
    """Run batch opt-out process"""
    try:
        # Parse broker list
        broker_list = None
        if args.brokers:
            broker_list = [b.strip() for b in args.brokers.split(',')]
        
        print("🤖 Starting Data Broker Opt-Out Bot")
        print("=" * 35)
        
        if broker_list:
            print(f"📋 Processing specific brokers: {', '.join(broker_list)}")
        else:
            print("📋 Processing all available brokers")
        
        print(f"🎛️  Mode: {'Headless' if args.headless else 'Visible browser'}")
        print(f"⏱️  Timeout: {args.timeout}s")
        print(f"🔄 Retry attempts: {args.retry_attempts}")
        print(f"⏳ Delay range: {args.delay_min}-{args.delay_max}s")
        
        if args.test:
            print("🧪 TEST MODE - Forms will not actually be submitted")
        
        print("\nStarting in 3 seconds... (Ctrl+C to cancel)")
        import time
        for i in range(3, 0, -1):
            print(f"{i}...")
            time.sleep(1)
        
        # Create bot instance
        bot = OptOutBot(config_path=args.config_file, headless=args.headless)
        
        # Run the batch process
        print("\n🚀 Running opt-out batch...")
        results = bot.run_opt_out_batch(broker_list)
        
        # Display results
        print("\n📊 Results Summary")
        print("=" * 20)
        
        success_count = sum(1 for r in results.values() if r['status'] == 'SUCCESS')
        partial_count = sum(1 for r in results.values() if r['status'] == 'PARTIAL')
        failed_count = sum(1 for r in results.values() if r['status'] == 'FAILED')
        
        print(f"✅ Successful: {success_count}")
        print(f"⚠️  Partial: {partial_count}")
        print(f"❌ Failed: {failed_count}")
        print(f"📈 Total processed: {len(results)}")
        
        # Detailed results
        print("\n📋 Detailed Results:")
        for broker_name, result in results.items():
            status_emoji = {"SUCCESS": "✅", "PARTIAL": "⚠️", "FAILED": "❌"}.get(result['status'], "❓")
            print(f"{status_emoji} {broker_name}: {result['message']}")
            if result.get('requires_verification'):
                print(f"   📧 Email verification may be required")
        
        # Check for verification requirements
        verification_needed = [name for name, result in results.items() if result.get('requires_verification')]
        if verification_needed:
            print(f"\n📧 Check your email for verification requests from: {', '.join(verification_needed)}")
        
        print(f"\n🎉 Batch processing completed!")
        print(f"📄 View detailed logs in: opt_out_bot.log")
        print(f"💾 Results stored in database: opt_out_log.db")
        
    except Exception as e:
        print(f"❌ Batch run failed: {e}")
        raise

def start_web_interface(args):
    """Start the Flask web interface"""
    print("🌐 Starting Data Broker Opt-Out Bot Web Interface")
    print("=" * 50)
    print("📋 Access the interface at: http://localhost:5000")
    print("⏹️  Press Ctrl+C to stop the server")
    print()
    
    # Import and run the Flask app
    from .__main__ import app, setup_scheduler
    
    # Setup the scheduler
    setup_scheduler()
    
    # Configure Flask app
    if args.debug:
        app.config['DEBUG'] = True
    
    # Run the Flask app
    try:
        app.run(
            debug=args.debug,
            host='0.0.0.0',
            port=5000,
            use_reloader=False  # Disable reloader to prevent scheduler issues
        )
    except KeyboardInterrupt:
        print("\n⏹️  Web interface stopped")

if __name__ == "__main__":
    main()