import discord
from discord.ext import commands, tasks
import mcstatus
import asyncio

class MinecraftCog(commands.Cog):
    def __init__(self, bot):
        class MinecraftCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.server_status_channel_ids = [123456789012345678] # Default channel IDs
        self.server_addresses = ["YOUR_MINECRAFT_SERVER_IP"] # Default server IPs
        self.server_query_interval = 300 # in seconds (5 minutes)

        # Start a task to periodically update the server status
        self.update_server_status.start()

    def cog_unload(self):
        # Stop the task when the cog is unloaded
        self.update_server_status.cancel()

    @tasks.loop(seconds=300)  # Default interval, will be changed in before_update_server_status
    async def update_server_status(self):
        await self.update_status()

    async def update_status(self):
        for server_address, channel_id in zip(self.server_addresses, self.server_status_channel_ids):
            try:
                server = mcstatus.MinecraftServer.lookup(server_address)
                status = server.status()

                # Format the server status information into an embed
                embed = discord.Embed(title="Minecraft Server Status", color=discord.Color.green())
                embed.add_field(name="Server", value=server_address)
                embed.add_field(name="Players Online", value=status.players.online)
                if status.players.sample:
                    player_names = "\n".join(player.name for player in status.players.sample)
                    embed.add_field(name="Player Names", value=player_names, inline=False)
                embed.add_field(name="Max Players", value=status.players.max)
                embed.add_field(name="Version", value=status.version.name)

                # Get the channel to send the message to
                channel = self.bot.get_channel(channel_id)

                # Fetch the previous message and edit it with the updated status
                async for message in channel.history(limit=1):
                    await message.edit(embed=embed)
                    break
                else:
                    # If no previous message is found, send a new one
                    await channel.send(embed=embed)
            except Exception as e:
                print(f"Error updating server status: {e}")

    @update_server_status.before_loop
    async def before_update_server_status(self):
        await self.bot.wait_until_ready()
        self.update_server_status.change_interval(seconds=self.server_query_interval)

    # The rest of your commands remain the same
