import os
import httpx
import discord
from discord.ext import commands
from typing import Optional, List, Dict, Any
from utils.database import MessageDatabase
from utils.steam_api import resolve_vanity_url as steam_resolve_vanity_url # Renamed to avoid conflict

class SteamUserTool(commands.Cog):
    def __init__(self, bot: commands.Bot, db: MessageDatabase):
        self.bot = bot
        self.db = db
        self.steam_web_api_key = os.getenv("STEAM_WEB")
        if not self.steam_web_api_key:
            print("WARNING: STEAM_WEB environment variable not set. Steam API tools may not function.")

    @commands.command(name="get_steam_id")
    async def get_steam_id(self, discord_user_id: str) -> Optional[str]:
        """
        Retrieves the linked Steam ID for a given Discord user ID.

        Args:
            discord_user_id (str): The Discord user's ID.

        Returns:
            Optional[str]: The 64-bit Steam ID as a string if linked, otherwise None.
        """
        try:
            user_settings = await self.db.get_user_settings(discord_user_id)
            return user_settings.get('steam_id')
        except Exception as e:
            print(f"❌ Error getting Steam ID for Discord user {discord_user_id}: {e}")
            return None

    @commands.command(name="get_steam_profile_summary")
    async def get_steam_profile_summary(self, discord_user_id: str) -> Optional[Dict]:
        """
        Fetches the Steam profile summary for a given Discord user ID.
        Requires the Discord user to have a linked Steam ID.

        Args:
            discord_user_id (str): The Discord user's ID.

        Returns:
            Optional[Dict]: A dictionary containing the Steam profile summary, or None if
                            the Steam ID is not linked or an error occurs.
        """
        steam_id = await self.get_steam_id(discord_user_id)
        if not steam_id:
            return None

        if not self.steam_web_api_key:
            print("STEAM_WEB API key is not set.")
            return None

        api_url = "https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
        params = {
            "key": self.steam_web_api_key,
            "steamids": steam_id
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, params=params)
                response.raise_for_status()
                data = response.json()

                players = data.get("response", {}).get("players")
                if players:
                    return players[0]
                return None
        except httpx.RequestError as e:
            print(f"❌ HTTP request error for Steam profile summary: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP status error for Steam profile summary ({e.response.status_code}): {e}")
            return None
        except Exception as e:
            print(f"❌ An unexpected error occurred while fetching Steam profile summary: {e}")
            return None

    @commands.command(name="get_user_owned_games")
    async def get_user_owned_games(self, discord_user_id: str) -> Optional[List[Dict]]:
        """
        Fetches the list of games owned by the Steam user linked to the given Discord user ID.
        Requires the Discord user to have a linked Steam ID.

        Args:
            discord_user_id (str): The Discord user's ID.

        Returns:
            Optional[List[Dict]]: A list of dictionaries, each representing an owned game,
                                  or None if the Steam ID is not linked or an error occurs.
        """
        steam_id = await self.get_steam_id(discord_user_id)
        if not steam_id:
            return None

        if not self.steam_web_api_key:
            print("STEAM_WEB API key is not set.")
            return None

        api_url = "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        params = {
            "key": self.steam_web_api_key,
            "steamid": steam_id,
            "include_appinfo": 1,
            "include_played_free_games": 1
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(api_url, params=params)
                response.raise_for_status()
                data = response.json()

                games = data.get("response", {}).get("games")
                return games if games else []
        except httpx.RequestError as e:
            print(f"❌ HTTP request error for user owned games: {e}")
            return None
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP status error for user owned games ({e.response.status_code}): {e}")
            return None
        except Exception as e:
            print(f"❌ An unexpected error occurred while fetching user owned games: {e}")
            return None

    @commands.command(name="resolve_steam_vanity_url")
    async def resolve_steam_vanity_url(self, vanity_url: str) -> Optional[str]:
        """
        Resolves a Steam custom URL (vanity URL) to a 64-bit Steam ID.

        Args:
            vanity_url (str): The Steam custom URL (vanity URL).

        Returns:
            Optional[str]: The 64-bit Steam ID as a string if successful,
                           or None if the vanity URL cannot be resolved or an error occurs.
        """
        try:
            return await steam_resolve_vanity_url(vanity_url)
        except Exception as e:
            print(f"❌ Error resolving Steam vanity URL '{vanity_url}': {e}")
            return None

async def setup(bot: commands.Bot):
    db_path = os.getenv("DB_PATH", "bot_messages.db")
    db = MessageDatabase(db_path)
    await db.initialize()
    await bot.add_cog(SteamUserTool(bot, db))