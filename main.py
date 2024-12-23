import discord
import wavelink
import jishaku
from discord.ext import commands
from discord.ext import tasks
import os
import asyncio
import sqlite3
import config
import json


con = sqlite3.connect('main.db')
cur = con.cursor()

intents = discord.Intents.default()  
intents.members = True 
intents.message_content = True

async def get_prefix(client, message):
  cursor = con.execute(
    f"""SELECT prefix FROM Prefix WHERE guild_id = {message.guild.id}""")
  resultz = cursor.fetchone()
  cursor = con.execute(f"SELECT users FROM Np")
  NP = cursor.fetchall()    
  if resultz is None:
    con.execute(
      "INSERT INTO Prefix(prefix, guild_id) VALUES(?, ?)", (
        ".",
        message.guild.id,
      ))
    con.commit()

  c = con.execute("SELECT prefix FROM Prefix WHERE guild_id = ?",
                              (message.guild.id, ))
  result = c.fetchone()
 
  if message.author.id in ([int(i[0]) for i in NP]):
    a = commands.when_mentioned_or('', result[0])(client, message)
    return sorted(a, reverse=True)
  else:
    return commands.when_mentioned_or(result[0])(client, message)
  
class Trixo(commands.AutoShardedBot):
  def __init__(self):
    super().__init__(command_prefix=get_prefix,intents=intents,case_insensitive=True,strip_after_prefix=True,status=discord.Status.online)  
client = Trixo()
shard_guild_counts = {}


@client.event
async def on_connect():
  await client.change_presence(status=discord.Status.online,activity=discord.Activity(type=discord.ActivityType.listening,name="/help"))

@client.event
async def setup_hook():
  cur.execute("CREATE TABLE IF NOT EXISTS Np(users INTEGER PRIMARY KEY)")
  cur.execute("CREATE TABLE IF NOT EXISTS Prefix(guild_id TEXT NOT NULL, prefix TEXT NOT NULL)")
  cur.execute("CREATE TABLE IF NOT EXISTS ignored_channels (guild_id INTEGER, channel_id INTEGER, PRIMARY KEY (guild_id, channel_id))")
  cur.execute("CREATE TABLE IF NOT EXISTS blacklist (user_id INTEGER PRIMARY KEY)")
  cur.execute("CREATE TABLE IF NOT EXISTS Owner (user_id INTEGER PRIMARY KEY)") 
  print("Table Initated")

@client.event
async def on_shard_ready(shard_id):
    guild_count = len(client.guilds)
    shard_guild_counts[shard_id] = guild_count
    print(f"Shard {shard_id} is ready and handling {guild_count} servers.")    

@client.event                      
async def on_ready():
  await connect_nodes()
  await client.load_extension("jishaku")
  client.owner_ids = [1188178871049265282, 1037677572298903593, 1043412897247789058, 1227885149258252298]
  cache_sweeper.start()
  await client.tree.sync()
  print(f"Connected as {client.user}")

@client.command()
async def guildinfo(ctx, guild_id: int):
    guild = client.get_guild(guild_id)
    if not guild:
        await ctx.send("Guild not found!")
        return
    invite_links = await guild.invites()
    if invite_links:
        invite = invite_links[0]
        await ctx.send(f"Guild Invite Link: {invite.url}")
    else:
        await ctx.send("No active invite links found for this guild!")


@client.event
async def connect_nodes():
    node = wavelink.Node(
        uri='http://node.raidenbot.xyz:5501',
        password='pwd'
    )
    await wavelink.Pool.connect(client=client, nodes=[node])
    print('Connected to Lavalink node!')

#message event    
@client.event
async def on_message(message):
    if message.author == client.user:
        return    
    cur.execute('SELECT * FROM ignored_channels WHERE channel_id = ?', (message.channel.id,))
    if cur.fetchone():
        return   
    cur.execute('SELECT * FROM blacklist WHERE user_id = ?', (message.author.id,))
    if cur.fetchone():
        return    
    await client.process_commands(message) 
    
@tasks.loop(minutes=60)
async def cache_sweeper():
    client._connection._private_channels.clear()
    client._connection._users.clear()
    client._connection._messages.clear()
    print("Cleared Cache")    

async def load():
  for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
      await client.load_extension(f"cogs.{filename[:-3]}")

async def main():
  async with client:
    await load()
    await client.start(config.DISCORD_TOKEN)


asyncio.run(main())