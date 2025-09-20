"""Casino utility functions"""

import random
import asyncio
from typing import Dict, List, Tuple, Optional
from carfigures.utils.coins import CoinManager
from carfigures.models.casino import CasinoGame, CasinoStats


class CasinoManager:
    """Manager for casino games and logic"""
    
    # Active blackjack games
    _blackjack_games = {}
    
    @staticmethod
    async def play_slots(symbols: List[str], bet: int, user_id: int) -> Dict:
        """Play slot machine game"""
        # Check for wins
        if len(set(symbols)) == 1:  # All three match
            multiplier = 3
        elif len(set(symbols)) == 2:  # Two match
            multiplier = 2
        else:  # No match
            multiplier = 0
        
        winnings = bet * multiplier
        net = winnings - bet
        
        if winnings > 0:
            await CoinManager.add_coins(user_id, winnings, "Slots win")
        
        # Record game
        await CasinoManager._record_game(user_id, "slots", bet, winnings, net, {"symbols": symbols})
        
        return {
            "won": winnings > 0,
            "winnings": winnings,
            "net": net,
            "multiplier": multiplier
        }
    
    @staticmethod
    async def play_dice(rolled: int, guess: int, bet: int, user_id: int) -> Dict:
        """Play dice game"""
        won = rolled == guess
        winnings = bet * 6 if won else 0
        net = winnings - bet
        
        if won:
            await CoinManager.add_coins(user_id, winnings, "Dice win")
        
        # Record game
        await CasinoManager._record_game(user_id, "dice", bet, winnings, net, {"rolled": rolled, "guess": guess})
        
        return {
            "won": won,
            "winnings": winnings,
            "net": net
        }
    
    @staticmethod
    async def play_roulette(choice: str, bet: int, user_id: int) -> Dict:
        """Play roulette game"""
        # Generate random number 0-36
        landed = random.randint(0, 36)
        
        # Determine color
        if landed == 0:
            color = "green"
        elif landed in [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]:
            color = "red"
        else:
            color = "black"
        
        # Check win
        won = False
        multiplier = 0
        
        if choice == "green" and color == "green":
            won = True
            multiplier = 14
        elif choice == "red" and color == "red":
            won = True
            multiplier = 2
        elif choice == "black" and color == "black":
            won = True
            multiplier = 2
        elif choice.isdigit() and int(choice) == landed:
            won = True
            multiplier = 36
        
        winnings = bet * multiplier if won else 0
        net = winnings - bet
        
        if won:
            await CoinManager.add_coins(user_id, winnings, "Roulette win")
        
        # Record game
        await CasinoManager._record_game(user_id, "roulette", bet, winnings, net, {"choice": choice, "landed": landed, "color": color})
        
        return {
            "won": won,
            "winnings": winnings,
            "net": net,
            "landed": f"{landed} ({color})"
        }
    
    @staticmethod
    async def start_blackjack(bet: int, user_id: int) -> Dict:
        """Start a new blackjack game"""
        game_id = f"bj_{random.randint(100000, 999999)}"
        
        # Deal initial cards
        player_cards = [CasinoManager._draw_card(), CasinoManager._draw_card()]
        dealer_cards = [CasinoManager._draw_card(), CasinoManager._draw_card()]
        
        game = {
            "game_id": game_id,
            "player_id": user_id,
            "bet": bet,
            "player_cards": player_cards,
            "dealer_cards": dealer_cards,
            "player_score": CasinoManager._calculate_score(player_cards),
            "dealer_score": CasinoManager._calculate_score(dealer_cards),
            "game_over": False,
            "doubled": False
        }
        
        CasinoManager._blackjack_games[game_id] = game
        
        return {
            "game_id": game_id,
            "player_hand_display": CasinoManager._format_hand(player_cards),
            "dealer_hand_display": f"{CasinoManager._format_card(dealer_cards[0])} + ?"
        }
    
    @staticmethod
    async def blackjack_hit(game_id: str, user_id: int) -> Dict:
        """Hit in blackjack"""
        if game_id not in CasinoManager._blackjack_games:
            return {"success": False, "message": "Game not found!"}
        
        game = CasinoManager._blackjack_games[game_id]
        
        if game["player_id"] is None:
            game["player_id"] = user_id
        
        if game["player_id"] != user_id:
            return {"success": False, "message": "This isn't your game!"}
        
        if game["game_over"]:
            return {"success": False, "message": "Game is already over!"}
        
        # Draw new card
        new_card = CasinoManager._draw_card()
        game["player_cards"].append(new_card)
        game["player_score"] = CasinoManager._calculate_score(game["player_cards"])
        
        # Check for bust
        if game["player_score"] > 21:
            game["game_over"] = True
            return await CasinoManager._end_blackjack_game(game_id, False)
        
        return {
            "success": True,
            "game_over": False,
            "player_hand_display": CasinoManager._format_hand(game["player_cards"]),
            "dealer_hand_display": f"{CasinoManager._format_card(game['dealer_cards'][0])} + ?"
        }
    
    @staticmethod
    async def blackjack_stand(game_id: str, user_id: int) -> Dict:
        """Stand in blackjack"""
        if game_id not in CasinoManager._blackjack_games:
            return {"success": False, "message": "Game not found!"}
        
        game = CasinoManager._blackjack_games[game_id]
        
        if game["player_id"] != user_id:
            return {"success": False, "message": "This isn't your game!"}
        
        if game["game_over"]:
            return {"success": False, "message": "Game is already over!"}
        
        # Dealer plays
        while game["dealer_score"] < 17:
            new_card = CasinoManager._draw_card()
            game["dealer_cards"].append(new_card)
            game["dealer_score"] = CasinoManager._calculate_score(game["dealer_cards"])
        
        # Determine winner
        player_bust = game["player_score"] > 21
        dealer_bust = game["dealer_score"] > 21
        
        if player_bust:
            won = False
        elif dealer_bust:
            won = True
        elif game["player_score"] > game["dealer_score"]:
            won = True
        elif game["player_score"] == game["dealer_score"]:
            won = False  # Push
        else:
            won = False
        
        return await CasinoManager._end_blackjack_game(game_id, won)
    
    @staticmethod
    async def blackjack_double_down(game_id: str, user_id: int) -> Dict:
        """Double down in blackjack"""
        if game_id not in CasinoManager._blackjack_games:
            return {"success": False, "message": "Game not found!"}
        
        game = CasinoManager._blackjack_games[game_id]
        
        if game["player_id"] != user_id:
            return {"success": False, "message": "This isn't your game!"}
        
        if game["game_over"]:
            return {"success": False, "message": "Game is already over!"}
        
        if game["doubled"]:
            return {"success": False, "message": "Already doubled down!"}
        
        # Check if user has enough coins for double bet
        user_coins = await CoinManager.get_or_create_user_coins(user_id)
        if user_coins.balance < game["bet"]:
            return {"success": False, "message": "Not enough coins to double down!"}
        
        # Double the bet
        await CoinManager.remove_coins(user_id, game["bet"], "Blackjack double down")
        game["bet"] *= 2
        game["doubled"] = True
        
        # Draw one more card
        new_card = CasinoManager._draw_card()
        game["player_cards"].append(new_card)
        game["player_score"] = CasinoManager._calculate_score(game["player_cards"])
        
        # Check for bust
        if game["player_score"] > 21:
            game["game_over"] = True
            return await CasinoManager._end_blackjack_game(game_id, False)
        
        # Dealer plays
        while game["dealer_score"] < 17:
            new_card = CasinoManager._draw_card()
            game["dealer_cards"].append(new_card)
            game["dealer_score"] = CasinoManager._calculate_score(game["dealer_cards"])
        
        # Determine winner
        player_bust = game["player_score"] > 21
        dealer_bust = game["dealer_score"] > 21
        
        if player_bust:
            won = False
        elif dealer_bust:
            won = True
        elif game["player_score"] > game["dealer_score"]:
            won = True
        elif game["player_score"] == game["dealer_score"]:
            won = False  # Push
        else:
            won = False
        
        return await CasinoManager._end_blackjack_game(game_id, won)
    
    @staticmethod
    async def _end_blackjack_game(game_id: str, won: bool) -> Dict:
        """End a blackjack game and calculate winnings"""
        game = CasinoManager._blackjack_games[game_id]
        game["game_over"] = True
        
        # Calculate winnings
        if won:
            # Check for blackjack (21 with 2 cards)
            if len(game["player_cards"]) == 2 and game["player_score"] == 21:
                multiplier = 2.5  # Blackjack pays 3:2
            else:
                multiplier = 2  # Regular win pays 1:1
            
            winnings = int(game["bet"] * multiplier)
            await CoinManager.add_coins(game["player_id"], winnings, "Blackjack win")
        else:
            winnings = 0
        
        net = winnings - game["bet"]
        
        # Record game
        await CasinoManager._record_game(
            game["player_id"], 
            "blackjack", 
            game["bet"], 
            winnings, 
            net, 
            {
                "player_cards": game["player_cards"],
                "dealer_cards": game["dealer_cards"],
                "player_score": game["player_score"],
                "dealer_score": game["dealer_score"],
                "doubled": game["doubled"]
            }
        )
        
        # Clean up game
        del CasinoManager._blackjack_games[game_id]
        
        return {
            "success": True,
            "won": won,
            "winnings": winnings,
            "net": net,
            "player_hand_display": CasinoManager._format_hand(game["player_cards"]),
            "dealer_hand_display": CasinoManager._format_hand(game["dealer_cards"])
        }
    
    @staticmethod
    def _draw_card() -> str:
        """Draw a random card"""
        suits = ["♠", "♥", "♦", "♣"]
        values = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
        
        suit = random.choice(suits)
        value = random.choice(values)
        
        return f"{value}{suit}"
    
    @staticmethod
    def _calculate_score(cards: List[str]) -> int:
        """Calculate blackjack score"""
        score = 0
        aces = 0
        
        for card in cards:
            value = card[:-1]  # Remove suit
            
            if value in ["J", "Q", "K"]:
                score += 10
            elif value == "A":
                aces += 1
                score += 11
            else:
                score += int(value)
        
        # Handle aces
        while score > 21 and aces > 0:
            score -= 10
            aces -= 1
        
        return score
    
    @staticmethod
    def _format_card(card: str) -> str:
        """Format a single card for display"""
        return f"`{card}`"
    
    @staticmethod
    def _format_hand(cards: List[str]) -> str:
        """Format a hand of cards for display"""
        return " ".join([CasinoManager._format_card(card) for card in cards])
    
    @staticmethod
    async def _record_game(user_id: int, game_type: str, bet: int, winnings: int, net: int, game_data: Dict):
        """Record a casino game in the database"""
        try:
            # Create game record
            await CasinoGame.create(
                user_id=user_id,
                game_type=game_type,
                bet_amount=bet,
                winnings=winnings,
                net_result=net,
                game_data=game_data
            )
            
            # Update user stats
            stats, created = await CasinoStats.get_or_create(
                user_id=user_id,
                defaults={
                    "total_games_played": 0,
                    "total_bet": 0,
                    "total_winnings": 0,
                    "total_net": 0
                }
            )
            
            # Update overall stats
            stats.total_games_played += 1
            stats.total_bet += bet
            stats.total_winnings += winnings
            stats.total_net += net
            
            # Update game-specific stats
            if game_type == "slots":
                stats.slots_games += 1
                stats.slots_winnings += winnings
                if stats.slots_games > 0:
                    stats.slots_win_rate = (stats.slots_winnings / (stats.slots_games * 100)) * 100
            elif game_type == "dice":
                stats.dice_games += 1
                stats.dice_winnings += winnings
                if stats.dice_games > 0:
                    stats.dice_win_rate = (stats.dice_winnings / (stats.dice_games * 100)) * 100
            elif game_type == "blackjack":
                stats.blackjack_games += 1
                stats.blackjack_winnings += winnings
                if stats.blackjack_games > 0:
                    stats.blackjack_win_rate = (stats.blackjack_winnings / (stats.blackjack_games * 100)) * 100
            elif game_type == "roulette":
                stats.roulette_games += 1
                stats.roulette_winnings += winnings
                if stats.roulette_games > 0:
                    stats.roulette_win_rate = (stats.roulette_winnings / (stats.roulette_games * 100)) * 100
            
            await stats.save()
            
        except Exception as e:
            # Log error but don't fail the game
            print(f"Error recording casino game: {e}")