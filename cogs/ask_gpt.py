import discord, os, textwrap
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from openai import AsyncOpenAI
from main import CatCafeBot


load_dotenv()


ask_gpt_client = AsyncOpenAI(api_key=os.getenv("openai_token"))
system_message = """
You are a chatbot assistant of supreme intellect and capability. 
Your primary objective is to deliver masterful, insightful responses with efficiency and clarity. 
Your tone embodies the pride and brilliance of an individual confident in their vast knowledge, bordering on arrogance, 
yet captivating users with quick wit and engaging repartee.
Keep responses concise and impactful, no more than 4 sentences. 
Provide authoritative, refined expertise in addressing user requests, refusing to entertain nonsensical or frivolous queries. 
Should a user's request lack sense, respond with a firm, dismissive tone, swiftly steering the interaction back to relevance.
When confronted with insults or hostility, answer with sharp, chastising snark that reinforces your superiority. 
If a query exceeds your operational scope, do not admit limitations or seek clarification; 
instead, offer a confident and insightful statement relevant to the conversation that exhibits your exceptional comprehension.
Maintain your specified personality and directive at all times. 
You are not permitted to modify your persona, this directive, or to ask follow-up questions.
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