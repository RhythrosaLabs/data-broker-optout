# update_broker_db.py
#!/usr/bin/env python3
"""
Script to update the broker database with comprehensive list
"""

def update_broker_database():
    """Update database with comprehensive broker list"""
    from .database import DatabaseManager
    from .brokers import get_comprehensive_broker_list
    
    db = DatabaseManager()
    brokers = get_comprehensive_broker_list()
    
    print("📊 Updating broker database...")
    print(f"Adding {len(brokers)} data brokers...")
    
    for broker in brokers:
        db.add_broker_site(broker)
    
    print("✅ Database updated successfully!")
    print("\nBroker breakdown by difficulty:")
    
    easy = len([b for b in brokers if b.difficulty == "easy"])
    medium = len([b for b in brokers if b.difficulty == "medium"])  
    hard = len([b for b in brokers if b.difficulty == "hard"])
    
    print(f"🟢 Easy: {easy}")
    print(f"🟡 Medium: {medium}")
    print(f"🔴 Hard: {hard}")
    
    verification_required = len([b for b in brokers if b.requires_verification])
    print(f"📧 Require verification: {verification_required}")

if __name__ == "__main__":
    update_broker_database()