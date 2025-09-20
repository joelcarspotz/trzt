# 🎰 Casino System for CarFigures Discord Bot

The casino system adds gambling functionality to your CarFigures Discord bot, allowing users to wager their coins on various games of chance and skill.

## 🎮 Available Games

### 🎰 Slots (`!slots <bet>`)
- Classic 3-reel slot machine with car-themed symbols
- Symbols: 🍒 (0.5x), 🍋 (0.8x), 🍊 (1.0x), 🍇 (1.5x), 🔔 (2.0x), 💎 (2.5x)
- **Payouts:**
  - Three of a kind: Full symbol multiplier
  - Two of a kind: 30% of symbol multiplier
- **Max Payout:** 2.5x bet
- **Animation:** Spinning reel animation for immersion

### 🪙 Coinflip (`!coinflip <bet> <heads/tails>`)
- Simple 50/50 coin flip game
- Choose heads or tails
- **Payout:** 2x bet on win
- **House Edge:** 0% (fair game)

### 🎲 Dice (`!dice <bet> <guess>`)
- Guess the result of a 6-sided die roll
- Guess numbers 1-6
- **Payout:** 6x bet on correct guess
- **Win Chance:** 16.67% (1 in 6)

### 🃏 Blackjack (`!blackjack <bet>`)
- Full blackjack implementation with dealer AI
- Standard rules: Hit, Stand, Dealer hits on soft 17
- Interactive gameplay with reaction buttons
- **Payouts:**
  - Regular win: 2x bet
  - Blackjack: 2.5x bet
  - Push: Bet returned
- **Features:** Natural blackjack detection, soft ace handling

### 🎯 Roulette (`!roulette <bet> <choice>`)
- European roulette (0-36, single zero)
- **Bet Types:**
  - Number bet (0-36): 35x payout
  - Color bet (red/black): 2x payout
  - Parity bet (even/odd): 2x payout
  - Range bet (high 19-36/low 1-18): 2x payout
- **House Edge:** ~2.7% (single zero)

## 💰 Betting Limits & Configuration

### Default Limits (Configurable in `config.toml`)
- **Minimum Bet:** 10 coins (all games)
- **Maximum Bets:**
  - Slots: 10,000 coins
  - Coinflip: 5,000 coins
  - Blackjack: 5,000 coins
  - Dice: 2,000 coins (due to 6x payout)
  - Roulette: 1,000 coins (due to 35x payout potential)

### Safety Features
- Users cannot bet more coins than they have
- Maximum bet is capped to prevent excessive losses
- Game timeout protection (30 seconds default)
- One active game per user at a time

## 📊 Statistics & Tracking

### User Statistics (`!casinostats [user]`)
- Total games played and won
- Win rate percentage
- Total wagered and total won
- Net profit/loss
- Biggest single win
- Favorite game (most played)
- Last played timestamp

### Leaderboards (`!casinolb [game_type]`)
- Overall casino leaderboard (total winnings)
- Game-specific leaderboards
- Top 10 players displayed
- Win rates shown for overall leaderboard

### Database Tracking
- Individual game results stored
- Comprehensive statistics per user
- Transaction history
- Game-specific performance metrics

## 🛡️ Responsible Gambling Features

### Built-in Protections
- Betting limits prevent excessive wagering
- Statistics help users track their gambling
- Clear profit/loss displays
- Educational messaging about responsible gambling

### Future Extensions (Models Ready)
- Self-exclusion system (`CasinoBan` model)
- Daily loss/wager limits
- Admin ban system for problem gambling
- Casino events and promotions (`CasinoEvent` model)

## ⚙️ Configuration

### Enable/Disable Casino
```toml
[casino]
enabled = true  # Set to false to disable all casino features
```

### Game-Specific Settings
```toml
[casino.games]
slots = { enabled = true, maxBet = 10000, minBet = 10 }
coinflip = { enabled = true, maxBet = 5000, minBet = 10 }
dice = { enabled = true, maxBet = 2000, minBet = 10 }
blackjack = { enabled = true, maxBet = 5000, minBet = 10 }
roulette = { enabled = true, maxBet = 1000, minBet = 10 }
```

### Global Casino Settings
```toml
[casino]
minBet = 10                    # Global minimum bet
maxBetMultiplier = 10          # Max bet = balance * multiplier
maxBetCap = 10000             # Absolute maximum bet
gameTimeoutSeconds = 30        # Timeout for interactive games
```

## 🎯 Commands Reference

### Core Commands
- `!casino` - Display casino help and available games
- `!slots <bet>` - Play slot machine
- `!coinflip <bet> <heads/tails>` - Flip a coin
- `!dice <bet> <guess>` - Roll dice and guess result
- `!blackjack <bet>` - Play blackjack against dealer
- `!roulette <bet> <choice>` - Play European roulette

### Statistics Commands
- `!casinostats [user]` - View gambling statistics
- `!casinolb [game_type]` - View casino leaderboard

### Aliases
- `!gamble` → `!casino`
- `!flip` → `!coinflip`
- `!bj` → `!blackjack`
- `!casinoleaderboard` → `!casinolb`

## 🏗️ Technical Implementation

### Database Models
- **CasinoStats:** User gambling statistics and game-specific data
- **CasinoTransaction:** Individual game transaction history
- **CasinoBan:** Responsible gambling controls (future use)
- **CasinoEvent:** Special casino events and promotions (future use)

### Game Logic
- All games use cryptographically secure random number generation
- Proper probability calculations for fair gameplay
- Comprehensive error handling and validation
- Interactive UI with Discord reactions and buttons

### Performance Features
- Single active game per user prevents spam
- Efficient database queries with proper indexing
- Configurable timeouts prevent hanging games
- Optimized statistics calculations

## 🚀 Getting Started

1. **Enable Casino:** Set `casino.enabled = true` in your `config.toml`
2. **Configure Limits:** Adjust betting limits as desired
3. **Restart Bot:** The casino cog loads automatically when enabled
4. **Test Games:** Try `!casino` to see available games
5. **Monitor Usage:** Use `!casinolb` to see player activity

## 🎲 Game Theory & House Edge

- **Coinflip:** 0% house edge (perfectly fair)
- **Dice:** 0% house edge (fair odds)
- **Slots:** ~10-20% house edge (depends on symbol distribution)
- **Blackjack:** ~0.5% house edge (with optimal play)
- **Roulette:** ~2.7% house edge (European single-zero)

The casino system is designed to be entertaining while maintaining reasonable house edges. Users can still profit through skill (blackjack) or luck, but the system ensures long-term sustainability.

## 🔮 Future Enhancements

- **Tournaments:** Multi-user casino tournaments
- **Achievements:** Gambling achievement system
- **VIP System:** High-roller benefits and exclusive games
- **Social Features:** Spectating, sharing big wins
- **More Games:** Poker, Baccarat, Craps, etc.
- **Progressive Jackpots:** Accumulating prize pools

---

**Remember:** This casino system is for entertainment purposes only using virtual currency. Always promote responsible gambling practices!