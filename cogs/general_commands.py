import discord, time
import cogs.variables as var
from discord.ext import commands
from discord import app_commands


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
                f"{var.error} This is not your command. Shoo!",
                ephemeral=True,
            )
        
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page], view=self
            )
        else:
            await interaction.response.send_message(
                f"{var.error} You are already on the first page."
                ,ephemeral=True)


    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.user.id:
            return await interaction.response.send_message(
                f"{var.error} This is not your command. Shoo!",
                ephemeral=True,
            )

        if self.current_page < len(self.embeds) - 1:
            self.current_page += 1
            await interaction.response.edit_message(
                embed=self.embeds[self.current_page], view=self
            )
        else:
            await interaction.response.send_message(
                f"{var.error} You are already on the last page."
                ,ephemeral=True)


class general_commands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
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
        await interaction.response.defer()
        bot_embed_colour = interaction.user.colour
        latency = self.bot.latency * 1000
        pingembed = discord.Embed(
            title="Pong",
            description=f"-# The bot took {latency:.2f} ms to respond to this command.",
            colour=bot_embed_colour,
        )
        await interaction.followup.send(embed=pingembed)
    
    
    # help command
    
    
    @app_commands.command(name="help", description="How does the bot work?")
    async def helpmessage(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot_embed_colour = interaction.user.colour
        help_command_list = discord.Embed(
            title="Help Menu:",
            description="A list of this bot's commands. They're all slash commands, there is no prefix.",
            colour=bot_embed_colour,
        )
        for cmd in self.bot.tree.get_commands():
            if isinstance(cmd, app_commands.Group):
                for sub in cmd.commands:
                    help_command_list.add_field(
                        name=f"{cmd.name} {sub.name}",
                        value=sub.description or "No description available",
                        inline=False,
                    )
            else:
                help_command_list.add_field(
                name=cmd.name, 
                value=cmd.description or "No description available", 
                inline=False
                )
        help_command_list.set_footer(text="Page 2 of 2")

        counting_game_info = discord.Embed(
            title="The Counting Game:",
            description=("This is the bot's primary purpose, to run the counting game. The rules are pretty simple:\n"
            "- Count in consecutive numbers, the goal is to get as high as possible.\n"
            "- You cannot count twice in a row.\n"
            "- Violations will result in the count being reset to the last multiple of 100.\n"
            "-  Some numbers are special and will merit a reaction from the bot. Keep an eye out for them!"),
            colour=bot_embed_colour,
        )
        counting_game_info.set_footer(text="Page 1 of 2")
        
        help_embed_list = [counting_game_info, help_command_list]
        view = HelpPage(user=interaction.user, embeds=help_embed_list)
        await interaction.followup.send(embed=help_embed_list[0], view=view)


    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context):
        start_time = time.time()
        try:
            synced = await self.bot.tree.sync()
            end_time = time.time()
            duration = end_time - start_time
            await ctx.send(
                f"Synced {len(synced)} commands globally in {duration:.2f} seconds."
            )
        except discord.HTTPException as e:
            await ctx.send(f"Error while syncing: {str(e)}")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.NotOwner):
            await ctx.send(
                f"{var.error} You do not have permission to use this command. This command is reserved for the bot owner."
            )
        else:
            raise error


async def setup(bot: commands.Bot):
    cog = (general_commands(bot))
    await bot.add_cog(cog)