"""Coin system models"""

from tortoise import fields
from tortoise.models import Model


class UserCoins(Model):
    """User coin balance"""
    id = fields.IntField(pk=True)
    user = fields.OneToOneField("models.User", related_name="coins")
    
    balance = fields.IntField(default=0)
    lifetime_earned = fields.IntField(default=0)
    lifetime_spent = fields.IntField(default=0)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "user_coins"


class DailyClaim(Model):
    """Daily coin claim tracking"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="daily_claims")
    
    claim_date = fields.DateField()
    amount_claimed = fields.IntField()
    
    # Streak tracking
    streak_count = fields.IntField(default=1)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "daily_claims"
        unique_together = ("user", "claim_date")