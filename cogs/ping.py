import discord
from discord.ext import commands
from discord import app_commands

class Ping(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        print("Ping.py is ready!")

    @commands.hybrid_command()
    async def ping(self, ctx):
        embed = discord.Embed()
        embed.title = "Pong! 🏓"
        embed.color = discord.Color.green()
        embed.description = f"Latency: {round(self.client.latency * 1000)}ms"
        embed.set_footer(text=f"Bot is stable")
        await ctx.send(embed=embed)



async def setup(client):
    await client.add_cog(Ping(client))