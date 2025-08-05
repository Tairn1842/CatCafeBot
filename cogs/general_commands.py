import discord, textwrap
from discord.ext import commands
from discord import app_commands
from main import CatCafeBot, bot_embed_colour

class HelpPage(discord.ui.View):
    def __init__(self, user, embeds):
        super().__init__(timeout=None) 
        self.user = user
        self.embeds = embeds
        self.current_page = 0

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(
                "<a:cross:1329494914945515593> This is not your command. Shoo!",
                ephemeral=True,
            )
        
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page], view=self
            )
        else:
            await interaction.response.send_message(
                "<a:cross:1329494914945515593> You are already on the first page."
                ,ephemeral=True)


    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(
                "<a:cross:1329494914945515593> This is not your command. Shoo!",
                ephemeral=True,
            )

        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page], view=self
            )
        else:
            await interaction.response.send_message(
                "<a:cross:1329494914945515593> You are already on the last page."
                ,ephemeral=True)

class general_commands(commands.Cog):
    def __init__(self, bot: CatCafeBot):
        self.bot = bot
        self.bot_embed_colour = bot_embed_colour
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        
        if "hello there" in message.content.lower():
            await message.reply(
                "https://tenor.com/view/hello-there-general-kenobi-star-wars-grevious-gif-17774326"
            )
    
    @app_commands.command(name="ping", description="How quickly is the bot responding?")
    async def botping(self, interaction: discord.Interaction):
        latency = self.bot.latency * 1000
        pingembed = discord.Embed(
            title="Pong",
            description=f"-# The bot took {latency:.2f} ms to respond to this command.",
            colour=bot_embed_colour,
        )
        await interaction.response.send_message(embed=pingembed)
    
    
    # help command
    
    
    @app_commands.command(name="help", description="How does the bot work?")
    async def helpmessage(self, interaction: discord.Interaction):

        help_command_list = discord.Embed(
            title="Help Menu:",
            description="A list of this bot's commands. They're all slash commands, there is no prefix.",
            colour=bot_embed_colour,
        )
        for cmd in self.bot.tree.get_commands():
            help_command_list.add_field(
                name=f"/{cmd.name}", value=cmd.description, inline=False
            )
        help_command_list.set_footer(text="Page 2 of 2")

        counting_game_info = discord.Embed(
            title="The Counting Game:",
            description=textwrap.dedent("""This is the bot's primary purpose, to run the counting game. The rules are pretty simple:
            \n - Count in consecutive numbers, the goal is to get as high as possible.
            \n - You cannot count twice in a row.
            \n - Failing to follow either of these rules will result in the count being reset to the last multiple of 100.
            \n -  Some numbers are special and will merit a reaction from the bot. Keep an eye out for them!"""),
            colour=bot_embed_colour,
        )
        counting_game_info.set_footer(text="Page 1 of 2")
        
        help_embed_list = [counting_game_info, help_command_list]
        view = HelpPage(user=interaction.user, embeds=help_embed_list)
        await interaction.response.send_message(embed=help_embed_list[0], view=view)


async def setup(bot: CatCafeBot):
    await bot.add_cog(general_commands(bot))