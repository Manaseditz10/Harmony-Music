import discord
from discord.ext import commands
import wavelink

class Filters(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.filters = {}
        self.color = 0x2F3136  

    @commands.Cog.listener()
    async def on_ready(self):
        print("Filters Is Ready")

    async def apply_filters(self, ctx, filter_name, filters):
        player: wavelink.Player = ctx.voice_client

        if not player:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any vc.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)

        if not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)

        if ctx.author.voice.channel != player.channel:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)

        if not player.playing:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not playing anything.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)

        if player.paused:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am currently paused please use `.resume`.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)

        await player.set_filters(filters)
        embed = discord.Embed(description=f"`{filter_name.capitalize()}` **filter has been applied!**\n**( It takes 5 second to apply filter.)**", color=self.color)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(aliases=['retro'], help="Music Like Retro", usage="vaporwave")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def vaporwave(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.timescale.set(speed=0.8, pitch=0.8)
        await self.apply_filters(ctx, "vaporwave", filters)

    @commands.hybrid_command(aliases=['classic'], help="Classic Music", usage="lofi")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lofi(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.timescale.set(speed=0.7500000238418579, pitch=0.800000011920929, rate=1)
        await self.apply_filters(ctx, "lofi", filters)

    @commands.hybrid_command(name="8d", aliases=['Rotation'], help="Surrounder Effect", usage="8d")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def _8d(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.rotation.set(rotation_hz=0.2)
        await self.apply_filters(ctx, "8d", filters)

    @commands.hybrid_command(aliases=['slow'], help="Slowed Music", usage="slowmo")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slowmo(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.timescale.set(speed=0.7)
        await self.apply_filters(ctx, "slowmo", filters)

    @commands.hybrid_command(aliases=['bass'], help="Hear The Boosted Music", usage="bassboost")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def bassboost(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.equalizer.set(band=[(0, 0.6), (1, 0.5), (2, 0.4), (3, 0.3), (4, 0.2)])
        await self.apply_filters(ctx, "bassboost", filters)

    @commands.hybrid_command(aliases=['nc'], help="Nightcore effect", usage="nightcore")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def nightcore(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.timescale.set(speed=1.2, pitch=1.2)
        await self.apply_filters(ctx, "nightcore", filters)

    @commands.hybrid_command(aliases=['tremoloo'], help="Tremolo effect", usage="tremolo")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def tremolo(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.tremolo.set(frequency=4.0, depth=0.5)
        await self.apply_filters(ctx, "tremolo", filters)

    @commands.hybrid_command(aliases=['vibratoo'], help="Vibrato effect", usage="vibrato")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def vibrato(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.vibrato.set(frequency=4.0, depth=0.5)
        await self.apply_filters(ctx, "vibrato", filters)
        
    @commands.hybrid_command(aliases=['reversee'], help="Reverse the audio", usage="reverse")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reverse(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.timescale.set(speed=-1)
        await self.apply_filters(ctx, "reverse", filters)

    @commands.hybrid_command(aliases=['chipmunkk'], help="Chipmunk voice effect", usage="chipmunk")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def chipmunk(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.timescale.set(speed=1.5, pitch=1.5)
        await self.apply_filters(ctx, "chipmunk", filters)

    @commands.hybrid_command(aliases=['darthh'], help="Darth Vader voice effect", usage="darthvader")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def darthvader(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.timescale.set(speed=0.8, pitch=0.7)
        await self.apply_filters(ctx, "darth vader", filters)
    @commands.hybrid_command(aliases=['kara'], help="Karaoke effect", usage="karaoke")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def karaoke(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.karaoke.set(level=1.0, mono_level=1.0, filter_band=220.0, filter_width=100.0)
        await self.apply_filters(ctx, "karaoke", filters)

    @commands.hybrid_command(aliases=['chan'], help="Channel mixer effect", usage="channelmix")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def channelmix(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.channel_mix.set(left_to_left=0.5, left_to_right=0.5, right_to_left=0.5, right_to_right=0.5)
        await self.apply_filters(ctx, "channel mix", filters)

    @commands.hybrid_command(aliases=['dist'], help="Distortion effect", usage="distortion")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def distortion(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.distortion.set(sin_offset=0, sin_scale=1, cos_offset=0, cos_scale=1, tan_offset=0, tan_scale=1, offset=0, scale=1)
        await self.apply_filters(ctx, "distortion", filters)

    @commands.hybrid_command(aliases=['lowp'], help="Low pass filter", usage="lowpass")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lowpass(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.low_pass.set(smoothing=20.0)
        await self.apply_filters(ctx, "low pass", filters)

    @commands.hybrid_command(aliases=['robo'], help="Robot voice effect", usage="robot")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def robot(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.timescale.set(speed=0.9, pitch=0.5, rate=0.1)
        await self.apply_filters(ctx, "robot", filters)

    @commands.hybrid_command(aliases=['echoo'], help="Echo effect", usage="echo")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def echo(self, ctx: commands.Context):
        filters = wavelink.Filters()
        filters.timescale.set(delay=0.5, decay=0.5)
        await self.apply_filters(ctx, "echo", filters)
      
   
    @commands.hybrid_command(aliases=['rfilters'], help="Removes All The Filters", usage="reset")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def reset(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        
        if not player:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not connected to any vc.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)
        
        if not getattr(ctx.author.voice, "channel", None):
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in a voice channel.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)
        
        if ctx.author.voice.channel != player.channel:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> You are not in the same voice channel.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)
        
        if not player.playing:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am not playing anything.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)
        
        if player.paused:
            embed = discord.Embed(description="<:stolen_emoji:1255171928986226730> I am currently paused please use `.resume`.", colour=self.color)
            return await ctx.reply(embed=embed, mention_author=False)

        await player.set_filters(wavelink.Filters())
        embed = discord.Embed(description=f"<:tickk:1256186475289247814> All the filters have been reset.\n**( It takes 5 second to reset filter.)**", color=self.color)
        await ctx.reply(embed=embed, mention_author=False)

async def setup(client):
    await client.add_cog(Filters(client))