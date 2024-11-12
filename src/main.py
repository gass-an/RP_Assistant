from typing import Final, List
import os 
from dotenv import load_dotenv
import discord 
from discord.ext import commands
import responses, gestionJson


# Récupérer le token + les ids des serveurs
load_dotenv()
TOKEN: Final[str] = os.getenv('discord_token')
MY_GUILDS: Final[List[int]] = list(map(int,os.getenv('guild_ids').split(',')))



# Initialiser le bot
intents = discord.Intents.default()
intents.message_content = True  # NOQA
bot = commands.Bot(intents=intents)



# Démarrage du bot
@bot.event
async def on_ready():
    try:
        # Synchronisation des commandes globales
        await bot.sync_commands()
        print("\nLes commandes globales ont été synchronisées.")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")
    print(f"{bot.user} est en cours d'exécution !")




# --------------------------- Commandes prises en charges ------------------------------------

# /ping (répond : Pong!) 
@bot.slash_command(name="ping",description="ping-pong (pour tester le bot)")
async def ping_command(interaction: discord.Interaction):
    
    answer = responses.ping(interaction)
    await interaction.response.send_message(answer)



# /roll pour faire un D20
@bot.slash_command(name="roll",description="Fait un jet de dés : D20", guild_ids=MY_GUILDS)
async def roll_command(interaction: discord.Interaction):

    nb_faces = 20
    answer = responses.roll(interaction, nb_faces, text_on_dice=True)
    
    if isinstance(answer[0], discord.Embed) :
        await interaction.response.send_message(embed=answer[0], files=answer[1])
        os.remove(f"./images/{answer[2]}.png")
    else :
        await interaction.response.send_message(answer)



# /roll2 int pour fair un D'int'
@bot.slash_command(name="roll2",description="Fait un jet de dés personalisé", guild_ids=MY_GUILDS)
@discord.option("nb_faces", int, description= "Entrez un nombre compris entre 1 et 100.", min_value=1, max_value=100)
async def roll2_command(interaction: discord.Interaction, nb_faces: int):

    answer = responses.roll(interaction, nb_faces, text_on_dice=False)
    
    if isinstance(answer[0], discord.Embed) :
        await interaction.response.send_message(embed=answer[0], files=answer[1])
        os.remove(f"./images/{answer[2]}.png")
    else :
        await interaction.response.send_message(answer)



# fonction pour l'autocompletion des ids (nom_prenom) des patients dans le /patient 
async def nom_autocomplete(interaction: discord.AutocompleteContext):
    user_input = interaction.value.lower()
    all_ids=gestionJson.get_all_ids()
    return [id for id in all_ids if user_input in id.lower()][:25]

# /patient qui affiche la fiche médicale du patient 
@bot.slash_command(name="patient", description="Affiche la fiche médicale du patient", guild_ids=MY_GUILDS)
@discord.option("nom_prenom", str, description= "Selectionner l'id du patient.", autocomplete=nom_autocomplete)
async def patient_command(interaction: discord.Interaction, nom_prenom: str):
    
    fiche = responses.embed_fiche_patient(nom_prenom)
    
    await interaction.response.send_message(embed=fiche[0], file=fiche[1])


def main():
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
