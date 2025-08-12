import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional

class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.authorized_user_id = 1141746562922459136  # Only this user can change bot status
    
    def is_authorized_user(self, user_id: int) -> bool:
        """Check if the user is authorized to change bot status"""
        return user_id == self.authorized_user_id
    
    @app_commands.command(name="setstatus", description="Set the bot's custom status (authorized users only)")
    @app_commands.describe(
        status_type="Type of status to set",
        text="The status text to display",
        url="URL for streaming status (only used if type is 'streaming')"
    )
    @app_commands.choices(status_type=[
        app_commands.Choice(name="Playing", value="playing"),
        app_commands.Choice(name="Listening", value="listening"),
        app_commands.Choice(name="Watching", value="watching"),
        app_commands.Choice(name="Streaming", value="streaming"),
        app_commands.Choice(name="Custom", value="custom"),
        app_commands.Choice(name="Competing", value="competing")
    ])
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def set_status(
        self, 
        interaction: discord.Interaction, 
        status_type: str, 
        text: str,
        url: Optional[str] = None
    ):
        """Set the bot's custom status"""
        
        # Check if user is authorized
        if not self.is_authorized_user(interaction.user.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You are not authorized to change the bot's status.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        # Validate inputs
        if len(text) > 128:
            embed = discord.Embed(
                title="❌ Error",
                description="Status text must be 128 characters or less.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Create the appropriate activity based on status type
            activity = None
            
            if status_type == "playing":
                activity = discord.Game(name=text)
            elif status_type == "listening":
                activity = discord.Activity(type=discord.ActivityType.listening, name=text)
            elif status_type == "watching":
                activity = discord.Activity(type=discord.ActivityType.watching, name=text)
            elif status_type == "streaming":
                if not url:
                    embed = discord.Embed(
                        title="❌ Error",
                        description="URL is required for streaming status.",
                        color=discord.Color.red()
                    )
                    await interaction.response.send_message(embed=embed, ephemeral=True)
                    return
                activity = discord.Streaming(name=text, url=url)
            elif status_type == "custom":
                activity = discord.Activity(type=discord.ActivityType.custom, name=text)
            elif status_type == "competing":
                activity = discord.Activity(type=discord.ActivityType.competing, name=text)
            
            # Set the bot's status
            await self.bot.change_presence(activity=activity)
            
            # Send success message
            embed = discord.Embed(
                title="✅ Status Updated",
                description=f"Bot status has been set to: **{status_type.title()}** {text}",
                color=discord.Color.green()
            )
            
            if status_type == "streaming" and url:
                embed.add_field(name="Stream URL", value=url, inline=False)
            
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to set status: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="clearstatus", description="Clear the bot's custom status (authorized users only)")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def clear_status(self, interaction: discord.Interaction):
        """Clear the bot's custom status"""
        
        # Check if user is authorized
        if not self.is_authorized_user(interaction.user.id):
            embed = discord.Embed(
                title="❌ Access Denied",
                description="You are not authorized to change the bot's status.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        try:
            # Clear the bot's status
            await self.bot.change_presence(activity=None)
            
            embed = discord.Embed(
                title="✅ Status Cleared",
                description="Bot status has been cleared.",
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to clear status: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="statusinfo", description="Show current bot status and authorization info")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def status_info(self, interaction: discord.Interaction):
        """Show information about the bot's current status and who can change it"""
        
        # Get current activity
        current_activity = self.bot.activity
        activity_info = "None"
        
        if current_activity:
            activity_type = current_activity.type.name.title()
            activity_name = current_activity.name
            activity_info = f"{activity_type}: {activity_name}"
            
            if hasattr(current_activity, 'url') and current_activity.url:
                activity_info += f"\nURL: {current_activity.url}"
        
        embed = discord.Embed(
            title="🤖 Bot Status Information",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Current Status", value=activity_info, inline=False)
        embed.add_field(name="Authorized User ID", value=str(self.authorized_user_id), inline=False)
        
        # Show if current user is authorized
        is_authorized = self.is_authorized_user(interaction.user.id)
        auth_status = "✅ Yes" if is_authorized else "❌ No"
        embed.add_field(name="You are authorized", value=auth_status, inline=False)
        
        if is_authorized:
            embed.add_field(
                name="Available Commands", 
                value="• `/setstatus` - Set bot status\n• `/clearstatus` - Clear bot status\n• `/statusinfo` - Show this info", 
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
