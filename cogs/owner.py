import discord
from discord.ext import commands
import sqlite3
import aiohttp

def extraowner():
    async def predicate(ctx: commands.Context):
        with sqlite3.connect('main.db') as con:
            cur = con.cursor()  
            cur.execute("SELECT user_id FROM Owner")
            ids_ = cur.fetchall()
            if ctx.author.id in [i[0] for i in ids_]:
                return True
            else:
                return False
    return commands.check(predicate)  

class owner(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.con = sqlite3.connect('main.db')
        self.cur = self.con.cursor()    

    @commands.group(description="Blacklist Commands", invoke_without_command=True)
    @commands.check_any(commands.is_owner())
    async def bl(self, ctx):
        await ctx.send("") 

    @bl.command(name="add")
    @commands.check_any(commands.is_owner())
    async def bl_add(self, ctx, user: discord.User):
      excluded_users = [1188178871049265282, 910881343884390400]
      if user.id in excluded_users:
        await ctx.send("You cannot blacklist your Daddy.")
        return

      self.cur.execute('SELECT * FROM blacklist WHERE user_id = ?', (user.id,))
      blacklisted = self.cur.fetchone()    
      if blacklisted:
        embed1 = discord.Embed(description=f"**{user.name}** is already in the blacklist.", color=0x2b2d31)
        await ctx.reply(embed=embed1, mention_author=False)
      else:
        self.cur.execute('INSERT INTO blacklist (user_id) VALUES (?)', (user.id,))
        self.con.commit()
        embed2 = discord.Embed(description=f"**{user.name}** has been blacklisted from my command successfully.", color=0x2b2d31)
        await ctx.reply(embed=embed2, mention_author=False)
        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(url="https://discord.com/api/webhooks/1254455063888269312/PrTKUoJ_Ukr40gvaidATZe5sj_LNJadgSa3Sa7BKA0Va6XlXMeSDYQzjixckIU_-ZJi4", session=session)
            embed3 = discord.Embed(title="Blacklist Added", description=f"**Action By:** {ctx.author} ({ctx.author.id})\n**User:** {user} ({user.id})", color=0x2b2d31)
            await webhook.send(embed=embed3)
  

    @bl.command(name="remove")
    @commands.check_any(commands.is_owner())
    async def bl_remove(self, ctx, user: discord.User):
        self.cur.execute('SELECT * FROM blacklist WHERE user_id = ?', (user.id,))
        blacklisted = self.cur.fetchone() 
        if blacklisted:
            self.cur.execute('DELETE FROM blacklist WHERE user_id = ?', (user.id,))
            self.con.commit()        
            embed1 = discord.Embed(description=f"**{user.name}** has been unblacklisted from my command, Now he/she is able to use my command.", color=0x2b2d31)
            await ctx.reply(embed=embed1, mention_author=False)
            async with aiohttp.ClientSession() as session:
                webhook = discord.Webhook.from_url(url="https://discord.com/api/webhooks/1254455063888269312/PrTKUoJ_Ukr40gvaidATZe5sj_LNJadgSa3Sa7BKA0Va6XlXMeSDYQzjixckIU_-ZJi4",session=session)
                embed3 = discord.Embed(title="Blacklist Removed", description=f"**Action By:** {ctx.author} ({ctx.author.id})\n**User:** {user} ({user.id})",color=0x2b2d31)
                await webhook.send(embed=embed3)          
        else:
            embed2 = discord.Embed(description=f"**{user.name}** is not in the blacklist.", color=0x2b2d31)
            await ctx.reply(embed=embed2, mention_author=False)




async def setup(client):
    await client.add_cog(owner(client))