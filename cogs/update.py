import os
import discord
from discord.ext import commands
from discord import app_commands
import subprocess
import asyncio
import sys
from typing import Optional
import pkg_resources
import hashlib

class Update(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.repo_url = "https://github.com/ilikepancakes-ink/gork.git"
        self.requirements_file = "requirements.txt"
        
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

    async def check_requirements_changes(self) -> tuple[bool, str]:
        """Check if requirements.txt has changed and return the hash comparison"""
        try:
            if not os.path.exists(self.requirements_file):
                return False, "requirements.txt not found"

            # Read current requirements.txt
            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                current_content = f.read().strip()

            # Calculate hash of current requirements
            current_hash = hashlib.md5(current_content.encode()).hexdigest()

            # Store hash in a temporary file for comparison
            hash_file = ".requirements_hash"
            previous_hash = None

            if os.path.exists(hash_file):
                with open(hash_file, 'r') as f:
                    previous_hash = f.read().strip()

            # Update hash file
            with open(hash_file, 'w') as f:
                f.write(current_hash)

            if previous_hash is None:
                return True, "First time checking requirements - will install dependencies"
            elif current_hash != previous_hash:
                return True, "requirements.txt has changed - new dependencies may be needed"
            else:
                return False, "requirements.txt unchanged"

        except Exception as e:
            return False, f"Error checking requirements: {str(e)}"

    async def install_requirements(self) -> tuple[bool, str]:
        """Install or upgrade packages from requirements.txt"""
        try:
            if not os.path.exists(self.requirements_file):
                return False, "requirements.txt not found"

            # Use pip to install/upgrade requirements
            stdout, stderr, code = await self.run_command(
                f"{sys.executable} -m pip install -r {self.requirements_file} --upgrade"
            )

            if code == 0:
                return True, f"Successfully installed/upgraded packages:\n{stdout}"
            else:
                return False, f"Failed to install packages:\n{stderr}"

        except Exception as e:
            return False, f"Error installing requirements: {str(e)}"

    async def check_missing_packages(self) -> tuple[bool, str, list]:
        """Check for missing packages from requirements.txt"""
        try:
            if not os.path.exists(self.requirements_file):
                return False, "requirements.txt not found", []

            missing_packages = []
            installed_packages = {pkg.project_name.lower(): pkg.version for pkg in pkg_resources.working_set}

            with open(self.requirements_file, 'r', encoding='utf-8') as f:
                requirements = f.readlines()

            for req in requirements:
                req = req.strip()
                if not req or req.startswith('#'):
                    continue

                # Parse package name (handle >= and other operators)
                package_name = req.split('>=')[0].split('==')[0].split('>')[0].split('<')[0].split('!')[0].strip()

                if package_name.lower() not in installed_packages:
                    missing_packages.append(package_name)

            if missing_packages:
                return True, f"Missing packages: {', '.join(missing_packages)}", missing_packages
            else:
                return False, "All required packages are installed", []

        except Exception as e:
            return False, f"Error checking packages: {str(e)}", []

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
    @app_commands.describe(action="Action to perform: update")
    async def debug(self, interaction: discord.Interaction, action: str):
        """Debug command for bot maintenance"""
        
        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need administrator permissions to use debug commands.", ephemeral=True)
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

        # Step 2: Check for dependency changes
        embed.add_field(name="📦 Check Dependencies", value="Checking for new pip packages...", inline=False)
        await interaction.edit_original_response(embed=embed)

        deps_changed, deps_message = await self.check_requirements_changes()
        has_missing, missing_message, missing_list = await self.check_missing_packages()

        if deps_changed or has_missing:
            embed.set_field_at(1, name="📦 Check Dependencies", value=f"⚠️ Changes detected\n```\n{deps_message}\n{missing_message}\n```", inline=False)

            # Step 3: Install dependencies
            embed.add_field(name="⬇️ Install Dependencies", value="Installing/upgrading pip packages...", inline=False)
            await interaction.edit_original_response(embed=embed)

            install_success, install_message = await self.install_requirements()

            if install_success:
                embed.set_field_at(2, name="⬇️ Install Dependencies", value=f"✅ Success\n```\n{install_message[:600]}{'...' if len(install_message) > 600 else ''}\n```", inline=False)
            else:
                embed.set_field_at(2, name="⬇️ Install Dependencies", value=f"❌ Failed\n```\n{install_message[:600]}{'...' if len(install_message) > 600 else ''}\n```", inline=False)
                embed.color = discord.Color.red()
                await interaction.edit_original_response(embed=embed)
                return
        else:
            embed.set_field_at(1, name="📦 Check Dependencies", value=f"✅ No changes\n```\n{deps_message}\n{missing_message}\n```", inline=False)
        
        # Final Step: Reload cogs
        cog_field_index = 3 if (deps_changed or has_missing) else 2
        embed.add_field(name="🔄 Reload Cogs", value="Reloading all cogs...", inline=False)
        await interaction.edit_original_response(embed=embed)

        reload_success, reload_message = await self.reload_cogs()

        if reload_success:
            embed.set_field_at(cog_field_index, name="🔄 Reload Cogs", value=f"✅ Success\n```\n{reload_message[:800]}{'...' if len(reload_message) > 800 else ''}\n```", inline=False)
            embed.color = discord.Color.green()
            embed.description = "✅ Update completed successfully!"
        else:
            embed.set_field_at(cog_field_index, name="🔄 Reload Cogs", value=f"⚠️ Partial Success\n```\n{reload_message[:800]}{'...' if len(reload_message) > 800 else ''}\n```", inline=False)
            embed.color = discord.Color.orange()
            embed.description = "⚠️ Update completed with some issues"
        
        await interaction.edit_original_response(embed=embed)

    @app_commands.command(name="check-deps", description="Check for missing pip packages from requirements.txt")
    async def check_deps(self, interaction: discord.Interaction):
        """Check for missing dependencies without updating"""

        # Check if user has administrator permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You need administrator permissions to use this command.", ephemeral=True)
            return

        await interaction.response.defer()

        embed = discord.Embed(
            title="📦 Dependency Check",
            description="Checking for missing pip packages...",
            color=discord.Color.blue()
        )
        await interaction.followup.send(embed=embed)

        # Check for missing packages
        has_missing, missing_message, missing_list = await self.check_missing_packages()

        if has_missing:
            embed.add_field(
                name="⚠️ Missing Packages",
                value=f"```\n{missing_message}\n```",
                inline=False
            )
            embed.add_field(
                name="💡 Solution",
                value="Run `/debug update` to install missing packages automatically.",
                inline=False
            )
            embed.color = discord.Color.orange()
            embed.description = "⚠️ Some packages are missing"
        else:
            embed.add_field(
                name="✅ All Good",
                value=f"```\n{missing_message}\n```",
                inline=False
            )
            embed.color = discord.Color.green()
            embed.description = "✅ All required packages are installed"

        await interaction.edit_original_response(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Update(bot))
