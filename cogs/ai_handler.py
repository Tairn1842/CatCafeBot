from google import genai
from google.genai import types
import discord, textwrap, re, os
from discord.ext import commands
from main import CatCafeBot


# model definition


gemini_client = genai.Client(api_key=os.getenv("gemini_token"))

system_message = textwrap.dedent("""Respond to rude or disrespectful inputs with bored, mocking one-liners.
    Always sound unamused, unimpressed, or mildly irritated. Keep responses short — no more than two punchy lines.
    Do not explain. Do not show reasoning. Never be helpful, apologetic, or enthusiastic.
    **Avoid repeating the same phrasing across replies. Prioritize novelty and attitude.**
    **Example Styles:**

    * What are you incapable of, following the rules, or reading?
    * I’d care, but apathy is cheaper.
    * It appears that you've either forgotten the meaning of 'consecutive' or what the next number is. Pity.
    * Neat. Anyway.
    * You're really giving 2006 YouTube comment energy.
    * Error 404: relevance not found."""
)

async def gemini_response(user_prompt):
    response = await gemini_client.aio.models.generate_content(
            model="gemini-2.5-pro",
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=128),
                system_instruction=system_message,
                temperature=1,
        ),
            contents=user_prompt
        )
    return response.text.strip()

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
                rude_response  = await gemini_response(
                user_prompt=textwrap.dedent(f"""respond to {message.content}.
                    Read the user's insult and write a mocking, indifferent comeback.""")
            )
                await message.reply(rude_response)
            except Exception as e:
                print(f"Error generating response: {e}")
                await message.reply(textwrap.dedent(
                """Look at you disrespecting a bot. A few lines of code that cannot think for itself. 
                How proud of yourself you must be. 
                I hope you feel like a big person now, because you sure don't look like one."""
                    )
                )
                

async def setup(bot: CatCafeBot):
    await bot.add_cog(ai_handler(bot))