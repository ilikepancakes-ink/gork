import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
from datetime import datetime, timedelta
import sys
import os
from typing import Optional

# Add the parent directory to the path so we can import from utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.database import MessageDatabase

class MessageLogger(commands.Cog):
    """Cog for logging messages and responses to database"""
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = MessageDatabase("data/bot_messages.db")
        self.cleanup_task.start()  # Start the cleanup task
    
    def cog_unload(self):
        """Clean up when cog is unloaded"""
        self.cleanup_task.cancel()
    
    @tasks.loop(hours=24)  # Run daily
    async def cleanup_task(self):
        """Periodic cleanup of old messages"""
        try:
            deleted_count = await self.db.cleanup_old_messages(days_to_keep=90)  # Keep 90 days
            if deleted_count > 0:
                print(f"🧹 Daily cleanup: Removed {deleted_count} old database entries")
        except Exception as e:
            print(f"❌ Error in daily cleanup task: {e}")
    
    @cleanup_task.before_loop
    async def before_cleanup_task(self):
        """Wait for bot to be ready before starting cleanup task"""
        await self.bot.wait_until_ready()
    
    async def log_user_message(self, message: discord.Message) -> bool:
        """Log a user message to the database"""
        try:
            # Extract attachment information if present
            attachment_info = None
            has_attachments = len(message.attachments) > 0
            
            if has_attachments:
                attachment_info = {
                    "count": len(message.attachments),
                    "files": [
                        {
                            "filename": att.filename,
                            "size": att.size,
                            "content_type": att.content_type,
                            "url": att.url
                        } for att in message.attachments
                    ]
                }
            
            # Get guild and channel information
            guild_id = str(message.guild.id) if message.guild else None
            guild_name = message.guild.name if message.guild else None
            channel_name = message.channel.name if hasattr(message.channel, 'name') else "DM"
            
            success = await self.db.log_user_message(
                user_id=str(message.author.id),
                username=message.author.name,
                user_display_name=message.author.display_name,
                channel_id=str(message.channel.id),
                channel_name=channel_name,
                guild_id=guild_id,
                guild_name=guild_name,
                message_id=str(message.id),
                message_content=message.content,
                has_attachments=has_attachments,
                attachment_info=attachment_info,
                timestamp=message.created_at
            )
            
            return success
            
        except Exception as e:
            print(f"❌ Error logging user message {message.id}: {e}")
            return False

    async def log_user_message_from_interaction(self, interaction: discord.Interaction, message_content: str) -> bool:
        """Log a user message from a slash command interaction"""
        try:
            # Get guild and channel information
            guild_id = str(interaction.guild.id) if interaction.guild else None
            guild_name = interaction.guild.name if interaction.guild else None
            channel_name = interaction.channel.name if hasattr(interaction.channel, 'name') else "DM"

            # Create a fake message ID for slash commands
            fake_message_id = f"slash_{interaction.id}"

            success = await self.db.log_user_message(
                user_id=str(interaction.user.id),
                username=interaction.user.name,
                user_display_name=interaction.user.display_name,
                channel_id=str(interaction.channel.id),
                channel_name=channel_name,
                guild_id=guild_id,
                guild_name=guild_name,
                message_id=fake_message_id,
                message_content=message_content,
                has_attachments=False,  # Slash commands don't support attachments
                attachment_info=None,
                timestamp=datetime.utcnow()
            )

            return success

        except Exception as e:
            print(f"❌ Error logging slash command message {interaction.id}: {e}")
            return False

    async def log_bot_response(self,
                              original_message: discord.Message,
                              response_message: discord.Message,
                              response_content: str,
                              processing_time_ms: Optional[int] = None,
                              model_used: Optional[str] = None,
                              chunk_info: tuple = (1, 1)) -> bool:
        """Log a bot response to the database"""
        try:
            response_chunks, chunk_number = chunk_info
            
            success = await self.db.log_bot_response(
                original_message_id=str(original_message.id),
                response_message_id=str(response_message.id),
                response_content=response_content,
                response_chunks=response_chunks,
                chunk_number=chunk_number,
                processing_time_ms=processing_time_ms,
                model_used=model_used,
                timestamp=response_message.created_at
            )
            
            return success
            
        except Exception as e:
            print(f"❌ Error logging bot response {response_message.id}: {e}")
            return False

    async def log_bot_response_from_interaction(self,
                                              interaction: discord.Interaction,
                                              response_message: discord.Message,
                                              response_content: str,
                                              processing_time_ms: Optional[int] = None,
                                              model_used: Optional[str] = None,
                                              chunk_info: tuple = (1, 1)) -> bool:
        """Log a bot response from a slash command interaction"""
        try:
            response_chunks, chunk_number = chunk_info

            # Create fake original message ID for slash commands
            fake_original_message_id = f"slash_{interaction.id}"

            success = await self.db.log_bot_response(
                original_message_id=fake_original_message_id,
                response_message_id=str(response_message.id),
                response_content=response_content,
                response_chunks=response_chunks,
                chunk_number=chunk_number,
                processing_time_ms=processing_time_ms,
                model_used=model_used,
                timestamp=response_message.created_at
            )

            return success

        except Exception as e:
            print(f"❌ Error logging bot response from interaction {response_message.id}: {e}")
            return False

    @app_commands.command(name="message_stats", description="Get message statistics")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def message_stats(self, interaction: discord.Interaction, user: Optional[discord.Member] = None):
        """Get message statistics for a user or overall"""
        await interaction.response.defer()
        
        try:
            user_id = str(user.id) if user else str(interaction.user.id)
            stats = await self.db.get_conversation_stats(user_id if user or not interaction.guild else None)
            
            embed = discord.Embed(
                title="📊 Message Statistics",
                color=discord.Color.blue(),
                timestamp=datetime.utcnow()
            )
            
            if user:
                embed.description = f"Statistics for {user.display_name}"
                embed.add_field(name="Messages Sent", value=stats.get('total_messages', 0), inline=True)
                embed.add_field(name="Bot Responses", value=stats.get('total_responses', 0), inline=True)
            else:
                embed.description = "Overall bot statistics"
                embed.add_field(name="Total Messages", value=stats.get('total_messages', 0), inline=True)
                embed.add_field(name="Total Responses", value=stats.get('total_responses', 0), inline=True)
                if 'unique_users' in stats:
                    embed.add_field(name="Unique Users", value=stats.get('unique_users', 0), inline=True)
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error retrieving statistics: {str(e)}")
    
    @app_commands.command(name="message_history", description="Get your recent message history")
    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    async def message_history(self, interaction: discord.Interaction, limit: int = 10):
        """Get recent message history for the user"""
        await interaction.response.defer(ephemeral=True)  # Make it ephemeral for privacy
        
        if limit > 50:
            limit = 50
        elif limit < 1:
            limit = 1
        
        try:
            user_id = str(interaction.user.id)
            history = await self.db.get_user_message_history(user_id, limit)
            
            if not history:
                await interaction.followup.send("No message history found.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title=f"📝 Your Recent Messages (Last {len(history)})",
                color=discord.Color.green(),
                timestamp=datetime.utcnow()
            )
            
            for i, msg in enumerate(history[:10], 1):  # Show max 10 in embed
                timestamp = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
                formatted_time = timestamp.strftime("%m/%d %H:%M")
                
                content = msg['message_content']
                if len(content) > 100:
                    content = content[:97] + "..."
                
                response_info = ""
                if msg['response_count'] > 0:
                    response_info = f" (✅ {msg['response_count']} response{'s' if msg['response_count'] > 1 else ''})"
                
                embed.add_field(
                    name=f"{i}. {formatted_time}{response_info}",
                    value=content or "*[No text content]*",
                    inline=False
                )
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.followup.send(f"❌ Error retrieving message history: {str(e)}", ephemeral=True)
    
    @commands.command(name="cleanup_messages", hidden=True)
    @commands.is_owner()
    async def cleanup_messages(self, ctx, days: int = 30):
        """Manually trigger message cleanup (owner only)"""
        try:
            deleted_count = await self.db.cleanup_old_messages(days_to_keep=days)
            await ctx.send(f"🧹 Cleaned up {deleted_count} database entries older than {days} days.")
        except Exception as e:
            await ctx.send(f"❌ Error during cleanup: {str(e)}")
    
    @commands.command(name="db_stats", hidden=True)
    @commands.is_owner()
    async def db_stats(self, ctx):
        """Get database statistics (owner only)"""
        try:
            stats = await self.db.get_conversation_stats()
            
            embed = discord.Embed(
                title="🗄️ Database Statistics",
                color=discord.Color.purple(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(name="Total Messages", value=stats.get('total_messages', 0), inline=True)
            embed.add_field(name="Total Responses", value=stats.get('total_responses', 0), inline=True)
            embed.add_field(name="Unique Users", value=stats.get('unique_users', 0), inline=True)
            
            # Add database file size if possible
            try:
                import os
                db_size = os.path.getsize(self.db.db_path)
                db_size_mb = db_size / (1024 * 1024)
                embed.add_field(name="Database Size", value=f"{db_size_mb:.2f} MB", inline=True)
            except:
                pass
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error retrieving database statistics: {str(e)}")

async def setup(bot: commands.Bot):
    await bot.add_cog(MessageLogger(bot))
