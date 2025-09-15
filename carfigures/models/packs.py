"""Pack system models"""

from tortoise import fields
from tortoise.models import Model


class Pack(Model):
    """Pack type definition"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, unique=True)
    description = fields.TextField()
    
    # Pricing and rewards
    price = fields.IntField()
    guaranteed_cars = fields.IntField(default=3)  # Number of cars guaranteed
    
    # Rarity chances (as percentages)
    common_chance = fields.FloatField(default=70.0)
    rare_chance = fields.FloatField(default=25.0)
    epic_chance = fields.FloatField(default=4.5)
    legendary_chance = fields.FloatField(default=0.5)
    
    # Pack appearance
    image_url = fields.TextField(null=True)
    color = fields.CharField(max_length=7, default="#1F8B4C")  # Hex color
    
    # Availability
    is_active = fields.BooleanField(default=True)
    is_limited_time = fields.BooleanField(default=False)
    available_until = fields.DatetimeField(null=True)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "packs"


class PackContent(Model):
    """Specific cars that can be found in packs"""
    id = fields.IntField(pk=True)
    pack = fields.ForeignKeyField("models.Pack", related_name="contents")
    car = fields.ForeignKeyField("models.Car", related_name="pack_appearances")
    
    # Drop rate for this specific car in this pack
    drop_rate = fields.FloatField()  # Percentage chance
    
    class Meta:
        table = "pack_contents"
        unique_together = ("pack", "car")


class UserPack(Model):
    """User pack purchase and opening history"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="pack_history")
    pack = fields.ForeignKeyField("models.Pack", related_name="purchases")
    
    # Purchase details
    price_paid = fields.IntField()
    purchased_at = fields.DatetimeField(auto_now_add=True)
    
    # Opening details
    is_opened = fields.BooleanField(default=False)
    opened_at = fields.DatetimeField(null=True)
    cars_received = fields.JSONField(default=list)  # List of car IDs received
    
    class Meta:
        table = "user_packs"