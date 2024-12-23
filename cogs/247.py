import discord
from discord.ext import commands, tasks
import sqlite3
import json
import wavelink
from topgg_api import TopGGAPI

class TwentyFourSeven(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('247.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS voice_247 
                             (guild_id INTEGER PRIMARY KEY, channel_id INTEGER)''')
        self.conn.commit()
        self.voice_clients = {}

    def cog_unload(self):
        self.check_voice_connections.cancel()
        self.conn.close()

    @commands.command(name="247", aliases=["24/7"], help="Toggle 24/7 voice channel connection")
    @commands.has_permissions(manage_guild=True)
    async def twentyfourseven(self, ctx):
        print(f"Command received: 247 in guild {ctx.guild.id}")
        guild_id = ctx.guild.id

        if not ctx.author.voice:
            embed = discord.Embed(
                description="You are not connected to a voice channel.",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)


        channel = ctx.author.voice.channel

        self.cursor.execute('SELECT channel_id FROM voice_247 WHERE guild_id = ?', (guild_id,))
        result = self.cursor.fetchone()

        try:
            if result:
                self.cursor.execute('DELETE FROM voice_247 WHERE guild_id = ?', (guild_id,))
                self.conn.commit()
                if guild_id in self.voice_clients:
                    await self.voice_clients[guild_id].disconnect()
                    del self.voice_clients[guild_id]
                embed = discord.Embed(
                    description="24/7 mode has been disabled. I've disconnected from the voice channel.",
                    color=discord.Color.blue()
                )
            else:
                if guild_id in self.voice_clients and self.voice_clients[guild_id].is_connected():
                    embed = discord.Embed(
                        description=f"24/7 mode enabled. I will stay in {channel.mention}.",
                        color=discord.Color.green()
                    )
                else:
                    await self.join_voice_channel(ctx.guild, channel)
                    embed = discord.Embed(
                        description=f"24/7 mode enabled. I will stay in {channel.mention}.",
                        color=discord.Color.green()
                    )
                self.cursor.execute('INSERT OR REPLACE INTO voice_247 (guild_id, channel_id) VALUES (?, ?)',
                                    (guild_id, channel.id))
                self.conn.commit()

            print(f"Sending response: {embed.description}")
            await ctx.send(embed=embed)
        except Exception as e:
            error_embed = discord.Embed(
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red()
            )
            await ctx.send(embed=error_embed)

    async def join_voice_channel(self, guild, channel):
        if guild.id in self.voice_clients:
            await self.voice_clients[guild.id].disconnect()

        voice_client = await channel.connect(cls=wavelink.Player, self_deaf=True)
        if not hasattr(voice_client, 'queue'):
            voice_client.queue = wavelink.Queue()
        self.voice_clients[guild.id] = voice_client

    @tasks.loop(minutes=5)
    async def check_voice_connections(self):
        self.cursor.execute('SELECT guild_id, channel_id FROM voice_247')
        for guild_id, channel_id in self.cursor.fetchall():
            guild = self.bot.get_guild(guild_id)
            if guild:
                channel = guild.get_channel(channel_id)
                if channel:
                    if guild.id not in self.voice_clients or not self.voice_clients[guild.id].is_connected():
                        try:
                            await self.join_voice_channel(guild, channel)
                        except discord.errors.ClientException:
                            print(f"Failed to connect to voice channel in guild {guild.id}")
                else:
                    self.cursor.execute('DELETE FROM voice_247 WHERE guild_id = ?', (guild_id,))
                    self.conn.commit()
            else:
                self.cursor.execute('DELETE FROM voice_247 WHERE guild_id = ?', (guild_id,))
                self.conn.commit()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        self.check_voice_connections.start()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member == self.bot.user and after.channel is None:
            guild_id = before.channel.guild.id
            self.cursor.execute('SELECT channel_id FROM voice_247 WHERE guild_id = ?', (guild_id,))
            result = self.cursor.fetchone()
            if result:
                channel_id = result[0]
                channel = self.bot.get_channel(channel_id)
                if channel:
                    try:
                        await self.join_voice_channel(channel.guild, channel)
                    except discord.errors.ClientException:
                        print(f"Failed to reconnect to voice channel in guild {guild_id}")


async def setup(bot):
    await bot.add_cog(TwentyFourSeven(bot))