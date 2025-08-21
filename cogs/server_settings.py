import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from utils.database import MessageDatabase

class ServerSettings(commands.Cog):
    """Cog for managing server-specific settings including random messages"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = MessageDatabase("data/bot_messages.db")
    
    @app_commands.command(name="server", description="Manage server settings (Admin only)")
    @app_commands.describe(
        setting="The setting to configure",
        enabled="Enable (True) or disable (False) the setting"
    )
    @app_commands.choices(setting=[
        app_commands.Choice(name="randommessages", value="randommessages")
    ])
    @app_commands.default_permissions(administrator=True)
    async def server_settings(self, interaction: discord.Interaction, setting: str, enabled: bool):
        """Configure server settings (Admin only)"""
        
        # Check if this is in a guild (server)
        if not interaction.guild:
            embed = discord.Embed(
                title="❌ Server Only Command",
                description="This command can only be used in a server, not in DMs.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You need Administrator permissions to use this command.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = str(interaction.guild.id)
        guild_name = interaction.guild.name
        
        if setting == "randommessages":
            # Update guild settings for random messages
            success = await self.db.update_guild_settings(
                guild_id=guild_id,
                guild_name=guild_name,
                random_messages_enabled=enabled
            )
            
            if success:
                status = "enabled" if enabled else "disabled"
                embed = discord.Embed(
                    title="✅ Server Settings Updated",
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
        else:
            embed = discord.Embed(
                title="❌ Invalid Setting",
                description=f"Unknown setting: {setting}",
                color=discord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="server_status", description="View current server settings")
    async def server_status(self, interaction: discord.Interaction):
        """Display current server settings"""
        
        # Check if this is in a guild (server)
        if not interaction.guild:
            embed = discord.Embed(
                title="❌ Server Only Command",
                description="This command can only be used in a server, not in DMs.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        guild_id = str(interaction.guild.id)
        settings = await self.db.get_guild_settings(guild_id)
        
        random_messages_status = "🎲 Enabled" if settings.get('random_messages_enabled', False) else "❌ Disabled"
        
        embed = discord.Embed(
            title="⚙️ Server Settings",
            description=f"Current settings for **{interaction.guild.name}**",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Random Messages",
            value=random_messages_status,
            inline=True
        )
        
        if settings.get('random_messages_enabled', False):
            embed.add_field(
                name="📊 Random Message Info",
                value="• 40% chance per message\n• Uses channel message history\n• Generates contextual responses",
                inline=False
            )
        
        embed.add_field(
            name="🔧 Configuration",
            value="Use `/server randommessages enabled:True/False` to toggle random messages\n"
                  "(Administrator permission required)",
            inline=False
        )
        
        embed.set_footer(text=f"Guild ID: {guild_id}")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerSettings(bot))
