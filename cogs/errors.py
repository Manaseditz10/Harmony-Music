from discord.ext import commands
import discord

class error(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        error = getattr(error, 'original', error)

        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="Missing Argument",
                description=f"You are missing the `{error.param.name}` argument.",
                color=discord.Color.red()
            )
            embed.add_field(name="Command Usage", value=f"`{ctx.prefix}{ctx.command.qualified_name} {ctx.command.signature}`")
            await ctx.send(embed=embed)
        else:
            raise error
        
        if isinstance(error, commands.CommandOnCooldown):
            bucket = commands.CooldownMapping.from_cooldown(1, 5, commands.BucketType.user)
            retry_after = bucket.get_bucket(ctx.message).update_rate_limit()
            if retry_after:
                return
            cooldown_embed = discord.Embed(description=f"You're on cooldown. Try again in **{round(error.retry_after, 2)}** seconds.", color=0x2b2d31)
            return await ctx.reply(embed=cooldown_embed, mention_author=False)
        if isinstance(error, commands.UserNotFound):
            user_not_found_embed = discord.Embed(description="The specified user was not found.", color=0x2b2d31)
            return await ctx.reply(embed=user_not_found_embed, mention_author=False)
        if isinstance(error, commands.MemberNotFound):
            member_not_found_embed = discord.Embed(description="The specified member was not found.", color=0x2b2d31)
            return await ctx.reply(embed=member_not_found_embed, mention_author=False)
        if isinstance(error, commands.RoleNotFound):
            role = error.argument
            role_not_found_embed = discord.Embed(description=f"The role **{role}** was not found.", color=0x2b2d31)
            return await ctx.reply(embed=role_not_found_embed, mention_author=False)
        if isinstance(error, commands.ChannelNotFound):
            channel = error.argument
            channel_not_found_embed = discord.Embed(description=f"The channel **{channel}** was not found.", color=0x2b2d31)
            return await ctx.reply(embed=channel_not_found_embed, mention_author=False)
        if isinstance(error, commands.MaxConcurrencyReached):
            max_concurrency_embed = discord.Embed(description=f"**{ctx.author}**, **{error}**", color=0x2b2d31)     
            return await ctx.reply(embed=max_concurrency_embed, mention_author=False)
        if isinstance(error, commands.CheckAnyFailure):
                if isinstance(error, commands.MissingPermissions):
                    missing_perms = ', '.join(error.missing_perms)
                    
                    embed = discord.Embed(
                        title="Missing Permissions",
                        description="❌ **You are missing the following permissions to run this command:**",
                        color=discord.Color.red()
                    )
                    
                    embed.add_field(name="Missing Permissions", value=missing_perms, inline=False)
                    embed.add_field(name="Command", value=f"`{ctx.prefix}{ctx.command}`", inline=False)
                    embed.add_field(name="Required Permissions", value=", ".join(ctx.command.checks[0].__closure__[0].cell_contents), inline=False)
                    await ctx.send(embed=embed)
                else:
                    raise error

async def setup(client):
    await client.add_cog(error(client))