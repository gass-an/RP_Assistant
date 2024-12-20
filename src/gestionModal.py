import discord
from discord import ui
import json
import responses

class FormulaireModal(ui.Modal):
    def __init__(self):
        super().__init__(title="Formulaire pour Embed") 

        self.titre = ui.InputText(
            label="Titre", 
            placeholder="Entrez le titre ici...", 
            required=True
            )
        
        self.description = ui.InputText(
            label="Description",
            placeholder="Entrez votre message ici...",
            style=discord.InputTextStyle.paragraph,
            required=True
            )
    
        self.footer = ui.InputText(
            label="Footer", 
            placeholder="Entrez votre message ici...", 
            required=False
            )

        self.add_item(self.titre)
        self.add_item(self.description)
        self.add_item(self.footer)
    
    async def callback(self, interaction: discord.Interaction):
        
        await interaction.response.defer()

        data = {
            "titre" : self.titre.value,
            "description" : self.description.value,
            "footer" : self.footer.value
        }
        with open('./json/message.json', "w") as file:
            json.dump(data, file, indent=4)


        embed,file = responses.user_embed()
        await interaction.followup.send(embed=embed, file=file)






# class TestModal(ui.Modal):
#     def __init__(self):
#         super().__init__(title="Test Modal")

#         self.input = ui.InputText(
#             label="Test Input",
#             placeholder="Écrivez quelque chose",
#             required=True
#         )
#         self.add_item(self.input)

#     async def callback(self, interaction: discord.Interaction):
#         print("on_submit appelée")  # Vérifiez si ce message s'affiche
#         await interaction.response.send_message(f"Vous avez écrit : {self.input.value}", ephemeral=True)
