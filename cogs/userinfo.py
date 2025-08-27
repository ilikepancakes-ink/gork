from discord.ext import commands
import discord
from datetime import datetime

class UserInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(description="Get information about a user.")
    async def userinfo(self, ctx, user: discord.Member = None):
        """Get information about a user."""
        if user is None:
            user = ctx.author

        embed = discord.Embed(title=f"{user.name}'s Information", color=discord.Color.blue())
        embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
        embed.add_field(name="User ID", value=user.id, inline=False)
        embed.add_field(name="Username", value=user.name, inline=True)
        embed.add_field(name="Nickname", value=user.nick if user.nick else "None", inline=True)
        embed.add_field(name="Joined Server", value=user.joined_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        embed.add_field(name="Account Created", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"), inline=False)
        
        roles = [role.mention for role in user.roles if role.name != "@everyone"]
        if roles:
            embed.add_field(name="Roles", value=" ".join(roles), inline=False)
        else:
            embed.add_field(name="Roles", value="No roles", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(UserInfo(bot))