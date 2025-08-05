import discord, textwrap
from discord.ext import commands
from discord import app_commands
from main import CatCafeBot, bot_embed_colour
from .ai_handler import gemini_response


class counting_game(commands.Cog):
    
    cross_reaction = "<a:cross:1329494914945515593>"
    tick_reaction = "<a:tick:1329494885279203450>"
    bluetick_reaction = "<a:bluetick:1329495657383329883>"
    hundred_reaction = "💯"
    
    def __init__(self, bot:CatCafeBot):
        self.bot = bot
        self.bot_embed_colour = bot_embed_colour
        self.bot.load_count()
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or self.bot.counting_channel is None or message.channel.id != self.bot.counting_channel:
            return
        if not message.content.isdigit():
            return

        counted_number = int(message.content)

        if message.author.id == self.bot.last_user_id:
            try:
                repeated_user_response = await gemini_response(
                    user_prompt=textwrap.dedent(f"""Note that the user is not allowed to count more than once at a time.
                    Comment on the user's failure to follow the rules with an insulting or mocking response.""")
                )
                await message.reply(repeated_user_response)
            except Exception as e:
                print(f"Error generating response: {e}")
                await message.reply(textwrap.dedent(
                """What are you incapable of, following the rules, or reading?"""
                    )
                )
            await self.reset_count_handler(message)
            return

        if counted_number != self.bot.current_count + 1:
            try:
                not_consecutive_response = await gemini_response(
                    user_prompt=textwrap.dedent(f"""The user has counted the wrong number.
                    Comment on the same with an insulting or mocking response. """)
                    )
                await message.reply(not_consecutive_response)
            except Exception as e:
                print(f"Error generating response: {e}")
                await message.reply(textwrap.dedent(
                """It appears that you've either forgotten the meaning of 'consecutive' or what the next number is. Pity."""
                    )
                )
            await self.reset_count_handler(message)
            return

        await self.correct_count_handler(message, counted_number)

    async def reset_count_handler(self, message):
        self.bot.current_count = (self.bot.current_count // 100) * 100
        self.bot.next_number = self.bot.current_count + 1
        self.bot.current_streak = 0
        self.bot.last_user_id = None
        self.bot.save_count()
        await message.add_reaction(self.cross_reaction)
        await message.channel.send(f"The next number is {self.bot.next_number}")

    async def correct_count_handler(self, message, counted_number):
        self.bot.current_count = counted_number
        self.bot.next_number = counted_number + 1
        self.bot.last_user_id = message.author.id
        self.bot.latest_message = message.id
        self.bot.record_save(message.author.id)
        self.bot.save_count()

        def special_number_checker(counted_number):
            checker_response = []
            # Sequence Checker
            num_digits = list(map(int, str(counted_number)[::-1]))
            if all(
                num_digits[i] - 1 == num_digits[i + 1]
                for i in range(len(num_digits) - 1)
            ) or all(
                num_digits[i] + 1 == num_digits[i + 1]
                for i in range(len(num_digits) - 1)
            ):
                checker_response.append(textwrap.dedent(
                """Hey, that's a perfect sequence[!]
                (https://tenor.com/view/thats-it-yes-thats-it-that-right-there-omg-that-thats-what-i-mean-gif-17579879)"""
                    )
                )
            # Palindrome Checker
            if str(counted_number) == str(counted_number)[::-1]:
                checker_response.append(textwrap.dedent(
                """Hey, that's a palindrome[!]
                (https://tenor.com/view/thats-it-yes-thats-it-that-right-there-omg-that-thats-what-i-mean-gif-17579879)"""
                    )
                )
            # SixtyNice Checker
            if "69" in str(counted_number) and "69" not in str(counted_number - 1):
                checker_response.append(
                "https://tenor.com/view/noice-nice-click-gif-8843762"
                )
            # Order 66 Checker
            if "66" in str(counted_number) and "66" not in str(counted_number - 1):
                checker_response.append(
                "https://tenor.com/view/execute-order66-order66-66-palpatine-star-wars-gif-20468321"
                )
            # Devil's Number Checker
            if "666" in str(counted_number) and "666" not in str(counted_number - 1):
                checker_response.append(
                "https://tenor.com/view/hail-satan-gif-25445039"
                )
            return checker_response

        if counted_number % 100 == 0:
            await message.add_reaction(self.hundred_reaction)
        elif counted_number == self.bot.counting_record:
            await message.add_reaction(self.bluetick_reaction)
        else:
            await message.add_reaction(self.tick_reaction)

        for i in special_number_checker(counted_number):
            await message.channel.send(i)


    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if self.bot.counting_channel is None:
            return
        if before.channel.id != self.bot.counting_channel:
            return
        if before.id == self.bot.latest_message:
            await before.channel.send(textwrap.dedent(
                f"""{before.author.mention} has edited their message, the sneaky devil!
                \nTheir number was {self.bot.current_count}. The next number is {self.bot.next_number}."""
                )
            )


    @commands.Cog.listener()
    async def on_message_delete(self, message=discord.Message):
        if self.bot.counting_channel is None:
            return
        if message.channel.id != self.bot.counting_channel:
            return
        if message.id == self.bot.latest_message:
            await message.channel.send(textwrap.dedent(
                f"""{message.author.mention} has deleted their message, the sneaky devil!
                \nTheir number was {self.bot.current_count}. The next number is {self.bot.next_number}."""
                )
            )


    # slash commands

    @app_commands.command(name="status", description="A full run-down of the bot's status.")
    async def status(self, interaction: discord.Interaction):
        statusembed = discord.Embed(
            title="All bot stats:",
            description=textwrap.dedent(f"""Channel: <#{self.bot.counting_channel}>\n
            Current Count: {self.bot.current_count}\n
            Next: {self.bot.next_number}\n
            Last user: <@{self.bot.last_user_id}>\n
            Reset Point: {(self.bot.current_count // 100) * 100}\n
            Record: {self.bot.counting_record}\n
            Record Holder: <@{self.bot.record_holder}>\n
            Current Streak: {self.bot.current_streak}\n
            Record Streak: {self.bot.record_streak}"""),
            colour=self.bot_embed_colour,
        )
        await interaction.response.send_message(embed=statusembed)


    @app_commands.command(name="record", description="Displays this server's counting record.")
    async def record(self, interaction: discord.Interaction):
        recordmebed = discord.Embed(
            title="Counting Record:",
            description=textwrap.dedent(f"""This server's counting record is __**{self.bot.counting_record}**__.
            \nIt was achieved by <@{self.bot.record_holder}>."""),
            colour=self.bot_embed_colour,
        )
        await interaction.response.send_message(embed=recordmebed)


    @app_commands.command(
        name="next",
        description="Tells you what the next number is. Because apparently reading is hard.",
    )
    async def nextnumber(self, interaction: discord.Interaction):
        nextembed = discord.Embed(
            title="Next Number:",
            description=textwrap.dedent(f"""The next number is __**{self.bot.next_number}**__.
            \nThe last person to count was <@{self.bot.last_user_id}>."""),
            colour=self.bot_embed_colour,
        )
        await interaction.response.send_message(embed=nextembed)


    @app_commands.command(
        name="streak", description="Displays the current and record counting streaks."
    )
    async def streakinfo(self, interaction: discord.Interaction):
        streakembed = discord.Embed(
            title="Streak Information:",
            description=textwrap.dedent(f"""The current streak is __**{self.bot.current_streak}**__.
            \nThe streak record is __**{self.bot.record_streak}**__."""),
            colour=self.bot_embed_colour,
        )
        await interaction.response.send_message(embed=streakembed)
    
    
    @commands.command()
    @commands.is_owner()
    async def setchannel(self, ctx: commands.Context, channel: discord.TextChannel = None):
        if self.bot.counting_channel is not None:
            return await ctx.send("Channel already set.")

        target_channel = channel or ctx.channel
        self.bot.counting_channel = target_channel.id
        self.bot.save_count()
        await ctx.send(
            f"Counting channel set to {target_channel.mention}. Let the counting begin!"
        )
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.NotOwner):
            await ctx.send(
                "You do not have permission to use this command. This command is reserved for the bot owner."
            )
        else:
            raise error

        
async def setup(bot: CatCafeBot):
    await bot.add_cog(counting_game(bot))