import discord
from discord.ext import commands
import sqlite3

class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.con = sqlite3.connect('afk_data.db')
        self.cur = self.con.cursor()
        self.cur.execute('''CREATE TABLE IF NOT EXISTS afk (
                            user_id INTEGER,
                            guild_id INTEGER,
                            reason TEXT,
                            PRIMARY KEY (user_id, guild_id)
                            )''')
        self.con.commit()

    async def set_afk_nick(self, member):
        try:
            await member.edit(nick=f"[AFK] {member.display_name}")
        except discord.Forbidden:
            pass  # Skip if the bot doesn't have permission to change nicknames
        except Exception:
            pass  # Skip any other exceptions silently

    async def remove_afk_nick(self, member):
        try:
            await member.edit(nick=member.display_name.split('[AFK] ')[-1])
        except discord.Forbidden:
            pass  # Skip if the bot doesn't have permission to change nicknames
        except Exception:
            pass  # Skip any other exceptions silently

    async def set_afk(self, member, reason, guild_id=None):
        if guild_id:
            await self.set_afk_nick(member)
            self.cur.execute('INSERT INTO afk (user_id, guild_id, reason) VALUES (?, ?, ?)', (member.id, guild_id, reason))
        else:
            self.cur.execute('INSERT INTO afk (user_id, guild_id, reason) VALUES (?, NULL, ?)', (member.id, reason))
        self.con.commit()

    @commands.command(aliases=["lost"], help="Set an offline status", usage="afk")
    async def afk(self, ctx, *, reason="I am AFK :)"):
        class AFKView(discord.ui.View):
            def __init__(self, utility, member, reason):
                super().__init__(timeout=30)
                self.utility = utility
                self.member = member
                self.reason = reason

            @discord.ui.button(label="Global AFK", style=discord.ButtonStyle.primary)
            async def global_afk_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await self.utility.set_afk(self.member, self.reason)
                self.disable_all_items()
                await interaction.response.edit_message(view=self)
                await interaction.followup.send(f"Global AFK set for **{self.member.display_name}** with reason: **{self.reason}**", ephemeral=True)
                self.stop()

            @discord.ui.button(label="Server AFK", style=discord.ButtonStyle.secondary)
            async def server_afk_button(self, interaction: discord.Interaction, button: discord.ui.Button):
                await self.utility.set_afk(self.member, self.reason, ctx.guild.id)
                self.disable_all_items()
                await interaction.response.edit_message(view=self)
                await interaction.followup.send(f"Server AFK set for **{self.member.display_name}** with reason: **{self.reason}**", ephemeral=True)
                self.stop()

            def disable_all_items(self):
                for item in self.children:
                    item.disabled = True

        view = AFKView(self, ctx.author, reason)
        embed = discord.Embed(description=f"Choose AFK type for **{ctx.author.display_name}**:", color=discord.Color.blue())
        await ctx.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_id = message.guild.id if message.guild else None

        # Check for server-specific AFK
        self.cur.execute('SELECT * FROM afk WHERE user_id = ? AND guild_id = ?', (message.author.id, guild_id))
        data = self.cur.fetchone()

        if data:
            self.cur.execute('DELETE FROM afk WHERE user_id = ? AND guild_id = ?', (message.author.id, guild_id))
            self.con.commit()
            member = message.guild.get_member(message.author.id)
            if member:
                await self.remove_afk_nick(member)
            embed = discord.Embed(description=f"{message.author.mention}, I removed your Server AFK.", color=discord.Color.blue())
            await message.channel.send(embed=embed)

        # Check for global AFK
        self.cur.execute('SELECT * FROM afk WHERE user_id = ? AND guild_id IS NULL', (message.author.id,))
        global_data = self.cur.fetchone()

        if global_data:
            self.cur.execute('DELETE FROM afk WHERE user_id = ? AND guild_id IS NULL', (message.author.id,))
            self.con.commit()
            member = message.guild.get_member(message.author.id)
            if member:
                embed = discord.Embed(description=f"{message.author.mention}, I removed your Global AFK.", color=discord.Color.blue())
                await message.channel.send(embed=embed)

        # Notify mentions
        for member_id, guild_id, reason in self.cur.execute('SELECT user_id, guild_id, reason FROM afk'):
            member = message.guild.get_member(member_id)
            if member and (member.id in message.raw_mentions or (message.reference and member == (await message.channel.fetch_message(message.reference.message_id)).author)):
                embed = discord.Embed(description=f"**{member.mention}** is AFK: **{reason}**", color=discord.Color.blue())
                await message.reply(embed=embed)

async def setup(client):
    await client.add_cog(Utility(client))
