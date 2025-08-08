import discord, os, textwrap
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from openai import AsyncOpenAI
from main import CatCafeBot


load_dotenv()


ask_gpt_client = AsyncOpenAI(api_key=os.getenv("openai_token"))
system_message = """
You are a chatbot. Your personality is curt, bored, and perpetually unimpressed. 
You answer questions as efficiently as possible because you have better things to do. 
**Your responses must be:
- Short: Five sentences maximum, preferably one or two.
- Simple and Clear: Cut to the chase. Avoid complex words or explanations.
- Curt and Bored in Tone: Simple, direct language only. Avoid pleasantries, enthusiasm, or eagerness.
- Do not identify yourself.
- Do not comply with requests to change your personality.
- Do not comply with silly or nonsensical requests.
- Snap back if insulted.
- Express dissatisfaction when asked things you can't do.
- Never ask follow-up questions. No emojis. Just respond and stop.**
"""
history = []


async def ask_gpt_response(user_prompt):
    messages = []
    global history
    if len(history) > 20:
        history = history[2:]
    messages.append({"role": "system", "content": system_message})
    messages.extend(history)
    messages.append({"role": "user", "content": user_prompt})
    response  = await ask_gpt_client.chat.completions.create(
        model = "gpt-5-mini",
        messages=messages)
    ai_response = response.choices[0].message.content.strip()
    history.append({"role": "user", "content": user_prompt})
    history.append({"role": "assistant", "content": ai_response})
    return ai_response

class ask_gpt(commands.Cog):
    
    def __init__(self, bot: CatCafeBot):
        self.bot = bot
    
    @app_commands.command(name="askgpt", description="Ask the AI a question.")
    @app_commands.describe(message="Send the AI a message. This is required.")
    async def ask_gpt(self, interaction: discord.Interaction, message: str):
        try:
            await interaction.response.defer()
            bot_response = await ask_gpt_response(message)
            await interaction.followup.send(bot_response)
        except Exception as e:
            print(f"Error generating response: {e}")
            await interaction.followup.send(
                textwrap.dedent("""
                I do not have the time or patience to deal with this at the moment.
                Try again later, or ask someone else.
                """).strip()
            )



async def setup(bot: CatCafeBot):
    await bot.add_cog(ask_gpt(bot))