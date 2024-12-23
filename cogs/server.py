import discord
from discord.ext import commands

class EmbedPaginator:
    def __init__(self, bot, ctx, pages):
        self.bot = bot
        self.ctx = ctx
        self.pages = pages
        self.current_page = 0
        self.message = None

    async def start(self):
        self.message = await self.ctx.send(embed=self.pages[self.current_page])
        await self.message.add_reaction("◀️")
        await self.message.add_reaction("▶️")
        self.bot.loop.create_task(self.wait_for_reactions())

    async def wait_for_reactions(self):
        def check(reaction, user):
            return user == self.ctx.author and reaction.message.id == self.message.id

        while True:
            reaction, user = await self.bot.wait_for("reaction_add", check=check)
            if str(reaction.emoji) == "▶️" and self.current_page < len(self.pages) - 1:
                self.current_page += 1
                await self.message.edit(embed=self.pages[self.current_page])
            elif str(reaction.emoji) == "◀️" and self.current_page > 0:
                self.current_page -= 1
                await self.message.edit(embed=self.pages[self.current_page])
            await self.message.remove_reaction(reaction, user)
            
            
class ServerManagement(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='serverlist', aliases= ["si"])
    @commands.is_owner()
    async def server_list(self, ctx):
        """Lists all servers the bot has joined with pagination and member counts."""
        servers = list(self.bot.guilds)
        pages = []

        # Define how many servers per page
        servers_per_page = 10

        # Create pages
        for i in range(0, len(servers), servers_per_page):
            chunk = servers[i:i+servers_per_page]
            description = '\n'.join(f"{guild.name} (ID: {guild.id}) - Members: {guild.member_count}" for guild in chunk)
            embed = discord.Embed(title="Server List", description=description, color=discord.Color.blue())
            pages.append(embed)

        # Start the paginator
        paginator = EmbedPaginator(self.bot, ctx, pages)
        await paginator.start()

    @commands.command(name='serverleave', aliases= ["sl"])
    @commands.is_owner()
    async def server_leave(self, ctx, server_id: int):
        """Makes the bot leave the specified server."""
        guild = self.bot.get_guild(server_id)
        if guild:
            await guild.leave()
            await ctx.send(f"Left server: {guild.name} (ID: {guild.id})")
        else:
            await ctx.send("Bot is not in a server with that ID.")

async def setup(bot):
    await bot.add_cog(ServerManagement(bot))
