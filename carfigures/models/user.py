"""User model"""

from tortoise import fields
from tortoise.models import Model


class User(Model):
    """Discord user model"""
    id = fields.BigIntField(pk=True)  # Discord user ID
    username = fields.CharField(max_length=255)
    discriminator = fields.CharField(max_length=4, null=True)
    avatar_url = fields.TextField(null=True)
    
    # User stats
    cars_caught = fields.IntField(default=0)
    total_coins_earned = fields.IntField(default=0)
    packs_opened = fields.IntField(default=0)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "users"