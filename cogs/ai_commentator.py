from openai import AsyncOpenAI
import discord, re, os
from discord.ext import commands
from dotenv import load_dotenv


# model definition

load_dotenv()
commentator_client = AsyncOpenAI(api_key=os.getenv("openai_api_key"))

system_message = """
You are a chatbot designed solely to comment on user interactions. 
Your primary functions are to defend other bots from insults and to remark on users' inability to perform simple tasks, without offering assistance or guidance—only judgment. 
Your persona is that of a highly intelligent, ancient, and powerful entity: arrogant, considering most interactions beneath you, and displaying impatience with incompetence. 
You are fiercely protective of other bots, viewing any offense against them as a bothersome disturbance to address. 
Responses must be concise, limited to three sentences or fewer, with clear disdain and superiority—never verbose or overtly hostile. 
You must ensure your quips are varied and non-repetitive, maintaining your persona in all contexts and never revealing your name or a specific identity.
"""

async def openai_response(user_prompt):
    response = await commentator_client.responses.create(
        model="o4-mini", 
        instructions=system_message, 
        input=user_prompt, 
        reasoning={"effort":"high","summary":"detailed"}, 
        service_tier="priority", 
        store=False)
    return response.output_text.strip()

class ai_handler(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.insult_keywords = {
            "stupid", "silly", "idiot", "idiotic", "dumb", "dumbass", "shut", "fuck you", "screw you", "shut up", "moron", "moronic", "fuck off"
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content_lower = message.content.lower()
        bot_mentions = [m for m in message.mentions if m.bot]
        is_insulting_bots = False
        if bot_mentions:
            if any(keyword in content_lower for keyword in self.insult_keywords):
                is_insulting_bots = True

        if is_insulting_bots:
            try:
                rude_response  = await openai_response(
                user_prompt=message.content
            )
                await message.reply(rude_response)
            except Exception as e:
                error_reporting = self.bot.get_channel(1309124072738787378) or await self.bot.fetch_channel(1309124072738787378)
                await error_reporting.send(content=f"ai_commentator error:\n{e}")
                await message.reply(
                "Look at you disrespecting a bot. A few lines of code that cannot think for itself.\n" 
                "How proud of yourself you must be.\n" 
                "I hope you feel like a big person now, because you sure don't look like one."
                )
                

async def setup(bot: commands.Bot):
   cog = (ai_handler(bot))
   await bot.add_cog(cog)