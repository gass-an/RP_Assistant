import random
import discord
import images


def ping(interaction: discord.Interaction):
    user = interaction.user
    username = user.name
    username_on_server = user.display_name
    channel = interaction.channel.name
    server_name = interaction.guild.name

    print(f"/ping | by '{username_on_server}' ({username}) on [{server_name} -> {channel}]")

    return "Pong !"


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
        
        # Couleur en fonction du résultat du dé
        if random_number == 1 :
            color = (255, 0, 0)
            color_hexa = 0xFF0000
        elif random_number > 1 and random_number < (nb_faces//2):
            color = (255, 127, 0)
            color_hexa = 0xFF7F00
        elif random_number == (nb_faces//2):
            color = (255, 255, 0)
            color_hexa = 0xFFFF00
        elif random_number > (nb_faces//2) and random_number < nb_faces:
            color = (0, 150, 0)
            color_hexa = 0x009600
        elif random_number == nb_faces : 
            color = (0, 230, 0)
            color_hexa = 0x00E600
    
    
    else : 
        font_path = "/app/fonts/LHANDW.TTF"
        bg_path = "./images/bg_roll.jpg"
        
        # Couleur en fonction du résultat du dé
        if random_number == 1 :
            color = (255, 0, 0)
            color_hexa = 0xFF0000
        elif random_number > 1 and random_number < (nb_faces//2):
            color = (255, 127, 0)
            color_hexa = 0xFF7F00
        elif random_number == (nb_faces//2):
            color = (255, 255, 0)
            color_hexa = 0xFFFF00
        elif random_number > (nb_faces//2) and random_number < nb_faces:
            color = (175, 255, 0)
            color_hexa = 0xAFFF00
        elif random_number == nb_faces : 
            color = (0, 255, 0)
            color_hexa = 0x00FF00
        




    # création de l'embed 
    embed = discord.Embed(
        title=f":game_die: **Jet de dés pour {username_on_server}** ",
        description=f":sparkles: Votre sort se joue maintenant ! \n\n**Type de dé** : D{nb_faces} \n\nRésultat :",
        colour= discord.Color(color_hexa)
    )

    embed.set_footer(text="L'hôpital vous remercie pour votre visite")
    
    
    images.create_bg_roll_Image(random_number_str, text_color=color, image_path=bg_path, font_path=font_path)

    image_path = f"./images/{random_number}.png"
    thumbnail_path = "./images/logo_PillboxHospital.png"
            
    image_file = discord.File(image_path, filename=f"{random_number}.png")
    thumbnail_file = discord.File(thumbnail_path, filename="logo_PillboxHospital.png")
    
    embed.set_image(url=f"attachment://{random_number}.png")
    embed.set_thumbnail(url="attachment://logo_PillboxHospital.png")


    return [embed,[image_file,thumbnail_file],random_number]
