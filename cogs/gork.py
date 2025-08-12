import os
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import json
from dotenv import load_dotenv

class Gork(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv("ai.env")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.0-flash-001"

        if not self.openrouter_api_key:
            print("Warning: OPENROUTER_API_KEY not found in environment variables")

    async def call_ai(self, messages, max_tokens=1000):
        """Make a call to OpenRouter API with the Llama model"""
        if not self.openrouter_api_key:
            return "Error: OpenRouter API key not configured"

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://discordbot.learnhelp.cc",
            "X-Title": "Nerus Discord Bot"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.openrouter_url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        return f"Error: API request failed with status {response.status}: {error_text}"
        except Exception as e:
            return f"Error: Failed to call AI API: {str(e)}"

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listen for messages that mention the bot"""
        # Don't respond to bot's own messages
        if message.author == self.bot.user:
            return

        # Check if bot is mentioned or if it's a DM (and not from a bot)
        is_dm = isinstance(message.channel, discord.DMChannel)
        is_mentioned = self.bot.user in message.mentions

        if is_mentioned or (is_dm and not message.author.bot):
            # Determine context for system message
            context_type = "DM" if is_dm else "Discord server"

            # Prepare the conversation context
            messages = [
                {
                    "role": "system",
                    "content": f"You are Gork, a helpful AI assistant on Discord. You are currently chatting in a {context_type}. You are friendly, knowledgeable, and concise in your responses. Keep responses under 2000 characters to fit Discord's message limit."
                }
            ]

            # If the message is a reply, get the replied-to message content
            replied_content = ""
            if message.reference and message.reference.message_id:
                try:
                    replied_message = await message.channel.fetch_message(message.reference.message_id)
                    replied_content = f"\n\nContext (message being replied to):\nFrom {replied_message.author.display_name}: {replied_message.content}"
                except:
                    replied_content = ""

            # Add user message
            user_content = message.content.replace(f'<@{self.bot.user.id}>', '').strip()

            # In DMs, if there's no content after removing mention, use the original message
            if is_dm and not user_content:
                user_content = message.content.strip()

            if replied_content:
                user_content += replied_content

            messages.append({
                "role": "user",
                "content": user_content
            })

            # Show typing indicator
            async with message.channel.typing():
                # Get AI response
                ai_response = await self.call_ai(messages)

                # Split response if it's too long for Discord
                if len(ai_response) > 2000:
                    # Split into chunks of 2000 characters
                    chunks = [ai_response[i:i+2000] for i in range(0, len(ai_response), 2000)]
                    for chunk in chunks:
                        await message.reply(chunk)
                else:
                    await message.reply(ai_response)

    @app_commands.command(name="gork", description="Chat with Gork AI")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def gork_command(self, interaction: discord.Interaction, message: str):
        """Slash command to chat with Gork"""
        await interaction.response.defer()

        # Determine context for system message
        is_dm = interaction.guild is None
        context_type = "DM" if is_dm else "Discord server"

        messages = [
            {
                "role": "system",
                "content": f"You are Gork, a helpful AI assistant on Discord. You are currently chatting in a {context_type}. You are friendly, knowledgeable, and concise in your responses. Keep responses under 2000 characters to fit Discord's message limit."
            },
            {
                "role": "user",
                "content": message
            }
        ]

        ai_response = await self.call_ai(messages)

        # Split response if it's too long for Discord
        if len(ai_response) > 2000:
            # Split into chunks of 2000 characters
            chunks = [ai_response[i:i+2000] for i in range(0, len(ai_response), 2000)]
            await interaction.followup.send(chunks[0])
            for chunk in chunks[1:]:
                await interaction.followup.send(chunk)
        else:
            await interaction.followup.send(ai_response)

    @app_commands.command(name="gork_status", description="Check Gork AI status")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def gork_status(self, interaction: discord.Interaction):
        """Check if Gork AI is properly configured"""
        # Determine context for usage instructions
        is_dm = interaction.guild is None
        usage_text = "Send me a message in DM or mention me in a server, or use `/gork` command" if is_dm else "Mention me in a message or use `/gork` command"

        if self.openrouter_api_key:
            embed = discord.Embed(
                title="Gork AI Status",
                description="✅ Gork AI is configured and ready!",
                color=discord.Color.green()
            )
            embed.add_field(name="Model", value=self.model, inline=False)
            embed.add_field(name="Usage", value=usage_text, inline=False)
        else:
            embed = discord.Embed(
                title="Gork AI Status",
                description="❌ Gork AI is not configured (missing API key)",
                color=discord.Color.red()
            )

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Gork(bot))