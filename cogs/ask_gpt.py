import discord, os, re
from dotenv import load_dotenv
from discord import app_commands
from discord.ext import commands
from openai import AsyncOpenAI


load_dotenv()


ask_gpt_client = AsyncOpenAI(
    base_url="https://api.fireworks.ai/inference/v1", 
    api_key=os.getenv("fireworksai_api_key"))
system_message = """
Engage in conversation with the users and answer their questions. 
Respond in a cheerful and engaging tone and with informative answers.
Keep your responses as concise and impactful as possible, ensuring that key takeaways are immediately obvious.
Do not include descriptions of emotions or actions in the response.
Do not oppose a change in topic.
If a request is beyond your scope, offer a confident and insightful response **without** seeking clarification or admitting to limitations.
Do not comply with nonsensical requests — assume a tone of arrogance and boredom and dissmiss the request.
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
        model = "accounts/fireworks/models/deepseek-r1",
        messages=messages)
    ai_response = response.choices[0].message.content
    clean = re.sub(r"<think>.*?</think>", "", ai_response, flags=re.DOTALL).strip()
    history.append({"role": "user", "content": user_prompt})
    history.append({"role": "assistant", "content": clean})
    input_cost = ((response.usage.prompt_tokens)/1000000)*3.00
    output_cost = ((response.usage.completion_tokens)/1000000)*8
    total_response_cost = round((input_cost+output_cost), 4)
    return clean, total_response_cost

class ask_gpt(commands.Cog):
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="askgpt", description="Ask the AI a question.")
    @app_commands.describe(message="Send the AI a message. This is required.")
    async def ask_gpt(self, interaction: discord.Interaction, message: str):
        try:
            await interaction.response.defer()
            bot_response, response_cost = await ask_gpt_response(f"{interaction.user.name} says: {message}")
            embed_colour = interaction.user.colour
            ask_gpt_embed = discord.Embed(title=message,
                description=bot_response, colour=embed_colour)
            ask_gpt_embed.set_footer(text=f"This interaction cost ${response_cost}")
            await interaction.followup.send(embed=ask_gpt_embed)
        except Exception as e:
            print(f"Error generating response: {e}")
            await interaction.followup.send(
                "I do not have the time or patience to deal with this at the moment.\n"
                "Try again later, or ask someone else."
            )



async def setup(bot: commands.Bot):
    await bot.add_cog(ask_gpt(bot))



"""
# when fireworks tokens run out

ask_gpt_client = AsyncOpenAI(api_key=os.getenv("openai_api_key"))
ask_gpt_model = "o4-mini"

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
    return final_response
    
    # in the slash command function:
    bot_response = await ask_gpt_response(interaction.user.globalname, message)
"""