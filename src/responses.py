import random
import discord
import images
import os



def ping(interaction: discord.Interaction):
    user = interaction.user
    username = user.name
    username_on_server = user.display_name
    channel = interaction.channel.name
    server_name = interaction.guild.name

    print(f"/ping | by '{username_on_server}' ({username}) on [{server_name} -> {channel}]")

    return "Pong !"


def roll(interaction: discord.Interaction, nb_faces: int):
    if nb_faces <= 0 : 
        return "J'attends un nombre supérieur à 1 !"
    else :
        username_on_server = interaction.user.display_name
        random_number = random.randint(1, nb_faces)
        embed = discord.Embed(
            title=f":game_die: **Jet de dés pour {username_on_server}** :game_die:",
            description=f":sparkles: Le sort de votre personnage se joue maintenant ! :sparkles: \n\n**Type de dé** : D{nb_faces} \n\nRésultat :",
            colour= discord.Color(0xFF0000)
        )

        embed.set_footer(text="L'hôpital vous remercie pour votre visite")
        
        random_number_str = str(random_number)
        color = (0,0,0)
        
        if random_number == 1 :
            color = (255, 0, 0)
        elif random_number > 1 and random_number < (nb_faces//2):
            color = (255, 127, 0)
        elif random_number == (nb_faces//2):
            color = (255, 180, 80)
        elif random_number > (nb_faces//2) and random_number < nb_faces:
            color = (255, 215, 60)
        elif random_number == nb_faces : 
            color = (255, 255, 0)
            
        images.create_Text_Image(random_number_str, color)



        image_path = f"./images/{random_number}.png"
        file = discord.File(image_path, filename=f"{random_number}.png")
        embed.set_image(url=f"attachment://{random_number}.png")
        
        return [embed,file,random_number]
225