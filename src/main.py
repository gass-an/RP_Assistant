from typing import Final, List
import os 
from dotenv import load_dotenv
import discord 
from discord.ext import commands, tasks
from datetime import datetime, time, timedelta
import responses, gestionJson


# Récupérer le token + les ids des serveurs / channels / rôles 
load_dotenv()
TOKEN: Final[str] = os.getenv('discord_token')
MY_GUILDS: Final[List[int]] = list(map(int,os.getenv('guild_ids').split(',')))
SAVE_GUILD_ID: Final[int] = int(os.getenv('guild_for_save'))
SAVE_CHANNEL_ID: Final[int] = int(os.getenv('channel_for_save'))  # channel pour save-auto du json
JSON_FILE_PATH = "./json/patients.json"
CHANNEL_FOR_ROLL: Final[int] = int(os.getenv('channel_for_roll'))
CHANNEL_FOR_MEDICAL: Final[int] = int(os.getenv('channel_for_medical'))
GUILD_FOR_BOT_UTILISATION: Final[int] = int(os.getenv('guild_for_bot_utilisation'))
ROLE_FOR_NEW_MEMBERS: Final[int] = int(os.getenv('role_for_new_members'))


# Initialiser le bot
intents = discord.Intents.default()
intents.message_content = True  # NOQA
intents.guilds = True
intents.members = True
bot = commands.Bot(intents=intents)

# --------------------------- Envoie le json à 12h tous les jours ------------------------------------

@tasks.loop(time=time(hour=1, minute=0)) # 12h heure du serveur host
async def daily_backup():
    print(f"Tâche planifiée appelée à {datetime.now()}")
    guild = bot.get_guild(SAVE_GUILD_ID)
    channel = guild.get_channel(SAVE_CHANNEL_ID)
    
    if os.path.exists(JSON_FILE_PATH):

        with open(JSON_FILE_PATH, "rb") as file:
            await channel.send(
                content="Sauvegarde quotidienne du fichier JSON.",
                file=discord.File(file, filename=f"backup_{datetime.now().strftime('%Y%m%d')}.json")
            )
        print(f"Sauvegarde envoyée avec succès dans {channel.name}")
    else:
        print("Le fichier JSON n'existe pas. Aucune sauvegarde envoyée.")



# Démarrage du bot
@bot.event
async def on_ready():
    try:
        # Synchronisation des commandes globales
        await bot.sync_commands()
        print("\nLes commandes globales ont été synchronisées.")
    except Exception as e:
        print(f"Erreur lors de la synchronisation des commandes : {e}")

    daily_backup.start()
    print(f"{bot.user} est en cours d'exécution !")



# --------------------------- Gestion des rôles ------------------------------------
# ajoute un rôle au nouveaux arrivants
@bot.event
async def on_member_join(member: discord.Member):

    if member.guild.id == GUILD_FOR_BOT_UTILISATION :
    
        role = member.guild.get_role(ROLE_FOR_NEW_MEMBERS)
        if role:
            try:
                # Ajoute le rôle au nouveau membre
                await member.add_roles(role)
                print(f"Le rôle {role.name} a été ajouté à {member.display_name}")
            
            except discord.errors.Forbidden:
                print("Le bot n'a pas les permissions nécessaires pour attribuer le rôle.")
            
            except Exception as e:
                print(f"Une erreur est survenue : {e}")
        else:
            print("Le rôle spécifié n'existe pas.")
    else: 
        print("Le rôle n'a pas pu être attribué, ce n'est pas le serveur attendu ! ")

# --------------------------- Commandes prises en charges ------------------------------------

# /ping (répond : Pong!) 
@bot.slash_command(name="ping",description="ping-pong (pour tester le bot)")
async def ping_command(interaction: discord.Interaction):
    
    answer = responses.ping(interaction)
    await interaction.response.send_message(answer)



# /roll pour faire un D20
@bot.slash_command(name="roll",description="Fait un jet de dés : D20", guild_ids=MY_GUILDS)
async def roll_command(interaction: discord.Interaction):

    if interaction.channel_id != CHANNEL_FOR_ROLL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
    else :
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

    if interaction.channel_id != CHANNEL_FOR_ROLL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
    else :
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
@commands.has_role("Equipe médicale")
async def patient_command(interaction: discord.Interaction, prenom_nom: str):
    if interaction.channel_id != CHANNEL_FOR_MEDICAL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
    else :
        fiche = responses.embed_fiche_patient(prenom_nom.lower())
        
        await interaction.response.send_message(embed=fiche[0], files=fiche[1])



# /creer_patient -> Créer un nouveau patient et affiche sa fiche médicale (vierge) 
@bot.slash_command(name="creer_patient", description="Créer un nouveau patient et affiche sa fiche médicale (vierge)", guild_ids=MY_GUILDS)
@discord.option("prenom", str, description= "Prénom du patient")
@discord.option("nom", str, description= "Nom du patient")
@discord.option("age", int, description= "Âge du patient")
@discord.option("sexe", str, description= "Sexe du patient", choices=["Femme","Homme","Autre"])
@commands.has_role("Médecin")
async def create_patient_command(interaction: discord.Interaction, prenom: str, nom: str, age: int, sexe: str):
    if interaction.channel_id != CHANNEL_FOR_MEDICAL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
    else :
        id_patient = gestionJson.create_patient(prenom=prenom, nom=nom, age=age, sexe=sexe)
        
        fiche = responses.embed_fiche_patient(id_patient.lower())
        await interaction.response.send_message(embed=fiche[0], files=fiche[1])



# /ajouter_operation -> Ajoute une opération au patient et affiche sa nouvelle fiche médicale
@bot.slash_command(name="ajouter_operation", description="Ajoute une opération au patient et affiche sa nouvelle fiche médicale", guild_ids=MY_GUILDS)
@discord.option("prenom_nom", str, description= "Selectionner l'id du patient.", autocomplete=nom_autocomplete)
@discord.option("date", str, description= "De la forme : JJ-MM-AAAA")
@discord.option("causes", str, description= "Pourquoi ce patient est à l'hôpital ?")
@discord.option("consequences", str, description= "Bref bilan médical")
@commands.has_role("Médecin")
async def add_operation_command(interaction: discord.Interaction, prenom_nom: str, date: str, causes: str, consequences: str):
    if interaction.channel_id != CHANNEL_FOR_MEDICAL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
    else :
    
        gestionJson.ajouter_operation(identifiant_patient=prenom_nom, nouvelle_date=date, causes=causes, consequenses=consequences)
        fiche = responses.embed_fiche_patient(prenom_nom.lower())
        await interaction.response.send_message(embed=fiche[0], files=fiche[1])



# /supprimer_operation -> Supprime une opération du patient et affiche sa nouvelle fiche médicale
@bot.slash_command(name="supprimer_operation", description="Supprime une opération du patient et affiche sa nouvelle fiche médicale", guild_ids=MY_GUILDS)
@discord.option("prenom_nom", str, description= "Selectionner l'id du patient.", autocomplete=nom_autocomplete)
@discord.option("id_operation", int, description= "N° de l'opération à supprimer (affiché sur sa fiche médicale)")
@commands.has_role("Médecin")
async def del_operation_command(interaction: discord.Interaction, prenom_nom: str, id_operation: int):
    if interaction.channel_id != CHANNEL_FOR_MEDICAL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
    else :
   
        gestionJson.supprimer_operation(identifiant_patient=prenom_nom, id=id_operation)
        fiche = responses.embed_fiche_patient(prenom_nom.lower())
        await interaction.response.send_message(embed=fiche[0], files=fiche[1])




# --------------------------- Gestion des erreurs de permissions  ------------------------------------
@bot.event
async def on_application_command_error(interaction: discord.Interaction, error):
    if isinstance(error, commands.MissingRole):
        await interaction.response.send_message(
            "Vous n'avez pas le rôle requis pour utiliser cette commande.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            "Une erreur est survenue lors de l'exécution de la commande.",
            ephemeral=True
        )


def main():
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
