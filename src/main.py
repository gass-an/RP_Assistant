from typing import Final, List
import os 
from dotenv import load_dotenv
import discord 
from discord.ext import commands
import responses


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
    print(f"{bot.user} est en cours d'exécution ")



# Commandes prises en charges
@bot.slash_command(name="ping",description="ping-pong (pour tester le bot)", guild_ids=MY_GUILDS)
async def ping_command(interaction: discord.Interaction):
    
    answer = responses.ping(interaction)
    await interaction.response.send_message(answer)



@bot.slash_command(name="roll",description="Fait un jet de dés : D20", guild_ids=MY_GUILDS)
async def roll_command(interaction: discord.Interaction):

    nb_faces = 20
    answer = responses.roll(interaction, nb_faces, text_on_dice=True)
    
    if isinstance(answer[0], discord.Embed) :
        await interaction.response.send_message(embed=answer[0], files=answer[1])
        os.remove(f"./images/{answer[2]}.png")
    else :
        await interaction.response.send_message(answer)


@bot.slash_command(name="roll2",description="Fait un jet de dés personalisé", guild_ids=MY_GUILDS)
@discord.option("nb_faces", int ,description= "Entrez un nombre compris entre 1 et 100.", min_value=1, max_value=100)
async def roll_command(interaction: discord.Interaction, nb_faces: int):

    answer = responses.roll(interaction, nb_faces, text_on_dice=False)
    
    if isinstance(answer[0], discord.Embed) :
        await interaction.response.send_message(embed=answer[0], files=answer[1])
        os.remove(f"./images/{answer[2]}.png")
    else :
        await interaction.response.send_message(answer)




# user = interaction.user
# username = user.name
# username_on_server = user.display_name
# channel = interaction.channel.name
# server_name = interaction.guild.name



def main():
    bot.run(TOKEN)

if __name__ == '__main__':
    main()
