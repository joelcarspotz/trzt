"""Sample data creation utilities"""

from carfigures.models import Car, Pack, PackContent


async def create_sample_cars():
    """Create sample Aston Martin cars"""
    sample_cars = [
        {
            "name": "DB11",
            "model": "DB11 V12",
            "year": 2023,
            "horsepower": 630,
            "weight": 1875,
            "rarity": 8.0,
            "type": "Grand Tourer",
            "is_exclusive": False,
        },
        {
            "name": "Vantage",
            "model": "V8 Vantage",
            "year": 2023,
            "horsepower": 503,
            "weight": 1530,
            "rarity": 6.0,
            "type": "Sports Car",
            "is_exclusive": False,
        },
        {
            "name": "DBS",
            "model": "DBS Superleggera",
            "year": 2023,
            "horsepower": 715,
            "weight": 1693,
            "rarity": 4.0,
            "type": "Grand Tourer",
            "is_exclusive": False,
        },
        {
            "name": "DBX",
            "model": "DBX707",
            "year": 2023,
            "horsepower": 697,
            "weight": 2245,
            "rarity": 5.0,
            "type": "SUV",
            "is_exclusive": False,
        },
        {
            "name": "Valkyrie",
            "model": "Valkyrie AMR Pro",
            "year": 2023,
            "horsepower": 1160,
            "weight": 1000,
            "rarity": 0.5,
            "type": "Hypercar",
            "is_exclusive": True,
        },
        {
            "name": "Victor",
            "model": "Victor One-77",
            "year": 2021,
            "horsepower": 836,
            "weight": 1630,
            "rarity": 0.1,
            "type": "Track Special",
            "is_exclusive": True,
        },
    ]
    
    created_cars = []
    for car_data in sample_cars:
        car, created = await Car.get_or_create(
            name=car_data["name"],
            model=car_data["model"],
            defaults=car_data
        )
        created_cars.append(car)
    
    return created_cars


async def create_sample_packs():
    """Create sample packs"""
    cars = await Car.all()
    
    if not cars:
        cars = await create_sample_cars()
    
    # Basic Pack
    basic_pack, _ = await Pack.get_or_create(
        name="Basic Pack",
        defaults={
            "description": "A basic pack with common Aston Martins",
            "price": 500,
            "guaranteed_cars": 3,
            "common_chance": 80.0,
            "rare_chance": 18.0,
            "epic_chance": 2.0,
            "legendary_chance": 0.0,
            "color": "#8B4513"
        }
    )
    
    # Premium Pack
    premium_pack, _ = await Pack.get_or_create(
        name="Premium Pack",
        defaults={
            "description": "A premium pack with better chances for rare cars",
            "price": 1000,
            "guaranteed_cars": 5,
            "common_chance": 60.0,
            "rare_chance": 30.0,
            "epic_chance": 9.0,
            "legendary_chance": 1.0,
            "color": "#4169E1"
        }
    )
    
    # Legendary Pack
    legendary_pack, _ = await Pack.get_or_create(
        name="Legendary Pack",
        defaults={
            "description": "The ultimate pack with guaranteed rare cars!",
            "price": 2500,
            "guaranteed_cars": 7,
            "common_chance": 40.0,
            "rare_chance": 35.0,
            "epic_chance": 20.0,
            "legendary_chance": 5.0,
            "color": "#FFD700"
        }
    )
    
    # Add cars to packs
    packs = [basic_pack, premium_pack, legendary_pack]
    
    for pack in packs:
        for car in cars:
            # Adjust drop rate based on car rarity and pack type
            if car.rarity <= 1.0:  # Legendary
                drop_rate = 0.5 if pack.name == "Basic Pack" else 2.0 if pack.name == "Premium Pack" else 5.0
            elif car.rarity <= 2.0:  # Epic
                drop_rate = 2.0 if pack.name == "Basic Pack" else 5.0 if pack.name == "Premium Pack" else 10.0
            elif car.rarity <= 5.0:  # Rare
                drop_rate = 10.0 if pack.name == "Basic Pack" else 15.0 if pack.name == "Premium Pack" else 20.0
            else:  # Common
                drop_rate = 30.0 if pack.name == "Basic Pack" else 25.0 if pack.name == "Premium Pack" else 15.0
            
            await PackContent.get_or_create(
                pack=pack,
                car=car,
                defaults={"drop_rate": drop_rate}
            )
    
    return packs