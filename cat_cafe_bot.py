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
      self.current_streak += 1
      if self.current_streak > self.record_streak:
        self.record_streak = self.current_streak


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
    if "hello there" in message.content.lower():
      await message.reply("https://tenor.com/view/hello-there-general-kenobi-star-wars-grevious-gif-17774326")
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
      await message.channel.send("Did you not learn to count? Or do you not know what 'consequtive' means?")
      await self.reset_count_handler(message)
      return

    await self.correct_count_handler(message,counted_number)

  async def reset_count_handler(self,message):
    self.bot.current_count = (self.bot.current_count // 100) * 100
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
    self.bot.save_count()

    def special_number_checker(counted_number):
      checker_response = []
      # Sequence Checker
      num_digits = list(map(int, str(counted_number)[::-1]))
      if all(num_digits[i] - 1 == num_digits[i + 1] for i in range(len(num_digits) - 1)) or all(num_digits[i] + 1 == num_digits[i + 1] for i in range(len(num_digits) - 1)):
        checker_response.append("Hey, that's a perfect sequence[!](https://tenor.com/view/thats-it-yes-thats-it-that-right-there-omg-that-thats-what-i-mean-gif-17579879)")
      # Palindrome Checker
      if str(counted_number) == str(counted_number)[::-1]:
        checker_response.append("Hey, that's a palindrome[!](https://tenor.com/view/thats-it-yes-thats-it-that-right-there-omg-that-thats-what-i-mean-gif-17579879)")
      # SixtyNice Checker
      if "69" in str(counted_number):
        checker_response.append("https://tenor.com/view/noice-nice-click-gif-8843762")
      # Order 66 Checker
      if "66" in str(counted_number):
        checker_response.append("https://tenor.com/view/execute-order66-order66-66-palpatine-star-wars-gif-20468321")
      # Devil's Number Checker
      if counted_number == 666:
        checker_response.append("https://tenor.com/view/hail-satan-gif-25445039")
      return checker_response

    if counted_number % 100 == 0:
      await message.add_reaction(self.hundred_reaction)
    elif counted_number == self.bot.counting_record:
      await message.add_reaction(self.bluetick_reaction)
    else:
      await message.add_reaction(self.tick_reaction)

    for i in special_number_checker(counted_number):
      await message.channel.send(i)


# Nitro Roles Menu

role_list = {'Brown Tabby' : 1397894010965856257, 'Orange Tabby' : 1397894291044433951, 'Calico' : 1397895186524405831, 'Tuxedo' : 1397895993671811155, 'Siamese' : 1397896948010450986, 'Tortie' : 1397897301342556232, 'Red' : 1200885809943941291, 'Burgundy' : 1200885966311805168, 'Vivid Orange' : 1200886299914149898, 'Royal Orange' : 1200886690638725230, 'Golden Yellow' : 1200886767700684880, 'Apple Green' : 1200887512671997953, 'Avocado' : 1200886400204152923, 'Iceberg' : 1200887825780969614, 'Cosmic Cobalt' : 1200887996673699911, 'Vivid Orchid' : 1200888167444775053, 'Deep Pink' : 1200888375612280913, 'Light Pink' : 1257019397197795530, 'Royal Purple' : 1200888542931468368, 'Void Kitty' : 1200888968804302920, 'Turquoise' : 1252837659433238550, 'Milk' : 1200889419746525264, 'Holographic' : 1387402028329734224}

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
  statusembed = discord.Embed(title = "All bot stats:", description = f"Channel: <#{bot.counting_channel}>\nCurrent Count: {bot.current_count}\nNext: {bot.next_number}\nLast user: <@{bot.last_user_id}>\nReset Point: {(bot.current_count // 100) * 100}\nRecord: {bot.counting_record}\nRecord Holder: <@{bot.record_holder}>\nCurrent Streak: {bot.current_streak}\nRecord Streak: {bot.record_streak}", colour=bot_embed_colour)
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


#help command

@bot.tree.command(name="help", description="How does the bot work?")
async def helpmessage(interaction: discord.Interaction):

  help_command_list = discord.Embed(title="Help Menu:", description="A list of this bot's commands. They're all slash commands, there is no prefix.", colour=bot_embed_colour)
  for cmd in bot.tree.get_commands():
    help_command_list.add_field(name=f"/{cmd.name}", value=cmd.description, inline=False)
  help_command_list.set_footer(text="Page 2 of 2")

  counting_game_info = discord.Embed(title="The Counging Game:", description="This is the bot's primary purpose, to run the counting game. The rules are pretty simple.\n - Count in consecutive numbers, the goal is to get as high as possible.\n - You cannot count twice in a row.\n - Failing to follow either of these rules will result in the count being reset to the last multiple of 100. If this happens, you'll be able to start the count again at the designated number.\n -  Some numbers are special and will merti a reaction from the bot. Keep an eye out for them!", colour=bot_embed_colour)
  counting_game_info.set_footer(text="Page 1 of 2")

  help_embed_list = [counting_game_info, help_command_list]

  class HelpPage(discord.ui.View):
    def __init__(self):
      super().__init__(timeout=None)
      self.current_page = 0

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous_page(self, button: discord.ui.Button, interaction: discord.Interaction):
      if not interaction.user == interaction.message.author:
        return await interaction.response.send_message("<a:cross:1329494914945515593> This is not your command. Shoo!", ephemeral=True)
      view = interaction.message.view
      if view.current_page == 1:
        view.current_page -= 1
        await interaction.response.edit_message(embed=help_embed_list[view.current_page], view=view)
      else:
        return await interaction.response.send_message("<a:cross:1329494914945515593> You are already on the first page.", ephemeral=True)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.secondary)
    async def next_page(self, button: discord.ui.Button, interaction: discord.Interaction):
      if not interaction.user == interaction.message.author:
        return await interaction.response.send_message("<a:cross:1329494914945515593> This is not your command. Shoo!", ephemeral=True)
      view = interaction.message.view
      if view.current_page == 0:
        view.current_page += 1
        await interaction.response.edit_message(embed=help_embed_list[view.current_page], view=view)
      else:
        return await interaction.response.send_message("<a:cross:1329494914945515593> You are already on the last page.", ephemeral=True)

  view = HelpPage()
  await interaction.response.send_message(embed=help_embed_list[0], view=view)


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


# Error handler for owner-only commands.

@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError):
  if isinstance(error, commands.NotOwner):
    await ctx.send("You do not have permission to use this command. This command is reserved for the bot owner.")
  else:
    raise error


# Bot runner.

bot.run(bottoken)