import discord
from discord.ext import commands
import datetime
import discord.ui
import psutil
import time
import wavelink
import sys
import sqlite3
import platform

start_time = datetime.datetime.now()

def get_uptime():
    now = datetime.datetime.now()
    uptime = now - start_time
    days, seconds = uptime.days, uptime.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{days} day, {hours}:{minutes}:{seconds}"

class MenuView(discord.ui.View):
    def __init__(self, author, bot):
        super().__init__(timeout=30)
        self.author = author
        self.client = bot
        self.value = None
        
    @discord.ui.button(label="System Info", style=discord.ButtonStyle.success)
    async def system_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        try:
            if interaction.user.id != self.author.id:
                await interaction.response.send_message("Sorry Bro, This is not your interaction.", ephemeral=True)
                return
            
            ram_info = psutil.virtual_memory()
            uptime = get_uptime()
            total_users = sum(guild.member_count for guild in self.client.guilds)
            total_guilds = len(self.client.guilds)
            cpu_percent = psutil.cpu_percent(interval=1)
            python_version = sys.version.split()[0]
            cpu_total_cores = psutil.cpu_count(logical=True)
            ram_used = ram_info.used / (1024 ** 3)
            latency = self.client.latency * 1000
            os_name = platform.system()
            
            
            embed = discord.Embed(colour=0x2b2d31, description=f"**<:1181899559853621419:1264778211544530974> Uptime: {uptime}**\n**<:ExoticUser:1264778296479191091> Users: {total_users}**\n**<:ExoticGuild:1264778405749194915> Guilds: {total_guilds}**\n**<:ExoticPing:1264791506586439715> Latency: {latency:.2f}**\n**<:ExoticCPU:1264797431229579294> Cpu: {cpu_percent}%**\n**<:ExoticRam:1264798433164923042> Ram Info: {ram_used:.2f}%**\n**<:ExoticPython:1264800097544306740> Python: {python_version}**\n**<:ExoticCores:1264800568371839027> Cores: {cpu_total_cores}**\n**<:wl_dark:1264800901777064017> Music Wrapper: Wavelink {wavelink.__version__}**\n**<:ExoticOS:1264801368091267113> Os: {os_name}**")
            embed.set_author(name="Some Informations About Me", icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text="Harmony Music", icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

    @discord.ui.button(label="Developer Info", style=discord.ButtonStyle.success)
    async def developer_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.author.id:
                await interaction.response.send_message("Sorry Bro, This is not your interaction.", ephemeral=True)
                return
            
            embed = discord.Embed(colour=0x2b2d31, description=f"<:arrow:1265246569683484743> Below Is The Information Regarding The Bot's Owner, Developer, And Team Members.\n\n<a:Developer:1265247364902420541> **Owner & Developers**\n`1.` [`DarkNighT`](https://discordapp.com/users/1188178871049265282) **[Developer]**\n`2.` [`Joker.xD`](https://discordapp.com/users/1043412897247789058) **[Developer]**\n`3.` [`hecronnn`](https://discordapp.com/users/764884417340375061) **[Owner]**")
            embed.set_author(name="Some Informations About My Devs", icon_url=interaction.user.display_avatar.url)
            embed.set_footer(text="Harmony Music", icon_url=interaction.user.display_avatar.url)
            await interaction.response.edit_message(embed=embed, view=self)
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
            

class Info(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.start_time = datetime.datetime.now()  # Updated line

    @commands.command(aliases=['up'], help="Shows the uptime of the bot", usage="Uptime")
    async def uptime(self, ctx):    
        current_time = datetime.datetime.now()  # Updated line
        uptime = current_time - self.start_time
        hours, remainder = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        uptime_str = f"{days} day(s), {hours} hour(s), {minutes} minute(s), {seconds} second(s)"
        embed = discord.Embed(description=f"Uptime: {uptime_str}", colour=0x2b2d31)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def vote(self, ctx):
        embed = discord.Embed(description="Enjoying with me? Don't forget to vote for me on top.gg", colour=0x2b2d31)
        view = discord.ui.View()
        button = discord.ui.Button(label="Vote Me", url="https://top.gg/bot/1146807200736612384/vote")
        view.add_item(button)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)
        await ctx.reply(embed=embed, mention_author=False, view=view) 
        
    @commands.command(aliases=['inv'], help="Gives you the invite link of the bot", usage="Invite")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def invite(self, ctx):
        embed = discord.Embed(description="Click the button to invite me", colour=0x2b2d31)
        view = discord.ui.View()
        button = discord.ui.Button(label="Invite Me", url="https://discord.com/api/oauth2/authorize?client_id=1146807200736612384&permissions=554104613249&scope=bot%20applications.commands")
        view.add_item(button)
        await ctx.reply(embed=embed, mention_author=False, view=view)
       
    @commands.command(aliases=['sup'], help="Gives you the support server link", usage="Support")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def support(self, ctx):
        embed = discord.Embed(description="Need support? Click the button below to join my support server.", colour=0x2b2d31)
        view = discord.ui.View()
        button = discord.ui.Button(label="Support", url="https://discord.gg/YfnwVw6jJM")
        view.add_item(button)
        await ctx.reply(embed=embed, mention_author=False, view=view)

    @commands.hybrid_command(aliases=['stats'], help="Shows the information of the bot", usage="Stats")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def statistics(self, ctx):
        view = MenuView(ctx.author, self.client)
        users = sum(g.member_count for g in self.client.guilds if g.member_count is not None)
        channel = len(set(self.client.get_all_channels()))
        total_users = sum([i.member_count for i in self.client.guilds])
        node: wavelink.Node = wavelink.Pool.get_node()
        st = await node._fetch_stats()
        author = ctx.message.author
        embed = discord.Embed(
            color=0x2b2d31,
            description=f"**- Introducing Harmony Music – a comprehensive Discord bot designed to transform your server into a vibrant, engaging, and secure community. With Harmony Music, you'll experience a seamless blend of rich user interface (UI), advanced functionalities, and robust security measures that work together to enhance your Discord experience. Let's delve into what makes Harmony Music the ideal companion for your server🚀🛡️**"
        )
        embed.set_author(name="Botinfo", icon_url=author.display_avatar.url)
        embed.set_thumbnail(url=author.display_avatar.url)
        embed.set_image(url="https://cdn.discordapp.com/attachments/1257642415964028979/1264777814788276394/1000080704.jpg?ex=669f1ba1&is=669dca21&hm=11be42a2efbe7d4ad2b9e6cef71ad6d2dee312e5ae62f0c3292b7885802360f5&")
        embed.set_footer(text=f"Requested By {ctx.author}", icon_url=ctx.author.display_avatar.url)
        embed.set_thumbnail(url=self.client.user.display_avatar.url)

        await ctx.send(embed=embed, view=view)

async def setup(client):
    await client.add_cog(Info(client))
