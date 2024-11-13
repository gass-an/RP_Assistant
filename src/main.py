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



# fonction pour l'autocompletion des ids (prenom_nom) des patients dans le /patient 
async def nom_autocomplete(interaction: discord.AutocompleteContext):
    user_input = interaction.value.lower()
    all_ids=gestionJson.get_all_ids()
    return [id for id in all_ids if user_input in id.lower()][:25]

# /afficher_patient -> Affiche la fiche médicale du patient 
@bot.slash_command(name="afficher_patient", description="Affiche la fiche médicale du patient", guild_ids=MY_GUILDS)
@discord.option("prenom_nom", str, description= "Selectionner l'id du patient.", autocomplete=nom_autocomplete)
async def patient_command(interaction: discord.Interaction, prenom_nom: str):
    
    fiche = responses.embed_fiche_patient(prenom_nom.lower())
    
    await interaction.response.send_message(embed=fiche[0], files=fiche[1])



# /creer_patient -> Créer un nouveau patient et affiche sa fiche médicale (vierge) 
@bot.slash_command(name="creer_patient", description="Créer un nouveau patient et affiche sa fiche médicale (vierge)", guild_ids=MY_GUILDS)
@discord.option("prenom", str, description= "Prénom du patient")
@discord.option("nom", str, description= "Nom du patient")
@discord.option("age", int, description= "Âge du patient")
@discord.option("sexe", str, description= "Sexe du patient", choices=["Femme","Homme","Autre"])
async def create_patient_command(interaction: discord.Interaction, prenom: str, nom: str, age: int, sexe: str):

    id_patient = gestionJson.create_patient(prenom=prenom, nom=nom, age=age, sexe=sexe)
    
    fiche = responses.embed_fiche_patient(id_patient.lower())
    await interaction.response.send_message(embed=fiche[0], files=fiche[1])



# /ajouter_operation -> Ajoute une opération au patient et affiche sa nouvelle fiche médicale
@bot.slash_command(name="ajouter_operation", description="Ajoute une opération au patient et affiche sa nouvelle fiche médicale", guild_ids=MY_GUILDS)
@discord.option("prenom_nom", str, description= "Selectionner l'id du patient.", autocomplete=nom_autocomplete)
@discord.option("date", str, description= "De la forme : JJ-MM-AAAA")
@discord.option("causes", str, description= "Pourquoi ce patient est à l'hôpital ?")
@discord.option("consequences", str, description= "Bref bilan médical")
async def add_operation_command(interaction: discord.Interaction, prenom_nom: str, date: str, causes: str, consequences: str):
    gestionJson.ajouter_operation(identifiant_patient=prenom_nom, nouvelle_date=date, causes=causes, consequenses=consequences)
    fiche = responses.embed_fiche_patient(prenom_nom.lower())
    await interaction.response.send_message(embed=fiche[0], files=fiche[1])



# /supprimer_operation -> Supprime une opération du patient et affiche sa nouvelle fiche médicale
@bot.slash_command(name="supprimer_operation", description="Supprime une opération du patient et affiche sa nouvelle fiche médicale", guild_ids=MY_GUILDS)
@discord.option("prenom_nom", str, description= "Selectionner l'id du patient.", autocomplete=nom_autocomplete)
@discord.option("id_operation", int, description= "N° de l'opération à supprimer (affiché sur sa fiche médicale)")
async def del_operation_command(interaction: discord.Interaction, prenom_nom: str, id_operation: int):
    gestionJson.supprimer_operation(identifiant_patient=prenom_nom, id=id_operation)
    fiche = responses.embed_fiche_patient(prenom_nom.lower())
    await interaction.response.send_message(embed=fiche[0], files=fiche[1])





def main():
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
