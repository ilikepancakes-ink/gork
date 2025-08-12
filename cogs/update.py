import os
import discord
from discord.ext import commands
from discord import app_commands
import subprocess
import asyncio
import sys
from typing import Optional

class Update(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.repo_url = "https://github.com/ilikepancakes-ink/gork.git"
        
    async def run_command(self, command: str, cwd: Optional[str] = None) -> tuple[str, str, int]:
        """Run a shell command asynchronously and return stdout, stderr, and return code"""
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            stdout, stderr = await process.communicate()
            return stdout.decode(), stderr.decode(), process.returncode
        except Exception as e:
            return "", str(e), 1

    async def git_pull(self) -> tuple[bool, str]:
        """Pull latest changes from the git repository"""
        try:
            # Check if we're in a git repository
            stdout, stderr, code = await self.run_command("git status")
            if code != 0:
                return False, "Not in a git repository or git not available"
            
            # Add remote if it doesn't exist
            stdout, stderr, code = await self.run_command("git remote get-url origin")
            if code != 0:
                # Add the remote
                stdout, stderr, code = await self.run_command(f"git remote add origin {self.repo_url}")
                if code != 0:
                    return False, f"Failed to add remote: {stderr}"
            
            # Fetch latest changes
            stdout, stderr, code = await self.run_command("git fetch origin")
            if code != 0:
                return False, f"Failed to fetch: {stderr}"
            
            # Pull changes
            stdout, stderr, code = await self.run_command("git pull origin main")
            if code != 0:
                return False, f"Failed to pull: {stderr}"
            
            return True, stdout
            
        except Exception as e:
            return False, f"Git operation failed: {str(e)}"

    async def reload_cogs(self) -> tuple[bool, str]:
        """Reload all cogs"""
        try:
            results = []
            failed_cogs = []
            
            # Get list of loaded cogs
            loaded_cogs = list(self.bot.cogs.keys())
            
            for cog_name in loaded_cogs:
                try:
                    # Skip reloading the update cog itself to avoid issues
                    if cog_name.lower() == 'update':
                        continue
                        
                    # Find the extension name (assuming cogs are in cogs/ directory)
                    extension_name = f"cogs.{cog_name.lower()}"
                    
                    # Reload the extension
                    await self.bot.reload_extension(extension_name)
                    results.append(f"✅ Reloaded {cog_name}")
                    
                except Exception as e:
                    failed_cogs.append(f"❌ Failed to reload {cog_name}: {str(e)}")
            
            # Try to load any new cogs that might have been added
            cogs_dir = "cogs"
            if os.path.exists(cogs_dir):
                for filename in os.listdir(cogs_dir):
                    if filename.endswith('.py') and not filename.startswith('__'):
                        cog_name = filename[:-3]  # Remove .py extension
                        extension_name = f"cogs.{cog_name}"
                        
                        # Skip if already loaded or if it's the update cog
                        if cog_name.lower() == 'update' or cog_name.title() in loaded_cogs:
                            continue
                            
                        try:
                            await self.bot.load_extension(extension_name)
                            results.append(f"✅ Loaded new cog: {cog_name}")
                        except Exception as e:
                            failed_cogs.append(f"❌ Failed to load new cog {cog_name}: {str(e)}")
            
            # Sync slash commands
            try:
                await self.bot.tree.sync()
                results.append("✅ Synced slash commands")
            except Exception as e:
                failed_cogs.append(f"❌ Failed to sync commands: {str(e)}")
            
            success_msg = "\n".join(results) if results else "No cogs to reload"
            error_msg = "\n".join(failed_cogs) if failed_cogs else ""
            
            full_msg = success_msg
            if error_msg:
                full_msg += f"\n\n**Errors:**\n{error_msg}"
            
            return len(failed_cogs) == 0, full_msg
            
        except Exception as e:
            return False, f"Reload operation failed: {str(e)}"

    @app_commands.command(name="debug", description="Debug commands for bot maintenance")
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.describe(action="Action to perform: update")
    async def debug(self, interaction: discord.Interaction, action: str):
        """Debug command for bot maintenance"""
        
        # Check if user has administrator permissions or if it's the bot owner in DMs
        if interaction.guild:
            # In a guild, check for administrator permissions
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message("❌ You need administrator permissions to use debug commands.", ephemeral=True)
                return
        else:
            # In DMs, only allow bot owners (you can modify this logic as needed)
            # For now, let's check if the user is in the bot's application owners
            app_info = await self.bot.application_info()
            if app_info.owner and interaction.user.id != app_info.owner.id:
                # Also check if it's a team and user is a team member
                if not (app_info.team and any(member.id == interaction.user.id for member in app_info.team.members)):
                    await interaction.response.send_message("❌ This command can only be used by the bot owner in DMs.", ephemeral=True)
                    return
        
        if action.lower() != "update":
            await interaction.response.send_message("❌ Invalid action. Use `update` to pull from git and reload cogs.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        embed = discord.Embed(
            title="🔄 Debug Update",
            description="Starting update process...",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed)
        
        # Step 1: Git pull
        embed.add_field(name="📥 Git Pull", value="Pulling latest changes...", inline=False)
        await interaction.edit_original_response(embed=embed)
        
        git_success, git_message = await self.git_pull()
        
        if git_success:
            embed.set_field_at(0, name="📥 Git Pull", value=f"✅ Success\n```\n{git_message[:500]}{'...' if len(git_message) > 500 else ''}\n```", inline=False)
        else:
            embed.set_field_at(0, name="📥 Git Pull", value=f"❌ Failed\n```\n{git_message[:500]}{'...' if len(git_message) > 500 else ''}\n```", inline=False)
            embed.color = discord.Color.red()
            await interaction.edit_original_response(embed=embed)
            return
        
        # Step 2: Reload cogs
        embed.add_field(name="🔄 Reload Cogs", value="Reloading all cogs...", inline=False)
        await interaction.edit_original_response(embed=embed)
        
        reload_success, reload_message = await self.reload_cogs()
        
        if reload_success:
            embed.set_field_at(1, name="🔄 Reload Cogs", value=f"✅ Success\n```\n{reload_message[:800]}{'...' if len(reload_message) > 800 else ''}\n```", inline=False)
            embed.color = discord.Color.green()
            embed.description = "✅ Update completed successfully!"
        else:
            embed.set_field_at(1, name="🔄 Reload Cogs", value=f"⚠️ Partial Success\n```\n{reload_message[:800]}{'...' if len(reload_message) > 800 else ''}\n```", inline=False)
            embed.color = discord.Color.orange()
            embed.description = "⚠️ Update completed with some issues"
        
        await interaction.edit_original_response(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Update(bot))
