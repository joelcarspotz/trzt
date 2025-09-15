# CarFigures Bot - Coin Reward System

This document describes the new coin reward system added to the CarFigures bot.

## Features Added

### 🪙 Coin System
- Users earn coins by catching cars when they spawn
- Base reward configurable in `config.toml` (default: 50 coins)
- Random bonus/penalty range for catch rewards (default: -10 to +25)
- Tracks lifetime earned and spent coins

### 📅 Daily Claims
- Users can claim daily coin rewards
- Base amount configurable (default: 100 coins)
- Streak system with bonus rewards (up to 50% bonus at 7+ day streaks)
- Prevents double claiming on same day

### 📦 Pack System
- Three types of packs available: Basic, Premium, Legendary
- Packs contain random cars based on rarity chances
- Pack prices configurable in config.toml
- Users can purchase packs with coins and open them later

### 🎯 Admin Panel Integration
- Web-based admin panel at `/admin` endpoint
- Manage users, cars, packs, and pack contents
- View user coins and pack purchase history
- Create and configure new packs

## New Commands

### User Commands
- `!daily` / `!claim` - Claim daily coin reward
- `!balance` / `!coins` / `!bal` - Check coin balance
- `!leaderboard` / `!lb` / `!top` - View top coin holders
- `!shop` / `!store` / `!packs` - View available packs
- `!buy <pack_name>` - Purchase a pack with coins
- `!inventory` / `!inv` - View unopened packs
- `!open <pack_id>` - Open a purchased pack
- `!garage` / `!collection` - View car collection
- `!info <car_name>` - Get information about a car

### Admin Commands
- `!give <user> <amount>` - Give coins to a user
- `!pack create <name> <price> <description>` - Create new pack
- `!pack list` - List all packs
- `!pack toggle <pack_id>` - Toggle pack availability

## Configuration

The coin system is configured in `config.toml`:

```toml
[coins]
# Coin reward system configuration
dailyClaimAmount = 100
catchRewardBase = 50
catchRewardBonusRange = [-10, 25]

[coins.packPrices]
basic = 500
premium = 1000
legendary = 2500
```

## Database Models

### New Tables
- `users` - Discord user information and stats
- `user_coins` - User coin balances and lifetime stats
- `daily_claims` - Daily claim tracking with streaks
- `cars` - Car figure definitions
- `user_cars` - User car collections
- `packs` - Pack type definitions
- `pack_contents` - Cars available in each pack
- `user_packs` - User pack purchases and openings

## Admin Panel Access

1. Start the panel service: `docker-compose up panel`
2. Access at `http://localhost:8000/admin`
3. Login with username: `admin` (configure password as needed)

## Pack Management

Admins can:
- Create new pack types with custom rarity chances
- Add/remove cars from pack contents
- Set drop rates for individual cars
- Toggle pack availability
- Create limited-time packs

## Technical Details

- Built with Discord.py 2.4+
- Uses Tortoise ORM for database management
- FastAPI admin panel with fastapi-admin
- Supports PostgreSQL (production) and SQLite (development)
- Comprehensive error handling and logging

## Sample Data

The bot automatically creates sample Aston Martin cars and packs on first run:
- 6 sample cars (DB11, Vantage, DBS, DBX, Valkyrie, Victor)
- 3 pack types (Basic, Premium, Legendary)
- Appropriate rarity distributions and pricing