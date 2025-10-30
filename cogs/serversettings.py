import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utils.database import MessageDatabase
import discord

class ServerSettings(commands.Cog):
    """Cog for managing server-specific settings including random messages"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = MessageDatabase("data/bot_messages.db")

    gorksettings = app_commands.Group(name="gorksettings", description="Manage Gork AI server settings")

    async def _check_admin_permissions(self, interaction: discord.Interaction) -> bool:
        """Helper to check for administrator permissions and send an ephemeral message if not met."""
        if not interaction.guild:
            embed = discord.Embed(
                title="❌ Server Only Command",
                description="This command can only be used in a server, not in DMs.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False

        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True

    @gorksettings.command(name="random_messages", description="Toggle Gork's random message generation")
    @app_commands.describe(enabled="Enable (True) or disable (False) random messages")
    @app_commands.default_permissions(administrator=True)
    async def random_messages(self, interaction: discord.Interaction, enabled: bool):
        """Toggle Gork's random message generation"""
        if not await self._check_admin_permissions(interaction):
            return

        guild_id = str(interaction.guild.id)
        guild_name = interaction.guild.name

        try:
            success = await self.db.update_guild_settings(
                guild_id=guild_id,
                guild_name=guild_name,
                random_messages_enabled=enabled
            )

            if success:
                status = "enabled" if enabled else "disabled"
                embed = discord.Embed(
                    title="✅ Gork Settings Updated",
                    description=f"Random messages have been **{status}** for this server.\n\n"
                               f"When enabled, there's a 4/10 chance that any message sent in this server "
                               f"will trigger the bot to generate and send the most likely next message based "
                               f"on the channel's message history.",
                    color=discord.Color.green()
                )
                if enabled:
                    embed.add_field(
                        name="📝 How it works",
                        value="• 40% chance to trigger on any message\n"
                              "• Bot analyzes recent channel messages\n"
                              "• Generates contextually appropriate response\n"
                              "• Only works in channels where bot can see message history",
                        inline=False
                    )
                    embed.add_field(
                        name="⚠️ Note",
                        value="The bot needs to have logged messages in this channel to generate responses. "
                              "If this is a new setup, it may take some time to build up message history.",
                        inline=False
                    )
            else:
                embed = discord.Embed(
                    title="❌ Error",
                    description="Failed to update server settings. Please try again.",
                    color=discord.Color.red()
                )
        except Exception as e:
            print(f"Error in random_messages command: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description=f"An unexpected error occurred: {e}",
                color=discord.Color.red()
            )
        await interaction.response.send_message(embed=embed)

    @gorksettings.command(name="bot_reply", description="Toggle Gork's replies to other bots")
    @app_commands.describe(enabled="Enable (True) or disable (False) Gork replying to other bots")
    @app_commands.default_permissions(administrator=True)
    async def bot_reply(self, interaction: discord.Interaction, enabled: bool):
        """Toggle Gork's replies to other bots"""
        if not await self._check_admin_permissions(interaction):
            return

        guild_id = str(interaction.guild.id)
        guild_name = interaction.guild.name

        try:
            success = await self.db.update_guild_settings(
                guild_id=guild_id,
                guild_name=guild_name,
                bot_reply_enabled=enabled
            )

            if success:
                status = "enabled" if enabled else "disabled"
                embed = discord.Embed(
                    title="✅ Gork Settings Updated",
                    description=f"Gork's replies to other bots have been **{status}** for this server.",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="❌ Error",
                    description="Failed to update server settings. Please try again.",
                    color=discord.Color.red()
                )
        except Exception as e:
            print(f"Error in bot_reply command: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description=f"An unexpected error occurred: {e}",
                color=discord.Color.red()
            )
        await interaction.response.send_message(embed=embed)

    @gorksettings.command(name="reply_all", description="Toggle Gork replying to all messages in the current channel")
    @app_commands.describe(enabled="Enable (True) or disable (False) Gork replying to all messages in this channel")
    @app_commands.default_permissions(administrator=True)
    async def reply_all(self, interaction: discord.Interaction, enabled: bool):
        """Toggle Gork replying to all messages in the current channel"""
        if not await self._check_admin_permissions(interaction):
            return

        if not interaction.channel or not interaction.guild:
            embed = discord.Embed(
                title="❌ Channel Only Command",
                description="This command can only be used in a server channel.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        channel_id = str(interaction.channel.id)
        guild_id = str(interaction.guild.id)
        
        try:
            success = await self.db.update_channel_settings(
                channel_id=channel_id,
                guild_id=guild_id,
                reply_all_enabled=enabled
            )

            if success:
                status = "enabled" if enabled else "disabled"
                embed = discord.Embed(
                    title="✅ Gork Settings Updated",
                    description=f"Gork will now reply to all messages (not just mentions/DMs) in this channel: **{status}**.",
                    color=discord.Color.green()
                )
                if enabled:
                    embed.add_field(
                        name="⚠️ Warning",
                        value="Enabling 'Reply All' can make Gork very chatty and may lead to high API usage. "
                              "Consider using this setting carefully.",
                        inline=False
                    )
            else:
                embed = discord.Embed(
                    title="❌ Error",
                    description="Failed to update channel settings. Please try again.",
                    color=discord.Color.red()
                )
        except Exception as e:
            print(f"Error in reply_all command: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description=f"An unexpected error occurred: {e}",
                color=discord.Color.red()
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="server_status", description="View current server and channel settings")
    async def server_status(self, interaction: discord.Interaction):
        """Display current server and channel settings"""
        
        if not interaction.guild:
            embed = discord.Embed(
                title="❌ Server Only Command",
                description="This command can only be used in a server, not in DMs.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = str(interaction.guild.id)
        guild_settings = await self.db.get_guild_settings(guild_id)
        
        random_messages_status = "🎲 Enabled" if guild_settings.get('random_messages_enabled', False) else "❌ Disabled"
        bot_reply_status = "🤖 Enabled" if guild_settings.get('bot_reply_enabled', False) else "❌ Disabled"
        
        embed = discord.Embed(
            title="⚙️ Server Settings",
            description=f"Current settings for **{interaction.guild.name}**",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Random Messages (Server)",
            value=random_messages_status,
            inline=True
        )
        embed.add_field(
            name="Reply to Bots (Server)",
            value=bot_reply_status,
            inline=True
        )

        
        if interaction.channel and isinstance(interaction.channel, discord.TextChannel):
            channel_id = str(interaction.channel.id)
            channel_settings = await self.db.get_channel_settings(channel_id, guild_id)
            reply_all_channel_status = "💬 Enabled" if channel_settings.get('reply_all_enabled', False) else "❌ Disabled"
            
            embed.add_field(
                name="Reply to All Messages (Current Channel)",
                value=reply_all_channel_status,
                inline=True
            )
        else:
            embed.add_field(
                name="Reply to All Messages (Current Channel)",
                value="N/A (Not a text channel)",
                inline=True
            )
        
        if guild_settings.get('random_messages_enabled', False):
            embed.add_field(
                name="📊 Random Message Info",
                value="• 40% chance per message\n• Uses channel message history\n• Generates contextual responses",
                inline=False
            )
        
        embed.add_field(
            name=" Configuration",
            value="Use `/gorksettings random_messages enabled:True/False` to toggle random messages (server-wide)\n"
                  "Use `/gorksettings bot_reply enabled:True/False` to toggle replying to bots (server-wide)\n"
                  "Use `/gorksettings reply_all enabled:True/False` to toggle replying to all messages (current channel)\n"
                  "(Administrator permission required)",
            inline=False
        )
        
        embed.set_footer(text=f"Guild ID: {guild_id}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    cog = ServerSettings(bot)
    await cog.db.initialize() 
    await bot.add_cog(cog)
