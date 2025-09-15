"""Pack system utilities"""

import random
from datetime import datetime
from typing import List, Optional, Tuple
from tortoise import models

from carfigures.models import Pack, PackContent, UserPack, Car, User, UserCar
from carfigures.utils.coins import CoinManager


class PackManager:
    """Manages pack operations"""
    
    @staticmethod
    async def get_available_packs() -> List[Pack]:
        """Get all available packs"""
        now = datetime.now()
        return await Pack.filter(
            is_active=True
        ).filter(
            # Either not limited time, or limited time but not expired
            models.Q(is_limited_time=False) |
            models.Q(available_until__gte=now)
        ).all()
    
    @staticmethod
    async def purchase_pack(user_id: int, pack_id: int) -> Tuple[bool, str, Optional[UserPack]]:
        """
        Purchase a pack for user
        Returns: (success, message, user_pack)
        """
        try:
            pack = await Pack.get(id=pack_id, is_active=True)
        except:
            return False, "Pack not found or not available!", None
        
        # Check if pack is still available (limited time)
        if pack.is_limited_time and pack.available_until:
            if datetime.now() > pack.available_until:
                return False, "This pack is no longer available!", None
        
        # Check if user has enough coins
        user_coins = await CoinManager.get_or_create_user_coins(user_id)
        if user_coins.balance < pack.price:
            return False, f"Insufficient coins! You need {pack.price} coins but only have {user_coins.balance}.", None
        
        # Spend coins
        success, _ = await CoinManager.spend_coins(user_id, pack.price)
        if not success:
            return False, "Failed to process payment!", None
        
        # Create pack record
        user, _ = await User.get_or_create(id=user_id)
        user_pack = await UserPack.create(
            user=user,
            pack=pack,
            price_paid=pack.price
        )
        
        return True, f"Successfully purchased {pack.name} pack!", user_pack
    
    @staticmethod
    async def open_pack(user_pack_id: int) -> Tuple[bool, str, List[Car]]:
        """
        Open a pack and get cars
        Returns: (success, message, cars_received)
        """
        try:
            user_pack = await UserPack.get(id=user_pack_id).prefetch_related("pack", "user")
        except:
            return False, "Pack not found!", []
        
        if user_pack.is_opened:
            return False, "This pack has already been opened!", []
        
        pack = user_pack.pack
        
        # Get available cars for this pack
        pack_contents = await PackContent.filter(pack=pack).prefetch_related("car")
        
        if not pack_contents:
            return False, "This pack has no available cars!", []
        
        # Generate cars based on rarity chances
        cars_received = []
        
        for _ in range(pack.guaranteed_cars):
            # Roll for rarity
            roll = random.random() * 100
            
            if roll <= pack.legendary_chance:
                rarity_threshold = 1.0  # Legendary
            elif roll <= pack.legendary_chance + pack.epic_chance:
                rarity_threshold = 2.0  # Epic
            elif roll <= pack.legendary_chance + pack.epic_chance + pack.rare_chance:
                rarity_threshold = 5.0  # Rare
            else:
                rarity_threshold = 10.0  # Common
            
            # Get cars of appropriate rarity
            available_cars = [
                pc.car for pc in pack_contents 
                if pc.car.rarity <= rarity_threshold
            ]
            
            if available_cars:
                # Weight selection by drop rate
                weights = [
                    next(pc.drop_rate for pc in pack_contents if pc.car.id == car.id)
                    for car in available_cars
                ]
                
                selected_car = random.choices(available_cars, weights=weights)[0]
                cars_received.append(selected_car)
                
                # Add to user's collection
                user_car, created = await UserCar.get_or_create(
                    user=user_pack.user,
                    car=selected_car
                )
                
                # Small chance for shiny variant
                if random.random() < 0.05:  # 5% chance
                    user_car.is_shiny = True
                    await user_car.save()
        
        # Mark pack as opened
        user_pack.is_opened = True
        user_pack.opened_at = datetime.now()
        user_pack.cars_received = [car.id for car in cars_received]
        await user_pack.save()
        
        # Update user stats
        user_pack.user.packs_opened += 1
        await user_pack.user.save()
        
        return True, f"Opened {pack.name} pack!", cars_received
    
    @staticmethod
    async def get_user_unopened_packs(user_id: int) -> List[UserPack]:
        """Get user's unopened packs"""
        return await UserPack.filter(
            user_id=user_id,
            is_opened=False
        ).prefetch_related("pack").order_by("-purchased_at")
    
    @staticmethod
    async def create_pack(
        name: str,
        description: str,
        price: int,
        guaranteed_cars: int = 3,
        common_chance: float = 70.0,
        rare_chance: float = 25.0,
        epic_chance: float = 4.5,
        legendary_chance: float = 0.5,
        image_url: Optional[str] = None,
        color: str = "#1F8B4C"
    ) -> Pack:
        """Create a new pack (admin function)"""
        return await Pack.create(
            name=name,
            description=description,
            price=price,
            guaranteed_cars=guaranteed_cars,
            common_chance=common_chance,
            rare_chance=rare_chance,
            epic_chance=epic_chance,
            legendary_chance=legendary_chance,
            image_url=image_url,
            color=color
        )