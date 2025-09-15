"""
CarFigures Bot Entry Point
"""

import asyncio
import logging
import os
from pathlib import Path

import uvloop
from tortoise import Tortoise

from carfigures.core.bot import CarFiguresBot
from carfigures.core.config import Config

# Database configuration for Tortoise ORM
TORTOISE_ORM = {
    "connections": {
        "default": os.environ.get("CARFIGURESBOT_DB_URL", "sqlite://db.sqlite3")
    },
    "apps": {
        "models": {
            "models": ["carfigures.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}

async def init_db():
    """Initialize database"""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    
    # Create sample data if needed
    from carfigures.models import Car
    car_count = await Car.all().count()
    if car_count == 0:
        from carfigures.utils.sample_data import create_sample_cars, create_sample_packs
        await create_sample_cars()
        await create_sample_packs()
        logging.info("Created sample data")

async def main():
    """Main entry point"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("carfigures.log"),
            logging.StreamHandler()
        ]
    )
    
    # Load configuration
    config_path = Path("config.toml")
    config = Config.from_file(config_path)
    
    # Initialize database
    await init_db()
    
    # Create and run bot
    bot = CarFiguresBot(config)
    await bot.start(config.bot_token)

if __name__ == "__main__":
    if os.name != "nt":
        uvloop.install()
    
    asyncio.run(main())