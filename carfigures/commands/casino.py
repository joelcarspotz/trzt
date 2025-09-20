"""Casino system commands"""

import discord
from discord.ext import commands
import random
import asyncio
from typing import List, Tuple, Dict

from carfigures.utils.coins import CoinManager
from carfigures.utils.casino import CasinoManager


class CasinoCommands(commands.Cog):
    """Commands for the casino system"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_games = {}  # Track active games per user
    
    @commands.command(name="casino", aliases=["gamble"])
    async def casino_help(self, ctx):
        """Show available casino games"""
        embed = discord.Embed(
            title="🎰 Aston Martin Casino",
            description="Welcome to the casino! Here are the available games:",
            color=int(self.bot.config.default_embed_color, 16)
        )
        
        embed.add_field(
            name="🎰 Slots",
            value="`!slots <bet>` - Classic slot machine (2.5x max payout)",
            inline=False
        )
        
        embed.add_field(
            name="🃏 Blackjack",
            value="`!blackjack <bet>` - Beat the dealer to 21 (2x payout)",
            inline=False
        )
        
        embed.add_field(
            name="🎲 Dice",
            value="`!dice <bet> <guess>` - Guess the dice roll 1-6 (6x payout)",
            inline=False
        )
        
        embed.add_field(
            name="🪙 Coinflip",
            value="`!coinflip <bet> <heads/tails>` - Simple coin flip (2x payout)",
            inline=False
        )
        
        embed.add_field(
            name="🎯 Roulette",
            value="`!roulette <bet> <number/color>` - European roulette (35x/2x payout)",
            inline=False
        )
        
        embed.add_field(
            name="📊 Stats",
            value="`!casino stats` - View your gambling statistics",
            inline=False
        )
        
        embed.set_footer(text="Gamble responsibly! You can only bet coins you have.")
        await ctx.send(embed=embed)
    
    @commands.command(name="slots")
    async def slots(self, ctx, bet: int):
        """Play the slot machine"""
        if ctx.author.id in self.active_games:
            await ctx.send("❌ You already have an active game! Finish it first.")
            return
        
        if bet <= 0:
            await ctx.send("❌ Bet must be positive!")
            return
        
        # Check if user has enough coins
        balance = await CoinManager.get_balance(ctx.author.id)
        if balance < bet:
            await ctx.send(f"❌ You don't have enough coins! Balance: {balance:,}")
            return
        
        # Minimum and maximum bets
        min_bet = 10
        max_bet = min(balance, 10000)
        if bet < min_bet:
            await ctx.send(f"❌ Minimum bet is {min_bet} coins!")
            return
        if bet > max_bet:
            await ctx.send(f"❌ Maximum bet is {max_bet:,} coins!")
            return
        
        self.active_games[ctx.author.id] = "slots"
        
        try:
            # Deduct bet
            success, _ = await CoinManager.spend_coins(ctx.author.id, bet)
            if not success:
                await ctx.send("❌ Failed to place bet!")
                return
            
            # Slot symbols with different rarities
            symbols = {
                "🍒": {"weight": 30, "payout": 0.5},
                "🍋": {"weight": 25, "payout": 0.8},
                "🍊": {"weight": 20, "payout": 1.0},
                "🍇": {"weight": 15, "payout": 1.5},
                "🔔": {"weight": 8, "payout": 2.0},
                "💎": {"weight": 2, "payout": 2.5}
            }
            
            symbol_list = []
            weights = []
            for symbol, data in symbols.items():
                symbol_list.append(symbol)
                weights.append(data["weight"])
            
            # Spin the reels
            reel1 = random.choices(symbol_list, weights=weights)[0]
            reel2 = random.choices(symbol_list, weights=weights)[0]
            reel3 = random.choices(symbol_list, weights=weights)[0]
            
            # Create spinning animation
            embed = discord.Embed(
                title="🎰 Aston Martin Slots",
                description="Spinning...",
                color=0xffff00
            )
            embed.add_field(name="Reels", value="🎰 | 🎰 | 🎰", inline=False)
            embed.add_field(name="Bet", value=f"{bet:,} coins", inline=True)
            
            message = await ctx.send(embed=embed)
            
            # Animation frames
            for i in range(3):
                await asyncio.sleep(1)
                frame = f"{'🎰' if i < 1 else reel1} | {'🎰' if i < 2 else reel2} | {'🎰' if i < 3 else reel3}"
                embed.set_field_at(0, name="Reels", value=frame, inline=False)
                await message.edit(embed=embed)
            
            # Check for win
            result_reels = [reel1, reel2, reel3]
            winnings = 0
            win_type = ""
            
            # Three of a kind
            if reel1 == reel2 == reel3:
                payout_multiplier = symbols[reel1]["payout"]
                winnings = int(bet * payout_multiplier)
                win_type = f"Three {reel1}s!"
            # Two of a kind
            elif reel1 == reel2 or reel2 == reel3 or reel1 == reel3:
                matching_symbol = reel1 if reel1 == reel2 else (reel2 if reel2 == reel3 else reel1)
                payout_multiplier = symbols[matching_symbol]["payout"] * 0.3
                winnings = int(bet * payout_multiplier)
                win_type = f"Two {matching_symbol}s!"
            
            # Update embed with results
            if winnings > 0:
                embed.title = "🎉 WINNER!"
                embed.color = 0x00ff00
                embed.add_field(name="Result", value=win_type, inline=True)
                embed.add_field(name="Winnings", value=f"+{winnings:,} coins", inline=True)
                
                # Add winnings
                await CoinManager.add_coins(ctx.author.id, winnings, "Slots win")
                
                # Update casino stats
                await CasinoManager.record_game(ctx.author.id, "slots", bet, winnings, True)
            else:
                embed.title = "💸 Better luck next time!"
                embed.color = 0xff0000
                embed.add_field(name="Result", value="No match", inline=True)
                embed.add_field(name="Loss", value=f"-{bet:,} coins", inline=True)
                
                # Update casino stats
                await CasinoManager.record_game(ctx.author.id, "slots", bet, 0, False)
            
            await message.edit(embed=embed)
            
        finally:
            self.active_games.pop(ctx.author.id, None)
    
    @commands.command(name="coinflip", aliases=["flip"])
    async def coinflip(self, ctx, bet: int, choice: str):
        """Flip a coin and double your money"""
        if ctx.author.id in self.active_games:
            await ctx.send("❌ You already have an active game! Finish it first.")
            return
        
        choice = choice.lower()
        if choice not in ["heads", "tails", "h", "t"]:
            await ctx.send("❌ Choose either `heads`/`h` or `tails`/`t`!")
            return
        
        if bet <= 0:
            await ctx.send("❌ Bet must be positive!")
            return
        
        # Check balance and limits
        balance = await CoinManager.get_balance(ctx.author.id)
        if balance < bet:
            await ctx.send(f"❌ You don't have enough coins! Balance: {balance:,}")
            return
        
        min_bet = 10
        max_bet = min(balance, 5000)
        if bet < min_bet or bet > max_bet:
            await ctx.send(f"❌ Bet must be between {min_bet} and {max_bet:,} coins!")
            return
        
        self.active_games[ctx.author.id] = "coinflip"
        
        try:
            # Deduct bet
            success, _ = await CoinManager.spend_coins(ctx.author.id, bet)
            if not success:
                await ctx.send("❌ Failed to place bet!")
                return
            
            # Normalize choice
            user_choice = "heads" if choice in ["heads", "h"] else "tails"
            
            # Create embed
            embed = discord.Embed(
                title="🪙 Coin Flip",
                description="Flipping coin...",
                color=0xffff00
            )
            embed.add_field(name="Your Choice", value=user_choice.title(), inline=True)
            embed.add_field(name="Bet", value=f"{bet:,} coins", inline=True)
            
            message = await ctx.send(embed=embed)
            await asyncio.sleep(2)
            
            # Flip result
            result = random.choice(["heads", "tails"])
            won = result == user_choice
            
            if won:
                winnings = bet * 2
                embed.title = "🎉 You Won!"
                embed.color = 0x00ff00
                embed.add_field(name="Result", value=f"🪙 {result.title()}", inline=False)
                embed.add_field(name="Winnings", value=f"+{winnings:,} coins", inline=True)
                
                await CoinManager.add_coins(ctx.author.id, winnings, "Coinflip win")
                await CasinoManager.record_game(ctx.author.id, "coinflip", bet, winnings, True)
            else:
                embed.title = "💸 You Lost!"
                embed.color = 0xff0000
                embed.add_field(name="Result", value=f"🪙 {result.title()}", inline=False)
                embed.add_field(name="Loss", value=f"-{bet:,} coins", inline=True)
                
                await CasinoManager.record_game(ctx.author.id, "coinflip", bet, 0, False)
            
            await message.edit(embed=embed)
            
        finally:
            self.active_games.pop(ctx.author.id, None)
    
    @commands.command(name="dice")
    async def dice_roll(self, ctx, bet: int, guess: int):
        """Guess the dice roll (1-6) for 6x payout"""
        if ctx.author.id in self.active_games:
            await ctx.send("❌ You already have an active game! Finish it first.")
            return
        
        if not 1 <= guess <= 6:
            await ctx.send("❌ Guess must be between 1 and 6!")
            return
        
        if bet <= 0:
            await ctx.send("❌ Bet must be positive!")
            return
        
        # Check balance and limits
        balance = await CoinManager.get_balance(ctx.author.id)
        if balance < bet:
            await ctx.send(f"❌ You don't have enough coins! Balance: {balance:,}")
            return
        
        min_bet = 10
        max_bet = min(balance, 2000)  # Lower max due to high payout
        if bet < min_bet or bet > max_bet:
            await ctx.send(f"❌ Bet must be between {min_bet} and {max_bet:,} coins!")
            return
        
        self.active_games[ctx.author.id] = "dice"
        
        try:
            # Deduct bet
            success, _ = await CoinManager.spend_coins(ctx.author.id, bet)
            if not success:
                await ctx.send("❌ Failed to place bet!")
                return
            
            # Create embed
            embed = discord.Embed(
                title="🎲 Dice Roll",
                description="Rolling dice...",
                color=0xffff00
            )
            embed.add_field(name="Your Guess", value=str(guess), inline=True)
            embed.add_field(name="Bet", value=f"{bet:,} coins", inline=True)
            
            message = await ctx.send(embed=embed)
            await asyncio.sleep(2)
            
            # Roll dice
            result = random.randint(1, 6)
            dice_emoji = ["", "⚀", "⚁", "⚂", "⚃", "⚄", "⚅"][result]
            won = result == guess
            
            if won:
                winnings = bet * 6
                embed.title = "🎉 Perfect Guess!"
                embed.color = 0x00ff00
                embed.add_field(name="Result", value=f"{dice_emoji} {result}", inline=False)
                embed.add_field(name="Winnings", value=f"+{winnings:,} coins", inline=True)
                
                await CoinManager.add_coins(ctx.author.id, winnings, "Dice win")
                await CasinoManager.record_game(ctx.author.id, "dice", bet, winnings, True)
            else:
                embed.title = "💸 Wrong Guess!"
                embed.color = 0xff0000
                embed.add_field(name="Result", value=f"{dice_emoji} {result}", inline=False)
                embed.add_field(name="Loss", value=f"-{bet:,} coins", inline=True)
                
                await CasinoManager.record_game(ctx.author.id, "dice", bet, 0, False)
            
            await message.edit(embed=embed)
            
        finally:
            self.active_games.pop(ctx.author.id, None)
    
    @commands.command(name="blackjack", aliases=["bj"])
    async def blackjack(self, ctx, bet: int):
        """Play blackjack against the dealer"""
        if ctx.author.id in self.active_games:
            await ctx.send("❌ You already have an active game! Finish it first.")
            return
        
        if bet <= 0:
            await ctx.send("❌ Bet must be positive!")
            return
        
        # Check balance and limits
        balance = await CoinManager.get_balance(ctx.author.id)
        if balance < bet:
            await ctx.send(f"❌ You don't have enough coins! Balance: {balance:,}")
            return
        
        min_bet = 10
        max_bet = min(balance, 5000)
        if bet < min_bet or bet > max_bet:
            await ctx.send(f"❌ Bet must be between {min_bet} and {max_bet:,} coins!")
            return
        
        self.active_games[ctx.author.id] = "blackjack"
        
        try:
            # Deduct bet
            success, _ = await CoinManager.spend_coins(ctx.author.id, bet)
            if not success:
                await ctx.send("❌ Failed to place bet!")
                return
            
            # Initialize game
            deck = self._create_deck()
            random.shuffle(deck)
            
            player_hand = [deck.pop(), deck.pop()]
            dealer_hand = [deck.pop(), deck.pop()]
            
            # Check for natural blackjack
            player_value = self._calculate_hand_value(player_hand)
            dealer_value = self._calculate_hand_value(dealer_hand)
            
            if player_value == 21 and dealer_value == 21:
                # Push
                embed = discord.Embed(
                    title="🤝 Push - Both Blackjack!",
                    color=0xffff00
                )
                embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} (21)", inline=True)
                embed.add_field(name="Dealer Hand", value=f"{' '.join(dealer_hand)} (21)", inline=True)
                embed.add_field(name="Result", value=f"Bet returned: {bet:,} coins", inline=False)
                
                await CoinManager.add_coins(ctx.author.id, bet, "Blackjack push")
                await CasinoManager.record_game(ctx.author.id, "blackjack", bet, bet, False)
                await ctx.send(embed=embed)
                return
            
            elif player_value == 21:
                # Player blackjack
                winnings = int(bet * 2.5)
                embed = discord.Embed(
                    title="🃏 BLACKJACK! You Win!",
                    color=0x00ff00
                )
                embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} (21)", inline=True)
                embed.add_field(name="Dealer Hand", value=f"{dealer_hand[0]} ❓ ({self._card_value(dealer_hand[0])}+)", inline=True)
                embed.add_field(name="Winnings", value=f"+{winnings:,} coins", inline=False)
                
                await CoinManager.add_coins(ctx.author.id, winnings, "Blackjack win")
                await CasinoManager.record_game(ctx.author.id, "blackjack", bet, winnings, True)
                await ctx.send(embed=embed)
                return
            
            # Regular game
            game_over = False
            while not game_over:
                player_value = self._calculate_hand_value(player_hand)
                
                # Check if player busted
                if player_value > 21:
                    embed = discord.Embed(
                        title="💥 BUST! You Lose!",
                        color=0xff0000
                    )
                    embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} ({player_value})", inline=True)
                    embed.add_field(name="Dealer Hand", value=f"{dealer_hand[0]} ❓", inline=True)
                    embed.add_field(name="Loss", value=f"-{bet:,} coins", inline=False)
                    
                    await CasinoManager.record_game(ctx.author.id, "blackjack", bet, 0, False)
                    await ctx.send(embed=embed)
                    return
                
                # Show current hands
                embed = discord.Embed(
                    title="🃏 Blackjack",
                    color=int(self.bot.config.default_embed_color, 16)
                )
                embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} ({player_value})", inline=True)
                embed.add_field(name="Dealer Hand", value=f"{dealer_hand[0]} ❓ ({self._card_value(dealer_hand[0])}+)", inline=True)
                embed.add_field(name="Options", value="React with 👊 to **Hit** or ✋ to **Stand**", inline=False)
                
                message = await ctx.send(embed=embed)
                await message.add_reaction("👊")  # Hit
                await message.add_reaction("✋")  # Stand
                
                def check(reaction, user):
                    return user == ctx.author and str(reaction.emoji) in ["👊", "✋"] and reaction.message.id == message.id
                
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
                    
                    if str(reaction.emoji) == "👊":  # Hit
                        player_hand.append(deck.pop())
                        await message.delete()
                    else:  # Stand
                        await message.delete()
                        game_over = True
                        
                except asyncio.TimeoutError:
                    await message.delete()
                    await ctx.send("⏰ Game timed out! Auto-standing...")
                    game_over = True
            
            # Dealer's turn
            dealer_value = self._calculate_hand_value(dealer_hand)
            while dealer_value < 17:
                dealer_hand.append(deck.pop())
                dealer_value = self._calculate_hand_value(dealer_hand)
            
            # Determine winner
            player_value = self._calculate_hand_value(player_hand)
            
            if dealer_value > 21:
                # Dealer bust
                winnings = bet * 2
                embed = discord.Embed(title="🎉 Dealer Busts! You Win!", color=0x00ff00)
                result_text = f"+{winnings:,} coins"
                await CoinManager.add_coins(ctx.author.id, winnings, "Blackjack win")
                await CasinoManager.record_game(ctx.author.id, "blackjack", bet, winnings, True)
            elif player_value > dealer_value:
                # Player wins
                winnings = bet * 2
                embed = discord.Embed(title="🎉 You Win!", color=0x00ff00)
                result_text = f"+{winnings:,} coins"
                await CoinManager.add_coins(ctx.author.id, winnings, "Blackjack win")
                await CasinoManager.record_game(ctx.author.id, "blackjack", bet, winnings, True)
            elif player_value == dealer_value:
                # Push
                embed = discord.Embed(title="🤝 Push - Tie!", color=0xffff00)
                result_text = f"Bet returned: {bet:,} coins"
                await CoinManager.add_coins(ctx.author.id, bet, "Blackjack push")
                await CasinoManager.record_game(ctx.author.id, "blackjack", bet, bet, False)
            else:
                # Dealer wins
                embed = discord.Embed(title="💸 Dealer Wins!", color=0xff0000)
                result_text = f"-{bet:,} coins"
                await CasinoManager.record_game(ctx.author.id, "blackjack", bet, 0, False)
            
            embed.add_field(name="Your Hand", value=f"{' '.join(player_hand)} ({player_value})", inline=True)
            embed.add_field(name="Dealer Hand", value=f"{' '.join(dealer_hand)} ({dealer_value})", inline=True)
            embed.add_field(name="Result", value=result_text, inline=False)
            
            await ctx.send(embed=embed)
            
        finally:
            self.active_games.pop(ctx.author.id, None)
    
    def _create_deck(self):
        """Create a standard deck of cards"""
        suits = ["♠️", "♥️", "♦️", "♣️"]
        ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        deck = []
        for suit in suits:
            for rank in ranks:
                deck.append(f"{rank}{suit}")
        return deck
    
    def _card_value(self, card):
        """Get the value of a single card"""
        rank = card[:-2] if len(card) == 3 else card[:-2]
        if rank in ["J", "Q", "K"]:
            return 10
        elif rank == "A":
            return 11
        else:
            return int(rank)
    
    def _calculate_hand_value(self, hand):
        """Calculate the total value of a hand"""
        value = 0
        aces = 0
        
        for card in hand:
            card_val = self._card_value(card)
            if card_val == 11:
                aces += 1
            value += card_val
        
        # Adjust for aces
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1
        
        return value
    
    @commands.command(name="roulette")
    async def roulette(self, ctx, bet: int, choice: str):
        """Play European roulette"""
        if ctx.author.id in self.active_games:
            await ctx.send("❌ You already have an active game! Finish it first.")
            return
        
        if bet <= 0:
            await ctx.send("❌ Bet must be positive!")
            return
        
        # Check balance and limits
        balance = await CoinManager.get_balance(ctx.author.id)
        if balance < bet:
            await ctx.send(f"❌ You don't have enough coins! Balance: {balance:,}")
            return
        
        min_bet = 10
        max_bet = min(balance, 1000)  # Lower max due to potential high payouts
        if bet < min_bet or bet > max_bet:
            await ctx.send(f"❌ Bet must be between {min_bet} and {max_bet:,} coins!")
            return
        
        # Parse choice
        choice = choice.lower()
        bet_type = None
        payout = 0
        
        # Number bet (0-36)
        if choice.isdigit() and 0 <= int(choice) <= 36:
            bet_type = "number"
            bet_number = int(choice)
            payout = 35
        # Color bets
        elif choice in ["red", "black"]:
            bet_type = "color"
            bet_color = choice
            payout = 2
        # Even/Odd bets
        elif choice in ["even", "odd"]:
            bet_type = "parity"
            bet_parity = choice
            payout = 2
        # High/Low bets
        elif choice in ["high", "low"]:
            bet_type = "range"
            bet_range = choice
            payout = 2
        else:
            await ctx.send("❌ Invalid choice! Use: number (0-36), red, black, even, odd, high, or low")
            return
        
        self.active_games[ctx.author.id] = "roulette"
        
        try:
            # Deduct bet
            success, _ = await CoinManager.spend_coins(ctx.author.id, bet)
            if not success:
                await ctx.send("❌ Failed to place bet!")
                return
            
            # Roulette wheel setup
            red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
            black_numbers = [2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35]
            
            # Create embed
            embed = discord.Embed(
                title="🎯 Roulette",
                description="Spinning the wheel...",
                color=0xffff00
            )
            embed.add_field(name="Your Bet", value=choice.title(), inline=True)
            embed.add_field(name="Amount", value=f"{bet:,} coins", inline=True)
            
            message = await ctx.send(embed=embed)
            await asyncio.sleep(3)
            
            # Spin result
            result = random.randint(0, 36)
            
            # Determine color
            if result == 0:
                color = "green"
                color_emoji = "🟢"
            elif result in red_numbers:
                color = "red"
                color_emoji = "🔴"
            else:
                color = "black"
                color_emoji = "⚫"
            
            # Check win
            won = False
            winnings = 0
            
            if bet_type == "number" and result == bet_number:
                won = True
                winnings = bet * payout
            elif bet_type == "color" and color == bet_color:
                won = True
                winnings = bet * payout
            elif bet_type == "parity" and result != 0:
                if (bet_parity == "even" and result % 2 == 0) or (bet_parity == "odd" and result % 2 == 1):
                    won = True
                    winnings = bet * payout
            elif bet_type == "range" and result != 0:
                if (bet_range == "low" and 1 <= result <= 18) or (bet_range == "high" and 19 <= result <= 36):
                    won = True
                    winnings = bet * payout
            
            # Update embed with results
            if won:
                embed.title = "🎉 You Won!"
                embed.color = 0x00ff00
                embed.add_field(name="Result", value=f"{color_emoji} {result}", inline=False)
                embed.add_field(name="Winnings", value=f"+{winnings:,} coins", inline=True)
                
                await CoinManager.add_coins(ctx.author.id, winnings, "Roulette win")
                await CasinoManager.record_game(ctx.author.id, "roulette", bet, winnings, True)
            else:
                embed.title = "💸 You Lost!"
                embed.color = 0xff0000
                embed.add_field(name="Result", value=f"{color_emoji} {result}", inline=False)
                embed.add_field(name="Loss", value=f"-{bet:,} coins", inline=True)
                
                await CasinoManager.record_game(ctx.author.id, "roulette", bet, 0, False)
            
            await message.edit(embed=embed)
            
        finally:
            self.active_games.pop(ctx.author.id, None)
    
    @commands.command(name="casinostats")
    async def casino_stats(self, ctx, user: discord.Member = None):
        """View gambling statistics"""
        target_user = user or ctx.author
        stats = await CasinoManager.get_user_stats(target_user.id)
        
        if not stats:
            await ctx.send(f"📊 {target_user.display_name} hasn't played any casino games yet!")
            return
        
        embed = discord.Embed(
            title=f"🎰 {target_user.display_name}'s Casino Stats",
            color=int(self.bot.config.default_embed_color, 16)
        )
        
        embed.add_field(
            name="Games Played",
            value=f"{stats['total_games']:,}",
            inline=True
        )
        
        embed.add_field(
            name="Games Won",
            value=f"{stats['games_won']:,} ({stats['win_rate']:.1f}%)",
            inline=True
        )
        
        embed.add_field(
            name="Total Wagered",
            value=f"{stats['total_wagered']:,} coins",
            inline=True
        )
        
        embed.add_field(
            name="Total Won",
            value=f"{stats['total_won']:,} coins",
            inline=True
        )
        
        net_profit = stats['total_won'] - stats['total_wagered']
        profit_emoji = "📈" if net_profit >= 0 else "📉"
        embed.add_field(
            name="Net Profit/Loss",
            value=f"{profit_emoji} {net_profit:+,} coins",
            inline=True
        )
        
        embed.add_field(
            name="Biggest Win",
            value=f"🏆 {stats['biggest_win']:,} coins",
            inline=True
        )
        
        # Favorite game
        if stats['favorite_game']:
            embed.add_field(
                name="Favorite Game",
                value=f"🎮 {stats['favorite_game'].title()}",
                inline=True
            )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        embed.set_footer(text="Remember to gamble responsibly!")
        
        await ctx.send(embed=embed)
    
    @commands.command(name="casinolb", aliases=["casinoleaderboard"])
    async def casino_leaderboard(self, ctx, game_type: str = None):
        """View casino leaderboard"""
        if game_type and game_type not in ["slots", "coinflip", "dice", "blackjack", "roulette"]:
            await ctx.send("❌ Invalid game type! Use: slots, coinflip, dice, blackjack, or roulette")
            return
        
        leaderboard = await CasinoManager.get_leaderboard(game_type, 10)
        
        if not leaderboard:
            await ctx.send("📊 No casino statistics found yet!")
            return
        
        title = f"🏆 Casino Leaderboard"
        if game_type:
            title += f" - {game_type.title()}"
        
        embed = discord.Embed(
            title=title,
            description="Top casino players",
            color=0xffd700
        )
        
        leaderboard_text = ""
        for i, entry in enumerate(leaderboard, 1):
            try:
                discord_user = self.bot.get_user(entry["user_id"])
                name = discord_user.display_name if discord_user else f"User {entry['user_id']}"
            except:
                name = f"User {entry['user_id']}"
            
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"#{i}"
            
            if game_type:
                leaderboard_text += f"{medal} **{name}** - {entry['total_won']:,} coins won\n"
            else:
                win_rate = entry.get('win_rate', 0)
                leaderboard_text += f"{medal} **{name}** - {entry['total_won']:,} coins won ({win_rate:.1f}% win rate)\n"
        
        embed.description = leaderboard_text
        embed.set_footer(text="Keep gambling to climb the leaderboard!")
        
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(CasinoCommands(bot))