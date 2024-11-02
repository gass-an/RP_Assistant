import random
import discord
from discord import Message, Embed

def get_response(message) :
    user_message = message.content
    lowered = user_message.lower()

    if lowered[0] == "." :
        if lowered[1:5] == "roll" :
            
            try :
                number = int(lowered[6:10])
            except : 
                return "J'attends un nombre entre 1 et 9999 \nExemple : /roll 100"
            if number <=0 : 
                return "J'attends un nombre entre 1 et 9999 \nExemple : /roll 100"
           
            random_number = random.randint(1,number)
            username = str(message.author)

            embed = Embed(
                title=f":game_die: **Jet de dés pour {username}** :game_die:",
                description=f":sparkles: Le sort de votre personnage se joue maintenant ! :sparkles: \n\n**Type de dé** : D{number} \nRésultat : **{random_number}**",
                colour=discord.Color.dark_magenta()
            )

            embed.set_footer(text="L'hôpital vous remercie pour votre visite")


            return embed
        


