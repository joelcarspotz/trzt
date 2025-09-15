"""Admin panel using FastAPI and fastapi-admin"""

import os
from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.enums import Method
from fastapi_admin.file_upload import FileUpload
from fastapi_admin.middlewares import AdminMiddleware
from fastapi_admin.models import AbstractAdmin
from fastapi_admin.providers.login import UsernamePasswordProvider
from fastapi_admin.resources import Action, Dropdown, Field, Link, Model, ToolbarAction
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request
from starlette.staticfiles import StaticFiles
from tortoise import Tortoise

from carfigures.models import User, Car, Pack, PackContent, UserCoins, UserPack
from carfigures.__main__ import TORTOISE_ORM

# Create FastAPI app
_app = FastAPI()

# Add session middleware
_app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "your-secret-key-here")
)

# Add admin middleware
_app.add_middleware(AdminMiddleware)

# Mount static files
_app.mount("/static", StaticFiles(directory="static"), name="static")


class AdminUser(AbstractAdmin):
    """Admin user for login"""
    last_login = None
    email = None
    avatar = ""
    intro = ""
    created_at = None
    pk = 1
    username = "admin"
    
    def __str__(self):
        return f"{self.username}"
    
    @classmethod
    async def get_by_username(cls, username: str) -> "AdminUser":
        if username == "admin":
            return cls()
        return None


# Configure admin
admin_app.add_admin_class(AdminUser)

# Login provider
admin_app.add_provider(
    UsernamePasswordProvider(
        admin_model=AdminUser,
        login_logo_url="https://preview.tabler.io/static/logo.svg",
    )
)

# File upload configuration
upload = FileUpload(uploads_dir="static/uploads")


# Admin resources
@admin_app.register
class UserResource(Model):
    label = "Users"
    model = User
    icon = "fas fa-users"
    page_pre_title = "User Management"
    page_title = "Users"
    filters = [
        Field("username", label="Username"),
        Field("cars_caught", label="Cars Caught"),
    ]
    fields = [
        Field("id", label="Discord ID"),
        Field("username", label="Username"),
        Field("cars_caught", label="Cars Caught"),
        Field("total_coins_earned", label="Total Coins Earned"),
        Field("packs_opened", label="Packs Opened"),
        Field("created_at", label="Joined At"),
    ]


@admin_app.register
class CarResource(Model):
    label = "Cars"
    model = Car
    icon = "fas fa-car"
    page_pre_title = "Car Management"
    page_title = "Car Figures"
    filters = [
        Field("name", label="Name"),
        Field("model", label="Model"),
        Field("type", label="Type"),
        Field("rarity", label="Rarity"),
    ]
    fields = [
        Field("id", label="ID"),
        Field("name", label="Name"),
        Field("model", label="Model"),
        Field("year", label="Year"),
        Field("horsepower", label="Horsepower"),
        Field("weight", label="Weight"),
        Field("rarity", label="Rarity"),
        Field("type", label="Type"),
        Field("is_exclusive", label="Exclusive"),
        Field("image_url", label="Image URL"),
        Field("logo_url", label="Logo URL"),
    ]


@admin_app.register
class PackResource(Model):
    label = "Packs"
    model = Pack
    icon = "fas fa-box"
    page_pre_title = "Pack Management"
    page_title = "Packs"
    filters = [
        Field("name", label="Name"),
        Field("is_active", label="Active"),
        Field("price", label="Price"),
    ]
    fields = [
        Field("id", label="ID"),
        Field("name", label="Name"),
        Field("description", label="Description"),
        Field("price", label="Price (Coins)"),
        Field("guaranteed_cars", label="Guaranteed Cars"),
        Field("common_chance", label="Common %"),
        Field("rare_chance", label="Rare %"),
        Field("epic_chance", label="Epic %"),
        Field("legendary_chance", label="Legendary %"),
        Field("is_active", label="Active"),
        Field("is_limited_time", label="Limited Time"),
        Field("available_until", label="Available Until"),
        Field("image_url", label="Image URL"),
        Field("color", label="Color"),
        Field("created_at", label="Created At"),
    ]


@admin_app.register
class PackContentResource(Model):
    label = "Pack Contents"
    model = PackContent
    icon = "fas fa-list"
    page_pre_title = "Pack Management"
    page_title = "Pack Contents"
    filters = [
        Field("pack", label="Pack"),
        Field("car", label="Car"),
    ]
    fields = [
        Field("id", label="ID"),
        Field("pack", label="Pack"),
        Field("car", label="Car"),
        Field("drop_rate", label="Drop Rate %"),
    ]


@admin_app.register
class UserCoinsResource(Model):
    label = "User Coins"
    model = UserCoins
    icon = "fas fa-coins"
    page_pre_title = "Economy"
    page_title = "User Coins"
    filters = [
        Field("balance", label="Balance"),
        Field("lifetime_earned", label="Lifetime Earned"),
    ]
    fields = [
        Field("id", label="ID"),
        Field("user", label="User"),
        Field("balance", label="Current Balance"),
        Field("lifetime_earned", label="Lifetime Earned"),
        Field("lifetime_spent", label="Lifetime Spent"),
        Field("updated_at", label="Last Updated"),
    ]


@admin_app.register
class UserPackResource(Model):
    label = "Pack Purchases"
    model = UserPack
    icon = "fas fa-shopping-cart"
    page_pre_title = "Economy"
    page_title = "Pack Purchases"
    filters = [
        Field("user", label="User"),
        Field("pack", label="Pack"),
        Field("is_opened", label="Opened"),
    ]
    fields = [
        Field("id", label="ID"),
        Field("user", label="User"),
        Field("pack", label="Pack"),
        Field("price_paid", label="Price Paid"),
        Field("purchased_at", label="Purchased At"),
        Field("is_opened", label="Opened"),
        Field("opened_at", label="Opened At"),
        Field("cars_received", label="Cars Received"),
    ]


# Custom actions
@admin_app.register
class PackActions:
    """Custom actions for pack management"""
    
    @staticmethod
    async def toggle_pack_status(request: Request):
        """Toggle pack active status"""
        pack_id = request.query_params.get("pack_id")
        if pack_id:
            pack = await Pack.get(id=pack_id)
            pack.is_active = not pack.is_active
            await pack.save()
        return {"success": True}


# Dashboard customization
@admin_app.register
class Dashboard:
    async def get_dashboard_data(self):
        """Get dashboard statistics"""
        total_users = await User.all().count()
        total_cars = await Car.all().count()
        total_packs = await Pack.all().count()
        active_packs = await Pack.filter(is_active=True).count()
        
        return {
            "total_users": total_users,
            "total_cars": total_cars,
            "total_packs": total_packs,
            "active_packs": active_packs,
        }


async def init_admin():
    """Initialize admin panel"""
    await Tortoise.init(config=TORTOISE_ORM)
    await admin_app.init()


# Mount admin app
_app.mount("/admin", admin_app)

# Initialize on startup
@_app.on_event("startup")
async def startup():
    await init_admin()

# Export app
app = _app