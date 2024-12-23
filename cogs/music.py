import discord
import datetime
import wavelink
import asyncio
from collections import deque
from typing import cast
import re
from discord.ui import Button, View
from discord.ext import commands, tasks
import config
import sqlite3

class MusicControlView(discord.ui.View):
    def __init__(self, player):
        super().__init__(timeout=None)
        self.player = player  

    @discord.ui.button(emoji="<:stolen_emoji:1255885071299379362>", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice:
            await interaction.response.send_message("<:stolen_emoji:1255171928986226730> You are not in a voice channel.", ephemeral=True)
            return
    
        if self.player.playing:
            await self.player.pause(True)
            await interaction.response.send_message("Music paused.", ephemeral=True)
        else:
            await interaction.response.send_message("No music is playing.", ephemeral=True)

    @discord.ui.button(emoji="<:stolen_emoji:1255885170813308940>", style=discord.ButtonStyle.secondary)
    async def resume(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice:
            await interaction.response.send_message("<:stolen_emoji:1255171928986226730> You are not in a voice channel.", ephemeral=True)
            return
        
        if self.player.paused:
            await self.player.pause(False)
            await interaction.response.send_message("Music resumed.", ephemeral=True)
        else:
            await interaction.response.send_message("Music is not paused.", ephemeral=True)

    @discord.ui.button(emoji="<:stolen_emoji:1255885259401072641>", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice:
            await interaction.response.send_message("<:stolen_emoji:1255171928986226730> You are not in a voice channel.", ephemeral=True)
            return
        
        if self.player.playing:
            await self.player.stop()
            await interaction.response.send_message("Skipped current track.", ephemeral=True)
        else:
            await interaction.response.send_message("No music is playing.", ephemeral=True)

    @discord.ui.button(emoji="<:stolen_emoji:1255885360521543761>", style=discord.ButtonStyle.secondary)
    async def stop(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.voice:
            await interaction.response.send_message("<:stolen_emoji:1255171928986226730> You are not in a voice channel.", ephemeral=True)
            return
        
        if self.player.playing:
            await self.player.disconnect()
            await interaction.response.send_message("Music stopped and bot disconnected.", ephemeral=True)
        else:
            await interaction.response.send_message("No music is playing.", ephemeral=True)

class Music(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.queuee = deque()
        self.conn = sqlite3.connect('247.db')
        self.cursor = self.conn.cursor()
        self.color = config.color
        self.autoplay_status = {}
        self.announce_status = {}
        
    def get_autoplay_status(self, guild_id):
        return self.autoplay_status.get(guild_id, 0)

    def set_autoplay_status(self, guild_id, status):
        self.autoplay_status[guild_id] = status    
        
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx):
        """Toggle announcements on or off."""
        current_status = self.announce_status.get(ctx.guild.id, True)
        new_status = not current_status
        self.announce_status[ctx.guild.id] = new_status
        status_message = 'send' if new_status else 'not send'
        embed = discord.Embed(color=discord.Color.blue())
        embed.description=f"Onwards on tracks start player will {status_message} embeds."
        embed.timestamp = ctx.message.created_at
        await ctx.send(embed=embed)
        
    @commands.command()
    async def settings(self, ctx):
        """Display current settings."""
        guild = ctx.guild
        announce_status = self.announce_status.get(ctx.guild.id, True)
        autoplay_status = self.get_autoplay_status(guild.id)
        status_message = 'Enabled' if announce_status else 'Disabled'
        autoplay_message = 'Enabled' if autoplay_status == 1 else 'Disabled'
        self.cursor.execute('SELECT channel_id FROM voice_247 WHERE guild_id = ?', (guild.id,))
        result = self.cursor.fetchone()
        twenty_four_seven_status = f'<#{result[0]}>' if result else 'Not set'
        
        embed = discord.Embed(color=discord.Color.blue())
        embed.add_field(name="-> 24/7 Voice Channel", value=f"<:blue_dot:1256451277030817873> {twenty_four_seven_status}", inline=False)
        embed.add_field(name=f"-> Autoplay [{autoplay_message}]", value="<:blue_dot:1256451277030817873> Yes", inline=False)
        embed.add_field(name=f"-> Announce Enabled [Embeds {status_message}]", value="<:blue_dot:1256451277030817873> Yes", inline=False)
        
        if guild.icon:
            embed.set_author(name=guild.name, icon_url=guild.icon.url)
        else:
            embed.set_author(name=guild.name)
            
        embed.timestamp = ctx.message.created_at
        await ctx.send(embed=embed)
           
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player = payload.player
        original: wavelink.Playable = payload.original
        track: wavelink.Playable = payload.track
        if not hasattr(original, 'requestor'):
            requestor = payload.player.client.user
        else:
            requestor = original.requestor
        bot_avatar_url = player.client.user.avatar.url
        duration_seconds = track.length / 1000
        minutes, seconds = divmod(duration_seconds, 60)
        volume = player.volume
        author = track.author
        minss = f"{int(minutes)}:{int(seconds):02d}"
        embed = discord.Embed()
        embed.set_author(name="| Playing", icon_url=bot_avatar_url)
        embed.color = discord.Color.dark_embed()
        embed.set_footer(text=f'Volume {volume}%')
        embed.description = f'<a:music:1261629625671614474> [{player.current.title}]({config.support_link})'
        embed.set_image(url="https://media.discordapp.net/attachments/1249001392056696912/1255500825103564931/1000080703.jpg?ex=667f5602&is=667e0482&hm=e835f1d7d4bd8df253c68474b3acc5bee7d075924404fc283b9ea30e572fd345&=&format=webp&width=1106&height=144")
        embed.set_thumbnail(url=player.current.artwork)
        embed.add_field(name="<:stolenemoji:1261679206304321639> Requester:", value=f"**- {requestor.mention}**")
        embed.add_field(name="<:stolenemoji:1261680560925839551> Duration:", value=f"- `{minss}`")
        embed.add_field(name="<:stolenemoji:1261631674026819626> Author:", value=f"- `{author}`")
        
        if self.announce_status.get(player.guild.id, True):  # Default to True if not set
            try:
                player.msg = await player.home.send(embed=embed, view=MusicControlView(player))
            except Exception as e:
                print(e)
            
        if isinstance(player.channel, discord.VoiceChannel):
            await player.channel.edit(status=f"▶ | {player.current.title} - {track.author}")
            
        player.queue.put(wavelink.QueueMode.loop)              
            
        if self.get_autoplay_status(player.guild.id) == 1:
            player.autoplay = wavelink.AutoPlayMode.partial
        else:
            player.autoplay = wavelink.AutoPlayMode.disabled
            
    @commands.Cog.listener()
    async def on_wavelink_inactive_player(self, player: wavelink.Player) -> None:
        if player.channel:
            embed = discord.Embed(color=discord.Color.blurple)
            bot_avatar_url = player.client.user.avatar.url
            embed.description = "As no one is listening to the song, I have chosen to exit your voice channel. Use the /247 command to keep the bot forever in your voice channel."
            embed.set_author(name="Leaving Voice Channel!", icon_url=bot_avatar_url)
            
            await player.disconnect()
            
            if isinstance(player.channel, discord.TextChannel):
                await player.channel.send(embed=embed)
        else:
            print("Player channel is not available or is invalid.")
            
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player: wavelink.Player = payload.player
        if hasattr(player, 'msg') and player.msg is not None:
            try:
                await player.msg.delete()
            except discord.DiscordException as e:
                print(f"Failed to delete message: {e}")
        else:
            self.logger.warning("Message to delete is not set or invalid.")

            
     
    @commands.hybrid_command(name="play",aliases=["p"], description = "Plays a song")
    async def play(self, ctx: commands.Context, *, query: str) -> None:    
        if not getattr(ctx.author.voice, "channel", None):
            emb = discord.Embed(color=0x2e2e2e)
            emb.set_footer(text=f"You are not connected to any of the voice channel.",icon_url=ctx.author.display_avatar.url)  
            return await ctx.reply(embed=emb,delete_after=6)
       
        
        youtube_regex = r'(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/)[^\s]+'
        if re.search(youtube_regex, query):
            emb = discord.Embed(color=0x2e2e2e)
            emb.set_footer(text=f"Songs from Youtube aren`t supported.",icon_url=ctx.author.display_avatar.url)  
            return await ctx.reply(embed=emb,delete_after=6)  
         
        player: wavelink.Player = ctx.voice_client
            
        if not player:
            try:
                player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)  
            except discord.ClientException:
                emb = discord.Embed(color=0x2e2e2e)
                emb.set_footer(text=f"I was unable to join this voice channel..",icon_url=ctx.author.display_avatar.url)  
                return await ctx.reply(embed=emb,delete_after=7)   
            
        player.autoplay = wavelink.AutoPlayMode.partial
        
        if ctx.author.voice.channel != ctx.voice_client.channel:
            embed3 = discord.Embed(description="<:stolen_emoji:1255171779031203864> You are not in the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed3, mention_author=False)
            return
            
        
        
        if not hasattr(player, "home"):
            player.home = ctx.channel
        
        if query.startswith('sp '):
            source = "spsearch"
            query = query.replace("sp","")
        elif query.startswith('dz '):
            source = "dzsearch"
            query = query.replace("dz","")
        else:
            source = "ytsearch"
        tracks: wavelink.Search = await wavelink.Playable.search(query, source=source)
        if not tracks:
            embed = discord.Embed(color=0x2e2e2e)
            embed.set_footer(text=f"No Tracks Found for the query..",icon_url=ctx.author.display_avatar.url) 
            return await ctx.reply(embed=embed,delete_after=6)

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            emb = discord.Embed(color=0x2e2e2e)
            emb.set_footer(text=f"Added tracks from the playlist `{tracks.name}` | {added} songs.",icon_url=ctx.author.display_avatar.url)
            await ctx.reply(embed=emb, mention_author=False)
        else:
            track: wavelink.Playable = tracks[0]
            track.requestor = ctx.author
            duration_seconds = track.length / 1000
            minutes, seconds = divmod(duration_seconds, 60)
            minss = f"{int(minutes)}:{int(seconds):02d}"
            await player.queue.put_wait(track)
            emb = discord.Embed(title="Enqueued Track", color=0x2e2e2e)
            emb.description = f'**<:tickk:1256186475289247814> Added [{track}](https://0.0.0.0) to the queue.**'
            await ctx.reply(embed=emb, mention_author=False)
        if not player.playing:
            await player.play(player.queue.get(), volume=80 ,add_history = True)
            
        if self.get_autoplay_status(ctx.guild.id) == 1:
            await self.enable_autoplay(player)
        else:
            await self.disable_autoplay(player)
            
            
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player = payload.player
        guild_id = player.guild.id if player.guild else None
        if not player.queue and self.get_autoplay_status(guild_id) == 1:
            try:
                related = await player.current.related()
                if related:
                    await player.play(related[0])
            except Exception:
                pass
        elif player.queue:
            await player.play(player.queue.get())

    async def enable_autoplay(self, player: wavelink.Player):
        player.autoplay = wavelink.AutoPlayMode.enabled
        self.set_autoplay_status(player.guild.id, 1)

    async def disable_autoplay(self, player: wavelink.Player):
        player.autoplay = wavelink.AutoPlayMode.disabled
        self.set_autoplay_status(player.guild.id, 0)

    @commands.hybrid_command(aliases=['ap'], help="Toggle autoplay feature", usage="autoplay")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def autoplay(self, ctx):
        if not ctx.voice_client:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any voice channel.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        
        current_status = self.get_autoplay_status(ctx.guild.id)
        new_status = 1 if current_status == 0 else 0
        self.set_autoplay_status(ctx.guild.id, new_status)
        
        status_text = "enabled" if new_status == 1 else "disabled"
        embed = discord.Embed(description=f"<:tickk:1256186475289247814> Autoplay has been {status_text}.", colour=self.color)
        await ctx.reply(embed=embed, mention_author=False)
        
        if new_status == 1:
            await self.enable_autoplay(player)
        else:
            await self.disable_autoplay(player)

        self.logger.info(f"Autoplay status changed to {status_text} for guild {ctx.guild.id}")
    
    @commands.hybrid_command(aliases=['wait'], help="Pause the current playing music!", usage="pause")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def pause(self, ctx):
        vc: wavelink.Player = ctx.voice_client
        if not vc:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any vc.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)
        if not ctx.author.voice:
            embed2 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.", colour=self.color)
            return await ctx.reply(embed=embed2, mention_author=False)
        player: wavelink.player = cast(wavelink.player, ctx.voice_client)
        if ctx.author.voice.channel != player.channel:
            embed3 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed3, mention_author=False)
        if not player.playing:
            embed5 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not playing anything.", colour=self.color)
            return await ctx.reply(embed=embed5, mention_author=False)
        await player.pause(True)          
        embed6 = discord.Embed(description="**<:tickk:1256186475289247814> Successfully Paused the player.**", colour=self.color)
        await ctx.reply(embed=embed6, mention_author=False)

    @commands.hybrid_command(aliases=['begin'], help="Resume the current playing music!", usage = "resume")
    @commands.cooldown(1, 5, commands.BucketType.user)  
    async def resume(self, ctx):
        if not ctx.voice_client:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any vc.",colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)        
        elif not getattr(ctx.author.voice, "channel", None):
            embed2 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.",colour=self.color)
            return await ctx.reply(embed=embed2, mention_author=False)       
        else:
            player: wavelink.player = cast(wavelink.player, ctx.voice_client)
            if ctx.author.voice.channel != player.channel:
                embed3 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in the same voice channel.", colour=self.color)
                return await ctx.reply(embed=embed3, mention_author=False)            
            if player.paused:
                await player.pause(False)
                embed4 = discord.Embed(description="**<:tickk:1256186475289247814> Resuming the player now**",colour=self.color)
                return await ctx.reply(embed=embed4, mention_author=False) 
            if not player.playing:
                embed5 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not playing anything.",colour=self.color)
                return await ctx.reply(embed=embed5, mention_author=False) 
            


    @commands.hybrid_command(aliases=['dc'], help="Stop The Music", usage = "stop")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def stop(self, ctx):
        if not ctx.voice_client:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any vc.",colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)        
        elif not getattr(ctx.author.voice, "channel", None):
            embed2 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.",colour=self.color)
            return await ctx.reply(embed=embed2, mention_author=False)       
        else:
            player: wavelink.player = cast(wavelink.player, ctx.voice_client)
            if ctx.author.voice.channel != player.channel:
                embed3 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are in not the same voice channel.", colour=self.color)
                return await ctx.reply(embed=embed3, mention_author=False)            
            if self.queuee:
                self.queuee.clear()
            await player.stop()
            embed4 = discord.Embed(description="<:tickk:1256186475289247814> Stopped music :/ ",colour=self.color)
            await ctx.reply(embed=embed4, mention_author=False)

    @commands.hybrid_command(aliases=['q'], help="Look Into The Queue", usage = "queue")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def queue(self, ctx):
        if not ctx.voice_client:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any vc.",colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)     
        if ctx.voice_client is None:
            embed2 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.",colour=self.color)
            return await ctx.reply(embed=embed2, mention_author=False)
        player: wavelink.player = cast(wavelink.player, ctx.voice_client)
        if not player.playing:
            embed3 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not playing any song.",colour=self.color)
            return await ctx.reply(embed=embed3, mention_author=False)       
        if ctx.author.voice.channel != player.channel:
            embed4 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are in not the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed4, mention_author=False)
        queue = enumerate(list(player.queue), start=1)
        track_list = '\n'.join(f'[{num}] {track.title}' for num, track in queue)
        length_seconds = round(player.current.length) / 1000
        hours, remainder = divmod(length_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        embed5 = discord.Embed(description=f'**__Now Playing__**\n  [{player.current.title}]({config.support_link})・[{duration_str}]({config.support_link})\n\n**\n- {track_list} -  [{duration_str}]**',color=self.color)
        await ctx.reply(embed=embed5, mention_author=False)

    @commands.hybrid_command(aliases=['vol'], help="Change the volume of playing music", usage = "Volume")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def volume(self, ctx: commands.Context, volume: int):
        player: wavelink.player = cast(wavelink.player, ctx.voice_client)
        if not ctx.voice_client:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any voice channel.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)      
        elif not getattr(ctx.author.voice, "channel", None):
            embed2 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.",colour=self.color)
            return await ctx.reply(embed=embed2, mention_author=False)     
        vc: wavelink.Player = ctx.voice_client
        if ctx.author.voice.channel != ctx.voice_client.channel:
            embed3 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed3, mention_author=False)                
        if not player.playing:
            embed4 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not playing anything.",colour=self.color)
            await ctx.reply(embed=embed4, mention_author=False)
            return 
        if not 0 <= volume <= 200:
            embed5 = discord.Embed(description="<:stolen_emoji:1255171779031203864> Please provide a volume to set in between 0 to 200.",colour=self.color)
            await ctx.reply(embed=embed5, mention_author=False)
            return        
        await player.set_volume(volume)
        embed6 = discord.Embed(description=f"<:tickk:1256186475289247814> Volume set to {volume}%",colour=self.color)
        await ctx.reply(embed=embed6, mention_author=False) 

    @commands.hybrid_command(aliases=['s'], help="Skip's current track")
    async def skip(self, ctx):
        player: wavelink.player = cast(wavelink.player, ctx.voice_client)
        if not player.connected:
            e = discord.Embed()
            e.color = 0x2e2e2e
            e.description = f'**<:stolen_emoji:1255171928986226730> Im not connected to any voice channel**'
            return await ctx.send(embed=e)
        if not player.playing:
            e = discord.Embed()
            e.color = 0x2e2e2e
            e.description = f'**<:stolen_emoji:1255171779031203864> Play the song to skip current song**'
            return await ctx.send(embed=e)
        if ctx.author.voice.channel != player.channel:
            e = discord.Embed()
            e.color = 0x2e2e2e
            e.description = f'**<:stolen_emoji:1255171928986226730> Please Connect to same voice channel as me.**'
            return await ctx.send(embed=e)
        i = await player.skip(force=True)
        if i:
            e = discord.Embed()
            e.color = 0x2e2e2e
            e.description = f'**<:tickk:1256186475289247814> Skipped the current playing tracks**'
            await ctx.send(embed=e)
    

    @commands.hybrid_command(aliases=['dvol'], help="Shows The Default Volume", usage = "defaultvolume")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def defaultvolume(self, ctx: commands.Context):
        player: wavelink.player = cast(wavelink.player, ctx.voice_client)
        if not ctx.voice_client:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any voice channel.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)        
        elif not getattr(ctx.author.voice, "channel", None):
            embed2 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.", colour=self.color)
            return await ctx.reply(embed=embed2, mention_author=False)      
        if ctx.author.voice.channel != ctx.voice_client.channel:
            embed3 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed3, mention_author=False)     
        if not player or not player.playing:
            embed4 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not playing anything.",colour=self.color)
            await ctx.reply(embed=embed4, mention_author=False)
            return      
        await player.set_volume(100)
        embed5 = discord.Embed(description="<:tickk:1256186475289247814> Default volume set to **`100%`**", colour=self.color)
        await ctx.reply(embed=embed5, mention_author=False)        

    @commands.hybrid_command(aliases=['j'], help="Joins the VC", usage = "join")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def join(self, ctx: commands.Context):
        if not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)
        if ctx.voice_client:
            if ctx.voice_client.channel != ctx.author.voice.channel:
                embed2 = discord.Embed(description=f"<:stolen_emoji:1255171779031203864> I am already in another voice channel", colour=self.color)
                return await ctx.reply(embed=embed2, mention_author=False)
            else:
                embed3 = discord.Embed(description=f"<:tickk:1256186475289247814> Sucessfully Joined voice channel", colour=self.color)
                await ctx.reply(embed=embed3, mention_author=False)  
        else:
            vc: wavelink.Player = await ctx.author.voice.channel.connect(cls=wavelink.Player, self_deaf=True)
            embed4 = discord.Embed(description=f"<:tickk:1256186475289247814> Successfully Joined your voice channel" , colour=self.color)
            return await ctx.reply(embed=embed4, mention_author=False)      
            

    @commands.hybrid_command(aliases=['quit'], help="Leaves The VC", usage = "leave")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def leave(self, ctx: commands.Context):
        if not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False) 
        if not ctx.voice_client:
            embed2 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any voice channel.", colour=self.color)
            return await ctx.reply(embed=embed2, mention_author=False)      
        if ctx.author.voice.channel != ctx.voice_client.channel:
            embed3 = discord.Embed(description="<:stolen_emoji:1255171779031203864> You are not in the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed3, mention_author=False)       
        await ctx.voice_client.disconnect()
        embed4 = discord.Embed(description="<:tickk:1256186475289247814> Sucessfully Left voice channel.", colour=self.color)
        await ctx.reply(embed=embed4, mention_author=False)             

    @commands.hybrid_command(aliases=['nowp'], help="Shows What's Playing", usage = "nowplaying")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def nowplaying(self, ctx):
        player: wavelink.player = cast(wavelink.player, ctx.voice_client)

        if ctx.voice_client is None:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any voice channel.",colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)      
        elif not getattr(ctx.author.voice, "channel", None):
            embed2 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.", colour=self.color)
            return await ctx.reply(embed=embed2, mention_author=False)             
        if player.paused:
            embed3 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am currently paused please use `.resume`.",colour=self.color)
            return await ctx.reply(embed=embed3, mention_author=False)
        if not player.playing:
            embed4 = discord.Embed(description="I am not playing any song.",colour=self.color)
            return await ctx.reply(embed=embed4, mention_author=False)   
        if ctx.author.voice.channel != ctx.voice_client.channel:
            embed5 = discord.Embed(description="<:stolen_emoji:1255171779031203864> You are not in the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed5, mention_author=False) 
        queue = enumerate(list(player.queue), start=1)
        length_seconds = round(player.current.length) / 1000
        hours, remainder = divmod(length_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        duration_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        embed6 = discord.Embed(title= "Now Playing", color=self.color)
        embed6.description=f"[{player.current.title}]({config.support_link})・[{duration_str}]({config.support_link})"
        await ctx.reply(embed=embed6, mention_author=False)
        
    @commands.hybrid_command(aliases=['further'], help="Forward The Track ", usage = "forward")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def forward(self, ctx):
        vc: wavelink.Player = ctx.voice_client
        player: wavelink.player = cast(wavelink.player, ctx.voice_client)
        if ctx.voice_client is None:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any voice channel.",colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)       
        elif not getattr(ctx.author.voice, "channel", None):
            embed2 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.", colour=self.color)
            return await ctx.reply(embed=embed2, mention_author=False)              
        if player.paused:
            embed3 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am currently paused please use `.resume`.",colour=self.color)
            return await ctx.reply(embed=embed3, mention_author=False)        
        if not player.playing:
            embed4 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not playing any song.",colour=self.color)
            return await ctx.reply(embed=embed4, mention_author=False)
        if ctx.author.voice.channel != ctx.voice_client.channel:
            embed5 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed5, mention_author=False)       
        position = player.position + 10000
        await player.seek(position)
        embed6 = discord.Embed(description="<:tickk:1256186475289247814> Skipped the track by **`10`** seconds.", colour=self.color)
        await ctx.reply(embed=embed6, mention_author=False)
        
    @commands.hybrid_command(aliases=['retreat'], help="Rewinds The Track", usage = "rewind")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rewind(self, ctx):
        vc: wavelink.Player = ctx.voice_client
        player: wavelink.player = cast(wavelink.player, ctx.voice_client)
        if ctx.voice_client is None:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any voice channel.",colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)      
        elif not getattr(ctx.author.voice, "channel", None):
            embed2 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.", colour=self.color)
            return await ctx.reply(embed=embed2, mention_author=False)              
        if player.paused:
            embed3 = discord.Embed(description="<:stolen_emoji:1255171779031203864> I am currently paused please use `.resume`.",colour=self.color)
            return await ctx.reply(embed=embed3, mention_author=False)       
        if not player.playing:
            embed4 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not playing any song.",colour=self.color)
            return await ctx.reply(embed=embed4, mention_author=False)       
        if ctx.author.voice.channel != ctx.voice_client.channel:
            embed5 = discord.Embed(description="<:stolen_emoji:1255171779031203864> You are not in the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed5, mention_author=False)     
        position = max(vc.position - 10000, 0)
        await player.seek(position)       
        embed6 = discord.Embed(description="<:tickk:1256186475289247814> Rewound by **`10`** seconds.", colour=self.color)
        await ctx.reply(embed=embed6, mention_author=False)
        
    @commands.hybrid_command(aliases=['look'], help="Seek Into The Track", usage = "seek <time>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def seek(self, ctx, *, time_str):
        vc: wavelink.Player = ctx.voice_client 
        player: wavelink.player = cast(wavelink.player, ctx.voice_client)     
        if ctx.voice_client is None:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any voice channel.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)       
        elif not getattr(ctx.author.voice, "channel", None):
            embed2 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.", colour=self.color)
            return await ctx.reply(embed=embed2, mention_author=False)         
        if player.paused:
            embed3 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am currently paused, please use `.resume`.", colour=self.color)
            return await ctx.reply(embed=embed3, mention_author=False)       
        if not player.playing:
            embed4 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not playing any song.", colour=self.color)
            return await ctx.reply(embed=embed4, mention_author=False)        
        if ctx.author.voice.channel != ctx.voice_client.channel:
            embed5 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed5, mention_author=False)       
        time_pattern = re.compile(r"(\d+:\d+|\d+)")
        match = time_pattern.match(time_str)
        if not match:
            embed6 = discord.Embed(description="<:stolen_emoji:1255171928986226730> Invalid time format. Please use either `mm:ss` or `ss`.", colour=self.color)
            return await ctx.reply(embed=embed6, mention_author=False)      
        time_seconds = 0
        if match.group(1):
            time_components = list(map(int, match.group(1).split(":")))
            time_seconds = sum(c * 60 ** i for i, c in enumerate(reversed(time_components)))         
            await player.seek(time_seconds * 1000)
            embed7 = discord.Embed(description=f"<:tickk:1256186475289247814> Successfully sought to {time_str}.", colour=self.color)
            await ctx.reply(embed=embed7, mention_author=False)
            
    @commands.hybrid_command(aliases=['detach'], help="Remove a Track From The Queue", usage = "remove <index>")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remove(self, ctx, index: int):
        vc: wavelink.Player = ctx.voice_client
        player: wavelink.player = cast(wavelink.player, ctx.voice_client)
        if ctx.voice_client is None:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any voice channel.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)            
        elif not getattr(ctx.author.voice, "channel", None):
            embed2 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.", colour=self.color)
            return await ctx.reply(embed=embed2, mention_author=False)           
        if player.paused:
            embed3 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am currently paused, please use `.resume`.", colour=self.color)
            return await ctx.reply(embed=embed3, mention_author=False)          
        if not player.playing:
            embed4 = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not playing any song.", colour=self.color)
            return await ctx.reply(embed=embed4, mention_author=False)          
        if ctx.author.voice.channel != ctx.voice_client.channel:
            embed5 = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed5, mention_author=False)       
        if not player.queue or index > len(player.queue) or index < 1:
            embed6 = discord.Embed(description=f"<:stolen_emoji:1255171928986226730> Invalid index. Must be between 1 and {len(player.queue)}", color=self.color)              
            return await ctx.reply(embed=embed6, mention_author=False)             
        removed = list(player.queue).pop(index - 1)
        player.queue = list(player.queue)[:index - 1] + list(player.queue)[index:]
        embed7 = discord.Embed(description=f"<:tickk:1256186475289247814> Successfully removed `[{removed.title}]({config.support_link})` from Queue.", color=self.color)    
        await ctx.reply(embed=embed7, mention_author=False)


async def setup(client):
    await client.add_cog(Music(client))