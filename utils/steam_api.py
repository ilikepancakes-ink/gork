import os
import httpx
from typing import Optional

async def resolve_vanity_url(vanity_url: str) -> Optional[str]:
    """
    Resolves a Steam custom URL (vanity URL) to a 64-bit Steam ID.

    Args:
        vanity_url (str): The Steam custom URL (vanity URL).

    Returns:
        Optional[str]: The 64-bit Steam ID as a string if successful,
                       or None if the vanity URL cannot be resolved or an error occurs.
    """
    steam_web_api_key = os.getenv("STEAM_WEB")
    if not steam_web_api_key:
        print("STEAM_WEB environment variable not set.")
        return None

    api_url = "https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
    params = {
        "key": steam_web_api_key,
        "vanityurl": vanity_url
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            data = response.json()

            if data and data.get("response", {}).get("success") == 1:
                steam_id = str(data["response"]["steamid"])
                return steam_id
            else:
                print(f"Failed to resolve vanity URL '{vanity_url}': {data.get('response', {}).get('message', 'Unknown error')}")
                return None
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}: {e}")
        return None
    except httpx.HTTPStatusError as e:
        print(f"Error response {e.response.status_code} while requesting {e.request.url!r}: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
