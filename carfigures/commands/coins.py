"""Coin system commands"""

import discord
from discord.ext import commands
from datetime import datetime

from carfigures.utils.coins import CoinManager


class CoinsCommands(commands.Cog):
    """Commands for the coin system"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="daily", aliases=["claim"])
    async def daily_claim(self, ctx):
        """Claim your daily coin reward"""
        config = self.bot.config.coin_config
        
        success, amount, streak = await CoinManager.claim_daily(
            ctx.author.id,
            config.daily_claim_amount
        )
        
        if not success:
            embed = discord.Embed(
                title="❌ Already Claimed",
                description="You have already claimed your daily reward today!\nCome back tomorrow for more coins.",
                color=0xff0000
            )
        else:
            embed = discord.Embed(
                title="💰 Daily Reward Claimed!",
                description=f"You received **{amount} coins**!",
                color=0x00ff00
            )
            
            if streak > 1:
                embed.add_field(
                    name="🔥 Streak Bonus",
                    value=f"Day {streak} streak! (+{int((streak * 5))}% bonus)",
                    inline=False
                )
            
            embed.add_field(
                name="💡 Tip",
                value="Claim daily to build up your streak for bonus coins!",
                inline=False
            )
        
        embed.set_footer(text="Use !balance to check your coin balance")
        await ctx.send(embed=embed)
    
    @commands.command(name="balance", aliases=["coins", "bal"])
    async def check_balance(self, ctx, user: discord.Member = None):
        """Check your or another user's coin balance"""
        target_user = user or ctx.author
        
        coins = await CoinManager.get_or_create_user_coins(target_user.id)
        
        embed = discord.Embed(
            title=f"💰 {target_user.display_name}'s Wallet",
            color=int(self.bot.config.default_embed_color, 16)
        )
        
        embed.add_field(
            name="Current Balance",
            value=f"🪙 {coins.balance:,} coins",
            inline=True
        )
        
        embed.add_field(
            name="Lifetime Earned",
            value=f"📈 {coins.lifetime_earned:,} coins",
            inline=True
        )
        
        embed.add_field(
            name="Lifetime Spent",
            value=f"📉 {coins.lifetime_spent:,} coins",
            inline=True
        )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        embed.set_footer(text="Earn coins by catching cars and claiming daily rewards!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="leaderboard", aliases=["lb", "top"])
    async def coin_leaderboard(self, ctx):
        """Show the top coin holders"""
        from carfigures.models import UserCoins, User
        
        # Get top 10 users by balance
        top_users = await UserCoins.filter(balance__gt=0).order_by("-balance").limit(10).prefetch_related("user")
        
        if not top_users:
            await ctx.send("No users found with coins yet!")
            return
        
        embed = discord.Embed(
            title="🏆 Coin Leaderboard",
            description="Top coin holders in the server",
            color=0xffd700
        )
        
        leaderboard_text = ""
        for i, user_coins in enumerate(top_users, 1):
            try:
                discord_user = self.bot.get_user(user_coins.user.id)
                name = discord_user.display_name if discord_user else f"User {user_coins.user.id}"
            except:
                name = f"User {user_coins.user.id}"
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            leaderboard_text += f"{medal} **{name}** - {user_coins.balance:,} coins\n"
        
        embed.description = leaderboard_text
        embed.set_footer(text="Keep catching cars and claiming daily rewards to climb the leaderboard!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="give", hidden=True)
    @commands.has_permissions(administrator=True)
    async def give_coins(self, ctx, user: discord.Member, amount: int):
        """Give coins to a user (Admin only)"""
        if amount <= 0:
            await ctx.send("Amount must be positive!")
            return
        
        await CoinManager.add_coins(user.id, amount, "Admin gift")
        
        embed = discord.Embed(
            title="💰 Coins Given",
            description=f"Gave **{amount:,} coins** to {user.mention}",
            color=0x00ff00
        )
        
        await ctx.send(embed=embed)