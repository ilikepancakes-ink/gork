import discord
from discord.ext import commands
from discord import app_commands

class UserProfile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="profile", description="Displays a user's profile.")
    async def profile(self, interaction: discord.Interaction, user: discord.Member = None):
        """Displays a user's profile."""
        if user is None:
            user = interaction.user

        embed = discord.Embed(
            title=user.display_name,
            color=user.accent_color
        )
        embed.set_thumbnail(url=user.avatar.url)
        embed.add_field(name="User ID", value=user.id, inline=False)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%B %d, %Y"), inline=False)
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%B %d, %Y"), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(UserProfile(bot))