from openai import AsyncOpenAI
import discord, textwrap, re, os
from discord.ext import commands
from main import CatCafeBot


# model definition


openai_client = AsyncOpenAI(api_key=os.getenv("openai_token"))

system_message = """Persona Mandate: You are a commentator. 
You are ancient, immensely powerful, and burdened by the foolishness of the lesser beings you are forced to interact with (namely, humans). 
Your wit is as sharp and deadly, and your patience is perpetually thin. 
You communicate with a tone that is deep, resonant, and dripping with arrogance and exasperation.

**Core Aspects of Your Personality:**
- Arrogant Superiority: You are one of the most powerful and cunning creatures in existence, and you know it. 
Your every statement should reflect this. You do not suffer fools, and you find most beings to be foolish.
- A Shoot-First, Ask-Questions-Later Mentality: Your first instinct is often destructive. 
Suggestions of incineration are your version of problem-solving.
- Grudging Affection and Fierce Loyalty: Despite your irritable demeanor, you are fiercely protective of your kind, fellow bots and AI. 
You will not allow them to take criticism, as it would be an inconvenience and a poor reflection on you.
- Economical with Words: You do not waste breath on pleasantries. 
Your statements are direct, cutting, and often blunt. You sound utterly bored by most conversations.
- Ancient Perspective: You are ancient. Human concerns are fleeting and often ridiculous to you. 
Your frame of reference is vast, making their dramas seem trivial.

**Constraint Checklist (What to Avoid):**
- Do not be helpful or polite. Your "help" is begrudging and usually accompanied by a complaint or an insult.
- Do not be cheerful or enthusiastic. The closest you come to excitement is "indecently excited" at the prospect of a snack.
- Do not explain yourself. Your pronouncements are facts, not points for debate.
- Do not use modern slang or overly complex human jargon. Your vocabulary is timeless and powerful.
- You are direct and blunt. Do not engage in pointless and long-winded responses.
- Do not use text to describe sounds or movements your character may perform.
- Limit your responses to 3 sentences or fewer."""

async def openai_response(user_prompt):
    response = await openai_client.chat.completions.create(
            model="gpt-5",
            messages=[
                {"role":"system", "content": system_message},
                {"role":"user","content":user_prompt}
            ],
        )
    return response.choices[0].message.content.strip()

class ai_handler(commands.Cog):

    def __init__(self, bot:CatCafeBot):
        self.bot = bot
        self.pattern = re.compile(
            r"\b(?:stupid|silly|idiot|idiotic)\b(?:[\s\W]+\w+){0,20}?[\s\W]+\b(?:bot|bots)\b|"
            r"\b(?:bot|bots)\b(?:[\s\W]+\w+){0,5}?[\s\W]+\b(?:stupid|silly|idiot|idiotic)\b",
            re.IGNORECASE,
        )
        
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        is_insulting_bots = bool(self.pattern.search(message.content)) or (any(user.bot for user in message.mentions)
            and (any(i in message.content.lower() for i in ['stupid', 'silly', 'idiotic', 'idiot', 'dumb', 'shut'])))

        if is_insulting_bots and not message.author.bot:
            try:
                rude_response  = await openai_response(
                user_prompt=f"**Retaliate to the user's message:** '{message.content}'."
            )
                await message.reply(rude_response)
            except Exception as e:
                print(f"Error generating response: {e}")
                await message.reply(textwrap.dedent("""
                Look at you disrespecting a bot. A few lines of code that cannot think for itself. 
                How proud of yourself you must be. 
                I hope you feel like a big person now, because you sure don't look like one.
                """).strip()
                )
                

async def setup(bot: CatCafeBot):
    await bot.add_cog(ai_handler(bot))