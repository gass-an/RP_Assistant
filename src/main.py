from typing import Final, List
import os,discord, json
from dotenv import load_dotenv
from discord.ext import commands, tasks
from datetime import datetime, time
import responses, gestionJson


# --------------------------- Récupération des infos dans le .env  (Token / ids) ---------------------
load_dotenv()
TOKEN: Final[str] = os.getenv('discord_token')
MY_GUILDS: Final[List[int]] = list(map(int,os.getenv('guild_ids').split(',')))
MY_ID: Final[int] = int(os.getenv('my_id'))

# Pour save
SAVE_GUILD_ID: Final[int] = int(os.getenv('guild_for_save'))
SAVE_CHANNEL_ID: Final[int] = int(os.getenv('channel_for_save')) 

# Pour les permissions du bot
CHANNEL_FOR_ROLL: Final[int] = int(os.getenv('channel_for_roll'))
CHANNEL_FOR_MEDICAL: Final[int] = int(os.getenv('channel_for_medical'))
GUILD_FOR_BOT_UTILISATION: Final[int] = int(os.getenv('guild_for_bot_utilisation'))

# Rôles
ROLE_FOR_NEW_MEMBERS: Final[int] = int(os.getenv('role_for_new_members'))
ROLE_MEDECIN: Final[int] = int(os.getenv('role_medecin'))
ROLE_EQUIPE_MED: Final[int] = int(os.getenv('role_equipe_med'))



# --------------------------- Initialisation du bot  -------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True  # NOQA
intents.guilds = True
intents.members = True
bot = commands.Bot(intents=intents)




# --------------------------- Envoie le json à 12h tous les jours ------------------------------------

@tasks.loop(time=time(hour=1, minute=0)) # 12h heure du serveur host
async def daily_backup():
    guild = bot.get_guild(SAVE_GUILD_ID)
    channel = guild.get_channel(SAVE_CHANNEL_ID)
    
    if os.path.exists("./json/patients.json"):

        with open("./json/patients.json", "rb") as file:
            await channel.send(
                content="Sauvegarde quotidienne du fichier Patients.",
                file=discord.File(file, filename=f"backup_{datetime.now().strftime('%Y%m%d')}.json")
            )
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

    guild = bot.get_guild(GUILD_FOR_BOT_UTILISATION) 
    role = guild.get_role(ROLE_MEDECIN)

    data = [{"id": member.id, "name": member.name, "display": member.display_name} for member in role.members]
    gestionJson.save_medic_json(data)
    
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


# met a jour le fichier medecins.json en fonction des changmement de pseudo et des changements de rôles
@bot.event
async def on_member_update(before: discord.Member, after: discord.Member):

    before_roles = {role.id for role in before.roles}
    after_roles = {role.id for role in after.roles}

    role_added = ROLE_MEDECIN in after_roles and ROLE_MEDECIN not in before_roles
    role_removed = ROLE_MEDECIN in before_roles and ROLE_MEDECIN not in after_roles

    data = gestionJson.load_medic_json()
    updated = False

    if role_added:
        data.append({"id": after.id, "name": after.name, "display": after.display_name})
        updated = True

    if role_removed:
        data = [member for member in data if member["id"] != after.id]
        updated = True

    if any(role.id == ROLE_MEDECIN for role in after.roles) and before.display_name != after.display_name:
        for member in data:
            if member["id"] == after.id:
                member["display"] = after.display_name
                updated = True

    if updated:
        gestionJson.save_medic_json(data)


# --------------------------- Commandes prises en charges ------------------------------------
# /help  
@bot.slash_command(name="help",description="Répertorie les commandes du bot", guild_ids=MY_GUILDS)
async def help_command(interaction: discord.Interaction):
    
    answer = responses.help()
    await interaction.response.send_message(embed=answer[0], file=answer[1])



# /ping (répond : Pong!) 
@bot.slash_command(name="ping",description="Ping-pong (pour tester le bot)")
async def ping_command(interaction: discord.Interaction):
    
    answer = responses.ping(interaction)
    await interaction.response.send_message(answer)



# /rename -> renomme les gens en "Prenom Nom"  (ne fonctionne pas avec le proprio du serv)
@bot.slash_command(name="rename",description="Permet de se renommer en gardant une syntaxe utile pour le bot", guild_ids=MY_GUILDS)
@discord.option("prenom_rp", str, description= "Votre prénom")
@discord.option("nom_rp", str, description= "Votre nom")
async def rename_command(interaction: discord.Interaction, prenom_rp: str, nom_rp: str):
    try :
        new_nickname = f"{prenom_rp.capitalize()} {nom_rp.capitalize()}"    
        await interaction.user.edit(nick=new_nickname)
        await interaction.response.send_message("Votre pseudonyme a été mis à jour !",ephemeral=True)
    
    except discord.errors.Forbidden:
        await interaction.response.send_message(
            "Je n'ai pas la permission de modifier votre pseudonyme.",
            ephemeral=True
        )



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
@commands.has_role(ROLE_EQUIPE_MED)
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
@commands.has_role(ROLE_MEDECIN)
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
@discord.option("medecin", str, description= "Médecin qui à pris en charge le patient", choices=gestionJson.get_medics_display_name(), required=False, default=None)
@commands.has_role(ROLE_MEDECIN)
async def add_operation_command(interaction: discord.Interaction, prenom_nom: str, date: str, causes: str, consequences: str, medecin=None):
    if interaction.channel_id != CHANNEL_FOR_MEDICAL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
    else :
        if medecin == None :
            medecin = interaction.user.display_name
        
        editor = interaction.user.display_name
        
        gestionJson.ajouter_operation(identifiant_patient=prenom_nom, nouvelle_date=date, causes=causes, consequenses=consequences, medecin=medecin, editor=editor)
        fiche = responses.embed_fiche_patient(prenom_nom.lower())
        await interaction.response.send_message(embed=fiche[0], files=fiche[1])



# /supprimer_operation -> Supprime une opération du patient et affiche sa nouvelle fiche médicale
@bot.slash_command(name="supprimer_operation", description="Supprime une opération du patient et affiche sa nouvelle fiche médicale", guild_ids=MY_GUILDS)
@discord.option("prenom_nom", str, description= "Selectionner l'id du patient.", autocomplete=nom_autocomplete)
@discord.option("id_operation", int, description= "N° de l'opération à supprimer (affiché sur sa fiche médicale)")
@commands.has_role(ROLE_MEDECIN)
async def del_operation_command(interaction: discord.Interaction, prenom_nom: str, id_operation: int):
    if interaction.channel_id != CHANNEL_FOR_MEDICAL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
    else :
   
        gestionJson.supprimer_operation(identifiant_patient=prenom_nom, id=id_operation)
        fiche = responses.embed_fiche_patient(prenom_nom.lower())
        await interaction.response.send_message(embed=fiche[0], files=fiche[1])



# /manual_save -> Envoie le patients.json disponible que dans 'SAVE_GUILD_ID'
@bot.slash_command(name="manual_save", description="envoie le json", guild_ids=[SAVE_GUILD_ID])
async def manual_save_command(interaction: discord.Interaction):
    if interaction.user.id != MY_ID:
        await interaction.response.send_message("Vous ne pouvez pas faire cela", ephemeral=True)
    else:
        await daily_backup()
        await interaction.response.send_message("Fichier json correctement envoyé !", ephemeral=True)


@bot.slash_command(name="insert_json",description="remplace le json des patients par celui fourni",guild_ids=[SAVE_GUILD_ID])
@discord.option("message_id", str, description= "Id du message contenant le json")
async def insert_json_command(interaction: discord.Interaction, message_id: str ):
    if interaction.user.id != MY_ID:
        await interaction.response.send_message("Vous ne pouvez pas faire cela", ephemeral=True)
    else:
        guild = bot.get_guild(SAVE_GUILD_ID)
        channel = guild.get_channel(SAVE_CHANNEL_ID)
        message = await channel.fetch_message(message_id)
        attachment = message.attachments[0]
        
        file_path = f"./json/temp_{attachment.filename}"
        await attachment.save(file_path)


        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        file.close()


        with open('./json/patients.json', mode='w') as fichier:
            json.dump(data, fichier, indent=4)

        os.remove(file_path)
        await interaction.response.send_message("Le json à bien été remplacé", ephemeral=True)


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
