"""General bot commands"""

import discord
from discord.ext import commands


class GeneralCommands(commands.Cog):
    """General bot commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="help")
    async def help_command(self, ctx, command_name: str = None):
        """Show help information"""
        if command_name:
            # Show help for specific command
            command = self.bot.get_command(command_name)
            if not command:
                await ctx.send(f"Command `{command_name}` not found!")
                return
            
            embed = discord.Embed(
                title=f"Help: {command.name}",
                description=command.help or "No description available",
                color=int(self.bot.config.default_embed_color, 16)
            )
            
            if command.aliases:
                embed.add_field(
                    name="Aliases",
                    value=", ".join(f"`{alias}`" for alias in command.aliases),
                    inline=False
                )
            
            embed.add_field(
                name="Usage",
                value=f"`{self.bot.command_prefix}{command.name} {command.signature}`",
                inline=False
            )
        else:
            # Show general help
            embed = discord.Embed(
                title="🚗 CarFigures Bot Help",
                description="Catch, collect and trade Aston Martins with coins!",
                color=int(self.bot.config.default_embed_color, 16)
            )
            
            # Coin commands
            coin_commands = (
                f"`{self.bot.command_prefix}daily` - Claim daily coin reward\n"
                f"`{self.bot.command_prefix}balance` - Check your coin balance\n"
                f"`{self.bot.command_prefix}leaderboard` - View top coin holders"
            )
            embed.add_field(name="💰 Coin Commands", value=coin_commands, inline=False)
            
            # Pack commands
            pack_commands = (
                f"`{self.bot.command_prefix}shop` - View available packs\n"
                f"`{self.bot.command_prefix}buy <pack_name>` - Purchase a pack\n"
                f"`{self.bot.command_prefix}inventory` - View your unopened packs\n"
                f"`{self.bot.command_prefix}open <pack_id>` - Open a pack"
            )
            embed.add_field(name="📦 Pack Commands", value=pack_commands, inline=False)
            
            # General commands
            general_commands = (
                f"`{self.bot.command_prefix}help [command]` - Show this help message\n"
                f"`{self.bot.command_prefix}garage` - View your car collection\n"
                f"`{self.bot.command_prefix}info <car_name>` - Get info about a car"
            )
            embed.add_field(name="ℹ️ General Commands", value=general_commands, inline=False)
            
            embed.set_footer(text="Catch cars when they spawn to earn coins!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="garage", aliases=["collection"])
    async def show_garage(self, ctx, user: discord.Member = None):
        """Show your car collection"""
        target_user = user or ctx.author
        
        from carfigures.models import UserCar
        
        user_cars = await UserCar.filter(user_id=target_user.id).prefetch_related("car").order_by("-caught_at")
        
        embed = discord.Embed(
            title=f"🏎️ {target_user.display_name}'s Garage",
            color=int(self.bot.config.default_embed_color, 16)
        )
        
        if not user_cars:
            embed.description = "No cars in garage yet!\nCatch cars when they spawn to start your collection."
        else:
            car_list = ""
            for i, user_car in enumerate(user_cars[:10], 1):  # Show first 10
                car = user_car.car
                rarity_emoji = "🟨" if car.rarity <= 1 else "🟪" if car.rarity <= 2 else "🟦" if car.rarity <= 5 else "🟫"
                shiny_text = "✨ " if user_car.is_shiny else ""
                fav_text = "❤️ " if user_car.is_favorite else ""
                
                car_list += f"{i}. {rarity_emoji} {shiny_text}{fav_text}**{car.name}** ({car.year})\n"
            
            if len(user_cars) > 10:
                car_list += f"\n... and {len(user_cars) - 10} more cars!"
            
            embed.description = car_list
            embed.add_field(
                name="Statistics",
                value=f"**Total Cars:** {len(user_cars)}\n**Unique Models:** {len(set(uc.car.name for uc in user_cars))}",
                inline=True
            )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        await ctx.send(embed=embed)
    
    @commands.command(name="info")
    async def car_info(self, ctx, *, car_name: str):
        """Get information about a specific car"""
        from carfigures.models import Car
        
        car = await Car.filter(name__icontains=car_name).first()
        
        if not car:
            embed = discord.Embed(
                title="❌ Car Not Found",
                description=f"Could not find a car named '{car_name}'",
                color=0xff0000
            )
            await ctx.send(embed=embed)
            return
        
        # Determine rarity text
        if car.rarity <= 1.0:
            rarity_text = "🟨 Legendary"
        elif car.rarity <= 2.0:
            rarity_text = "🟪 Epic"
        elif car.rarity <= 5.0:
            rarity_text = "🟦 Rare"
        else:
            rarity_text = "🟫 Common"
        
        embed = discord.Embed(
            title=f"🚗 {car.name}",
            description=f"**Model:** {car.model}\n**Year:** {car.year}",
            color=int(self.bot.config.default_embed_color, 16)
        )
        
        embed.add_field(name="Rarity", value=rarity_text, inline=True)
        embed.add_field(name="Type", value=car.type, inline=True)
        embed.add_field(name="Exclusive", value="Yes" if car.is_exclusive else "No", inline=True)
        
        embed.add_field(name="Horsepower", value=f"{car.horsepower} HP", inline=True)
        embed.add_field(name="Weight", value=f"{car.weight} KG", inline=True)
        
        if car.image_url:
            embed.set_image(url=car.image_url)
        
        if car.logo_url:
            embed.set_thumbnail(url=car.logo_url)
        
        await ctx.send(embed=embed)