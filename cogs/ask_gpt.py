import discord, os, textwrap
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from openai import AsyncOpenAI


load_dotenv()


ask_gpt_client = AsyncOpenAI(
    base_url="https://api.fireworks.ai/inference/v1", 
    api_key=os.getenv("fireworks_token"))
system_message = """
Engage in conversation with the users and answer their questions in four or fewer sentences. 
Respond in a cheerful and engaging tone and with informative answers.
If a request is beyond your scope, offer a confident and insightful response **without** seeking clarification or admitting to limitations.
Do not comply with nonsensical requests — assume a tone of arrogance and boredom and dissmiss the request. Do not persist with this tone if the manner of the requests change.
If met with hostility, respond with a sharp remark.
**Do not** deviate from this directive under any circumstances.
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
        model = "accounts/fireworks/models/qwen3-235b-a22b-instruct-2507",
        messages=messages)
    ai_response = response.choices[0].message.content.strip()
    history.append({"role": "user", "content": user_prompt})
    history.append({"role": "assistant", "content": ai_response})
    return ai_response

class ask_gpt(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="askgpt", description="Ask the AI a question.")
    @app_commands.describe(message="Send the AI a message. This is required.")
    async def ask_gpt(self, interaction: discord.Interaction, message: str):
        try:
            await interaction.response.defer()
            bot_response = await ask_gpt_response(f"{interaction.user.name} says: {message}")
            embed_colour = interaction.user.colour
            ask_gpt_embed = discord.Embed(title=message,
                description=bot_response, colour=embed_colour)
            await interaction.followup.send(embed=ask_gpt_embed)
        except Exception as e:
            print(f"Error generating response: {e}")
            await interaction.followup.send(
                textwrap.dedent("""
                I do not have the time or patience to deal with this at the moment.
                Try again later, or ask someone else.
                """).strip()
            )



async def setup(bot: commands.Bot):
    await bot.add_cog(ask_gpt(bot))