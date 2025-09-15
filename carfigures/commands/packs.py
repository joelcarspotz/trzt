"""Pack system commands"""

import discord
from discord.ext import commands
from typing import Optional

from carfigures.utils.packs import PackManager
from carfigures.utils.coins import CoinManager
from carfigures.models import Pack


class PackCommands(commands.Cog):
    """Commands for the pack system"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="shop", aliases=["store", "packs"])
    async def show_shop(self, ctx):
        """Show available packs in the shop"""
        packs = await PackManager.get_available_packs()
        
        if not packs:
            embed = discord.Embed(
                title="🏪 Pack Shop",
                description="No packs are currently available!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        embed = discord.Embed(
            title="🏪 Pack Shop",
            description="Available packs to purchase with coins",
            color=int(self.bot.config.default_embed_color, 16)
        )
        
        for pack in packs:
            rarity_info = (
                f"🟫 Common: {pack.common_chance}%\n"
                f"🟦 Rare: {pack.rare_chance}%\n"
                f"🟪 Epic: {pack.epic_chance}%\n"
                f"🟨 Legendary: {pack.legendary_chance}%"
            )
            
            embed.add_field(
                name=f"{pack.name} - 🪙 {pack.price:,} coins",
                value=(
                    f"{pack.description}\n"
                    f"**Guaranteed Cars:** {pack.guaranteed_cars}\n"
                    f"**Rarity Chances:**\n{rarity_info}"
                ),
                inline=False
            )
        
        embed.set_footer(text="Use !buy <pack_name> to purchase a pack")
        await ctx.send(embed=embed)
    
    @commands.command(name="buy", aliases=["purchase"])
    async def buy_pack(self, ctx, *, pack_name: str):
        """Buy a pack from the shop"""
        # Find pack by name (case insensitive)
        pack = await Pack.filter(
            name__icontains=pack_name,
            is_active=True
        ).first()
        
        if not pack:
            embed = discord.Embed(
                title="❌ Pack Not Found",
                description=f"Could not find a pack named '{pack_name}'.\nUse `!shop` to see available packs.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Attempt purchase
        success, message, user_pack = await PackManager.purchase_pack(ctx.author.id, pack.id)
        
        if success:
            embed = discord.Embed(
                title="🎉 Pack Purchased!",
                description=message,
                color=0x00ff00
            )
            embed.add_field(
                name="Pack Details",
                value=(
                    f"**Name:** {pack.name}\n"
                    f"**Price:** 🪙 {pack.price:,} coins\n"
                    f"**Guaranteed Cars:** {pack.guaranteed_cars}"
                ),
                inline=False
            )
            embed.add_field(
                name="Next Steps",
                value=f"Use `!open {user_pack.id}` to open your pack!",
                inline=False
            )
        else:
            embed = discord.Embed(
                title="❌ Purchase Failed",
                description=message,
                color=0xff0000
            )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="inventory", aliases=["inv", "unopened"])
    async def show_inventory(self, ctx, user: discord.Member = None):
        """Show your unopened packs"""
        target_user = user or ctx.author
        
        unopened_packs = await PackManager.get_user_unopened_packs(target_user.id)
        
        embed = discord.Embed(
            title=f"📦 {target_user.display_name}'s Unopened Packs",
            color=int(self.bot.config.default_embed_color, 16)
        )
        
        if not unopened_packs:
            embed.description = "No unopened packs found!\nVisit the shop with `!shop` to buy some packs."
        else:
            pack_list = ""
            for user_pack in unopened_packs:
                pack_list += (
                    f"**Pack #{user_pack.id}:** {user_pack.pack.name}\n"
                    f"💰 Paid: {user_pack.price_paid:,} coins\n"
                    f"📅 Purchased: {user_pack.purchased_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                )
            
            embed.description = pack_list
            embed.set_footer(text="Use !open <pack_id> to open a pack")
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @commands.command(name="open")
    async def open_pack(self, ctx, pack_id: int):
        """Open one of your packs"""
        from carfigures.models import UserPack
        
        # Verify ownership
        try:
            user_pack = await UserPack.get(
                id=pack_id,
                user_id=ctx.author.id
            ).prefetch_related("pack")
        except:
            embed = discord.Embed(
                title="❌ Pack Not Found",
                description="Could not find that pack in your inventory!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        if user_pack.is_opened:
            embed = discord.Embed(
                title="❌ Already Opened",
                description="This pack has already been opened!",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Open the pack
        success, message, cars_received = await PackManager.open_pack(pack_id)
        
        if not success:
            embed = discord.Embed(
                title="❌ Failed to Open Pack",
                description=message,
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Create success embed
        embed = discord.Embed(
            title="🎉 Pack Opened!",
            description=f"Opened **{user_pack.pack.name}** pack!",
            color=0x00ff00
        )
        
        if cars_received:
            car_list = ""
            for i, car in enumerate(cars_received, 1):
                rarity_emoji = "🟨" if car.rarity <= 1 else "🟪" if car.rarity <= 2 else "🟦" if car.rarity <= 5 else "🟫"
                car_list += f"{rarity_emoji} **{car.name}** ({car.year})\n"
            
            embed.add_field(
                name=f"Cars Received ({len(cars_received)})",
                value=car_list,
                inline=False
            )
        
        embed.set_footer(text="Check your collection with !garage")
        await ctx.send(embed=embed)
    
    @commands.group(name="pack", hidden=True, invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def pack_admin(self, ctx):
        """Admin pack management commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="🔧 Pack Admin Commands",
                description=(
                    "`!pack create <name> <price> <description>` - Create a new pack\n"
                    "`!pack list` - List all packs\n"
                    "`!pack toggle <pack_id>` - Toggle pack availability\n"
                    "`!pack delete <pack_id>` - Delete a pack"
                ),
                color=int(self.bot.config.default_embed_color, 16)
            )
            await ctx.send(embed=embed)
    
    @pack_admin.command(name="create")
    @commands.has_permissions(administrator=True)
    async def create_pack(self, ctx, name: str, price: int, *, description: str):
        """Create a new pack"""
        if price <= 0:
            await ctx.send("Price must be positive!")
            return
        
        try:
            pack = await PackManager.create_pack(
                name=name,
                description=description,
                price=price
            )
            
            embed = discord.Embed(
                title="✅ Pack Created",
                description=f"Created pack **{pack.name}** with price {pack.price:,} coins",
                color=0x00ff00
            )
            embed.add_field(name="Pack ID", value=pack.id, inline=True)
            embed.add_field(name="Description", value=pack.description, inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error Creating Pack",
                description=f"Failed to create pack: {str(e)}",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @pack_admin.command(name="list")
    @commands.has_permissions(administrator=True)
    async def list_packs(self, ctx):
        """List all packs (admin)"""
        packs = await Pack.all().order_by("-created_at")
        
        if not packs:
            await ctx.send("No packs found!")
            return
        
        embed = discord.Embed(
            title="📦 All Packs",
            color=int(self.bot.config.default_embed_color, 16)
        )
        
        for pack in packs:
            status = "✅ Active" if pack.is_active else "❌ Inactive"
            embed.add_field(
                name=f"#{pack.id} - {pack.name}",
                value=(
                    f"**Status:** {status}\n"
                    f"**Price:** {pack.price:,} coins\n"
                    f"**Cars:** {pack.guaranteed_cars}\n"
                    f"**Created:** {pack.created_at.strftime('%Y-%m-%d')}"
                ),
                inline=True
            )
        
        await ctx.send(embed=embed)