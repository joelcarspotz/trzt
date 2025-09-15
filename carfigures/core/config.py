"""Configuration management"""

import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class SpawnMessage:
    message: str
    rarity: float


@dataclass
class SpawnManagerConfig:
    required_message_range: List[int]
    spawn_messages: List[SpawnMessage]
    catch_button_messages: List[SpawnMessage]
    wrong_name_messages: List[SpawnMessage]
    catch_bonus_rate: List[int]
    cooldown_time: int
    minimum_members_required: int


@dataclass
class TeamConfig:
    roots: List[int]
    super_guilds: List[int]
    super_users: List[int]
    log_channel: int


@dataclass
class CoinConfig:
    daily_claim_amount: int
    catch_reward_base: int
    catch_reward_bonus_range: List[int]
    pack_prices: Dict[str, int]


@dataclass
class Config:
    bot_token: str
    bot_description: str
    bot_name: str
    prefix: str
    max_favorites: int
    default_embed_color: str
    spawn_manager: SpawnManagerConfig
    team: TeamConfig
    coin_config: CoinConfig
    
    @classmethod
    def from_file(cls, path: Path) -> "Config":
        with open(path, "rb") as f:
            data = tomllib.load(f)
        
        # Parse spawn messages
        spawn_messages = [
            SpawnMessage(msg["message"], msg["rarity"])
            for msg in data["spawn-manager"]["spawnMessages"]
        ]
        
        catch_button_messages = [
            SpawnMessage(msg["message"], msg["rarity"])
            for msg in data["spawn-manager"]["catchButtonMessages"]
        ]
        
        wrong_name_messages = [
            SpawnMessage(msg["message"], msg["rarity"])
            for msg in data["spawn-manager"]["wrongNameMessages"]
        ]
        
        spawn_manager = SpawnManagerConfig(
            required_message_range=data["spawn-manager"]["requiredMessageRange"],
            spawn_messages=spawn_messages,
            catch_button_messages=catch_button_messages,
            wrong_name_messages=wrong_name_messages,
            catch_bonus_rate=data["spawn-manager"]["catchBonusRate"],
            cooldown_time=data["spawn-manager"]["cooldownTime"],
            minimum_members_required=data["spawn-manager"]["minimumMembersRequired"]
        )
        
        team = TeamConfig(
            roots=data["team"]["roots"],
            super_guilds=data["team"]["superGuilds"],
            super_users=data["team"]["superUsers"],
            log_channel=data["team"]["logChannel"]
        )
        
        # Parse coin configuration
        coin_data = data.get("coins", {})
        coin_config = CoinConfig(
            daily_claim_amount=coin_data.get("dailyClaimAmount", 100),
            catch_reward_base=coin_data.get("catchRewardBase", 50),
            catch_reward_bonus_range=coin_data.get("catchRewardBonusRange", [-10, 25]),
            pack_prices=coin_data.get("packPrices", {
                "basic": 500,
                "premium": 1000,
                "legendary": 2500
            })
        )
        
        return cls(
            bot_token=data["settings"]["botToken"],
            bot_description=data["settings"]["botDescription"],
            bot_name=data["settings"]["botName"],
            prefix=data["settings"]["prefix"],
            max_favorites=data["settings"]["maxFavorites"],
            default_embed_color=data["settings"]["defaultEmbedColor"],
            spawn_manager=spawn_manager,
            team=team,
            coin_config=coin_config
        )