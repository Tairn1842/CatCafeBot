import discord
from discord.ext import commands


# nitro setup definition


role_list = {
    "Brown Tabby": 1397894010965856257,
    "Orange Tabby": 1397894291044433951,
    "Calico": 1397895186524405831,
    "Tuxedo": 1397895993671811155,
    "Siamese": 1397896948010450986,
    "Tortie": 1397897301342556232,
    "Red": 1200885809943941291,
    "Burgundy": 1200885966311805168,
    "Vivid Orange": 1200886299914149898,
    "Royal Orange": 1200886690638725230,
    "Golden Yellow": 1200886767700684880,
    "Apple Green": 1200887512671997953,
    "Avocado": 1200886400204152923,
    "Iceberg": 1200887825780969614,
    "Cosmic Cobalt": 1200887996673699911,
    "Vivid Orchid": 1200888167444775053,
    "Deep Pink": 1200888375612280913,
    "Light Pink": 1257019397197795530,
    "Royal Purple": 1200888542931468368,
    "Void Kitty": 1200888968804302920,
    "Turquoise": 1252837659433238550,
    "Milk": 1200889419746525264,
    "Holographic": 1387402028329734224,
}

class nitro_role_list(discord.ui.Select):

    def __init__(self):
        options = [discord.SelectOption(label=label, value=label) for label in role_list]
        super().__init__(
            placeholder="Select a role to add, or deselect one to remove",
            min_values=0,
            max_values=1,
            options=options,
            custom_id="role_select",
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild

        if not self.values:
            to_remove = [
                r for r in (guild.get_role(rid) for rid in role_list.values())
                if r and r in member.roles
            ]
            if not to_remove:
                return await interaction.response.send_message(
                    "ℹ️ You don’t currently have a colour role.", ephemeral=True
                )
            try:
                await member.remove_roles(*to_remove, reason="Colour cleared")
                return await interaction.response.send_message(
                    "✅ Cleared your colour role.", ephemeral=True
                )
            except discord.Forbidden:
                return await interaction.response.send_message(
                    "❌ Missing Permissions. Please contact staff.", ephemeral=True
                )

        selected_key = self.values[0]

        target = guild.get_role(role_list[selected_key])
        if not target:
            return await interaction.response.send_message("❌ Role not found.")

        to_remove = [
            guild.get_role(rid)
            for cid, rid in role_list.items()
            if cid != selected_key and guild.get_role(rid) in member.roles
        ]

        try:
            if to_remove:
                await member.remove_roles(*to_remove, reason="Colour Swap")

            if target in member.roles:
                await member.remove_roles(target, reason="Colour toggled off.")
                await interaction.response.send_message(
                    f"✅ Successfully removed role: **__{target.name}__**",
                    ephemeral=True,
                )

            else:
                await member.add_roles(target, reason="Colour role added.")
                await interaction.response.send_message(
                    f"✅ Successfully added role: **__{target.name}__**", ephemeral=True
                )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Missing Permissions. Please contact staff.", ephemeral=True
            )


class nitro_role_picker(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(nitro_role_list())


class nitro_setup(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot
    
    @commands.command()
    @commands.is_owner()
    async def nitrosetup(self, ctx: commands.Context):
        nitro_role_list = [ctx.guild.get_role(rid) for rid in list(role_list.values())]
        mentions = "\n".join(role.mention for role in nitro_role_list)
        nitro_embed = discord.Embed(
            title="Congratulations! If you're here, you've either boosted the server or are level 100 or higher.\n"
            "As a reward for your contribution, you can pick a colour role from those listed below:",
            description=mentions,
            colour=discord.Colour.blurple(),
        )
        await ctx.send(
            embed=nitro_embed,
            view=nitro_role_picker(),
            allowed_mentions=discord.AllowedMentions(roles=True),
        )
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.NotOwner):
            await ctx.send(
                "You do not have permission to use this command. This command is reserved for the bot owner."
            )
        else:
            raise error


async def setup(bot: commands.Bot):
    cog = (nitro_setup(bot))
    await bot.add_cog(cog)