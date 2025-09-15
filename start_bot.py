#!/usr/bin/env python3
"""
Simple startup script for CarFigures bot
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set environment variables if not set
if not os.environ.get("CARFIGURESBOT_DB_URL"):
    os.environ["CARFIGURESBOT_DB_URL"] = "sqlite://db.sqlite3"

# Import and run the bot
from carfigures.__main__ import main

if __name__ == "__main__":
    print("🚗 Starting CarFigures Bot...")
    print("📁 Project root:", project_root)
    print("🗄️  Database URL:", os.environ.get("CARFIGURESBOT_DB_URL"))
    print("⚠️  Make sure to set your bot token in config.toml!")
    print()
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot crashed: {e}")
        sys.exit(1)