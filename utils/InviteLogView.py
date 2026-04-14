import discord
from discord import ButtonStyle, Button
from discord.ui import View

from utils.invite_store import save_invites


class InviteLogView(View):
    def __init__(self, listener, invite: str):
        super().__init__(timeout=None)
        self.listener = listener
        self.invite = invite

    @discord.ui.button(label="Remove Invite from ban list", style=ButtonStyle.danger, custom_id="remove_invite_btn")
    async def remove_invite(self, interaction: discord.Interaction, button: Button):
        if self.invite in self.listener.known_invites:
            self.listener.known_invites.remove(self.invite)
            save_invites(self.listener.known_invites)

            button.disabled = True
            button.label = "Removed from blacklist"

            await interaction.response.edit_message(view=self)
            await interaction.followup.send(f"Invite `{self.invite}` removed from blacklist.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Invite `{self.invite}` was not in the blacklist.", ephemeral=True)