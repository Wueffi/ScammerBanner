import discord
import random
import operator
import collections.abc

from discord import ButtonStyle, Button
from discord.ui import View, Modal, TextInput

from config import TEMPBAN_ROLE_NAME


operations: dict[collections.abc.Callable[[int, int], int], str] = {
    operator.add: "{a} + {b}",
    operator.sub: "{a} - {b}",
    operator.mul: "{a} * {b}",
}


def choose_op[K, V](mapping: dict[K, V]) -> tuple[K, V]:
    lenght = len(mapping) - 1
    keys = list(mapping.keys())
    key = keys[random.randint(0, lenght)
    return key, mapping[key]


class CaptchaModal(Modal):
    def __init__(self, member: discord.Member, temp_role: discord.Role):
        super().__init__(title="Human verification")

        self.a = random.randint(0, 10)
        self.b = random.randint(0, 10)
        operation, string = choose_op(operations)
        
        self.correct = operation(a, b)
        self.member = member
        self.temp_role = temp_role
        self.answer = TextInput(label=f"What is {string.format(a=self.a, b=self.b)?", placeholder="Enter a number", required=True)
        self.add_item(self.answer)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            user_answer = int(self.answer.value)
        except ValueError:
            return await interaction.response.send_message("Invalid input.", ephemeral=True)

        if user_answer == self.correct:
            try:
                if self.temp_role:
                    await self.member.remove_roles(self.temp_role, reason="Captcha passed")
            except Exception:
                pass

            await interaction.response.send_message("Access restored.", ephemeral=True)
        else:
            await interaction.response.send_message("Wrong answer. Try again.", ephemeral=True)


class VerificationView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="I am not a robot", style=ButtonStyle.success, custom_id="verify_human_btn")
    async def verify(self, interaction: discord.Interaction, button: Button):
        member = interaction.user
        guild = interaction.guild

        temp_role = discord.utils.get(guild.roles, name=TEMPBAN_ROLE_NAME)

        modal = CaptchaModal(member, temp_role)

        await interaction.response.send_modal(modal)
