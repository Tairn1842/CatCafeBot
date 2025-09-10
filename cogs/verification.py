import discord
import cogs.variables as var
from discord.ext import commands

class user_verification_button(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Get Verified!", style=discord.ButtonStyle.green, custom_id="verify:get_verified")
    async def on_verification(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        water = 1200520588570144779
        water_role = guild.get_role(water) or await guild.fetch_role(water)
        unverified = 1412648523723309176
        unverified_role = guild.get_role(unverified) or await guild.fetch_role(unverified)
        member = interaction.user
        if len(member.roles) <= 1:
            await interaction.response.send_message(f"{var.error} You do not appear to have any roles. Please contact staff by opening a ticket.", 
                ephemeral=True)
            return
        if unverified_role in member.roles:
            if water_role in member.roles:
                await interaction.user.remove_roles(unverified_role, reason="Successfully verified")
                await interaction.response.send_message(f"{var.approve_tick} You have been successfully verified!\n"
                f"Have a great time! {var.cat_heart}", ephemeral=True)
                return
            else:
                await interaction.user.add_roles(water_role, reason="Successfully verified")
                await interaction.user.remove_roles(unverified_role, reason="Successfully verified")
                await interaction.response.send_message(f"{var.approve_tick} You have been successfully verified!\n"
                    f"Have a great time! {var.cat_heart}", ephemeral=True)
                return
        else:
            await interaction.response.send_message(f"{var.error} You're already verified. Shoo!", ephemeral=True)
            return


class verification(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def verification(self, ctx: commands.Context):
        verification_embed = discord.Embed(
            title="Get verified!",
            description="Welcome to Cat Cafe! To gain complete access to the server, press the button below.\n",
            colour=discord.Colour.blurple())
        verification_embed.set_footer(text=
            "By proceeding, you verify that you have read and understood the rules as stated above and that you agree to abide by them."
        )
        await ctx.send(embed=verification_embed,
                       view=user_verification_button())
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.NotOwner):
            await ctx.send(
                f"{var.error} You do not have permission to use this command. This command is reserved for the bot owner."
            )
        else:
            raise error

async def setup(bot: commands.Bot):
    cog = (verification(bot))
    await bot.add_cog(cog)