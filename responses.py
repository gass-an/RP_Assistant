import random

def get_response(user_message) :
    lowered = user_message.lower()

    if lowered[0] == "/" :
        if lowered[1:5] == "roll" :
            try :
                number = int(lowered[6:10])
            except : 
                return "J'attends un nombre entre 1 et 9999 \nExemple : /roll 100"

            random_number = random.randint(1,number)
            return f"{random_number} (1-{number})"
