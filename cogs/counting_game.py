import discord,asyncio
from discord.ext import commands
from discord import app_commands
from .ai_commentator import openai_response


class counting_game(commands.Cog):
    
    cross_reaction = "<a:cross:1329494914945515593>"
    tick_reaction = "<a:tick:1329494885279203450>"
    bluetick_reaction = "<a:bluetick:1329495657383329883>"
    hundred_reaction = "💯"
    
    def __init__(self, bot:commands.Bot):
        self.bot = bot
        self.bot.load_count()
    
    async def daily_status_update(self, bot: commands.Bot):
        while True:
            await asyncio.sleep(21600)
            channel = self.bot.get_channel(1309124072738787378) or await self.bot.fetch_channel(1309124072738787378)
            bot_embed_colour = discord.Colour.blurple()
            statusembed = discord.Embed(
                title="All bot stats:",
                description=f"Channel: <#{self.bot.counting_channel}>\n"
                f"Current Count: {self.bot.current_count}\n"
                f"Next: {self.bot.next_number}\n"
                f"Last user: <@{self.bot.last_user_id}>\n"
                f"Reset Point: {(self.bot.current_count // 100) * 100}\n"
                f"Record: {self.bot.counting_record}\n"
                f"Record Holder: <@{self.bot.record_holder}>\n"
                f"Current Streak: {self.bot.current_streak}\n"
                f"Record Streak: {self.bot.record_streak}",
                colour=bot_embed_colour,
            )
            await channel.send(content= "Six-hour update...", embed=statusembed)
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or self.bot.counting_channel is None or message.channel.id != self.bot.counting_channel:
            return
        if not message.content.isdigit():
            return

        counted_number = int(message.content)

        if message.author.id == self.bot.last_user_id:
            try:
                repeated_user_response = await openai_response(
                    user_prompt="Chastise the user for counting repeatedly."
                )
                await message.reply(repeated_user_response)
            except Exception as e:
                print(f"Error generating response: {e}")
                await message.reply("What are you incapable of, following the rules, or reading?")
            await self.reset_count_handler(message)
            return

        if counted_number != self.bot.current_count + 1:
            try:
                not_consecutive_response = await openai_response(
                    user_prompt="Admonish the user for counting the wrong number."
                    )
                await message.reply(not_consecutive_response)
            except Exception as e:
                print(f"Error generating response: {e}")
                await message.reply(
                    "It appears that you've either forgotten the meaning of 'consecutive' or what the next number is. Pity."
                    )
            await self.reset_count_handler(message)
            return

        await self.correct_count_handler(message, counted_number)

    async def reset_count_handler(self, message):
        self.bot.current_count = (self.bot.current_count // 100) * 100
        self.bot.next_number = self.bot.current_count + 1
        self.bot.current_streak = 0
        self.bot.last_user_id = None
        try:
            self.bot.save_count()
        except Exception as e:
            channel = self.bot.get_channel(1309124072738787378) or await self.bot.fetch_channel(1309124072738787378)
            await channel.send(f"Save Count error:\n{e.__cause__}")
            pass
        await message.add_reaction(self.cross_reaction)
        await message.channel.send(f"The next number is {self.bot.next_number}")

    async def correct_count_handler(self, message, counted_number):
        self.bot.current_count = counted_number
        self.bot.next_number = counted_number + 1
        self.bot.last_user_id = message.author.id
        self.bot.latest_message = message.id
        self.bot.record_save(message.author.id)
        try:
            self.bot.save_count()
        except Exception as e:
            channel = self.bot.get_channel(1309124072738787378) or await self.bot.fetch_channel(1309124072738787378)
            await channel.send(f"Save Count error:\n{e.__cause__}")
            pass

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
                checker_response.append(
                "Hey, that's a perfect sequence[!](https://tenor.com/view/thats-it-yes-thats-it-that-right-there-omg-that-thats-what-i-mean-gif-17579879)"
                    )

            # Palindrome Checker
            if str(counted_number) == str(counted_number)[::-1]:
                checker_response.append(
                "Hey, that's a palindrome[!](https://tenor.com/view/thats-it-yes-thats-it-that-right-there-omg-that-thats-what-i-mean-gif-17579879)"
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
            try:
                edited_response = await openai_response(
                    user_prompt="Inform the channel that the last person to count has edited their message."
                )
                await before.channel.send(
                    (f"{edited_response}\n The number was {self.bot.current_count}.\n"
                    f"The next number is {self.bot.next_number}.")
                    )
            except Exception as e:
                print(f"Error generating response: {e}")
                await before.channel.send(
                    f"{before.author.mention} has edited their message, the sneaky devil!\n"
                    f"The number was {self.bot.current_count}. The next number is {self.bot.next_number}."
                    )


    @commands.Cog.listener()
    async def on_message_delete(self, message=discord.Message):
        if self.bot.counting_channel is None:
            return
        if message.channel.id != self.bot.counting_channel:
            return
        if message.id == self.bot.latest_message:
            try:
                deleted_response = await openai_response(
                    user_prompt="Inform the channel that the last person to count has deleted their message."
                    )
                await message.channel.send(
                    f"{deleted_response}\n The number was {self.bot.current_count}.\n"
                    f"The next number is {self.bot.next_number}."
                    )
            except Exception as e:
                print(f"Error generating response: {e}")
                await message.channel.send(
                    f"{message.author.mention} has deleted their message, the sneaky devil!\n"
                    f"Their number was {self.bot.current_count}. The next number is {self.bot.next_number}."
                    )


    # slash commands
    counting_commands = app_commands.Group(name="counting", description="commands related to the counting game")

    @counting_commands.command(name="status", description="A full run-down of the bot's status.")
    async def status(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot_embed_colour = interaction.user.colour
        statusembed = discord.Embed(
            title="All bot stats:",
            description=f"Channel: <#{self.bot.counting_channel}>\n"
            f"Current Count: {self.bot.current_count}\n"
            f"Next: {self.bot.next_number}\n"
            f"Last user: <@{self.bot.last_user_id}>\n"
            f"Reset Point: {(self.bot.current_count // 100) * 100}\n"
            f"Record: {self.bot.counting_record}\n"
            f"Record Holder: <@{self.bot.record_holder}>\n"
            f"Current Streak: {self.bot.current_streak}\n"
            f"Record Streak: {self.bot.record_streak}",
            colour=bot_embed_colour,
        )
        await interaction.followup.send(embed=statusembed)


    @counting_commands.command(name="record", description="Displays this server's counting record.")
    async def record(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot_embed_colour = interaction.user.colour
        recordmebed = discord.Embed(
            title="Counting Record:",
            description=f"This server's counting record is __**{self.bot.counting_record}**__.\n"
            f"It was achieved by <@{self.bot.record_holder}>.",
            colour=bot_embed_colour,
        )
        await interaction.followup.send(embed=recordmebed)


    @counting_commands.command(
        name="next",
        description="Tells you what the next number is. Because apparently reading is hard.",
    )
    async def nextnumber(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot_embed_colour = interaction.user.colour
        nextembed = discord.Embed(
            title="Next Number:",
            description=f"The next number is __**{self.bot.next_number}**__.\n"
            f"The last person to count was <@{self.bot.last_user_id}>.",
            colour=bot_embed_colour,
        )
        await interaction.followup.send(embed=nextembed)


    @counting_commands.command(
        name="streak", description="Displays the current and record counting streaks."
    )
    async def streakinfo(self, interaction: discord.Interaction):
        await interaction.response.defer()
        bot_embed_colour = interaction.user.colour
        streakembed = discord.Embed(
            title="Streak Information:",
            description=f"The current streak is __**{self.bot.current_streak}**__.\n"
            f"The streak record is __**{self.bot.record_streak}**__.",
            colour=bot_embed_colour,
        )
        await interaction.followup.send(embed=streakembed)
    
    
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

        
async def setup(bot: commands.Bot):
    cog = (counting_game(bot))
    await bot.add_cog(cog)

    async def _start_loop():
        await bot.wait_until_ready()
        bot.loop.create_task(cog.daily_status_update(bot))
    bot.loop.create_task(_start_loop())