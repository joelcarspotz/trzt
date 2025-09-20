"""Casino system models"""

from tortoise import fields
from tortoise.models import Model


class CasinoStats(Model):
    """User casino statistics"""
    id = fields.IntField(pk=True)
    user = fields.OneToOneField("models.User", related_name="casino_stats")
    
    # Overall stats
    total_games = fields.IntField(default=0)
    games_won = fields.IntField(default=0)
    total_wagered = fields.IntField(default=0)
    total_won = fields.IntField(default=0)
    biggest_win = fields.IntField(default=0)
    
    # Game-specific stats stored as JSON
    slots_stats = fields.JSONField(default=dict)
    coinflip_stats = fields.JSONField(default=dict)
    dice_stats = fields.JSONField(default=dict)
    blackjack_stats = fields.JSONField(default=dict)
    roulette_stats = fields.JSONField(default=dict)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    last_played = fields.DatetimeField(null=True)
    
    class Meta:
        table = "casino_stats"
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.total_games == 0:
            return 0.0
        return (self.games_won / self.total_games) * 100
    
    @property
    def net_profit(self) -> int:
        """Calculate net profit/loss"""
        return self.total_won - self.total_wagered
    
    def get_game_stats(self, game_type: str) -> dict:
        """Get statistics for a specific game type"""
        return getattr(self, f"{game_type}_stats", {})
    
    def set_game_stats(self, game_type: str, stats: dict):
        """Set statistics for a specific game type"""
        setattr(self, f"{game_type}_stats", stats)


class CasinoTransaction(Model):
    """Casino transaction history"""
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="casino_transactions")
    
    game_type = fields.CharField(max_length=20)  # slots, coinflip, dice, blackjack, roulette
    bet_amount = fields.IntField()
    winnings = fields.IntField(default=0)
    won = fields.BooleanField()
    
    # Game-specific data stored as JSON
    game_data = fields.JSONField(default=dict)  # Store specific game results
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    
    class Meta:
        table = "casino_transactions"
        ordering = ["-created_at"]


class CasinoBan(Model):
    """Casino ban system for problem gambling"""
    id = fields.IntField(pk=True)
    user = fields.OneToOneField("models.User", related_name="casino_ban")
    
    # Ban details
    is_banned = fields.BooleanField(default=False)
    ban_reason = fields.TextField(null=True)
    banned_by = fields.BigIntField(null=True)  # Admin user ID
    
    # Self-exclusion support
    is_self_excluded = fields.BooleanField(default=False)
    self_exclusion_until = fields.DatetimeField(null=True)
    
    # Daily limits
    daily_loss_limit = fields.IntField(null=True)
    daily_wager_limit = fields.IntField(null=True)
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "casino_bans"


class CasinoEvent(Model):
    """Special casino events and promotions"""
    id = fields.IntField(pk=True)
    
    name = fields.CharField(max_length=100)
    description = fields.TextField()
    
    # Event timing
    start_time = fields.DatetimeField()
    end_time = fields.DatetimeField()
    is_active = fields.BooleanField(default=True)
    
    # Event bonuses
    win_multiplier = fields.FloatField(default=1.0)  # Multiply winnings
    free_spins = fields.IntField(default=0)  # Free slot spins
    bonus_coins = fields.IntField(default=0)  # Bonus coins for participation
    
    # Restrictions
    max_participants = fields.IntField(null=True)
    min_bet = fields.IntField(default=10)
    max_bet = fields.IntField(null=True)
    allowed_games = fields.JSONField(default=list)  # List of allowed game types
    
    # Timestamps
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "casino_events"


class CasinoEventParticipant(Model):
    """Track event participation"""
    id = fields.IntField(pk=True)
    event = fields.ForeignKeyField("models.CasinoEvent", related_name="participants")
    user = fields.ForeignKeyField("models.User", related_name="casino_event_participations")
    
    # Participation stats
    games_played = fields.IntField(default=0)
    total_wagered = fields.IntField(default=0)
    total_won = fields.IntField(default=0)
    bonus_coins_earned = fields.IntField(default=0)
    
    # Timestamps
    joined_at = fields.DatetimeField(auto_now_add=True)
    last_activity = fields.DatetimeField(auto_now=True)
    
    class Meta:
        table = "casino_event_participants"
        unique_together = ("event", "user")