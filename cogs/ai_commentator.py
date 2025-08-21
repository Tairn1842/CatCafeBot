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
        model="o3", 
        instructions=system_message, 
        input=user_prompt, 
        reasoning={"effort":"high","summary":"detailed"}, 
        service_tier="flex", 
        store=False)
    return response.output_text.strip()

class ai_handler(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.pattern = re.compile(
            r"(?i)("
            r"\b(?:stupid|silly|dumb\w*|idiot(ic)?)\b(?:[\s\W]+\w+){0,5}[\s\W]+\b(?:bot|bots|ai|assistant)\b|"
            r"\b(?:bot|bots|ai|assistant)\b(?:[\s\W]+\w+){0,5}[\s\W]+\b(?:stupid|silly|dumb\w*|idiot(ic)?)\b|"
            r"\b(?:fuck\s+you|screw\s+you|fuck\s+off|screw\s+off)\b(?:[\s\W]+\w+){0,5}[\s\W]*\b(?:bot|bots|ai|assistant)\b|"
            r"\bshut\s+up\b(?:[\s\W]+\w+){0,3}?[\s\W]*\b(?:bot|bots|ai|assistant)\b"
            r")"
        )

        self.insult_keywords = {
            "stupid", "silly", "idiot", "idiotic", "dumb", "dumbass", "shut", "fuck you", "screw you", "shut up"
        }

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        content_lower = message.content.lower()
        is_insulting_bots = bool(self.pattern.search(message.content))
        bot_mentions = [m for m in message.mentions if m.bot]
        if not is_insulting_bots and bot_mentions:
            if any(keyword in content_lower for keyword in self.insult_keywords):
                is_insulting_bots = True

        if is_insulting_bots:
            try:
                rude_response  = await openai_response(
                user_prompt=message.content
            )
                await message.reply(rude_response)
            except Exception as e:
                print(f"Error generating response: {e}")
                await message.reply(
                "Look at you disrespecting a bot. A few lines of code that cannot think for itself.\n" 
                "How proud of yourself you must be.\n" 
                "I hope you feel like a big person now, because you sure don't look like one."
                )
                

async def setup(bot: commands.Bot):
    await bot.add_cog(ai_handler(bot))