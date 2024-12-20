from typing import Final, List
import os,discord,json
from dotenv import load_dotenv
from discord.ext import commands, tasks
from datetime import datetime, time, timezone
from dateutil.relativedelta import relativedelta
import pytz
import responses, gestionJson, gestionPages, gestionModal


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
CHANNEL_FOR_FORMATION: Final[int] = int(os.getenv('channel_for_formation'))
CHANNEL_FOR_LOGS: Final[int] = int(os.getenv('channel_for_logs'))
CHANNEL_FOR_FACTURES: Final[int] = int(os.getenv('channel_for_factures'))
GUILD_FOR_BOT_UTILISATION: Final[int] = int(os.getenv('guild_for_bot_utilisation'))

# Rôles
ROLE_PATIENT: Final[int] = int(os.getenv('role_patient'))
ROLE_MEDECIN: Final[int] = int(os.getenv('role_medecin'))
ROLE_EQUIPE_MED: Final[int] = int(os.getenv('role_equipe_med'))
ROLE_CHIRURGIEN: Final[int] = int(os.getenv('role_chirurgien'))



# ------------------------------------ Initialisation du bot  -------------------------------------------------
intents = discord.Intents.default()
intents.message_content = True  # NOQA
intents.guilds = True
intents.members = True
bot = commands.Bot(intents=intents)




# ------------------------------------ Envoie le json à 12h tous les jours ------------------------------------

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
    role_medic = guild.get_role(ROLE_MEDECIN)
    role_chirurgien = guild.get_role(ROLE_CHIRURGIEN)
    role_equipe_med = guild.get_role(ROLE_EQUIPE_MED)

    data_medic = [{"id": member.id, "name": member.name, "display": member.display_name} for member in role_medic.members]
    data_chirurgien = [{"id": member.id, "name": member.name, "display": member.display_name} for member in role_chirurgien.members]
    data_equipe_med = [{"id": member.id, "name": member.name, "display": member.display_name} for member in role_equipe_med.members]
    gestionJson.save_roles_json({"medic" : data_medic, "chirurgien" : data_chirurgien, "team": data_equipe_med})
    
    print(f"{bot.user} est en cours d'exécution !")


# ------------------------------------ Gestion des rôles ----------------------------------------------
# ajoute un rôle au nouveaux arrivants
@bot.event
async def on_member_join(member: discord.Member):

    if member.guild.id == GUILD_FOR_BOT_UTILISATION :
    
        role = member.guild.get_role(ROLE_PATIENT)
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

    role_medic_added = ROLE_MEDECIN in after_roles and ROLE_MEDECIN not in before_roles
    role_medic_removed = ROLE_MEDECIN in before_roles and ROLE_MEDECIN not in after_roles

    role_chirurgien_added = ROLE_CHIRURGIEN in after_roles and ROLE_CHIRURGIEN not in before_roles
    role_chirurgien_removed = ROLE_CHIRURGIEN in before_roles and ROLE_CHIRURGIEN not in after_roles

    role_team_added = ROLE_EQUIPE_MED in after_roles and ROLE_EQUIPE_MED not in before_roles
    role_team_removed = ROLE_EQUIPE_MED in before_roles and ROLE_EQUIPE_MED not in after_roles

    json_data = gestionJson.load_roles_json()
    data_medic = json_data.get("medic",[])
    data_chirurgien = json_data.get("chirurgien",[])
    data_team = json_data.get("team",[])
    updated = False

    if role_medic_added:
        data_medic.append({
            "id": after.id, 
            "name": after.name, 
            "display": after.display_name
            })
        updated = True

    if role_medic_removed:
        data_medic = [member for member in data_medic if member["id"] != after.id]
        updated = True

    if any(role.id == ROLE_MEDECIN for role in after.roles) and before.display_name != after.display_name:
        for member in data_medic:
            if member["id"] == after.id:
                member["display"] = after.display_name
                updated = True


    if role_chirurgien_added:
        data_chirurgien.append({
            "id": after.id, 
            "name": after.name, 
            "display": after.display_name
            })
        updated = True

    if role_chirurgien_removed:
        data_chirurgien = [member for member in data_chirurgien if member["id"] != after.id]
        updated = True

    if any(role.id == ROLE_CHIRURGIEN for role in after.roles) and before.display_name != after.display_name:
        for member in data_chirurgien:
            if member["id"] == after.id:
                member["display"] = after.display_name
                updated = True



    if role_team_added:
        data_team.append({
            "id": after.id, 
            "name": after.name, 
            "display": after.display_name
            })
        updated = True

    if role_team_removed:
        data_team = [member for member in data_team if member["id"] != after.id]
        updated = True

    if any(role.id == ROLE_EQUIPE_MED for role in after.roles) and before.display_name != after.display_name:
        for member in data_team:
            if member["id"] == after.id:
                member["display"] = after.display_name
                updated = True




    if updated:
        gestionJson.save_roles_json({"medic" : data_medic, "chirurgien" : data_chirurgien, "team": data_team})

        guild = bot.get_guild(SAVE_GUILD_ID)
        channel = guild.get_channel(SAVE_CHANNEL_ID)
        
        if os.path.exists("./json/roles.json"):

            with open("./json/roles.json", "rb") as file:
                await channel.send(
                    content="Sauvegarde du fichier Rôles suite à une mise à jour.",
                    file=discord.File(file, filename=f"backup_{datetime.now().strftime('%Y%m%d')}.json")
                )
        else:
            print("Le fichier JSON n'existe pas. Aucune sauvegarde envoyée.")


# ------------------------------------ Gestion des messages --------------------------------------------
async def send_message(message: discord.Message, user_message) :
    if not user_message:
        print("Le message est vide")
        return
    
    response = responses.get_response(user_message)
    if response == None:
        return    
    await message.channel.send(response)


@bot.event
async def on_message(message: discord.Message):
    if message.author == bot.user:
        return
    user_message = message.content
    await send_message(message, user_message)


@bot.event
async def on_message_edit(before: discord.Message, after:discord.Message):
    if after.author == bot.user:
        return
    user_message = after.content
    await send_message(after, user_message)

    if after.guild.id == GUILD_FOR_BOT_UTILISATION : 
        log_channel = bot.get_channel(CHANNEL_FOR_LOGS)
        if log_channel:
            channel = str(after.channel)
            username = str(after.author.name)
            username_on_server = after.author.display_name
            
            edit_time = after.edited_at.astimezone(pytz.timezone('Pacific/Noumea'))
            formated_edit_time = edit_time.strftime("%d/%m/%Y %H:%M:%S")
            
            created_time = after.created_at.astimezone(pytz.timezone('Pacific/Noumea'))
            formated_created_time = created_time.strftime("%d/%m/%Y %H:%M:%S")
            
            attachments = before.attachments
            attachments_list = []
            if attachments:
                for attachment in attachments:
                    attachments_list.append(attachment.url)

            await log_channel.send(
                f"## :recycle: **Edit d'un Message** \n"
                f"**Channel :** {channel} \t **From : **{username} ({username_on_server})\t "
                f"**Created time :** {formated_created_time} \t "
                f"**Edit time :** {formated_edit_time} \n"
                f"**Avant Edit :** {before.content}\n"
                f"**Après Edit :** {after.content}\n"
                f"**Avant Attachments :** {attachments_list}"
            )


@bot.event
async def on_message_delete(message: discord.Message):
    if message.guild.id == GUILD_FOR_BOT_UTILISATION : 
        log_channel = bot.get_channel(CHANNEL_FOR_LOGS)
        if log_channel:
            channel = str(message.channel)
            username = str(message.author.name)
            username_on_server = message.author.display_name
            
            supression_time = datetime.now().astimezone(pytz.timezone('Pacific/Noumea'))
            formated_supression_time = supression_time.strftime("%d/%m/%Y %H:%M:%S")
            
            created_time = message.created_at.astimezone(pytz.timezone('Pacific/Noumea'))
            formated_created_time = created_time.strftime("%d/%m/%Y %H:%M:%S")

            attachments = message.attachments
            attachments_list = []
            if attachments:
                for attachment in attachments:
                    attachments_list.append(attachment.url)

            await log_channel.send(
                f"## :put_litter_in_its_place: **Supression d'un Message** \n"
                f"**Channel :** {channel} \t **From : **{username} ({username_on_server})\t"
                f"**Created time :** {formated_created_time} \t" 
                f"**Supression time :** {formated_supression_time} \n"
                f"**Contenu :** {message.content}\n"
                f"**Attachments :** {attachments_list}" 
            )


# ------------------------------------ Fonctions pour l'autocompletion ------------------------------------ 
# ids (prenom_nom) des patients dans le /patient 
async def nom_autocomplete(interaction: discord.AutocompleteContext):
    user_input = interaction.value.lower()
    all_ids=gestionJson.get_all_patient_ids()
    return [id for id in all_ids if user_input in id.lower()][:25]

async def medic_autocomplete(interaction: discord.AutocompleteContext):
    display_names = gestionJson.get_medics_display_name()
    return display_names

async def chirurgien_autocomplete(interaction: discord.AutocompleteContext):
    display_names = gestionJson.get_chirurgien_display_name()
    return display_names

async def team_autocomplete(interaction: discord.AutocompleteContext):
    display_names = gestionJson.get_team_display_name()
    return display_names


# ------------------------------------ Commandes prises en charges ------------------------------------
# /help  
@bot.slash_command(name="help",description="Répertorie les commandes du bot", guild_ids=[GUILD_FOR_BOT_UTILISATION])
async def help_command(interaction: discord.Interaction):
    
    answer = responses.help()
    await interaction.response.send_message(embed=answer[0], file=answer[1])



# /ping (répond : Pong!) 
@bot.slash_command(name="ping",description="Ping-pong (pour tester le bot)")
async def ping_command(interaction: discord.Interaction):
    
    answer = responses.ping(interaction)
    await interaction.response.send_message(answer)



# /rename -> renomme les gens en "Prenom Nom"  (ne fonctionne pas avec le proprio du serv)
@bot.slash_command(name="rename",description="Permet de se renommer en gardant une syntaxe utile pour le bot", guild_ids=[GUILD_FOR_BOT_UTILISATION])
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



# ------- Roll --------

# /roll int pour faire un D'int'
@bot.slash_command(name="roll",description="Fait un jet de dés personalisé", guild_ids=[GUILD_FOR_BOT_UTILISATION])
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


# /roll pour faire un D20
@bot.slash_command(name="roll20",description="Fait un jet de dés : D20", guild_ids=[GUILD_FOR_BOT_UTILISATION])
async def roll_command(interaction: discord.Interaction):

    if interaction.channel_id != CHANNEL_FOR_ROLL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
    else :
        nb_faces = 5
        answer = responses.roll(interaction, nb_faces, text_on_dice=True)
        
        if isinstance(answer[0], discord.Embed) :
            await interaction.response.send_message(embed=answer[0], files=answer[1])
            os.remove(f"./images/{answer[2]}.png")
        else :
            await interaction.response.send_message(answer)



# ------- Patients --------

# /liste_patient -> Affiche le nom des patients inscrits à l'hôpital
@bot.slash_command(name="liste_patient", description="Affiche le nom des patients inscrits à l'hôpital", guild_ids=[GUILD_FOR_BOT_UTILISATION])
@commands.has_role(ROLE_EQUIPE_MED)
async def patient_list_command(interaction: discord.Interaction):
    if interaction.channel_id != CHANNEL_FOR_MEDICAL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
        return
    
    patients = gestionJson.get_all_patient_ids()
    patients.sort()
    if not patients:
        await interaction.response.send_message(
            "Aucun patient n'est enregistré pour le moment.", ephemeral=True
        )
        return
    

    await interaction.response.defer()
    paginator = gestionPages.Paginator(items=patients,embed_generator=responses.generate_list_patient_embed)
    embed,files = paginator.create_embed()
    await interaction.followup.send(embed=embed, files=files, view=paginator)



# /afficher_patient -> Affiche la fiche médicale du patient 
@bot.slash_command(name="afficher_patient", description="Affiche la fiche médicale du patient", guild_ids=[GUILD_FOR_BOT_UTILISATION])
@discord.option("prenom_nom", str, description= "Selectionner l'id du patient.", autocomplete=nom_autocomplete)
@commands.has_role(ROLE_EQUIPE_MED)
async def patient_command(interaction: discord.Interaction, prenom_nom: str):
    if interaction.channel_id != CHANNEL_FOR_MEDICAL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
    else :
        
        operations = gestionJson.get_patient_infos(prenom_nom.lower())["operations"]
        await interaction.response.defer()
        paginator = gestionPages.Paginator(items=operations,embed_generator=responses.generate_fiche_patient_embed, identifiant_for_embed=prenom_nom.lower())
        embed,files = paginator.create_embed()
        await interaction.followup.send(embed=embed, files=files, view=paginator)



# /creer_patient -> Créer un nouveau patient et affiche sa fiche médicale (vierge) 
@bot.slash_command(name="creer_patient", description="Créer un nouveau patient et affiche sa fiche médicale (vierge)", guild_ids=[GUILD_FOR_BOT_UTILISATION])
@discord.option("prenom", str, description= "Prénom du patient")
@discord.option("nom", str, description= "Nom du patient")
@discord.option("sexe", str, description= "Sexe du patient", choices=["Femme","Homme","Autre"])
@discord.option("age", int, description= "Âge du patient", required=False, default=20)
@commands.has_role(ROLE_MEDECIN)
async def create_patient_command(interaction: discord.Interaction, prenom: str, nom: str, sexe: str, age: int):
    if interaction.channel_id != CHANNEL_FOR_MEDICAL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
        return
    
    creator = interaction.user.name
    id_patient = gestionJson.create_patient(prenom=prenom, nom=nom, age=age, sexe=sexe, creator=creator)
    
    operations = gestionJson.get_patient_infos(id_patient.lower())["operations"]
    await interaction.response.defer()
    paginator = gestionPages.Paginator(items=operations,embed_generator=responses.generate_fiche_patient_embed, identifiant_for_embed=id_patient.lower())
    embed,files = paginator.create_embed()
    await interaction.followup.send(embed=embed, files=files, view=paginator)



# /ajouter_operation -> Ajoute une opération au patient et affiche sa nouvelle fiche médicale
@bot.slash_command(name="ajouter_operation", description="Ajoute une opération au patient et affiche sa nouvelle fiche médicale", guild_ids=[GUILD_FOR_BOT_UTILISATION])
@discord.option("prenom_nom", str, description= "Selectionner l'id du patient.", autocomplete=nom_autocomplete)
@discord.option("date", str, description= "De la forme : JJ-MM-AAAA")
@discord.option("causes", str, description= "Pourquoi ce patient est à l'hôpital ?")
@discord.option("consequences", str, description= "Bref bilan médical")
@discord.option("medecin", str, description= "Médecin qui à pris en charge le patient", autocomplete=medic_autocomplete)
@commands.has_role(ROLE_MEDECIN)
async def add_operation_command(interaction: discord.Interaction, prenom_nom: str, date: str, causes: str, consequences: str, medecin: str):
    if interaction.channel_id != CHANNEL_FOR_MEDICAL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
    else :

        editor = interaction.user.display_name
        creator = interaction.user.name
        gestionJson.ajouter_operation(
            identifiant_patient=prenom_nom,
            nouvelle_date=date,
            causes=causes,
            consequenses=consequences,
            medecin=medecin,
            editor=editor,
            discord_name=creator
        )

        operations = gestionJson.get_patient_infos(prenom_nom.lower())["operations"]
        await interaction.response.defer()
        paginator = gestionPages.Paginator(items=operations,embed_generator=responses.generate_fiche_patient_embed, identifiant_for_embed=prenom_nom.lower())
        embed,files = paginator.create_embed()
        await interaction.followup.send(embed=embed, files=files, view=paginator)



# /supprimer_operation -> Supprime une opération du patient et affiche sa nouvelle fiche médicale
@bot.slash_command(name="supprimer_operation", description="Supprime une opération du patient et affiche sa nouvelle fiche médicale", guild_ids=[GUILD_FOR_BOT_UTILISATION])
@discord.option("prenom_nom", str, description= "Selectionner l'id du patient.", autocomplete=nom_autocomplete)
@discord.option("id_operation", int, description= "N° de l'opération à supprimer (affiché sur sa fiche médicale)")
@commands.has_role(ROLE_MEDECIN)
async def del_operation_command(interaction: discord.Interaction, prenom_nom: str, id_operation: int):
    if interaction.channel_id != CHANNEL_FOR_MEDICAL:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
        return

    gestionJson.supprimer_operation(identifiant_patient=prenom_nom, id=id_operation)
    
    operations = gestionJson.get_patient_infos(prenom_nom.lower())["operations"]
    await interaction.response.defer()
    paginator = gestionPages.Paginator(items=operations,embed_generator=responses.generate_fiche_patient_embed, identifiant_for_embed=prenom_nom.lower())
    embed,files = paginator.create_embed()
    await interaction.followup.send(embed=embed, files=files, view=paginator)




# ------- Formations --------

# /afficher_formation -> Affiche la liste des personnels formés
@bot.slash_command(name="afficher_formation", description="Affiche la liste des personnels formés", guild_ids=[GUILD_FOR_BOT_UTILISATION])
@discord.option("formation", str, description= "Selectionner la formation.", choices=["Brancardiers","Infirmiers","Médecins","Ambulances","Hélicoptères"])
@commands.has_role(ROLE_EQUIPE_MED)
async def formation_command(interaction: discord.Interaction, formation: str):
    if interaction.channel_id != CHANNEL_FOR_FORMATION:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
        return
    

    formations = gestionJson.get_infos_formations(formation)
    
    await interaction.response.defer()
    paginator = gestionPages.Paginator(items=formations, embed_generator=responses.generate_formation_embed, identifiant_for_embed=formation)
    embed,files = paginator.create_embed()
    await interaction.followup.send(embed=embed, files=files, view=paginator)




# /ajouter_formation -> Ajoute une formation dans la liste des personnels formés
@bot.slash_command(name="ajouter_formation", description="Ajoute un nouveau personnel formé dans la liste adéquate.", guild_ids=[GUILD_FOR_BOT_UTILISATION])
@discord.option("formation", str, description= "Selectionner la formation.", choices=["Brancardiers","Infirmiers","Médecins","Ambulances","Hélicoptères"])
@discord.option("prenom_nom", str, description= "Selectionner l'id du patient.", autocomplete=team_autocomplete)
@discord.option("date", str, description= "De la forme : JJ-MM-AAAA")
@discord.option("valideur", str, description= "Personnel qui à validé la formation", autocomplete=medic_autocomplete)
@commands.has_role(ROLE_MEDECIN)
async def add_formation_command(interaction: discord.Interaction, formation: str, prenom_nom: str, date: str, valideur: str):
    if interaction.channel_id != CHANNEL_FOR_FORMATION:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
        return
    

    chirurgien_role = discord.utils.get(interaction.user.roles, id=ROLE_CHIRURGIEN)
    if formation == "Médecins" and not chirurgien_role: 
        await interaction.response.send_message(
            "Le rôle de chirurgien est nécessaire pour valider cette formation ! ", ephemeral=True
        )
        return
    
    editor = interaction.user.display_name
    discord_name = interaction.user.name
    
    gestionJson.ajouter_formation(
        identifiant_formation=formation,
        prenom_nom=prenom_nom,
        date=date,
        valideur=valideur,
        editor=editor,
        discord_name=discord_name
    )

    formations = gestionJson.get_infos_formations(formation)
    await interaction.response.defer()
    paginator = gestionPages.Paginator(items=formations, embed_generator=responses.generate_formation_embed, identifiant_for_embed=formation)
    embed,files = paginator.create_embed()
    await interaction.followup.send(embed=embed, files=files, view=paginator)


    # Envoie le fichier après la modification
    guild = bot.get_guild(SAVE_GUILD_ID)
    channel = guild.get_channel(SAVE_CHANNEL_ID)

    if os.path.exists("./json/formation.json"):
        with open("./json/formation.json", "rb") as file:
            await channel.send(
                content="Sauvegarde du fichier Formation suite à modification.",
                file=discord.File(file, filename=f"backup_{datetime.now().strftime('%Y%m%d')}.json")
            )
    else:
        print("Le fichier JSON n'existe pas. Aucune sauvegarde envoyée.")




# /supprimer_formation -> Supprime une formation dans la liste des personnels formés
@bot.slash_command(name="supprimer_formation", description="Supprime une formation dans la liste des personnels formés", guild_ids=[GUILD_FOR_BOT_UTILISATION])
@discord.option("formation", str, description= "Selectionner la formation.", choices=["Brancardiers","Infirmiers","Médecins","Ambulances","Hélicoptères"])
@discord.option("id_formation", int, description= "N° de la formation à supprimer (affiché sur la fiche de formation)")
@commands.has_role(ROLE_MEDECIN)
async def del_formation_command(interaction: discord.Interaction, formation: str, id_formation: int):
    if interaction.channel_id != CHANNEL_FOR_FORMATION:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
        return
    
    gestionJson.supprimer_formation(identifiant_formation=formation, id=id_formation)

    formations = gestionJson.get_infos_formations(formation)
    await interaction.response.defer()
    paginator = gestionPages.Paginator(items=formations, embed_generator=responses.generate_formation_embed, identifiant_for_embed=formation)
    embed,files = paginator.create_embed()
    await interaction.followup.send(embed=embed, files=files, view=paginator)

    # Envoie le fichier après la modification
    guild = bot.get_guild(SAVE_GUILD_ID)
    channel = guild.get_channel(SAVE_CHANNEL_ID)

    if os.path.exists("./json/formation.json"):
        with open("./json/formation.json", "rb") as file:
            await channel.send(
                content="Sauvegarde du fichier Formation suite à modification.",
                file=discord.File(file, filename=f"backup_{datetime.now().strftime('%Y%m%d')}.json")
            )
    else:
        print("Le fichier JSON n'existe pas. Aucune sauvegarde envoyée.")




# ------- Factures --------
@bot.slash_command(name="afficher_facture", description="Affiche ce que nous doit une entité", guild_ids=[GUILD_FOR_BOT_UTILISATION])
@discord.option("identifiant_facture", str, description="Selectionner l'identifiant.", choices=["Police","Gouvernement"])
@commands.has_role(ROLE_EQUIPE_MED)
async def view_facture(interaction: discord.Interaction, identifiant_facture: str):
    if interaction.channel_id != CHANNEL_FOR_FACTURES:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
        return
    factures: dict = gestionJson.get_infos_factures(identifiant_facture)["details"]
    factures_list = list(factures.items())
    
    await interaction.response.defer()
    paginator = gestionPages.Paginator(
        items=factures_list,
        embed_generator=responses.generate_factures_details_embed,
        identifiant_for_embed=identifiant_facture
        )
    embed,files = paginator.create_embed()
    await interaction.followup.send(embed=embed, file=files[0], view=paginator)



@bot.slash_command(name="ajouter_facture", description="Ajoute une facture", guild_ids=[GUILD_FOR_BOT_UTILISATION])
@discord.option("identifiant_facture", str, description="Selectionner l'identifiant.", choices=["Police","Gouvernement"])
@discord.option("montant", int, description= "Montant de la facture en dollars")
@commands.has_role(ROLE_EQUIPE_MED)
async def add_facture(interaction: discord.Interaction, identifiant_facture: str, montant: int):
    if interaction.channel_id != CHANNEL_FOR_FACTURES:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
        return
    date = datetime.now().astimezone(pytz.timezone('Pacific/Noumea'))
    date_in_6_years = date + relativedelta(years=6)
    formated_date = date_in_6_years.strftime("%d/%m/%Y")
    gestionJson.ajouter_facture(identifiant_facture=identifiant_facture, montant=montant, date=formated_date)

    factures: dict = gestionJson.get_infos_factures(identifiant_facture)["details"]
    factures_list = list(factures.items())
    
    await interaction.response.defer()
    paginator = gestionPages.Paginator(
        items=factures_list,
        embed_generator=responses.generate_factures_details_embed,
        identifiant_for_embed=identifiant_facture
        )
    embed,files = paginator.create_embed()
    await interaction.followup.send(embed=embed, file=files[0], view=paginator)


@bot.slash_command(name="supprimer_facture", description="Remet à 0 une facture", guild_ids=[GUILD_FOR_BOT_UTILISATION])
@discord.option("identifiant_facture", str, description="Selectionner l'identifiant.", choices=["Police","Gouvernement"])
@commands.has_role(ROLE_EQUIPE_MED)
async def reset_facture(interaction: discord.Interaction, identifiant_facture: str):
    if interaction.channel_id != CHANNEL_FOR_FACTURES:
        await interaction.response.send_message(
            "Cette commande ne peut pas être utilisée dans ce salon.", ephemeral=True
        )
        return
    gestionJson.supprimer_facture(identifiant_facture=identifiant_facture)
    
    factures: dict = gestionJson.get_infos_factures(identifiant_facture)["details"]
    factures_list = list(factures.items())
    
    await interaction.response.defer()
    paginator = gestionPages.Paginator(
        items=factures_list,
        embed_generator=responses.generate_factures_details_embed,
        identifiant_for_embed=identifiant_facture
        )
    embed,files = paginator.create_embed()
    await interaction.followup.send(embed=embed, file=files[0], view=paginator)


# ------- Envoi Embed --------

@bot.slash_command(name="send_embed", description="Envoie un embed en fonction des réponses d'un formulaire",guild_ids=[GUILD_FOR_BOT_UTILISATION])
async def send_form(interaction: discord.Interaction):
    if interaction.user.id != MY_ID:
        await interaction.response.send_message("Vous ne pouvez pas faire cela", ephemeral=True)
        return
    await interaction.response.send_modal(gestionModal.FormulaireModal())













# ------- Saves --------

# /manual_save -> Envoie le patients.json disponible que dans 'SAVE_GUILD_ID'
@bot.slash_command(name="manual_save", description="envoie le json", guild_ids=[SAVE_GUILD_ID])
async def manual_save_command(interaction: discord.Interaction):
    if interaction.user.id != MY_ID:
        await interaction.response.send_message("Vous ne pouvez pas faire cela", ephemeral=True)
    else:
        await daily_backup()
        await interaction.response.send_message("Fichiers envoyés !", ephemeral=True)


        guild = bot.get_guild(SAVE_GUILD_ID)
        channel = guild.get_channel(SAVE_CHANNEL_ID)

        if os.path.exists("./json/formation.json"):
            with open("./json/formation.json", "rb") as file:
                await channel.send(
                    content="Sauvegarde du fichier Formation suite à une demande.",
                    file=discord.File(file, filename=f"backup_{datetime.now().strftime('%Y%m%d')}.json")
                )
        else:
            print("Le fichier JSON n'existe pas. Aucune sauvegarde envoyée.")



# /insert_patients_json -> Remplace le json des patients par celui fourni 'SAVE_GUILD_ID'
@bot.slash_command(name="insert_patients_json", description="Remplace le json des patients par celui fourni",guild_ids=[SAVE_GUILD_ID])
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


# /insert_formation_json -> Remplace le json des patients par celui fourni 'SAVE_GUILD_ID'
@bot.slash_command(name="insert_formation_json", description="Remplace le json des patients par celui fourni",guild_ids=[SAVE_GUILD_ID])
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


        with open('./json/formation.json', mode='w') as fichier:
            json.dump(data, fichier, indent=4)

        os.remove(file_path)
        await interaction.response.send_message("Le json à bien été remplacé", ephemeral=True)



# ------------------------------------ Gestion des erreurs de permissions  ------------------------------------
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

