"""Main bot class"""

import logging
from typing import Optional

import discord
from discord.ext import commands

from carfigures.core.config import Config
from carfigures.commands.coins import CoinsCommands
from carfigures.commands.packs import PackCommands
from carfigures.commands.general import GeneralCommands
from carfigures.commands.casino import CasinoCommands
from carfigures.utils.coins import CoinManager

logger = logging.getLogger(__name__)


class CarFiguresBot(commands.Bot):
    """Main CarFigures bot class"""
    
    def __init__(self, config: Config):
        self.config = config
        
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix=config.prefix,
            description=config.bot_description,
            intents=intents,
            help_command=None
        )
        
        # Message tracking for spawning
        self.message_counts = {}
        self.last_spawn = {}
        
    async def setup_hook(self):
        """Setup bot extensions and commands"""
        logger.info("Setting up bot...")
        
        # Add cogs
        await self.add_cog(CoinsCommands(self))
        await self.add_cog(PackCommands(self))
        await self.add_cog(GeneralCommands(self))
        
        # Add casino commands if enabled
        if self.config.casino_config.enabled:
            await self.add_cog(CasinoCommands(self))
        
        logger.info("Bot setup complete!")
    
    async def on_ready(self):
        """Called when bot is ready"""
        logger.info(f"Logged in as {self.user} (ID: {self.user.id})")
        logger.info(f"Connected to {len(self.guilds)} guilds")
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="for Aston Martins! | !help"
        )
        await self.change_presence(activity=activity)
    
    async def on_message(self, message: discord.Message):
        """Handle message events for spawning and commands"""
        if message.author.bot:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Handle car spawning logic
        if message.guild:
            await self._handle_spawning(message)
    
    async def _handle_spawning(self, message: discord.Message):
        """Handle car spawning based on message activity"""
        guild_id = message.guild.id
        
        # Initialize tracking for this guild
        if guild_id not in self.message_counts:
            self.message_counts[guild_id] = 0
            self.last_spawn[guild_id] = None
        
        self.message_counts[guild_id] += 1
        
        # Check if we should spawn (simplified logic for now)
        required_messages = self.config.spawn_manager.required_message_range[1]
        
        if self.message_counts[guild_id] >= required_messages:
            # Check member requirement
            if len(message.guild.members) >= self.config.spawn_manager.minimum_members_required:
                await self._spawn_car(message.channel)
                self.message_counts[guild_id] = 0
    
    async def _spawn_car(self, channel: discord.TextChannel):
        """Spawn a car in the channel"""
        import random
        
        # Select spawn message based on rarity
        spawn_messages = self.config.spawn_manager.spawn_messages
        weights = [msg.rarity for msg in spawn_messages]
        selected_msg = random.choices(spawn_messages, weights=weights)[0]
        
        # Create spawn embed
        embed = discord.Embed(
            title="🚗 A Wild Aston Martin Appears!",
            description=selected_msg.message,
            color=int(self.config.default_embed_color, 16)
        )
        
        # Select catch button message
        button_messages = self.config.spawn_manager.catch_button_messages
        button_weights = [msg.rarity for msg in button_messages]
        button_msg = random.choices(button_messages, weights=button_weights)[0]
        
        # Create view with catch button
        view = CarCatchView(self, selected_msg.rarity)
        
        try:
            await channel.send(embed=embed, view=view)
            logger.info(f"Spawned car in {channel.guild.name}#{channel.name}")
        except discord.Forbidden:
            logger.warning(f"Cannot send message in {channel.guild.name}#{channel.name}")


class CarCatchView(discord.ui.View):
    """View for catching cars"""
    
    def __init__(self, bot: CarFiguresBot, rarity: float):
        super().__init__(timeout=60.0)
        self.bot = bot
        self.rarity = rarity
        self.caught = False
    
    @discord.ui.button(label="Catch Me!", style=discord.ButtonStyle.primary, emoji="🚗")
    async def catch_car(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Handle car catch attempt"""
        if self.caught:
            await interaction.response.send_message(
                "This car has already been caught!", 
                ephemeral=True
            )
            return
        
        self.caught = True
        
        # Award coins for catching
        config = self.bot.config.coin_config
        coins_earned = await CoinManager.reward_catch(
            interaction.user.id,
            config.catch_reward_base,
            config.catch_reward_bonus_range
        )
        
        # Create success embed
        embed = discord.Embed(
            title="🎉 Car Caught!",
            description=f"{interaction.user.mention} caught the Aston Martin!",
            color=0x00ff00
        )
        embed.add_field(
            name="💰 Coins Earned",
            value=f"+{coins_earned} coins",
            inline=True
        )
        
        # Disable button
        button.disabled = True
        await interaction.response.edit_message(embed=embed, view=self)
        
        # Stop the view
        self.stop()
    
    async def on_timeout(self):
        """Handle view timeout"""
        # Disable all buttons
        for item in self.children:
            item.disabled = True