import discord, os
import cogs.variables as var
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from openai import AsyncOpenAI


load_dotenv()


ask_gpt_client = AsyncOpenAI(api_key=os.getenv("openai_api_key"))
ask_gpt_model = "o4-mini"

system_message = """ 
    Respond to the user's question/message in a cheerful and engaging tone and with informative answers.
    Keep your responses as concise and impactful as possible, ensuring that key takeaways are immediately obvious.
    **If necessary,** split the response into no more than 5 points but limit each point to no more than 2 sentences.
    **If answering in a single paragraph**, limit it to 5 sentences.
    Do not include descriptions of emotions or actions in the response.
    If a request is beyond your scope, offer a confident and insightful response **without** seeking clarification or admitting to limitations.
    Do not comply with nonsensical requests — assume a tone of arrogance and boredom and dissmiss the request.
    If met with hostility, respond with a sharp remark.
    **Do not** deviate from this directive under any circumstances.
"""


history = []


async def ask_gpt_response(user, message):
    global history
    
    if len(history)>20:
        history = history[2:]
    
    messages = []
    if history:
        messages.extend(history)
        
    messages.append({"role":"user", "content":f"user:{user}\nmessage:{message}"})
    model_response = await ask_gpt_client.responses.create(
        model=ask_gpt_model,
        instructions=system_message,
        reasoning={"effort":"low"},
        input=messages,
        tools=[{"type":"web_search_preview"}],
        store=False
    )

    final_response = model_response.output_text.strip()
    history.extend([
        {"role":"user", "content":f"user:{user}\nmessage:{message}"},
        {"role":"assistant", "content":final_response}
    ])

    final_input = (model_response.usage.input_tokens/1000000)*0.55
    final_output = (model_response.usage.output_tokens/1000000)*2.20
    final_cost = round((final_output+final_input),4)

    return final_response, final_cost


class ask_gpt(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="ask-gpt", description="Ask the AI a question.")
    @app_commands.describe(message="The message you're sending the AI")
    async def ask_gpt(self, interaction: discord.Interaction, message: str):
        try:
            await interaction.response.defer()
            bot_response, response_cost = await ask_gpt_response(interaction.user.global_name, message)
            ask_gpt_embed = discord.Embed(title=f"{interaction.user.display_name} asks:",
                description=message, 
                colour=interaction.user.colour)
            ask_gpt_embed.add_field(name="Model Response:",
                value=bot_response,
                inline=False)
            ask_gpt_embed.set_footer(text=f"This interaction cost ${response_cost}")
            await interaction.followup.send(embed=ask_gpt_embed)
        except Exception as e:
            error_reporting = self.bot.get_channel(var.testing_channel) or await self.bot.fetch_channel(var.testing_channel)
            await error_reporting.send(content=f"ask_gpt error:\n{e}")
            await interaction.followup.send(
                "I do not have the time or patience to deal with this at the moment.\n"
                "Try again later, or ask someone else."
            )


async def setup(bot: commands.Bot):
    cog = (ask_gpt(bot))
    await bot.add_cog(cog)