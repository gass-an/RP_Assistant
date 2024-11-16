import random
import discord
import images, gestionJson


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
    embed.add_field(name=':white_circle: /ping', value='ping-pong (pour tester le bot)',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name=':white_circle: /rename', value='Permet de se renommer en gardant une syntaxe utile pour le bot',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name=':white_circle: /roll', value='Fait un jet de dés : D20',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name=':white_circle: /roll2', value='Fait un jet de dés personalisé',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name=':white_circle: /afficher_patient', value='Affiche la fiche médicale du patient \n Cette commande nécessite un rôle particulier',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name=':white_circle: /creer_patient', value='Créer un nouveau patient et affiche sa fiche médicale (vierge) \n Cette commande nécessite un rôle particulier',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name=':white_circle: /ajouter_operation', value='Ajoute une opération au patient et affiche sa nouvelle fiche médicale \n Cette commande nécessite un rôle particulier',inline=False)
    embed.add_field(name='', value='',inline=False)
    embed.add_field(name=':white_circle: /supprimer_operation', value='Supprime une opération du patient et affiche sa nouvelle fiche médicale \n Cette commande nécessite un rôle particulier',inline=False)
    embed.add_field(name='', value='',inline=False)

    thumbnail_path = "./images/logo_PillboxHospital.png"
    thumbnail_file = discord.File(thumbnail_path, filename="logo_PillboxHospital.png")
    embed.set_thumbnail(url="attachment://logo_PillboxHospital.png")
    return [embed,thumbnail_file]


def roll(interaction: discord.Interaction, nb_faces: int, text_on_dice:bool):

    username_on_server = interaction.user.display_name
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
        description=f":sparkles: Votre sort se joue maintenant ! \n\n**Type de dé** : D{nb_faces} \n\nRésultat :",
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


def embed_fiche_patient(id_patient: str):

    actual_patient= gestionJson.get_patient_infos(id_patient)

    embed=discord.Embed(
        title=f"Fiche médicale de {actual_patient['prenom']} {actual_patient['nom']}",
        description=f":page_facing_up: {actual_patient['sexe']} de {actual_patient['age']} ans",
        colour=discord.Color(0xFF0000)
    )

    embed.set_footer(text=f"Patient n° {actual_patient['id_patient']} : {actual_patient['prenom']} {actual_patient['nom']}")

    nb_operation = len(actual_patient["operations"])
    for i in  range(nb_operation): 
        operation_i = actual_patient["operations"][i]
        embed.add_field(name='', value='',inline=False)
        embed.add_field(
            name=f"\n\n :red_circle: Opération n°{operation_i['id']} : {operation_i['causes']} ", 
            value=f"** Date : ** {operation_i['date']} \n  {operation_i['consequences' ]} \n ** Médecin : ** {operation_i['medecin']}",
            inline=False
            )
        
    thumbnail_path = "./images/logo_PillboxHospital.png"
    thumbnail_file = discord.File(thumbnail_path, filename="logo_PillboxHospital.png")
    embed.set_thumbnail(url="attachment://logo_PillboxHospital.png")

    image_path = f"./images/banner_PillboxHospital.png"
    image_file = discord.File(image_path, filename=f"banner_PillboxHospital.png")
    embed.set_image(url=f"attachment://banner_PillboxHospital.png")

    return [embed,[thumbnail_file, image_file]]

