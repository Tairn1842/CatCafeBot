import discord, textwrap, time
from discord.ext import commands
from main import CatCafeBot


class exclusive_commands(commands.Cog):
    def __init__(self, bot: CatCafeBot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context):
        start_time = time.time()
        try:
            synced = await self.bot.tree.sync()
            end_time = time.time()
            duration = end_time - start_time
            await ctx.send(
                f"Synced {len(synced)} commands globally in {duration:.2f} seconds."
            )
        except discord.HTTPException as e:
            await ctx.send(f"Error while syncing: {str(e)}")
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.NotOwner):
            await ctx.send(
                "You do not have permission to use this command. This command is reserved for the bot owner."
            )
        else:
            raise error


async def setup(bot: CatCafeBot):
    await bot.add_cog(exclusive_commands(bot))