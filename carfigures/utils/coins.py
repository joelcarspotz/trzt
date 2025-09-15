"""Coin system utilities"""

import random
from datetime import date, datetime, timedelta
from typing import Optional, Tuple

from carfigures.models import User, UserCoins, DailyClaim


class CoinManager:
    """Manages coin operations for users"""
    
    @staticmethod
    async def get_or_create_user_coins(user_id: int) -> UserCoins:
        """Get or create user coins record"""
        user, _ = await User.get_or_create(id=user_id)
        coins, _ = await UserCoins.get_or_create(user=user)
        return coins
    
    @staticmethod
    async def add_coins(user_id: int, amount: int, reason: str = "Unknown") -> UserCoins:
        """Add coins to user balance"""
        coins = await CoinManager.get_or_create_user_coins(user_id)
        coins.balance += amount
        coins.lifetime_earned += amount
        await coins.save()
        return coins
    
    @staticmethod
    async def spend_coins(user_id: int, amount: int) -> Tuple[bool, UserCoins]:
        """
        Spend coins from user balance
        Returns: (success, user_coins)
        """
        coins = await CoinManager.get_or_create_user_coins(user_id)
        
        if coins.balance < amount:
            return False, coins
        
        coins.balance -= amount
        coins.lifetime_spent += amount
        await coins.save()
        return True, coins
    
    @staticmethod
    async def get_balance(user_id: int) -> int:
        """Get user's current coin balance"""
        coins = await CoinManager.get_or_create_user_coins(user_id)
        return coins.balance
    
    @staticmethod
    async def can_claim_daily(user_id: int) -> Tuple[bool, Optional[DailyClaim]]:
        """
        Check if user can claim daily reward
        Returns: (can_claim, last_claim)
        """
        today = date.today()
        user, _ = await User.get_or_create(id=user_id)
        
        last_claim = await DailyClaim.filter(user=user).order_by("-claim_date").first()
        
        if not last_claim:
            return True, None
        
        if last_claim.claim_date < today:
            return True, last_claim
        
        return False, last_claim
    
    @staticmethod
    async def claim_daily(user_id: int, base_amount: int) -> Tuple[bool, int, int]:
        """
        Claim daily reward
        Returns: (success, amount_claimed, streak_count)
        """
        can_claim, last_claim = await CoinManager.can_claim_daily(user_id)
        
        if not can_claim:
            return False, 0, 0
        
        user, _ = await User.get_or_create(id=user_id)
        today = date.today()
        
        # Calculate streak
        streak_count = 1
        if last_claim:
            yesterday = today - timedelta(days=1)
            if last_claim.claim_date == yesterday:
                streak_count = last_claim.streak_count + 1
        
        # Calculate bonus based on streak (max 50% bonus at 7+ days)
        streak_bonus = min(streak_count * 0.05, 0.5)
        amount = int(base_amount * (1 + streak_bonus))
        
        # Create daily claim record
        await DailyClaim.create(
            user=user,
            claim_date=today,
            amount_claimed=amount,
            streak_count=streak_count
        )
        
        # Add coins to user
        await CoinManager.add_coins(user_id, amount, "Daily claim")
        
        return True, amount, streak_count
    
    @staticmethod
    async def reward_catch(user_id: int, base_reward: int, bonus_range: list) -> int:
        """
        Reward coins for catching a car
        Returns: amount_rewarded
        """
        bonus = random.randint(bonus_range[0], bonus_range[1])
        total_reward = base_reward + bonus
        
        await CoinManager.add_coins(user_id, total_reward, "Car catch")
        
        # Update user stats
        user, _ = await User.get_or_create(id=user_id)
        user.cars_caught += 1
        user.total_coins_earned += total_reward
        await user.save()
        
        return total_reward