import discord
from discord.ext import commands
from discord.ui import Button, View

# Global color variable
global_color = discord.Color.default()

def create_embed(title: str, description: str) -> discord.Embed:
    """Helper function to create an embed with the global color."""
    return discord.Embed(title=title, description=description, color=global_color)

class ColorChangeView(View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label='Blue', style=discord.ButtonStyle.primary, custom_id='blue')
    async def blue_button(self, interaction: discord.Interaction, button: Button):
        global global_color
        global_color = discord.Color.blue()
        await self.change_color(interaction, global_color)

    @discord.ui.button(label='Red', style=discord.ButtonStyle.danger, custom_id='red')
    async def red_button(self, interaction: discord.Interaction, button: Button):
        global global_color
        global_color = discord.Color.red()
        await self.change_color(interaction, global_color)

    @discord.ui.button(label='Yellow', style=discord.ButtonStyle.secondary, custom_id='yellow')
    async def yellow_button(self, interaction: discord.Interaction, button: Button):
        global global_color
        global_color = discord.Color.yellow()
        await self.change_color(interaction, global_color)

    @discord.ui.button(label='Green', style=discord.ButtonStyle.success, custom_id='green')
    async def green_button(self, interaction: discord.Interaction, button: Button):
        global global_color
        global_color = discord.Color.green()
        await self.change_color(interaction, global_color)

    @discord.ui.button(label='Grey', style=discord.ButtonStyle.secondary, custom_id='grey')
    async def grey_button(self, interaction: discord.Interaction, button: Button):
        global global_color
        global_color = discord.Color.greyple()
        await self.change_color(interaction, global_color)

    @discord.ui.button(label='Custom Color', style=discord.ButtonStyle.primary, custom_id='custom')
    async def custom_button(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Please provide a hex color code (e.g., #FF5733).", ephemeral=True)
        # Implement custom color handling logic here

    async def change_color(self, interaction: discord.Interaction, color: discord.Color):
        embed = create_embed("Colored Embed", "This embed color has been changed.")
        await interaction.response.edit_message(embed=embed, view=None)

class ColorCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='setembedcolor')
    async def setembedcolor(self, ctx):
        view = ColorChangeView()
        await ctx.send(content="Choose an Embed Color", view=view)


async def setup(bot):
    await bot.add_cog(ColorCog(bot))
