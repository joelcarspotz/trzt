"""Coin system commands"""

import discord
from discord.ext import commands
from datetime import datetime
import random

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
    
    @commands.command(name="casino", aliases=["gamble", "bet"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def casino(self, ctx, amount: str = None):
        """Gamble your coins. Usage: !casino <amount|all|half>"""
        if amount is None:
            await ctx.send(f"Usage: `{self.bot.command_prefix}casino <amount|all|half>`")
            return
        
        user_id = ctx.author.id
        balance = await CoinManager.get_balance(user_id)
        
        # Parse bet amount
        bet_amount: int
        arg = amount.lower()
        if arg == "all":
            bet_amount = balance
        elif arg == "half":
            bet_amount = max(1, balance // 2)
        else:
            try:
                bet_amount = int(arg)
            except ValueError:
                await ctx.send("Enter a valid number, or use `all`/`half`.")
                return
        
        # Validate bet
        min_bet = 10
        if bet_amount < min_bet:
            await ctx.send(f"Minimum bet is {min_bet} coins.")
            return
        if bet_amount > balance:
            await ctx.send("You don't have enough coins for that bet.")
            return
        
        # Take the bet
        success, _ = await CoinManager.spend_coins(user_id, bet_amount)
        if not success:
            await ctx.send("You don't have enough coins for that bet.")
            return
        
        # Resolve outcome (47% win chance)
        win = random.random() < 0.47
        if win:
            winnings = bet_amount * 2
            await CoinManager.add_coins(user_id, winnings, "Casino win")
            new_balance = await CoinManager.get_balance(user_id)
            embed = discord.Embed(
                title="🎰 Casino Result",
                description=f"You won! +{winnings:,} coins",
                color=0x00ff00
            )
            embed.add_field(name="Bet", value=f"{bet_amount:,}")
            embed.add_field(name="Chance", value="47% win")
            embed.add_field(name="New Balance", value=f"{new_balance:,}")
        else:
            new_balance = await CoinManager.get_balance(user_id)
            embed = discord.Embed(
                title="🎰 Casino Result",
                description=f"You lost {bet_amount:,} coins",
                color=0xff0000
            )
            embed.add_field(name="Bet", value=f"{bet_amount:,}")
            embed.add_field(name="Chance", value="53% lose")
            embed.add_field(name="New Balance", value=f"{new_balance:,}")
        
        embed.set_footer(text="Gamble responsibly. Cooldown: 10s")
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