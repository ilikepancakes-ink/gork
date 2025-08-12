import os
import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import json
import base64
import asyncio
import subprocess
from dotenv import load_dotenv
import urllib.parse

class Gork(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        load_dotenv("ai.env")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY")
        self.openrouter_url = "https://openrouter.ai/api/v1/chat/completions"
        self.model = "google/gemini-2.5-flash"

        # Whitelist of safe commands that can be executed
        self.safe_commands = {
            'fastfetch': 'fastfetch --stdout',
            'whoami': 'whoami',
            'pwd': 'pwd',
            'date': 'date',
            'uptime': 'uptime',
            'uname': 'uname -a',
            'df': 'df -h',
            'free': 'free -h',
            'lscpu': 'lscpu',
            'lsb_release': 'lsb_release -a',
            'hostnamectl': 'hostnamectl',
            'systemctl_status': 'systemctl --no-pager status',
            'ps': 'ps aux',
            'top': 'top -b -n1',
            'sensors': 'sensors',
            'lsblk': 'lsblk',
            'lsusb': 'lsusb',
            'lspci': 'lspci',
            'ip_addr': 'ip addr show',
            'netstat': 'netstat -tuln',
            'ss': 'ss -tuln'
        }

        # SearchAPI.io configuration
        self.searchapi_key = os.getenv("SEARCHAPI_KEY")
        self.searchapi_url = "https://www.searchapi.io/api/v1/search"

        if not self.openrouter_api_key:
            print("Warning: OPENROUTER_API_KEY not found in environment variables")
        if not self.searchapi_key:
            print("Warning: SEARCHAPI_KEY not found. Web search functionality will be disabled.")

    async def process_files(self, message):
        """Process files and images from a Discord message and return them in the format expected by the AI API"""
        content_parts = []

        # Define supported text file extensions
        text_extensions = {'.txt', '.py', '.js', '.html', '.css', '.json', '.xml', '.md', '.yml', '.yaml',
                          '.csv', '.sql', '.php', '.java', '.cpp', '.c', '.h', '.cs', '.rb', '.go',
                          '.rs', '.ts', '.jsx', '.tsx', '.vue', '.svelte', '.sh', '.bat', '.ps1',
                          '.dockerfile', '.gitignore', '.env', '.ini', '.cfg', '.conf', '.log'}

        # Define supported binary file extensions for analysis
        binary_extensions = {'.bin'}

        # Check for attachments
        for attachment in message.attachments:
            try:
                # Handle images
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    # Download the image
                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as response:
                            if response.status == 200:
                                image_data = await response.read()
                                # Convert to base64
                                base64_image = base64.b64encode(image_data).decode('utf-8')

                                # Add to content array in the format expected by OpenAI-compatible APIs
                                content_parts.append({
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:{attachment.content_type};base64,{base64_image}"
                                    }
                                })

                # Handle text files
                elif any(attachment.filename.lower().endswith(ext) for ext in text_extensions):
                    # Download the text file
                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as response:
                            if response.status == 200:
                                # Try to decode as text
                                try:
                                    file_content = await response.text(encoding='utf-8')
                                    # Limit file size to prevent overwhelming the AI
                                    if len(file_content) > 10000:  # 10KB limit
                                        file_content = file_content[:10000] + "\n... (file truncated due to size)"

                                    content_parts.append({
                                        "type": "text",
                                        "text": f"File: {attachment.filename}\n```\n{file_content}\n```"
                                    })
                                except UnicodeDecodeError:
                                    # If it can't be decoded as text, skip it
                                    content_parts.append({
                                        "type": "text",
                                        "text": f"File: {attachment.filename} (binary file - cannot display content)"
                                    })

                # Handle binary files (.bin)
                elif any(attachment.filename.lower().endswith(ext) for ext in binary_extensions):
                    # Download the binary file for analysis
                    async with aiohttp.ClientSession() as session:
                        async with session.get(attachment.url) as response:
                            if response.status == 200:
                                binary_data = await response.read()
                                file_size = len(binary_data)

                                # Provide basic file information and hex preview
                                hex_preview = ""
                                if file_size > 0:
                                    # Show first 256 bytes as hex
                                    preview_bytes = binary_data[:256]
                                    hex_preview = " ".join(f"{b:02x}" for b in preview_bytes)
                                    if file_size > 256:
                                        hex_preview += " ... (truncated)"

                                content_parts.append({
                                    "type": "text",
                                    "text": f"Binary File: {attachment.filename}\n"
                                           f"Size: {file_size} bytes\n"
                                           f"Hex Preview (first 256 bytes):\n```\n{hex_preview}\n```\n"
                                           f"Note: This is a binary file. I can analyze its structure, size, and hex data."
                                })

            except Exception as e:
                print(f"Error processing attachment {attachment.filename}: {e}")

        # Check for embeds with images (like from other bots or links)
        for embed in message.embeds:
            if embed.image and embed.image.url:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(embed.image.url) as response:
                            if response.status == 200:
                                content_type = response.headers.get('content-type', 'image/png')
                                if content_type.startswith('image/'):
                                    image_data = await response.read()
                                    base64_image = base64.b64encode(image_data).decode('utf-8')

                                    content_parts.append({
                                        "type": "image_url",
                                        "image_url": {
                                            "url": f"data:{content_type};base64,{base64_image}"
                                        }
                                    })
                except Exception as e:
                    print(f"Error processing embed image: {e}")

        return content_parts

    async def execute_safe_command(self, command_name: str) -> str:
        """Execute a safe command and return its output"""
        if command_name not in self.safe_commands:
            return f"❌ Command '{command_name}' is not in the safe commands list. Available commands: {', '.join(self.safe_commands.keys())}"

        command = self.safe_commands[command_name]

        try:
            # Execute the command with a timeout
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )

            # Wait for the command to complete with a 30-second timeout
            try:
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=30.0)
            except asyncio.TimeoutError:
                process.kill()
                return f"❌ Command '{command_name}' timed out after 30 seconds"

            # Decode the output
            output = stdout.decode('utf-8', errors='replace').strip()
            error = stderr.decode('utf-8', errors='replace').strip()

            if process.returncode != 0:
                return f"❌ Command '{command_name}' failed with exit code {process.returncode}:\n```\n{error or 'No error message'}\n```"

            if not output and error:
                output = error

            if not output:
                return f"✅ Command '{command_name}' executed successfully but produced no output"

            # For fastfetch, return raw output for AI to summarize
            if command_name == 'fastfetch':
                return output

            # For other commands, limit output length to prevent Discord message limits
            if len(output) > 1800:
                output = output[:1800] + "\n... (output truncated)"

            return f"✅ Command '{command_name}' output:\n```\n{output}\n```"

        except Exception as e:
            return f"❌ Error executing command '{command_name}': {str(e)}"

    async def web_search(self, query: str, num_results: int = 5) -> str:
        """Perform a web search using SearchAPI.io and return formatted results"""
        if not self.searchapi_key:
            return "❌ Web Search is not configured. Please set SEARCHAPI_KEY environment variable."

        try:
            # Prepare search parameters for SearchAPI.io
            params = {
                'api_key': self.searchapi_key,
                'q': query,
                'engine': 'google',
                'num': min(num_results, 10)  # Limit to 10 results max
            }

            async with aiohttp.ClientSession() as session:
                async with session.get(self.searchapi_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()

                        # Check if we have organic results
                        organic_results = data.get('organic_results', [])
                        if not organic_results:
                            return f"🔍 No search results found for: {query}"

                        # Format search results
                        results = []
                        for i, item in enumerate(organic_results[:num_results], 1):
                            title = item.get('title', 'No title')
                            link = item.get('link', '')
                            snippet = item.get('snippet', 'No description available')

                            # Truncate snippet if too long
                            if len(snippet) > 150:
                                snippet = snippet[:150] + "..."

                            results.append(f"**{i}. {title}**\n{snippet}\n🔗 {link}")

                        # Get search information
                        search_info = data.get('search_information', {})
                        total_results = search_info.get('total_results', 'Unknown')
                        search_time = search_info.get('time_taken_displayed', 'Unknown')

                        formatted_results = f"🔍 **Web Search Results for:** {query}\n"
                        formatted_results += f"📊 Found {total_results} results in {search_time}\n\n"
                        formatted_results += "\n\n".join(results)

                        return formatted_results

                    else:
                        error_text = await response.text()
                        return f"❌ SearchAPI.io error (status {response.status}): {error_text}"

        except Exception as e:
            return f"❌ Error performing web search: {str(e)}"

    async def call_ai(self, messages, max_tokens=1000):
        """Make a call to OpenRouter API with the Llama model"""
        if not self.openrouter_api_key:
            return "Error: OpenRouter API key not configured"

        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://discordbot.learnhelp.cc",
            "X-Title": "Gork"
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
            safe_commands_list = ', '.join(self.safe_commands.keys())
            web_search_status = "enabled" if self.searchapi_key else "disabled"

            system_content = f"You are Gork, a helpful AI assistant on Discord. You are currently chatting in a {context_type}. You are friendly, knowledgeable, and concise in your responses. You can see and analyze images, and read and analyze text files (including .txt, .py, .js, .html, .css, .json, .md, and many other file types) that users send. \n\nYou can also execute safe system commands to gather server information. When a user asks for system information, you can use the following format to execute commands:\n\n**EXECUTE_COMMAND:** command_name\n\nAvailable safe commands: {safe_commands_list}\n\nFor example, if someone asks about system info, you can respond with:\n**EXECUTE_COMMAND:** fastfetch\n\nWhen you execute fastfetch, analyze and summarize the output in a user-friendly way, highlighting key system information like OS, CPU, memory, etc. Don't just show the raw output - provide a nice summary."

            if web_search_status == "enabled":
                system_content += f"\n\nYou can also perform web searches when users ask for information that requires current/real-time data or information you don't have. Use this format:\n\n**WEB_SEARCH:** search query\n\nFor example, if someone asks 'What's the weather in New York?' you can respond with:\n**WEB_SEARCH:** weather New York today\n\nOr if they ask about current events, news, stock prices, or recent information, use web search to find up-to-date information."

            system_content += "\n\nKeep responses under 2000 characters to fit Discord's message limit."

            messages = [
                {
                    "role": "system",
                    "content": system_content
                }
            ]

            # If the message is a reply, get the replied-to message content and files
            replied_content = ""
            replied_files = []
            if message.reference and message.reference.message_id:
                try:
                    replied_message = await message.channel.fetch_message(message.reference.message_id)
                    replied_content = f"\n\nContext (message being replied to):\nFrom {replied_message.author.display_name}: {replied_message.content}"
                    # Also get files from the replied message
                    replied_files = await self.process_files(replied_message)
                except:
                    replied_content = ""
                    replied_files = []

            # Add user message
            user_content = message.content.replace(f'<@{self.bot.user.id}>', '').strip()

            # In DMs, if there's no content after removing mention, use the original message
            if is_dm and not user_content:
                user_content = message.content.strip()

            if replied_content:
                user_content += replied_content

            # Process files and images from the message
            file_contents = await self.process_files(message)

            # Combine current message files with replied message files
            all_files = file_contents + replied_files

            # Create the user message content
            if all_files:
                # If there are files/images, create a content array with text and files
                content_parts = []

                # Add text content if it exists
                if user_content:
                    content_parts.append({
                        "type": "text",
                        "text": user_content
                    })
                else:
                    # If no text but there are files, add a default prompt
                    content_parts.append({
                        "type": "text",
                        "text": "Please analyze the attached files/images."
                    })

                # Add all file contents (from current message and replied message)
                content_parts.extend(all_files)

                messages.append({
                    "role": "user",
                    "content": content_parts
                })
            else:
                # No files/images, just text content
                messages.append({
                    "role": "user",
                    "content": user_content
                })

            # Show typing indicator
            async with message.channel.typing():
                # Get AI response
                ai_response = await self.call_ai(messages)

                # Check if the AI wants to execute a command or perform a Google search
                if "**EXECUTE_COMMAND:**" in ai_response:
                    # Extract command from response
                    lines = ai_response.split('\n')
                    command_line = None
                    for line in lines:
                        if "**EXECUTE_COMMAND:**" in line:
                            command_line = line
                            break

                    if command_line:
                        # Extract command name
                        command_name = command_line.split("**EXECUTE_COMMAND:**")[1].strip()

                        # Execute the command
                        command_output = await self.execute_safe_command(command_name)

                        # If it's fastfetch, ask AI to summarize the output
                        if command_name == 'fastfetch' and not command_output.startswith('❌'):
                            # Create a new message to ask AI to summarize fastfetch output
                            summary_messages = [
                                {
                                    "role": "system",
                                    "content": "You are Gork, a helpful AI assistant. Analyze the following fastfetch output and provide a concise, user-friendly summary of the system information. Highlight key details like OS, CPU, memory, storage, etc. Format it nicely for Discord."
                                },
                                {
                                    "role": "user",
                                    "content": f"Please summarize this fastfetch output:\n\n{command_output}"
                                }
                            ]

                            # Get AI summary
                            summary_response = await self.call_ai(summary_messages, max_tokens=800)
                            ai_response = ai_response.replace(command_line, summary_response)
                        else:
                            # Replace the command instruction with the output
                            ai_response = ai_response.replace(command_line, command_output)

                elif "**WEB_SEARCH:**" in ai_response:
                    # Extract search query from response
                    lines = ai_response.split('\n')
                    search_line = None
                    for line in lines:
                        if "**WEB_SEARCH:**" in line:
                            search_line = line
                            break

                    if search_line:
                        # Extract search query
                        search_query = search_line.split("**WEB_SEARCH:**")[1].strip()

                        # Perform web search
                        search_results = await self.web_search(search_query)

                        # Replace the search instruction with the results
                        ai_response = ai_response.replace(search_line, search_results)

                # Split response if it's too long for Discord
                if len(ai_response) > 2000:
                    # Split into chunks of 2000 characters
                    chunks = [ai_response[i:i+2000] for i in range(0, len(ai_response), 2000)]
                    for chunk in chunks:
                        await message.reply(chunk)
                else:
                    await message.reply(ai_response)

    @app_commands.command(name="gork", description="Chat with Gork AI (for files/images, mention me in a message with attachments)")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def gork_command(self, interaction: discord.Interaction, message: str):
        """Slash command to chat with Gork"""
        await interaction.response.defer()

        # Determine context for system message
        is_dm = interaction.guild is None
        context_type = "DM" if is_dm else "Discord server"

        safe_commands_list = ', '.join(self.safe_commands.keys())
        web_search_status = "enabled" if self.searchapi_key else "disabled"

        system_content = f"You are Gork, a helpful AI assistant on Discord. You are currently chatting in a {context_type}. You are friendly, knowledgeable, and concise in your responses. You can see and analyze images, and read and analyze text files (including .txt, .py, .js, .html, .css, .json, .md, and many other file types) that users send. \n\nYou can also execute safe system commands to gather server information. When a user asks for system information, you can use the following format to execute commands:\n\n**EXECUTE_COMMAND:** command_name\n\nAvailable safe commands: {safe_commands_list}\n\nFor example, if someone asks about system info, you can respond with:\n**EXECUTE_COMMAND:** fastfetch\n\nWhen you execute fastfetch, analyze and summarize the output in a user-friendly way, highlighting key system information like OS, CPU, memory, etc. Don't just show the raw output - provide a nice summary."

        if web_search_status == "enabled":
            system_content += f"\n\nYou can also perform web searches when users ask for information that requires current/real-time data or information you don't have. Use this format:\n\n**WEB_SEARCH:** search query\n\nFor example, if someone asks 'What's the weather in New York?' you can respond with:\n**WEB_SEARCH:** weather New York today\n\nOr if they ask about current events, news, stock prices, or recent information, use web search to find up-to-date information."

        system_content += "\n\nKeep responses under 2000 characters to fit Discord's message limit."

        messages = [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": message
            }
        ]

        ai_response = await self.call_ai(messages)

        # Check if the AI wants to execute a command or perform a Google search
        if "**EXECUTE_COMMAND:**" in ai_response:
            # Extract command from response
            lines = ai_response.split('\n')
            command_line = None
            for line in lines:
                if "**EXECUTE_COMMAND:**" in line:
                    command_line = line
                    break

            if command_line:
                # Extract command name
                command_name = command_line.split("**EXECUTE_COMMAND:**")[1].strip()

                # Execute the command
                command_output = await self.execute_safe_command(command_name)

                # If it's fastfetch, ask AI to summarize the output
                if command_name == 'fastfetch' and not command_output.startswith('❌'):
                    # Create a new message to ask AI to summarize fastfetch output
                    summary_messages = [
                        {
                            "role": "system",
                            "content": "You are Gork, a helpful AI assistant. Analyze the following fastfetch output and provide a concise, user-friendly summary of the system information. Highlight key details like OS, CPU, memory, storage, etc. Format it nicely for Discord."
                        },
                        {
                            "role": "user",
                            "content": f"Please summarize this fastfetch output:\n\n{command_output}"
                        }
                    ]

                    # Get AI summary
                    summary_response = await self.call_ai(summary_messages, max_tokens=800)
                    ai_response = ai_response.replace(command_line, summary_response)
                else:
                    # Replace the command instruction with the output
                    ai_response = ai_response.replace(command_line, command_output)

        elif "**WEB_SEARCH:**" in ai_response:
            # Extract search query from response
            lines = ai_response.split('\n')
            search_line = None
            for line in lines:
                if "**WEB_SEARCH:**" in line:
                    search_line = line
                    break

            if search_line:
                # Extract search query
                search_query = search_line.split("**WEB_SEARCH:**")[1].strip()

                # Perform web search
                search_results = await self.web_search(search_query)

                # Replace the search instruction with the results
                ai_response = ai_response.replace(search_line, search_results)

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
        usage_text = "Send me a message in DM (with optional files/images) or mention me in a server, or use `/gork` command" if is_dm else "Mention me in a message (with optional files/images) or use `/gork` command"

        if self.openrouter_api_key:
            embed = discord.Embed(
                title="Gork AI Status",
                description="✅ Gork AI is configured and ready!",
                color=discord.Color.green()
            )
            embed.add_field(name="Model", value=self.model, inline=False)

            # Check web search status
            web_search_status = "✅ Web Search (SearchAPI.io)" if self.searchapi_key else "❌ Web Search (not configured)"

            capabilities = f"✅ Text chat\n✅ Image analysis\n✅ File reading (.txt, .py, .js, .html, .css, .json, .md, etc.)\n✅ Binary file analysis (.bin)\n✅ Safe system command execution\n{web_search_status}"
            embed.add_field(name="Capabilities", value=capabilities, inline=False)
            embed.add_field(name="Safe Commands", value=f"Available: {', '.join(list(self.safe_commands.keys())[:10])}{'...' if len(self.safe_commands) > 10 else ''}", inline=False)
            embed.add_field(name="Usage", value=usage_text, inline=False)
        else:
            embed = discord.Embed(
                title="Gork AI Status",
                description="❌ Gork AI is not configured (missing API key)",
                color=discord.Color.red()
            )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="gork_commands", description="List all available safe commands for system information")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def gork_commands(self, interaction: discord.Interaction):
        """List all available safe commands"""
        embed = discord.Embed(
            title="🔧 Gork Safe Commands",
            description="These commands can be executed by Gork to gather system information:",
            color=discord.Color.blue()
        )

        # Group commands by category
        system_info = ['fastfetch', 'whoami', 'pwd', 'date', 'uptime', 'uname', 'lsb_release', 'hostnamectl']
        hardware_info = ['lscpu', 'sensors', 'lsblk', 'lsusb', 'lspci', 'free', 'df']
        process_info = ['ps', 'top', 'systemctl_status']
        network_info = ['ip_addr', 'netstat', 'ss']

        embed.add_field(name="🖥️ System Info", value=', '.join(system_info), inline=False)
        embed.add_field(name="⚙️ Hardware Info", value=', '.join(hardware_info), inline=False)
        embed.add_field(name="📊 Process Info", value=', '.join(process_info), inline=False)
        embed.add_field(name="🌐 Network Info", value=', '.join(network_info), inline=False)

        embed.add_field(
            name="💡 How to use",
            value="Just ask Gork for system information! For example:\n• 'Show me system info'\n• 'What's the CPU usage?'\n• 'Display network connections'\n\nGork will automatically choose and execute the appropriate command.",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Gork(bot))