import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
import os
from utils.database import MessageDatabase
from utils.steam_api import resolve_vanity_url

class UserSettings(commands.Cog):
    """Cog for managing user-specific settings including NSFW mode"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = MessageDatabase("data/bot_messages.db")
    
    @app_commands.command(name="nsfw_mode", description="Enable or disable NSFW content mode")
    @app_commands.describe(
        enabled="Enable (True) or disable (False) NSFW content mode"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def nsfw_mode(self, interaction: discord.Interaction, enabled: bool):
        """Toggle NSFW mode for the user"""
        
        user_id = str(interaction.user.id)
        username = interaction.user.name
        user_display_name = interaction.user.display_name
        
        # Update user settings
        success = await self.db.update_user_settings(
            user_id=user_id,
            username=username,
            user_display_name=user_display_name,
            nsfw_mode=enabled
        )
        
        if success:
            status = "enabled" if enabled else "disabled"
            color = discord.Color.orange() if enabled else discord.Color.green()
            
            embed = discord.Embed(
                title="🔞 NSFW Mode Updated" if enabled else "✅ NSFW Mode Updated",
                description=f"NSFW content mode has been **{status}** for your account.",
                color=color
            )
            
            if enabled:
                embed.add_field(
                    name="⚠️ Important Notice",
                    value="• NSFW mode allows the AI to discuss mature content\n"
                          "• This setting is per-user and private\n"
                          "• You can disable this at any time\n"
                          "• Use responsibly and follow Discord's Terms of Service",
                    inline=False
                )
            else:
                embed.add_field(
                    name="ℹ️ Content Filtering",
                    value="• NSFW content will be filtered\n"
                          "• The AI will maintain appropriate responses\n"
                          "• You can re-enable NSFW mode anytime",
                    inline=False
                )
            
            embed.set_footer(text="Use /my_settings to view all your current settings")
            
        else:
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to update NSFW mode settings. Please try again later.",
                color=discord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="content_filter", description="Set content filtering level")
    @app_commands.describe(
        level="Content filtering level: strict, moderate, or minimal"
    )
    @app_commands.choices(level=[
        app_commands.Choice(name="Strict (Default)", value="strict"),
        app_commands.Choice(name="Moderate", value="moderate"),
        app_commands.Choice(name="Minimal (NSFW Mode Required)", value="minimal")
    ])
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def content_filter(self, interaction: discord.Interaction, level: str):
        """Set content filtering level"""
        
        user_id = str(interaction.user.id)
        username = interaction.user.name
        user_display_name = interaction.user.display_name
        
        # Check if user is trying to set minimal filter without NSFW mode
        if level == "minimal":
            current_settings = await self.db.get_user_settings(user_id)
            if not current_settings.get('nsfw_mode', False):
                embed = discord.Embed(
                    title="❌ NSFW Mode Required",
                    description="You must enable NSFW mode before setting content filter to 'minimal'.\n\n"
                               "Use `/nsfw_mode enabled:True` first, then try again.",
                    color=discord.Color.red()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                return
        
        # Update user settings
        success = await self.db.update_user_settings(
            user_id=user_id,
            username=username,
            user_display_name=user_display_name,
            content_filter_level=level
        )
        
        if success:
            level_descriptions = {
                "strict": "Maximum content filtering - blocks all potentially inappropriate content",
                "moderate": "Balanced filtering - allows some mature topics with appropriate context",
                "minimal": "Minimal filtering - allows NSFW content (requires NSFW mode)"
            }
            
            embed = discord.Embed(
                title="🛡️ Content Filter Updated",
                description=f"Content filtering level set to **{level.title()}**",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="Filter Description",
                value=level_descriptions[level],
                inline=False
            )
            
            if level == "minimal":
                embed.add_field(
                    name="⚠️ Reminder",
                    value="Minimal filtering is active. Please use responsibly.",
                    inline=False
                )
            
            embed.set_footer(text="Use /my_settings to view all your current settings")
            
        else:
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to update content filter settings. Please try again later.",
                color=discord.Color.red()
            )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="my_settings", description="View your current user settings")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def my_settings(self, interaction: discord.Interaction):
        """Display current user settings"""
        
        user_id = str(interaction.user.id)
        settings = await self.db.get_user_settings(user_id)
        
        nsfw_status = "🔞 Enabled" if settings.get('nsfw_mode', False) else "✅ Disabled"
        filter_level = settings.get('content_filter_level', 'strict').title()
        
        embed = discord.Embed(
            title="⚙️ Your Settings",
            description=f"Current settings for {interaction.user.display_name}",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="NSFW Mode",
            value=nsfw_status,
            inline=True
        )
        
        embed.add_field(
            name="Content Filter",
            value=f"🛡️ {filter_level}",
            inline=True
        )
        
        embed.add_field(
            name="Last Updated",
            value=f"<t:{int(discord.utils.parse_time(settings.get('updated_at', settings.get('created_at', '2024-01-01T00:00:00'))).timestamp())}:R>",
            inline=True
        )
        
        embed.add_field(
            name="Available Commands",
            value="• `/nsfw_mode` - Toggle NSFW content\n"
                  "• `/content_filter` - Set filtering level\n"
                  "• `/my_settings` - View current settings",
            inline=False
        )
        
        if settings.get('nsfw_mode', False):
            embed.add_field(
                name="⚠️ NSFW Mode Active",
                value="NSFW content is enabled for your account. Use responsibly.",
                inline=False
            )
        
        embed.set_footer(text="All settings are private and user-specific")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="nsfw_stats", description="View NSFW mode statistics (Bot owner only)")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def nsfw_stats(self, interaction: discord.Interaction):
        """Display NSFW mode statistics for bot owners"""

        # Check if user is bot owner (you can modify this check as needed)
        if interaction.user.id != 1141746562922459136:  # Replace with your bot owner ID
            embed = discord.Embed(
                title="❌ Access Denied",
                description="This command is only available to bot owners.",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        try:
            # Get users with NSFW enabled
            nsfw_users = await self.db.get_users_with_nsfw_enabled()

            embed = discord.Embed(
                title="📊 NSFW Mode Statistics",
                description="Current NSFW mode usage statistics",
                color=discord.Color.blue()
            )

            embed.add_field(
                name="🔞 NSFW Mode Enabled",
                value=f"**{len(nsfw_users)}** users",
                inline=True
            )

            if nsfw_users:
                # Count by filter level
                filter_counts = {}
                for user in nsfw_users:
                    level = user.get('content_filter_level', 'strict')
                    filter_counts[level] = filter_counts.get(level, 0) + 1

                filter_text = []
                for level, count in filter_counts.items():
                    filter_text.append(f"• {level.title()}: {count}")

                embed.add_field(
                    name="🛡️ Filter Levels",
                    value="\n".join(filter_text) if filter_text else "None",
                    inline=True
                )

                # Show recent activity
                recent_users = [user for user in nsfw_users[:5]]
                if recent_users:
                    recent_text = []
                    for user in recent_users:
                        username = user.get('username', 'Unknown')
                        level = user.get('content_filter_level', 'strict')
                        recent_text.append(f"• {username} ({level})")

                    embed.add_field(
                        name="📋 Recent NSFW Users",
                        value="\n".join(recent_text),
                        inline=False
                    )

            embed.add_field(
                name="ℹ️ Note",
                value="All user data is private and secure. This information is for administrative purposes only.",
                inline=False
            )

            embed.set_footer(text="Use the web admin interface for detailed user management")

        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to retrieve NSFW statistics: {str(e)}",
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="link_steam", description="Link your Steam account to your Discord profile")
    @app_commands.describe(
        customurl="Your Steam custom URL (e.g., 'gabelogannewell')",
        steam_id="Your 64-bit Steam ID (e.g., '76561198000000000')"
    )
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def link_steam(self, interaction: discord.Interaction, customurl: Optional[str] = None, steam_id: Optional[str] = None):
        """Link a Steam account to the user's Discord profile."""
        
        user_id = str(interaction.user.id)
        username = interaction.user.name
        user_display_name = interaction.user.display_name

        await interaction.response.defer(ephemeral=True)

        resolved_steam_id = None
        steam_username = None

        try:
            if customurl:
                await interaction.followup.send(f"Resolving Steam custom URL: `{customurl}`...", ephemeral=True)
                resolved_steam_id = await resolve_vanity_url(customurl)
                if not resolved_steam_id:
                    embed = discord.Embed(
                        title="❌ Steam Link Failed",
                        description=f"Could not resolve custom URL `{customurl}`. Please check the URL and try again, or use your 64-bit Steam ID directly.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                else:
                    await interaction.followup.send(f"Custom URL resolved to Steam ID: `{resolved_steam_id}`", ephemeral=True)
                    # For vanity URLs, we don't get a username directly, so we'll use a placeholder or fetch later if needed.
                    # For now, we'll just store the ID.
                    steam_username = customurl # Use customURL as a temporary username for display if needed
            elif steam_id:
                if not steam_id.isdigit() or len(steam_id) != 17:
                    embed = discord.Embed(
                        title="❌ Invalid Steam ID",
                        description="A 64-bit Steam ID must be a 17-digit number. Please check your input.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return
                resolved_steam_id = steam_id
                # No username from raw Steam ID, can fetch later if needed.
                steam_username = f"SteamID:{steam_id}" # Placeholder
            else:
                embed = discord.Embed(
                    title="ℹ️ Missing Input",
                    description="Please provide either a `customURL` or a `steam_id` to link your Steam account.",
                    color=discord.Color.blue()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            if resolved_steam_id:
                # Validate the Steam ID against existing links
                validation_result = await self.db.validate_steam_id_link(resolved_steam_id, user_id)
                if not validation_result['valid']:
                    embed = discord.Embed(
                        title="❌ Steam Link Failed",
                        description=validation_result['error'],
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    return

                # Update user settings with the Steam ID
                success = await self.db.update_user_settings(
                    user_id=user_id,
                    username=username,
                    user_display_name=user_display_name,
                    steam_id=resolved_steam_id,
                    steam_username=steam_username # Store the resolved username or placeholder
                )

                if success:
                    embed = discord.Embed(
                        title="✅ Steam Account Linked!",
                        description=f"Your Steam account (`{resolved_steam_id}`) has been successfully linked to your Discord profile.",
                        color=discord.Color.green()
                    )
                    embed.set_footer(text="You can view your linked Steam ID with /my_settings")
                    await interaction.followup.send(embed=embed, ephemeral=True)
                else:
                    embed = discord.Embed(
                        title="❌ Steam Link Failed",
                        description="Failed to link Steam account due to a database error. Please try again later.",
                        color=discord.Color.red()
                    )
                    await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embed = discord.Embed(
                    title="❌ Steam Link Failed",
                    description="Could not determine a valid Steam ID from your input. Please ensure your custom URL is correct or provide a valid 64-bit Steam ID.",
                    color=discord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            print(f"Error linking Steam account for user {user_id}: {e}")
            embed = discord.Embed(
                title="❌ An Unexpected Error Occurred",
                description="An error occurred while trying to link your Steam account. Please try again later.",
                color=discord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(UserSettings(bot))
