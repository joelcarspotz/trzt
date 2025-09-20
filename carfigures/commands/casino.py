"""Casino system commands"""

import discord
from discord.ext import commands
import random
import asyncio
from typing import Optional

from carfigures.utils.coins import CoinManager
from carfigures.utils.casino import CasinoManager


class CasinoCommands(commands.Cog):
    """Commands for the casino system"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="slots", aliases=["slot"])
    async def slots(self, ctx, bet: int):
        """Play the slot machine! Usage: !slots <bet_amount>"""
        if bet <= 0:
            await ctx.send("❌ Bet amount must be positive!")
            return
        
        # Check if user has enough coins
        user_coins = await CoinManager.get_or_create_user_coins(ctx.author.id)
        if user_coins.balance < bet:
            await ctx.send("❌ You don't have enough coins for this bet!")
            return
        
        # Deduct bet amount
        await CoinManager.remove_coins(ctx.author.id, bet, "Slots bet")
        
        # Create slot machine display
        embed = discord.Embed(
            title="🎰 Slot Machine",
            description="Spinning...",
            color=0xffd700
        )
        
        # Show spinning animation
        message = await ctx.send(embed=embed)
        
        # Simulate spinning with multiple updates
        for _ in range(3):
            await asyncio.sleep(0.5)
            symbols = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
            spinning = [random.choice(symbols) for _ in range(3)]
            
            embed.description = f"🎰 {' | '.join(spinning)}"
            await message.edit(embed=embed)
        
        # Final result
        final_symbols = [random.choice(symbols) for _ in range(3)]
        result = await CasinoManager.play_slots(final_symbols, bet, ctx.author.id)
        
        # Update embed with result
        embed.description = f"🎰 {' | '.join(final_symbols)}"
        
        if result["won"]:
            embed.color = 0x00ff00
            embed.add_field(
                name="🎉 Result",
                value=f"You won **{result['winnings']:,} coins**!",
                inline=False
            )
        else:
            embed.color = 0xff0000
            embed.add_field(
                name="💸 Result",
                value="Better luck next time!",
                inline=False
            )
        
        embed.add_field(
            name="💰 Net Result",
            value=f"{'+' if result['net'] >= 0 else ''}{result['net']:,} coins",
            inline=True
        )
        
        await message.edit(embed=embed)
    
    @commands.command(name="dice", aliases=["roll"])
    async def dice(self, ctx, bet: int, guess: int):
        """Roll dice and guess the number! Usage: !dice <bet> <guess(1-6)>"""
        if bet <= 0:
            await ctx.send("❌ Bet amount must be positive!")
            return
        
        if guess < 1 or guess > 6:
            await ctx.send("❌ Guess must be between 1 and 6!")
            return
        
        # Check if user has enough coins
        user_coins = await CoinManager.get_or_create_user_coins(ctx.author.id)
        if user_coins.balance < bet:
            await ctx.send("❌ You don't have enough coins for this bet!")
            return
        
        # Deduct bet amount
        await CoinManager.remove_coins(ctx.author.id, bet, "Dice bet")
        
        # Roll the dice
        dice_roll = random.randint(1, 6)
        result = await CasinoManager.play_dice(dice_roll, guess, bet, ctx.author.id)
        
        embed = discord.Embed(
            title="🎲 Dice Roll",
            color=0x00ff00 if result["won"] else 0xff0000
        )
        
        embed.add_field(
            name="🎯 Your Guess",
            value=f"**{guess}**",
            inline=True
        )
        
        embed.add_field(
            name="🎲 Rolled",
            value=f"**{dice_roll}**",
            inline=True
        )
        
        if result["won"]:
            embed.add_field(
                name="🎉 Result",
                value=f"You won **{result['winnings']:,} coins**!",
                inline=False
            )
        else:
            embed.add_field(
                name="💸 Result",
                value="Better luck next time!",
                inline=False
            )
        
        embed.add_field(
            name="💰 Net Result",
            value=f"{'+' if result['net'] >= 0 else ''}{result['net']:,} coins",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="blackjack", aliases=["bj", "21"])
    async def blackjack(self, ctx, bet: int):
        """Play blackjack! Usage: !blackjack <bet_amount>"""
        if bet <= 0:
            await ctx.send("❌ Bet amount must be positive!")
            return
        
        # Check if user has enough coins
        user_coins = await CoinManager.get_or_create_user_coins(ctx.author.id)
        if user_coins.balance < bet:
            await ctx.send("❌ You don't have enough coins for this bet!")
            return
        
        # Deduct bet amount
        await CoinManager.remove_coins(ctx.author.id, bet, "Blackjack bet")
        
        # Start blackjack game
        game = await CasinoManager.start_blackjack(bet, ctx.author.id)
        
        embed = discord.Embed(
            title="🃏 Blackjack",
            description="Game started! Use the buttons below to play.",
            color=0x00ff00
        )
        
        embed.add_field(
            name="Your Hand",
            value=game["player_hand_display"],
            inline=True
        )
        
        embed.add_field(
            name="Dealer Hand",
            value=game["dealer_hand_display"],
            inline=True
        )
        
        embed.add_field(
            name="Bet",
            value=f"**{bet:,} coins**",
            inline=True
        )
        
        view = BlackjackView(self.bot, game["game_id"])
        await ctx.send(embed=embed, view=view)
    
    @commands.command(name="roulette", aliases=["rl"])
    async def roulette(self, ctx, bet: int, choice: str):
        """Play roulette! Usage: !roulette <bet> <red/black/green/number>"""
        if bet <= 0:
            await ctx.send("❌ Bet amount must be positive!")
            return
        
        # Check if user has enough coins
        user_coins = await CoinManager.get_or_create_user_coins(ctx.author.id)
        if user_coins.balance < bet:
            await ctx.send("❌ You don't have enough coins for this bet!")
            return
        
        # Validate choice
        choice = choice.lower()
        valid_choices = ["red", "black", "green", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30", "31", "32", "33", "34", "35", "36"]
        
        if choice not in valid_choices:
            await ctx.send("❌ Invalid choice! Use: red, black, green, or a number (0-36)")
            return
        
        # Deduct bet amount
        await CoinManager.remove_coins(ctx.author.id, bet, "Roulette bet")
        
        # Spin the wheel
        result = await CasinoManager.play_roulette(choice, bet, ctx.author.id)
        
        embed = discord.Embed(
            title="🎡 Roulette",
            color=0x00ff00 if result["won"] else 0xff0000
        )
        
        embed.add_field(
            name="🎯 Your Choice",
            value=f"**{choice.title()}**",
            inline=True
        )
        
        embed.add_field(
            name="🎲 Landed On",
            value=f"**{result['landed']}**",
            inline=True
        )
        
        if result["won"]:
            embed.add_field(
                name="🎉 Result",
                value=f"You won **{result['winnings']:,} coins**!",
                inline=False
            )
        else:
            embed.add_field(
                name="💸 Result",
                value="Better luck next time!",
                inline=False
            )
        
        embed.add_field(
            name="💰 Net Result",
            value=f"{'+' if result['net'] >= 0 else ''}{result['net']:,} coins",
            inline=True
        )
        
        await ctx.send(embed=embed)
    
    @commands.command(name="casino", aliases=["gambling"])
    async def casino_info(self, ctx):
        """Show casino information and available games"""
        embed = discord.Embed(
            title="🎰 Casino Games",
            description="Welcome to the Aston Martin Casino! Try your luck with these games:",
            color=0xffd700
        )
        
        embed.add_field(
            name="🎰 Slots",
            value="`!slots <bet>` - Spin the slot machine!",
            inline=False
        )
        
        embed.add_field(
            name="🎲 Dice",
            value="`!dice <bet> <guess(1-6)>` - Roll dice and guess the number!",
            inline=False
        )
        
        embed.add_field(
            name="🃏 Blackjack",
            value="`!blackjack <bet>` - Play 21 against the dealer!",
            inline=False
        )
        
        embed.add_field(
            name="🎡 Roulette",
            value="`!roulette <bet> <red/black/green/number>` - Spin the wheel!",
            inline=False
        )
        
        embed.add_field(
            name="💰 Payouts",
            value="• Slots: 3x for 3 matching, 2x for 2 matching\n• Dice: 6x for correct guess\n• Blackjack: 2x for win, 2.5x for blackjack\n• Roulette: 2x for red/black, 14x for green, 36x for number",
            inline=False
        )
        
        embed.set_footer(text="Use !balance to check your coins!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="casinostats", aliases=["gamblestats", "casinolb"])
    async def casino_stats(self, ctx, user: discord.Member = None):
        """Show casino statistics for you or another user"""
        target_user = user or ctx.author
        
        # Get user's casino stats
        from carfigures.models.casino import CasinoStats
        
        try:
            stats = await CasinoStats.get(user_id=target_user.id)
        except:
            await ctx.send("❌ No casino statistics found for this user!")
            return
        
        embed = discord.Embed(
            title=f"🎰 {target_user.display_name}'s Casino Stats",
            color=0xffd700
        )
        
        # Overall stats
        embed.add_field(
            name="📊 Overall",
            value=f"Games Played: **{stats.total_games_played}**\n"
                  f"Total Bet: **{stats.total_bet:,} coins**\n"
                  f"Total Winnings: **{stats.total_winnings:,} coins**\n"
                  f"Net Result: **{stats.total_net:,} coins**",
            inline=False
        )
        
        # Game-specific stats
        if stats.slots_games > 0:
            embed.add_field(
                name="🎰 Slots",
                value=f"Games: **{stats.slots_games}**\n"
                      f"Winnings: **{stats.slots_winnings:,} coins**\n"
                      f"Win Rate: **{stats.slots_win_rate:.1f}%**",
                inline=True
            )
        
        if stats.dice_games > 0:
            embed.add_field(
                name="🎲 Dice",
                value=f"Games: **{stats.dice_games}**\n"
                      f"Winnings: **{stats.dice_winnings:,} coins**\n"
                      f"Win Rate: **{stats.dice_win_rate:.1f}%**",
                inline=True
            )
        
        if stats.blackjack_games > 0:
            embed.add_field(
                name="🃏 Blackjack",
                value=f"Games: **{stats.blackjack_games}**\n"
                      f"Winnings: **{stats.blackjack_winnings:,} coins**\n"
                      f"Win Rate: **{stats.blackjack_win_rate:.1f}%**",
                inline=True
            )
        
        if stats.roulette_games > 0:
            embed.add_field(
                name="🎡 Roulette",
                value=f"Games: **{stats.roulette_games}**\n"
                      f"Winnings: **{stats.roulette_winnings:,} coins**\n"
                      f"Win Rate: **{stats.roulette_win_rate:.1f}%**",
                inline=True
            )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        embed.set_footer(text="Keep playing to improve your stats!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="casinoleaderboard", aliases=["gamblelb", "casinolb"])
    async def casino_leaderboard(self, ctx):
        """Show casino leaderboard"""
        from carfigures.models.casino import CasinoStats
        
        # Get top 10 users by total winnings
        top_users = await CasinoStats.filter(
            total_winnings__gt=0
        ).order_by("-total_winnings").limit(10).prefetch_related("user")
        
        if not top_users:
            await ctx.send("❌ No casino statistics found yet!")
            return
        
        embed = discord.Embed(
            title="🏆 Casino Leaderboard",
            description="Top casino winners by total winnings",
            color=0xffd700
        )
        
        leaderboard_text = ""
        for i, user_stats in enumerate(top_users, 1):
            try:
                discord_user = self.bot.get_user(user_stats.user.id)
                name = discord_user.display_name if discord_user else f"User {user_stats.user.id}"
            except:
                name = f"User {user_stats.user.id}"
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            leaderboard_text += f"{medal} **{name}** - {user_stats.total_winnings:,} coins won\n"
        
        embed.description = leaderboard_text
        embed.set_footer(text="Play casino games to climb the leaderboard!")
        
        await ctx.send(embed=embed)


class BlackjackView(discord.ui.View):
    """View for blackjack game"""
    
    def __init__(self, bot, game_id: str):
        super().__init__(timeout=300.0)  # 5 minute timeout
        self.bot = bot
        self.game_id = game_id
    
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.primary, emoji="🃏")
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Hit - draw another card"""
        result = await CasinoManager.blackjack_hit(self.game_id, interaction.user.id)
        
        if not result["success"]:
            await interaction.response.send_message("❌ " + result["message"], ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🃏 Blackjack",
            color=0x00ff00 if result["game_over"] and result["won"] else 0xff0000 if result["game_over"] else 0x00ff00
        )
        
        embed.add_field(
            name="Your Hand",
            value=result["player_hand_display"],
            inline=True
        )
        
        embed.add_field(
            name="Dealer Hand",
            value=result["dealer_hand_display"],
            inline=True
        )
        
        if result["game_over"]:
            if result["won"]:
                embed.add_field(
                    name="🎉 Result",
                    value=f"You won **{result['winnings']:,} coins**!",
                    inline=False
                )
            else:
                embed.add_field(
                    name="💸 Result",
                    value="You lost!",
                    inline=False
                )
            
            embed.add_field(
                name="💰 Net Result",
                value=f"{'+' if result['net'] >= 0 else ''}{result['net']:,} coins",
                inline=True
            )
            
            # Disable all buttons
            for item in self.children:
                item.disabled = True
        else:
            embed.add_field(
                name="Action",
                value="Choose your next move!",
                inline=False
            )
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Stand", style=discord.ButtonStyle.secondary, emoji="✋")
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Stand - keep current hand"""
        result = await CasinoManager.blackjack_stand(self.game_id, interaction.user.id)
        
        if not result["success"]:
            await interaction.response.send_message("❌ " + result["message"], ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🃏 Blackjack",
            color=0x00ff00 if result["won"] else 0xff0000
        )
        
        embed.add_field(
            name="Your Hand",
            value=result["player_hand_display"],
            inline=True
        )
        
        embed.add_field(
            name="Dealer Hand",
            value=result["dealer_hand_display"],
            inline=True
        )
        
        if result["won"]:
            embed.add_field(
                name="🎉 Result",
                value=f"You won **{result['winnings']:,} coins**!",
                inline=False
            )
        else:
            embed.add_field(
                name="💸 Result",
                value="You lost!",
                inline=False
            )
        
        embed.add_field(
            name="💰 Net Result",
            value=f"{'+' if result['net'] >= 0 else ''}{result['net']:,} coins",
            inline=True
        )
        
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="Double Down", style=discord.ButtonStyle.danger, emoji="💰")
    async def double_down(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Double down - double bet and take one more card"""
        result = await CasinoManager.blackjack_double_down(self.game_id, interaction.user.id)
        
        if not result["success"]:
            await interaction.response.send_message("❌ " + result["message"], ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🃏 Blackjack",
            color=0x00ff00 if result["won"] else 0xff0000
        )
        
        embed.add_field(
            name="Your Hand",
            value=result["player_hand_display"],
            inline=True
        )
        
        embed.add_field(
            name="Dealer Hand",
            value=result["dealer_hand_display"],
            inline=True
        )
        
        if result["won"]:
            embed.add_field(
                name="🎉 Result",
                value=f"You won **{result['winnings']:,} coins**!",
                inline=False
            )
        else:
            embed.add_field(
                name="💸 Result",
                value="You lost!",
                inline=False
            )
        
        embed.add_field(
            name="💰 Net Result",
            value=f"{'+' if result['net'] >= 0 else ''}{result['net']:,} coins",
            inline=True
        )
        
        # Disable all buttons
        for item in self.children:
            item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def on_timeout(self):
        """Handle view timeout"""
        # Disable all buttons
        for item in self.children:
            item.disabled = True