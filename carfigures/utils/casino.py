"""Casino system utilities"""

from datetime import datetime
from typing import Dict, Optional, Tuple, List
from collections import defaultdict

from carfigures.models import User


class CasinoManager:
    """Manages casino operations and statistics"""
    
    @staticmethod
    async def record_game(
        user_id: int, 
        game_type: str, 
        bet_amount: int, 
        winnings: int, 
        won: bool
    ) -> None:
        """Record a casino game result"""
        from carfigures.models.casino import CasinoStats
        
        user, _ = await User.get_or_create(id=user_id)
        
        # Get or create casino stats
        stats, created = await CasinoStats.get_or_create(user=user)
        
        # Update stats
        stats.total_games += 1
        stats.total_wagered += bet_amount
        stats.total_won += winnings
        
        if won:
            stats.games_won += 1
        
        # Update biggest win
        if winnings > stats.biggest_win:
            stats.biggest_win = winnings
        
        # Update game-specific stats
        game_stats = getattr(stats, f"{game_type}_stats", {})
        if not game_stats:
            game_stats = {
                "games_played": 0,
                "games_won": 0,
                "total_wagered": 0,
                "total_won": 0,
                "biggest_win": 0
            }
        
        game_stats["games_played"] += 1
        game_stats["total_wagered"] += bet_amount
        game_stats["total_won"] += winnings
        
        if won:
            game_stats["games_won"] += 1
        
        if winnings > game_stats["biggest_win"]:
            game_stats["biggest_win"] = winnings
        
        # Save game-specific stats
        setattr(stats, f"{game_type}_stats", game_stats)
        
        # Update last played
        stats.last_played = datetime.now()
        
        await stats.save()
    
    @staticmethod
    async def get_user_stats(user_id: int) -> Optional[Dict]:
        """Get comprehensive casino statistics for a user"""
        from carfigures.models.casino import CasinoStats
        
        user, _ = await User.get_or_create(id=user_id)
        stats = await CasinoStats.filter(user=user).first()
        
        if not stats:
            return None
        
        # Calculate win rate
        win_rate = (stats.games_won / stats.total_games * 100) if stats.total_games > 0 else 0
        
        # Find favorite game
        favorite_game = None
        max_games = 0
        
        game_types = ["slots", "coinflip", "dice", "blackjack", "roulette"]
        for game_type in game_types:
            game_stats = getattr(stats, f"{game_type}_stats", {})
            if game_stats and game_stats.get("games_played", 0) > max_games:
                max_games = game_stats["games_played"]
                favorite_game = game_type
        
        return {
            "total_games": stats.total_games,
            "games_won": stats.games_won,
            "win_rate": win_rate,
            "total_wagered": stats.total_wagered,
            "total_won": stats.total_won,
            "biggest_win": stats.biggest_win,
            "favorite_game": favorite_game,
            "last_played": stats.last_played
        }
    
    @staticmethod
    async def get_leaderboard(game_type: str = None, limit: int = 10) -> List[Dict]:
        """Get casino leaderboard"""
        from carfigures.models.casino import CasinoStats
        
        if game_type:
            # Game-specific leaderboard
            stats = await CasinoStats.all().prefetch_related("user")
            
            leaderboard = []
            for stat in stats:
                game_stats = getattr(stat, f"{game_type}_stats", {})
                if game_stats and game_stats.get("total_won", 0) > 0:
                    leaderboard.append({
                        "user_id": stat.user.id,
                        "total_won": game_stats["total_won"],
                        "games_played": game_stats["games_played"],
                        "games_won": game_stats.get("games_won", 0)
                    })
            
            leaderboard.sort(key=lambda x: x["total_won"], reverse=True)
        else:
            # Overall leaderboard
            stats = await CasinoStats.filter(total_won__gt=0).order_by("-total_won").limit(limit).prefetch_related("user")
            
            leaderboard = []
            for stat in stats:
                win_rate = (stat.games_won / stat.total_games * 100) if stat.total_games > 0 else 0
                leaderboard.append({
                    "user_id": stat.user.id,
                    "total_won": stat.total_won,
                    "total_games": stat.total_games,
                    "games_won": stat.games_won,
                    "win_rate": win_rate
                })
        
        return leaderboard[:limit]
    
    @staticmethod
    def calculate_slot_payout(symbols: List[str], bet: int) -> Tuple[int, str]:
        """Calculate slot machine payout"""
        symbol_values = {
            "🍒": 0.5,
            "🍋": 0.8,
            "🍊": 1.0,
            "🍇": 1.5,
            "🔔": 2.0,
            "💎": 2.5
        }
        
        # Check for three of a kind
        if symbols[0] == symbols[1] == symbols[2]:
            multiplier = symbol_values.get(symbols[0], 1.0)
            payout = int(bet * multiplier)
            return payout, f"Three {symbols[0]}s!"
        
        # Check for two of a kind
        if symbols[0] == symbols[1] or symbols[1] == symbols[2] or symbols[0] == symbols[2]:
            # Find the matching symbol
            if symbols[0] == symbols[1]:
                matching_symbol = symbols[0]
            elif symbols[1] == symbols[2]:
                matching_symbol = symbols[1]
            else:
                matching_symbol = symbols[0]
            
            multiplier = symbol_values.get(matching_symbol, 1.0) * 0.3
            payout = int(bet * multiplier)
            return payout, f"Two {matching_symbol}s!"
        
        return 0, "No match"
    
    @staticmethod
    def get_roulette_color(number: int) -> str:
        """Get the color of a roulette number"""
        if number == 0:
            return "green"
        
        red_numbers = [1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36]
        return "red" if number in red_numbers else "black"
    
    @staticmethod
    def calculate_roulette_payout(bet_type: str, bet_value: str, result: int, bet_amount: int) -> Tuple[int, bool]:
        """Calculate roulette payout"""
        won = False
        payout = 0
        
        if bet_type == "number":
            if int(bet_value) == result:
                won = True
                payout = bet_amount * 35
        elif bet_type == "color":
            result_color = CasinoManager.get_roulette_color(result)
            if bet_value == result_color:
                won = True
                payout = bet_amount * 2
        elif bet_type == "parity" and result != 0:
            if (bet_value == "even" and result % 2 == 0) or (bet_value == "odd" and result % 2 == 1):
                won = True
                payout = bet_amount * 2
        elif bet_type == "range" and result != 0:
            if (bet_value == "low" and 1 <= result <= 18) or (bet_value == "high" and 19 <= result <= 36):
                won = True
                payout = bet_amount * 2
        
        return payout, won
    
    @staticmethod
    def get_daily_casino_bonus() -> Dict[str, int]:
        """Get daily casino bonuses (could be used for special events)"""
        from datetime import date
        import random
        
        # Seed random with today's date for consistent daily bonuses
        today = date.today()
        random.seed(today.toordinal())
        
        bonuses = {
            "free_spins": random.randint(0, 5),  # Free slot spins
            "bonus_multiplier": random.choice([1.0, 1.1, 1.2, 1.5]),  # Win multiplier
            "max_bet_bonus": random.randint(0, 1000)  # Extra max bet allowance
        }
        
        # Reset random seed
        random.seed()
        
        return bonuses
    
    @staticmethod
    async def get_casino_achievements(user_id: int) -> List[Dict]:
        """Get casino achievements for a user"""
        stats = await CasinoManager.get_user_stats(user_id)
        if not stats:
            return []
        
        achievements = []
        
        # Games played achievements
        if stats["total_games"] >= 1:
            achievements.append({"name": "First Timer", "description": "Play your first casino game", "emoji": "🎮"})
        if stats["total_games"] >= 10:
            achievements.append({"name": "Regular Player", "description": "Play 10 casino games", "emoji": "🎯"})
        if stats["total_games"] >= 100:
            achievements.append({"name": "High Roller", "description": "Play 100 casino games", "emoji": "🎰"})
        
        # Win streak achievements
        if stats["games_won"] >= 1:
            achievements.append({"name": "Lucky Strike", "description": "Win your first game", "emoji": "🍀"})
        if stats["games_won"] >= 10:
            achievements.append({"name": "Winner", "description": "Win 10 games", "emoji": "🏆"})
        
        # Big win achievements
        if stats["biggest_win"] >= 1000:
            achievements.append({"name": "Big Winner", "description": "Win 1,000+ coins in a single game", "emoji": "💰"})
        if stats["biggest_win"] >= 5000:
            achievements.append({"name": "Jackpot", "description": "Win 5,000+ coins in a single game", "emoji": "💎"})
        
        # Profit achievements
        net_profit = stats["total_won"] - stats["total_wagered"]
        if net_profit > 0:
            achievements.append({"name": "In the Green", "description": "Have positive net profit", "emoji": "📈"})
        
        return achievements