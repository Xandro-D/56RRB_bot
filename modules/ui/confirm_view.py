import discord

class ConfirmView(discord.ui.View):
    def __init__(self, true_label: str, false_label: str):
        super().__init__(timeout=60 * 4)
        self.value = None
        self.kick.label = true_label
        self.skip.label = false_label

    @discord.ui.button(label="Kick", style=discord.ButtonStyle.danger)
    async def kick(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Skip", style=discord.ButtonStyle.secondary)
    async def skip(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        self.stop()
        await interaction.response.defer()