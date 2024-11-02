from typing import Final
import os 
from dotenv import load_dotenv
from discord import Intents, Client, Message, Embed
from responses import get_response

# Récupérer le token
load_dotenv()
TOKEN: Final[str] = os.getenv('discord_token')



# Initialiser le bot
intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)



# Fonction pour envoyer un message
async def send_message(message: Message, user_message) :
    if not user_message:
        print("Le message est vide")
        return
    
    response = get_response(message)
    if isinstance(response, Embed) :
        await message.channel.send(embed=response)
    else :
        await message.channel.send(response)



# Au démarrage du bot 
@client.event
async def on_ready():
    print(f"{client.user} est en cours d'exécution ")


# Gérer les messages entrant
@client.event
async def on_message(message: Message) : 
    if message.author == client.user : 
        return

    username = str(message.author)
    user_message = message.content
    channel = str(message.channel)

    print(f"[{channel}] {username} : '{user_message}' ")
    await send_message(message, user_message)


def main():
    client.run(token=TOKEN)

main()