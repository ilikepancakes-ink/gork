
import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from datetime import datetime, timezone


from utils.database import MessageDatabase
from lists import config


class UserInfoCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = MessageDatabase("data/bot_messages.db") 
        self.developer_badges = {
            config.Owners.ILIKEPANCAKES: f"{config.CustomEmoji.STAFF_BLUE}OpenGuard Developer",
            config.Owners.SLIPSTREAM: f"{config.CustomEmoji.STAFF_PINK}OpenGuard Developer",
        }
        
        self.custom_data_file = "user_data.json"
        self.custom_user_data = {}

    def _truncate_field_value(self, text: str, max_length: int = 1020) -> str:
        """Truncate text to fit Discord embed field limits."""
        if len(text) > max_length:
            return text[: max_length - 3] + "..."
        return text

    def _format_time_difference(self, past_time: datetime) -> str:
        """Calculate and format the time difference from a past datetime to now."""
        now = datetime.now(timezone.utc)
        
        if past_time.tzinfo is None:
            past_time = past_time.replace(tzinfo=timezone.utc)

        diff = now - past_time

        
        total_minutes = int(diff.total_seconds() / 60)

        
        years = total_minutes // (365 * 24 * 60)
        remaining_minutes = total_minutes % (365 * 24 * 60)

        days = remaining_minutes // (24 * 60)
        remaining_minutes = remaining_minutes % (24 * 60)

        hours = remaining_minutes // 60
        minutes = remaining_minutes % 60

        
        parts = []
        if years > 0:
            parts.append(f"{years} year{'s' if years != 1 else ''}")
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")
        if hours > 0:
            parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
        if minutes > 0:
            parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

        if not parts:
            return "Less than a minute"

        return ", ".join(parts)

    async def load_custom_data(self):
        """Legacy function - now a no-op since data is loaded from database."""
        pass

    async def save_custom_data(self):
        """Legacy function - now a no-op since data is saved directly to database."""
        pass

    async def is_authorized_admin(self, ctx: commands.Context):
        return ctx.author.guild_permissions.administrator

    @commands.hybrid_command(
        name="aboutuser",
        description="Display comprehensive info about a user or yourself.",
    )
    @app_commands.describe(user="The user to get info about (optional)")
    async def aboutuser(self, ctx: commands.Context, user: Optional[discord.Member] = None):
        member = user or ctx.author
        if ctx.guild:
            member = ctx.guild.get_member(member.id) or member
        user_obj = member._user if hasattr(member, "_user") else member
        banner_url = None
        try:
            user_obj = await self.bot.fetch_user(member.id)
            if user_obj.banner:
                banner_url = user_obj.banner.url
        except Exception:
            pass
        user_data = {
            "member": member,
            "user_obj": user_obj,
            "banner_url": banner_url,
            "is_guild_member": isinstance(member, discord.Member) and ctx.guild,
            "interaction_user_id": ctx.author.id,
        }
        embed, view = await self._create_main_view(user_data)
        await ctx.reply(embed=embed, view=view)

    async def _create_main_view(self, user_data):
        member = user_data["member"]
        user_obj = user_data["user_obj"]
        banner_url = user_data["banner_url"]
        is_guild_member = user_data["is_guild_member"]
        status = "Unknown"
        device_str = "Unknown"
        if is_guild_member:
            status = str(member.status).title()
            if member.desktop_status != "offline":
                device_str = "Desktop"
            elif member.mobile_status != "offline":
                device_str = "Mobile"
            elif member.web_status != "offline":
                device_str = "Website"
        activity_str = "None"
        if member.activities:
            activity = member.activities[0]
            if isinstance(activity, discord.Game):
                activity_str = f"Playing {activity.name}"
            elif isinstance(activity, discord.Streaming):
                activity_str = f"Streaming on {activity.platform}"
            elif isinstance(activity, discord.CustomActivity):
                activity_str = f"{activity.emoji} {activity.name}"
            elif isinstance(activity, discord.Spotify):
                activity_str = f"Listening to {activity.title} by {activity.artist}"

        
        activity_str = self._truncate_field_value(activity_str)
        roles_str = "None"
        if is_guild_member and member.roles:
            roles = [role.mention for role in reversed(member.roles) if role.name != "@everyone"]
            if roles:
                roles_str = ", ".join(roles)
                
                roles_str = self._truncate_field_value(roles_str)
            else:
                roles_str = "None"
        badge_map = {
            "staff": "Discord Staff 🛡️",
            "partner": "Partner ⭐",
            "hypesquad": "HypeSquad Event 🏆",
            "bug_hunter": "Bug Hunter 🐛",
            "hypesquad_bravery": "Bravery 🦁",
            "hypesquad_brilliance": "Brilliance 🧠",
            "hypesquad_balance": "Balance ⚖️",
            "early_supporter": "Early Supporter 🕰️",
            "team_user": "Team User 👥",
            "system": "System 🤖",
            "bug_hunter_level_2": "Bug Hunter Level 2 🐞",
            "verified_bot": "Verified Bot 🤖",
            "verified_developer": "Early Verified Bot Dev 🛠️",
            "discord_certified_moderator": "Certified Mod 🛡️",
            "active_developer": "Active Developer 🧑‍💻",
        }
        user_flags = getattr(user_obj, "public_flags", None)
        badges = []
        if user_flags:
            for flag in badge_map:
                if getattr(user_flags, flag, False):
                    badges.append(badge_map[flag])
        badge_str = ", ".join(badges) if badges else ""
        developer_badge = self.developer_badges.get(member.id)
        if developer_badge:
            badge_str = (badge_str + ", " if badge_str else "") + developer_badge

        
        badge_str = self._truncate_field_value(badge_str)
        embed = discord.Embed(
            title=f"User Info: {member.display_name}",
            color=member.color if hasattr(member, "color") else discord.Color.blurple(),
            description=f"Profile of {member.mention}",
        )

        
        if banner_url:
            embed.set_image(url=banner_url)

        
        embed.set_thumbnail(url=member.display_avatar.url)

        if badge_str:
            embed.add_field(name="Badge", value=badge_str, inline=False)

        
        
        
        
        
        
        
        
        
        embed.add_field(name="Nickname", value=member.nick or "None", inline=True)
        embed.add_field(name="Username", value=f"{member.name}
        embed.add_field(name="User ID", value=member.id, inline=True)
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Device", value=device_str, inline=True)
        embed.add_field(name="Activity", value=activity_str, inline=True)
        embed.add_field(name="Roles", value=roles_str, inline=False)
        
        account_age = self._format_time_difference(member.created_at)
        account_created_text = f"{member.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n({account_age} ago)"

        embed.add_field(
            name="Account Created",
            value=account_created_text,
            inline=True,
        )
        if hasattr(member, "joined_at") and member.joined_at:
            server_join_age = self._format_time_difference(member.joined_at)
            joined_server_text = f"{member.joined_at.strftime('%Y-%m-%d %H:%M:%S UTC')}\n({server_join_age} ago)"
            embed.add_field(
                name="Joined Server",
                value=joined_server_text,
                inline=True,
            )
        embed.set_footer(
            text=f"Requested by {user_data['interaction_user_id']}",
            icon_url=self.bot.get_user(user_data["interaction_user_id"]).display_avatar.url,
        )
        view = discord.ui.View()
        view.add_item(
            discord.ui.Button(
                label="View Permissions",
                style=discord.ButtonStyle.secondary,
                custom_id=f"userinfo_permissions_{member.id}",
            )
        )
        return embed, view

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.component and interaction.data["custom_id"].startswith(
            "userinfo_"
        ):
            custom_id_parts = interaction.data["custom_id"].split("_")
            action = custom_id_parts[1]
            user_id = int(custom_id_parts[2])

            if action == "permissions":
                await self.show_permissions(interaction, user_id)

    async def show_permissions(self, interaction: discord.Interaction, user_id: int):
        if not interaction.guild:
            await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)
            return

        member = interaction.guild.get_member(user_id)
        if not member:
            await interaction.response.send_message("Could not find that member in this server.", ephemeral=True)
            return

        permissions = member.guild_permissions
        sorted_perms = sorted(list(permissions), key=lambda x: x[0])

        embed = discord.Embed(
            title=f"Permissions for {member.display_name}",
            color=member.color,
            description="✅ = Granted, ❌ = Denied",
        )

        columns = [[], [], []]
        col_char_limits = [0, 0, 0]
        max_col_chars = 900

        for perm, value in sorted_perms:
            perm_str = f"{'✅' if value else '❌'} {perm.replace('_', ' ').title()}\n"

            best_col = -1
            min_len = float("inf")
            for i in range(3):
                if col_char_limits[i] + len(perm_str) < max_col_chars:
                    if col_char_limits[i] < min_len:
                        min_len = col_char_limits[i]
                        best_col = i

            if best_col != -1:
                columns[best_col].append(perm_str)
                col_char_limits[best_col] += len(perm_str)
            else:
                shortest_col = col_char_limits.index(min(col_char_limits))
                columns[shortest_col].append(perm_str)
                col_char_limits[shortest_col] += len(perm_str)

        for i in range(3):
            if columns[i]:
                embed.add_field(name=f"Permissions {i + 1}", value="".join(columns[i]), inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(UserInfoCog(bot))
