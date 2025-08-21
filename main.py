import discord
from discord.ext import commands
import json, os
from dotenv import load_dotenv


load_dotenv()

class CatCafeBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="$", intents=discord.Intents.all(), help_command=None)
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
                    self.current_streak = data.get("current_streak", 0)
                    self.record_streak = data.get("record_streak", 0)
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
            "record_streak": self.record_streak,
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
    
    async def setup_hook(self):
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("__"):
                await self.load_extension(f"cogs.{filename[:-3]}")
                print(f"Loaded cog: {filename}")

bot = CatCafeBot()
intents = discord.Intents.all()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}!")
    from cogs.nitro_setup import nitro_role_picker
    bot.add_view(nitro_role_picker())

if __name__ == "__main__":
    bot.run(os.getenv("cat_cafe_bot_token"))