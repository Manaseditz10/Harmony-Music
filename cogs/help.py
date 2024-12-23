import discord
import asyncio
import sqlite3
import config
from discord.ext import commands

class MenuView(discord.ui.View):
    def __init__(self, author, timeout=30):
        super().__init__(timeout=timeout)
        self.author = author
        self.value = None  
        self.con = sqlite3.connect('main.db')
        self.cur = self.con.cursor()        

    @discord.ui.select(placeholder="Choose a category", options=[
        discord.SelectOption(label="Music", value="music"),
        discord.SelectOption(label="Filter", value="filter"),
        discord.SelectOption(label="Information", value="info"),
        discord.SelectOption(label="Guild Config", value="util"),
    ])
    async def select_category(self, interaction: discord.Interaction, select: discord.ui.Select):
        try:
            if interaction.user.id != self.author.id:
                await interaction.response.send_message("Sorry Bro, This is not your interaction.", ephemeral=True)
                return
            selected_values = select.values
            if selected_values and "music" in selected_values:
                embed1 = discord.Embed(colour=0x2b2d31, description="**`Autoplay`**, **`Play`**, **`Pause`**, **`Resume`**, **`Stop`**, **`Queue`**, **`Volume`**, **`Skip`**, **`Defaultvolume`**, **`Join`**, **`Leave`**, **`Nowplaying`**, **`Forward`**, **`Rewind`**, **`Seek`**, **`Remove`**")
                embed1.set_author(name="Music Commands", icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed1, view=self)
                
            elif selected_values and "filter" in selected_values:
                embed2 = discord.Embed(colour=0x2b2d31, description="**`Bassboost`**, **`Channelmix`**, **`Chipmunk`**, **`Darthvader`**, **`Distortion`**, **`Echo`**, **`Karaoke`**, **`Lowpass`**, **`Nightcore`**, **`Robot`**, **`Slowmo`**, **`Tremolo`**, **`Vaporwave`**, **`Vibrato`**, **`Reset`**")
                embed2.set_author(name="Filter Commands", icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed2, view=self)
                
            elif selected_values and "info" in selected_values:
                embed3 = discord.Embed(colour=0x2b2d31, description="**`Uptime`**, **`Vote`**, **`Invite`**, **`Support`**, **`Stats`**, **`Ping`**, **`Help`**")
                embed3.set_author(name="Info Commands", icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed3, view=self)
                
            elif selected_values and "util" in selected_values:
                embed2 = discord.Embed(colour=0x2b2d31, description="**`247`**, **`Announce`**, **`Settings`**")
                embed2.set_author(name="Config Commands", icon_url=interaction.user.display_avatar.url)
                await interaction.response.edit_message(embed=embed2, view=self)
               
                
                select.placeholder = None 
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
           
            
    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
    async def delete_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            if interaction.user.id != self.author.id:
                await interaction.response.send_message("Sorry Bro, This is not your interaction.", ephemeral=True)
                return
            await interaction.message.delete()
        except Exception as e:
            print(f"An error occurred: {e}")
            raise 


class Help(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.client.remove_command("help")
        self.con = sqlite3.connect('main.db')
        self.cur = self.con.cursor()          

    @commands.Cog.listener()
    async def on_ready(self):
        print("Help Is Ready")    

    @commands.hybrid_command(aliases=['h'], help="Shows the help command of the bot", usage = "Help")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def help(self, ctx, query=None):
        if query:
            command = self.client.get_command(query)
            if command:
                aliases = ", ".join(command.aliases)
                embed = discord.Embed(
                    colour=0x2b2d31, description=f"**{command.help}**"
                )
                embed.add_field(name="Aliases", value=f"`{aliases}`", inline=False)
                embed.add_field(name="Usage", value=f"`{command.usage}`", inline=False)
                embed.set_author(
                    name=ctx.author.name, icon_url=ctx.author.display_avatar.url
                )
                embed.set_thumbnail(url=ctx.author.display_avatar.url)
                await ctx.send(embed=embed)
                return
            else:
                await ctx.send("Command not found.")
                return

        view = MenuView(ctx.author)
        cur = self.con.cursor()
        cur.execute("SELECT prefix FROM Prefix WHERE guild_id = ?", (ctx.guild.id,))
        server_prefix = cur.fetchone()
        bot_avatar_url = ctx.bot.user.avatar.url if ctx.bot.user.avatar else ctx.bot.user.default_avatar.url
        prefix = server_prefix[0] if server_prefix else "."
        embed = discord.Embed(colour=0x2b2d31, description=f"# [Help Menu & Support Panel]({config.support_link})\n\n<:emoji_54:1254350345019199489> Use `/play <track name>` after joining a voice channel to start playing song.\n<:emoji_54:1254350345019199489> For more information use `.help or /help`")
        embed.add_field(name='<:M_Links:1256238064213426198> __Links__', value=f'**[Support]({config.support_link})** <:emoji_54:1254350345019199489> **[Invite Me]({config.bot_link})**', inline=False)
        embed.add_field(name='<:stolen_emoji:1255503035119964191> __Command Categories__', value='<a:gato_musical:1265244057286873192> **[Music](https://0.0.0.0)**\n<:filters:1265244153705533443> **[Filters](https://0.0.0.0)**\n<a:info:1265244577527238717> **[Information](https://0.0.0.0)**\n<a:utility67:1265244670771073024> **[Guild Config](https://0.0.0.0)**', inline=False)
        embed.set_thumbnail(url=bot_avatar_url)
        embed.set_image(url="https://media.discordapp.net/attachments/1211297152479789086/1255532134928486510/1000080705.jpg?ex=667e21ab&is=667cd02b&hm=fbf655fedd70f0ac6d9608315ec22e40c0b6014c135ad7051605465fad1f51b2&=&format=webp&width=915&height=514")
        embed.set_footer(text=f"Powered by MoonNodes")
        message = await ctx.reply(embed=embed, view=view, mention_author=False)

        try:
            await asyncio.sleep(view.timeout)
        except asyncio.CancelledError:
            pass
        else:
            for child in view.children:
                child.disabled = True
            await message.edit(embed=embed, view=view)

async def setup(client):
    await client.add_cog(Help(client))