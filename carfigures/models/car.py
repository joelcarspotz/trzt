"""Car models"""

from tortoise import fields
from tortoise.models import Model


class Car(Model):
    """Car figure model"""
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    model = fields.CharField(max_length=255)
    year = fields.IntField()
    
    # Car stats
    horsepower = fields.IntField()
    weight = fields.IntField()
    
    # Rarity and appearance
    rarity = fields.FloatField()  # Lower = rarer
    image_url = fields.TextField(null=True)
    logo_url = fields.TextField(null=True)
    
    # Classification
    type = fields.CharField(max_length=100)  # Album equivalent
    is_exclusive = fields.BooleanField(default=False)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "cars"


class UserCar(Model):
    """User's car collection"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="cars")
    car = fields.ForeignKeyField("models.Car", related_name="owners")
    
    # Catch details
    caught_at = fields.DatetimeField(auto_now_add=True)
    catch_bonus = fields.IntField(default=0)  # Bonus coins earned when caught
    
    # Special attributes
    is_favorite = fields.BooleanField(default=False)
    is_shiny = fields.BooleanField(default=False)  # Special variant
    
    class Meta:
        table = "user_cars"
        unique_together = ("user", "car")