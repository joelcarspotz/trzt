"""Casino system models"""

from tortoise import fields
from tortoise.models import Model


class CasinoGame(Model):
    """Track individual casino games"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="casino_games")
    
    game_type = fields.CharField(max_length=20)  # slots, dice, blackjack, roulette
    bet_amount = fields.IntField()
    winnings = fields.IntField()
    net_result = fields.IntField()  # winnings - bet_amount
    
    # Game-specific data
    game_data = fields.JSONField(default=dict)  # Store game-specific information
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "casino_games"


class CasinoStats(Model):
    """User casino statistics"""
    id = fields.IntField(pk=True)
    user = fields.OneToOneField("models.User", related_name="casino_stats")
    
    # Overall stats
    total_games_played = fields.IntField(default=0)
    total_bet = fields.IntField(default=0)
    total_winnings = fields.IntField(default=0)
    total_net = fields.IntField(default=0)
    
    # Game-specific stats
    slots_games = fields.IntField(default=0)
    slots_winnings = fields.IntField(default=0)
    
    dice_games = fields.IntField(default=0)
    dice_winnings = fields.IntField(default=0)
    
    blackjack_games = fields.IntField(default=0)
    blackjack_winnings = fields.IntField(default=0)
    
    roulette_games = fields.IntField(default=0)
    roulette_winnings = fields.IntField(default=0)
    
    # Win rates
    slots_win_rate = fields.FloatField(default=0.0)
    dice_win_rate = fields.FloatField(default=0.0)
    blackjack_win_rate = fields.FloatField(default=0.0)
    roulette_win_rate = fields.FloatField(default=0.0)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "casino_stats"


class CasinoLeaderboard(Model):
    """Casino leaderboard entries"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="casino_leaderboard")
    
    # Leaderboard categories
    total_winnings = fields.IntField(default=0)
    biggest_win = fields.IntField(default=0)
    win_streak = fields.IntField(default=0)
    current_streak = fields.IntField(default=0)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "casino_leaderboard"