import random
import discord
import images, gestionJson
import os

EPHEMERE = False

def ping(interaction: discord.Interaction):
    user = interaction.user
    username = user.name
    username_on_server = user.display_name
    channel = interaction.channel.name
    server_name = interaction.guild.name

    print(f"/ping | by '{username_on_server}' ({username}) on [{server_name} -> {channel}]")

    return "Pong !"


def help():
    embed=discord.Embed(
        title="Le /help",
        description="C'est ici qu'est répertorié chaque fonctionnalité du bot !",
        colour=discord.Color(0xFFFFFF)
    )

    embed.set_footer(text="En éspérant avoir aidé")
    
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name='· /ping', value='ping-pong (pour tester le bot)',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name='· /rename', value='Permet de se renommer en gardant une syntaxe utile pour le bot',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name='· /roll', value='Fait un jet de dés personalisé',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name='· /roll20', value='Fait un jet de dés : D20',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name='· /liste_patient', value='Affiche le nom des patients inscrits à l\'hôpital \n Cette commande nécessite un rôle particulier',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name='· /afficher_patient', value='Affiche la fiche médicale du patient \n Cette commande nécessite un rôle particulier',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name='· /creer_patient', value='Créer un nouveau patient et affiche sa fiche médicale (vierge) \n Cette commande nécessite un rôle particulier',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name='· /ajouter_operation', value='Ajoute une opération au patient et affiche sa nouvelle fiche médicale \n Cette commande nécessite un rôle particulier',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name='· /supprimer_operation', value='Supprime une opération du patient et affiche sa nouvelle fiche médicale \n Cette commande nécessite un rôle particulier',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name='· /afficher_formation', value='Affiche la liste des personnels formés \n Cette commande nécessite un rôle particulier',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name='· /ajouter_formation', value='Ajoute un nouveau personnel formé dans la liste adéquate. \n Cette commande nécessite un rôle particulier',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name='· /supprimer_formation', value='Supprime une formation dans la liste des personnels formés \n Cette commande nécessite un rôle particulier',inline=False)
    embed.add_field(name='', value='',inline=False)

    thumbnail_path = "./images/logo_PillboxHospital.png"
    thumbnail_file = discord.File(thumbnail_path, filename="logo_PillboxHospital.png")
    embed.set_thumbnail(url="attachment://logo_PillboxHospital.png")
    return [embed,thumbnail_file]


def roll(interaction: discord.Interaction, nb_faces: int, text_on_dice:bool):
    global EPHEMERE

    username_on_server = interaction.user.display_name
    if EPHEMERE:
        random_number = random.randint(1, 5)
        EPHEMERE = False
    else:
        random_number = random.randint(1, nb_faces)
    random_number_str = str(random_number)

    # Chemins en fonction de l'image de fond souhaitée
    if text_on_dice :
        
        font_path = "/app/fonts/arial.ttf"
        if random_number in [2,4,6,8,10,12,14,16,18,20]:
            bg_path = "./images/bg_dice_impairs.png"
        else :
            bg_path = "./images/bg_dice_pairs.png"
        

        # Couleur et footer en fonction du résultat du dé
        if random_number == 1 :
            color = (255, 0, 0)
            color_hexa = 0xFF0000
            text_footer = "Échec critique !"
        elif random_number > 1 and random_number < (nb_faces//2):
            color = (255, 127, 0)
            color_hexa = 0xFF7F00
            text_footer = "Échec ... "
        elif random_number == (nb_faces//2):
            color = (255, 255, 0)
            color_hexa = 0xFFFF00
            text_footer = "Ni bon, ni mauvais... "
        elif random_number > (nb_faces//2) and random_number < nb_faces:
            color = (0, 150, 0)
            color_hexa = 0x009600
            text_footer = "Réussite."
        elif random_number == nb_faces : 
            color = (0, 230, 0)
            color_hexa = 0x00E600
            text_footer = "Réussite critique !" 
    
    
    else : 
        font_path = "/app/fonts/LHANDW.TTF"
        bg_path = "./images/bg_roll.jpg"

        # Couleur et footer en fonction du résultat du dé
        if random_number == 1 :
            color = (255, 0, 0)
            color_hexa = 0xFF0000
            text_footer = "Échec critique !"
        elif random_number > 1 and random_number < (nb_faces//2):
            color = (255, 127, 0)
            color_hexa = 0xFF7F00
            text_footer = "Échec ... "
        elif random_number == (nb_faces//2):
            color = (255, 255, 0)
            color_hexa = 0xFFFF00
            text_footer = "Ni bon, ni mauvais... "
        elif random_number > (nb_faces//2) and random_number < nb_faces:
            color = (175, 255, 0)
            color_hexa = 0xAFFF00
            text_footer = "Réussite."
        elif random_number == nb_faces : 
            color = (0, 255, 0)
            color_hexa = 0x00FF00
            text_footer = "Réussite critique !" 
        

    # création de l'embed 
    embed = discord.Embed(
        title=f":game_die: **Jet de dés pour {username_on_server}** ",
        description= f":sparkles: Votre sort se joue maintenant ! \n\n**Type de dé** : D{nb_faces} \n\nRésultat :",
        colour= discord.Color(color_hexa)
    )

    embed.set_footer(text=text_footer)
    
    
    images.create_bg_roll_Image(random_number_str, text_color=color, image_path=bg_path, font_path=font_path)

    image_path = f"./images/{random_number}.png"
    thumbnail_path = "./images/logo_PillboxHospital.png"
            
    image_file = discord.File(image_path, filename=f"{random_number}.png")
    thumbnail_file = discord.File(thumbnail_path, filename="logo_PillboxHospital.png")
    
    embed.set_image(url=f"attachment://{random_number}.png")
    embed.set_thumbnail(url="attachment://logo_PillboxHospital.png")


    return [embed,[image_file,thumbnail_file],random_number]


def generate_list_patient_embed(patients, current_page, total_pages, identifiant):
    
    embed=discord.Embed(
            title="Liste des patients",
            description="Voici ci-dessous la liste de tous les patients enregistés à l'hôpital (par ordre alphabétique).",
            colour=discord.Color(0xFF0000)
        )
    embed.set_footer(text=f"Nombre de patients inscrits : {len(gestionJson.get_all_patient_ids())}\nPage {current_page + 1}/{total_pages}")

    for patient_id in patients:
        prenom, nom = patient_id.split("_")
        embed.add_field(name='', value='',inline=False)
        embed.add_field(
            name=f"· {prenom.capitalize()} {nom.capitalize()}",
            value="",
            inline=False
        )
    
    thumbnail_path = "./images/logo_PillboxHospital.png"
    thumbnail_file = discord.File(thumbnail_path, filename="logo_PillboxHospital.png")
    embed.set_thumbnail(url="attachment://logo_PillboxHospital.png")

    image_path = f"./images/banner_PillboxHospital.png"
    image_file = discord.File(image_path, filename="banner_PillboxHospital.png")
    embed.set_image(url="attachment://banner_PillboxHospital.png")

    files =[thumbnail_file,image_file]

    return embed,files


def generate_fiche_patient_embed(operations, current_page, total_pages, id_patient):
    
    actual_patient= gestionJson.get_patient_infos(id_patient)

    embed=discord.Embed(
        title=f"Fiche médicale de {actual_patient['prenom']} {actual_patient['nom']}",
        description=f":page_facing_up: {actual_patient['sexe']} de {actual_patient['age']} ans",
        colour=discord.Color(0xFF0000)
    )

    embed.set_footer(text=f"Patient n° {actual_patient['id_patient']} : {actual_patient['prenom']} {actual_patient['nom']}\nPage {current_page + 1}/{total_pages}")

    for operation in operations: 
        embed.add_field(name='', value='',inline=False)
        embed.add_field(
            name=f"\n\n :red_circle: Opération n°{operation['id']} : {operation['causes']} ", 
            value=f"** Date : ** {operation['date']} \n  {operation['consequences' ]} \n ** Médecin : ** {operation['medecin']}",
            inline=False
            )
        
    thumbnail_path = "./images/logo_PillboxHospital.png"
    thumbnail_file = discord.File(thumbnail_path, filename="logo_PillboxHospital.png")
    embed.set_thumbnail(url="attachment://logo_PillboxHospital.png")

    image_path = f"./images/banner_PillboxHospital.png"
    image_file = discord.File(image_path, filename="banner_PillboxHospital.png")
    embed.set_image(url="attachment://banner_PillboxHospital.png")

    return embed,[thumbnail_file, image_file]


def generate_formation_embed(formations, current_page, total_pages, identifiant_formation: str):

    actual_formation= gestionJson.get_infos_formations(identifiant_formation)

    if identifiant_formation == "Brancardiers" : 
        title= "Fiche des brancardiers"
        description= "Suite à cette formation les brancardiers peuvent utiliser tous les types de pansements ainsi que les kits de sutures"
        image_path = "./images/brancardiers.png"
        image_file = discord.File(image_path, filename="brancardiers.png")
        image_url = "attachment://brancardiers.png"

    elif identifiant_formation == "Infirmiers" :
        title= "Fiche des Infirmiers"
        description= "Suite à cette formation les infirmiers peuvent utiliser de la morphine, de l'adrénaline, du sang, et le sérum"
        image_path = "./images/infirmiers.png"
        image_file = discord.File(image_path, filename="infirmiers.png")
        image_url = "attachment://infirmiers.png"

    elif identifiant_formation == "Médecins" :
        title= "Fiche des Médecins"
        description= "Suite à cette formation les médecins peuvent utiliser le propofol"
        image_path = "./images/medic.png"
        image_file = discord.File(image_path, filename="medic.png")
        image_url = "attachment://medic.png"

    elif identifiant_formation == "Ambulances" :
        title= "Fiche des personnes possédant le permis Poids-lourds"
        description= "Suite à cette formation vous avez le droit de piloter les ambulances"
        image_path = "./images/ambulance.jpg"
        image_file = discord.File(image_path, filename="ambulance.jpg")
        image_url = "attachment://ambulance.jpg"

    elif identifiant_formation == "Hélicoptères" :
        title= "Fiche des personnes possédant le permis Hélicoptère"
        description= "Suite à cette formation vous avez le droit de piloter les hélicoptères"
        image_path = "./images/helico.png"
        image_file = discord.File(image_path, filename="helico.png")
        image_url = "attachment://helico.png"


    embed=discord.Embed(
        title=title,
        description=description,
        colour=discord.Color(0xFF0000)
    )

    nb_personnel = len(actual_formation)
    
    for formation in formations:
        embed.add_field(name='', value='',inline=False)
        embed.add_field(
            name=f" :red_circle: {formation['nom_prenom']}", 
            value=f" ** Date ** : {formation['date']} \n ** Validé par : ** {formation['valideur']} \nNuméro de formation :  {formation['id']}",
            inline=False
            )
    
    embed.set_footer(text=f"Nombre de personnes formées : {nb_personnel}\nPage {current_page + 1}/{total_pages}")

    thumbnail_path = "./images/logo_PillboxHospital.png"
    thumbnail_file = discord.File(thumbnail_path, filename="logo_PillboxHospital.png")
    embed.set_thumbnail(url="attachment://logo_PillboxHospital.png")

    embed.set_image(url=image_url)
    return [embed,[thumbnail_file, image_file]]


def generate_factures_details_embed(factures, current_page, total_pages, identifiant_facture: str):
    
    montant_total = gestionJson.get_infos_factures(identifiant_facture)["total"]
    
    embed=discord.Embed(
        title=f"Facture {identifiant_facture}",
        description=f"Voici la facture détaillée de l'entité {identifiant_facture}",
        colour=discord.Color(0xFF0000)
    )
    for facture in factures:
        embed.add_field(name='', value='',inline=False)
        value_str = ""
        for i in facture[1]:
            value_str += f"** Montant ** : {i}\n"
        embed.add_field(
            name=f" :red_circle: Date : {facture[0]}", 
            value=value_str,
            inline=False
            )
    
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name=f':green_circle: Montant total : {montant_total}', value='',inline=False)

    embed.set_footer(text=f"Page {current_page + 1}/{total_pages}")
    thumbnail_path = "./images/logo_PillboxHospital.png"
    thumbnail_file = discord.File(thumbnail_path, filename="logo_PillboxHospital.png")
    embed.set_thumbnail(url="attachment://logo_PillboxHospital.png")
    return [embed,[thumbnail_file]]


def get_response(user_message):
    lowered = user_message.lower()
    words = set(lowered.split())

    ems = {"ems", "medic", "médic", "médecin", "medecin","médecins", "medecins", "docteur", "quelqu'un", "quelqu un", "qulequun"}
    action = {"co", "connecte", "connecté","connectes", "connectés", "ville", "arrive", "arrivent", "svp", "service", "services", "avoir", "dispo", "disponible", "disponibles"}

    if len(lowered) < 50 :    
        if words & ems:
            if words & action:
                message = ("## Message du Pillbox Hospital\n"
                        "Il existe une façon in-game pour le savoir ! \n\n"
                        "Utilise ton téléphone -> Contact -> EMS, si tu peux nous appeler alors on est là !\n\n"
                        "Dans ce cas, si ça fait longtemps que tu atttends n'hésite pas à faire un /911ems\n"
                        "Et si on est pas là, il y a toujours l'unité X :)\n"
                        "Toute l'équipe médicale te remercie et te souhaite bon jeu."
                        )
                return message

    return None


def user_embed():
    infos_message = gestionJson.get_infos_message()

    embed=discord.Embed(
            title=infos_message['titre'],
            description=infos_message['description'],
            colour=discord.Color(0xFF0000)
        )
    embed.set_footer(text=infos_message['footer'])
    
    thumbnail_path = "./images/logo_PillboxHospital.png"
    thumbnail_file = discord.File(thumbnail_path, filename="logo_PillboxHospital.png")
    embed.set_thumbnail(url="attachment://logo_PillboxHospital.png")


    os.remove(f"./json/message.json")

    return embed,thumbnail_file

