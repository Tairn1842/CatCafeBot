import discord
from discord.ext import commands
from discord import app_commands
import json
import os
from dotenv import load_dotenv
import time

load_dotenv()
bottoken = os.getenv("token")


# Bot defintion.


intents = discord.Intents.all()
bot_embed_colour = discord.Colour.from_str("#5865f2")


class CountingBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="$", intents=intents, help_command=None)
        self.current_count = 0
        self.last_user_id = None
        self.last_reset = 0
        self.counting_channel = None
        self.latest_message = None
        self.counting_record = 0
        self.record_holder = None
        self.current_streak = 0
        self.record_streak = 0

        self.load_count()
        self.next_number = self.current_count + 1

    def load_count(self):
        if os.path.exists("icb_memory.json"):
            with open("icb_memory.json", "r") as f:
                try:
                    data = json.load(f)
                    self.current_count = data.get("current_count", 0)
                    self.last_user_id = data.get("last_user_id", None)
                    self.last_reset = data.get("last_reset", 0)
                    self.counting_channel = data.get("counting_channel", None)
                    self.latest_message = data.get("latest_message", None)
                    self.counting_record = data.get("counting_record", 0)
                    self.record_holder = data.get("record_holder", None)
                    self.current_streak = data.get("current_streak",0)
                    self.record_streak = data.get("record_streak",0)
                except json.JSONDecodeError:
                    self.save_count()

    def save_count(self):
        data = {
            "current_count": self.current_count,
            "last_user_id": self.last_user_id,
            "last_reset": self.last_reset,
            "counting_channel": self.counting_channel,
            "latest_message": self.latest_message,
            "counting_record": self.counting_record,
            "record_holder": self.record_holder,
            "current_streak": self.current_streak,
            "record_streak": self.record_streak
            }
        with open("icb_memory.json", "w") as f:
            json.dump(data, f)

    def record_save(self, message_author):
        if self.current_count > self.counting_record:
            self.counting_record = self.current_count
            self.record_holder = message_author


# Interaction Handler.


class CountingBot_MessageHandler:
    cross_reaction = "<a:cross:1329494914945515593>"
    tick_reaction = "<a:tick:1329494885279203450>"
    bluetick_reaction = "<a:bluetick:1329495657383329883>"
    hundred_reaction = "💯"
    
    def __init__(self, bot):
        self.bot = bot
    async def message_handler(self,message):
        if message.author.bot:
            return
        
        if message.content.startswith(self.bot.command_prefix):
            await self.bot.process_commands(message)
            return
        
        if self.bot.counting_channel is None:
            return
        
        if message.channel.id != self.bot.counting_channel:
            return
        
        if not message.content.isdigit():
            return
        
        counted_number = int(message.content)
        
        if message.author.id == self.bot.last_user_id:
            await message.channel.send("Greedy much? You aren't soloing this count! Wait for someone else before you rush in.")
            await self.reset_count_handler(message)
            return
        
        if counted_number != self.bot.current_count + 1:
            await message.channel.send("Did you forget to learn how to count? Or do you not know what 'consequtive' means?")
            await self.reset_count_handler(message)
            return
        
        await self.correct_count_handler(message,counted_number)
        
    async def reset_count_handler(self,message):
        self.bot.current_count = self.bot.last_reset
        self.bot.next_number = self.bot.current_count + 1
        self.bot.current_streak = 0
        self.bot.last_user_id = None
        self.bot.save_count()
        await message.add_reaction(self.cross_reaction)
        await message.channel.send(f"Next number is: {self.bot.next_number}")
        
    async def correct_count_handler(self,message,counted_number):
        self.bot.current_count = counted_number
        self.bot.next_number = counted_number + 1
        self.bot.last_user_id = message.author.id
        self.bot.latest_message = message.id
        self.bot.record_save(message.author.id)
        
        if counted_number % 100 == 0:
            self.bot.last_reset = counted_number
            await message.add_reaction(self.hundred_reaction)
        elif counted_number == self.bot.counting_record:
            self.bot.current_streak += 1
            if self.bot.current_streak > self.bot.record_streak:
                self.bot.record_streak = self.bot.current_streak
            await message.add_reaction(self.bluetick_reaction)
        else:
            await message.add_reaction(self.tick_reaction)
        
        self.bot.save_count()

        if self.is_perfect_sequence(counted_number):
            await message.channel.send("A perfect sequence, would you look at that!")
        
        if self.is_plaindrome(counted_number):
            await message.channel.send("A palindrome! Neat!")

    def is_perfect_sequence(self, counted_number):
        digits = list(map(int, str(counted_number)[::-1]))
        return all(digits[i] - 1 == digits[i + 1] for i in range(len(digits) - 1))
    
    def is_plaindrome(self, counted_number):
        str_num = str(counted_number)
        return str_num == str_num[::-1]


# Nitro Roles Menu


role_list = {'Red' : 1200885809943941291, 'Burgundy' : 1200885966311805168, 'Vivid Orange' : 1200886299914149898, 'Royal Orange' : 1200886690638725230, 'Golden Yellow' : 1200886767700684880, 'Apple Green' : 1200887512671997953, 'Avocado' : 1200886400204152923, 'Iceberg' : 1200887825780969614, 'Cosmic Cobalt' : 1200887996673699911, 'Vivid Orchid' : 1200888167444775053, 'Deep Pink' : 1200888375612280913, 'Light Pink' : 1257019397197795530, 'Royal Purple' : 1200888542931468368, 'Void Kitty' : 1200888968804302920, 'Turquoise' : 1252837659433238550, 'Milk' : 1200889419746525264, 'Holographic' : 1387402028329734224}

class nitro_role_list(discord.ui.Select):
    def __init__(self):
        options= [discord.SelectOption(label="🚫 No Color", value="none")]+[discord.SelectOption(label=label, value=label) for label in role_list]
        super().__init__(placeholder="Choose your role...", min_values=1, max_values=1, options=options, custom_id="role_select")
    
    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild  = interaction.guild
        selected_key = self.values[0]
        
        if selected_key == "none":
            to_remove = [guild.get_role(rid) for rid in role_list.values() if guild.get_role(rid) in member.roles]
            if to_remove:
                await member.remove_roles(*to_remove, reason="Cleared color roles")
            await interaction.response.send_message("✅ Color roles cleared.", ephemeral=True)
            return
        
        target = guild.get_role(role_list[selected_key])
        if not target:
            return await interaction.response.send_message("❌ Role not found.")
        to_remove = [guild.get_role(rid) for cid, rid in role_list.items() if cid != selected_key and guild.get_role(rid) in member.roles]
        
        try:
            if to_remove:
                await member.remove_roles(*to_remove, reason = "Colour Swap")
            if target in member.roles:
                await member.remove_roles(target, reason = 'Colour toggled off.')
                await interaction.response.send_message(f'✅ Successfully removed role: **__{target.name}__**',ephemeral=True)
            else:
                await member.add_roles(target, reason = "Colour role added.")
                await interaction.response.send_message(f'✅ Successfully added role: **__{target.name}__**',ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message('❌ Missing Permissions. Please contact staff.', ephemeral=True)

class nitro_role_picker(discord.ui.View):
    def __init__(self):
        super().__init__(timeout = None)
        self.add_item(nitro_role_list())          
    
        
# Event hander within counts.        

    
bot = CountingBot()
run_message_handler = CountingBot_MessageHandler(bot)
tree = bot.tree
@bot.event
async def on_ready():
    bot.add_view(nitro_role_picker())
    print(f'Logged in as {bot.user}!')

@bot.event
async def on_message(message):
    await run_message_handler.message_handler(message)

@bot.event
async def on_message_edit(before: discord.Message,after: discord.Message):
    if bot.counting_channel is None:
        return
    if before.channel.id != bot.counting_channel:
        return
    if before.id == bot.latest_message:
        await before.channel.send(f'{before.author.mention} has edited their message, the sneaky devil! Their number was {bot.current_count}. The next number is {bot.next_number}.')

@bot.event
async def on_message_delete(message):
    if bot.counting_channel is None:
        return
    if message.channel.id != bot.counting_channel:
        return
    if message.id == bot.latest_message:
        await message.channel.send(f'{message.author.mention} has deleted their message, the sneaky devil! Their number was {bot.current_count}. The next number is {bot.next_number}.')


# Slash commands.


@bot.tree.command(name = "status", description="A full run-down of the bot's status.")
async def bot_status(interaction: discord.Interaction):
    statusembed = discord.Embed(title = "All bot stats:", description = f"Channel: <#{bot.counting_channel}>\nCurrent Count: {bot.current_count}\nNext: {bot.next_number}\nLast user: <@{bot.last_user_id}>\nReset Point: {bot.last_reset}\nRecord: {bot.counting_record}\nRecord Holder: <@{bot.record_holder}>\nCurrent Streak: {bot.current_streak}\nRecord Streak: {bot.record_streak}", colour=bot_embed_colour)
    await interaction.response.send_message(embed=statusembed)


@bot.tree.command(name="record", description="Displays this server's counting record.")
async def record(interaction: discord.Interaction):
    recordmebed = discord.Embed(title="Counting Record:", description=f"This server's counting record is __**{bot.counting_record}**__. It was achieved by <@{bot.record_holder}>.", colour=bot_embed_colour)
    await interaction.response.send_message(embed=recordmebed)


@bot.tree.command(name="next", description="Tells you what the next number is. Because apparently reading is hard.")
async def nextnumber(interaction: discord.Interaction):
    nextembed = discord.Embed(title="Next Number:", description=f"The next number is __**{bot.next_number}**__. The last person to count was <@{bot.last_user_id}>.", colour=bot_embed_colour)
    await interaction.response.send_message(embed=nextembed)


@bot.tree.command(name= "streak", description= "Displays the current and record counting streaks.")
async def streakinfo(interaction: discord.Interaction):
    streakembed = discord.Embed(title="Streak Information:", description=f"The current streak is __**{bot.current_streak}**__, and the streak record is __**{bot.record_streak}**__.", colour=bot_embed_colour)
    await interaction.response.send_message(embed=streakembed)


@bot.tree.command(name="ping", description= "How quickly is the bot responding?")
async def botping(interaction: discord.Interaction):
    latency = bot.latency * 1000
    pingembed = discord.Embed(title="Pong", description=f"-# The bot took {latency:.2f} ms to respond to this command.", colour=bot_embed_colour)
    await interaction.response.send_message(embed=pingembed)


@bot.tree.command(name="help", description="A list of the bot's commands.")
async def helpmessage(interaction: discord.Interaction):
    helpembed = discord.Embed(title="Help Menu:", description="A list of this bot's commands. They're all slash commands, there is no prefix.", colour=bot_embed_colour)
    for cmd in bot.tree.get_commands():
            helpembed.add_field(name=f"/{cmd.name}", value=cmd.description, inline=False)
    await interaction.response.send_message(embed=helpembed)


### Owner-only manual commands. 

@bot.command()
@commands.is_owner()
async def sync(ctx: commands.Context):
    start_time = time.time()
    
    try:
        synced = await bot.tree.sync()
        end_time = time.time()
        duration = end_time - start_time
        await ctx.send(f"Synced {len(synced)} commands globally in {duration:.2f} seconds.")
        
    except discord.HTTPException as e:
        await ctx.send(f"Error while syncing: {str(e)}")


@bot.command()
@commands.is_owner()
async def nitrosetup(ctx: commands.Context):
    nitro_role_list = [ctx.guild.get_role(rid) for rid in list(role_list.values())]
    mentions = "\n".join(role.mention for role in nitro_role_list)
    nitro_embed = discord.Embed(title = 'Thank you for boosting the server! As a reward for your contribution, you can pick a colour role from those listed below.', description = mentions, colour=bot_embed_colour)
    await ctx.send(embed = nitro_embed, view = nitro_role_picker(), allowed_mentions = discord.AllowedMentions(roles = True))
    

@bot.command()
@commands.is_owner()
async def setchannel(ctx: commands.Context, channel: discord.TextChannel = None):
    if bot.counting_channel is not None:
        return await ctx.send("Channel already set.")

    target_channel = channel or ctx.channel
    bot.counting_channel = target_channel.id
    bot.save_count()
    await ctx.send(f"Counting channel set to {target_channel.mention}. Let the counting begin!")


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.NotOwner):
        await ctx.send("You do not have permission to use this command. This command is reserved for the bot owner.")
    else:
        raise error



# Bot runner.


bot.run(bottoken)