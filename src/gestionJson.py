import json


def create_patient(nom: str, prenom: str):
    try:
        with open('./assets/json/patients.json', mode='r') as fichier:
            patients = json.load(fichier)
    except FileNotFoundError:
        patients = {}

    identifiant = f"{nom.lower()}_{prenom.lower()}"
    
    if identifiant not in patients:
        patients[identifiant] = {"nom": nom, "prenom": prenom, "operations": []}

        with open('./assets/json/patients.json', mode='w') as fichier:
            json.dump(patients, fichier, indent=4)
    
    return "La fiche du patient à bien été crée !"


def ajouter_operation(identifiant: str, nouvelle_date: str, causes: str, consequenses: str):
    try:
        with open('./assets/json/patients.json', mode='r') as fichier:
            patients = json.load(fichier)
    except FileNotFoundError:
        patients = {}
        
    if identifiant not in patients : 
        return "Patient non touvé !"

    # Ajouter la nouvelle opération
    patients[identifiant]["operations"].append({
        "id" : len(patients[identifiant]["operations"]) + 1,
        "date": nouvelle_date,
        "causes": causes,
        "consequences" : consequenses
    })

    # Sauvegarder les données mises à jour
    with open('./assets/json/patients.json', mode='w') as fichier:
        json.dump(patients, fichier, indent=4)
    return "L'opération à bien été ajoutée !" 


def supprimer_operation(identifiant: str, id: int):
    try:
        with open('./assets/json/patients.json', mode='r') as fichier:
            patients = json.load(fichier)
    except FileNotFoundError:
        patients = {}

    if identifiant not in patients : 
        return "Patient non touvé !"
    
    # Supprimer la nouvelle opération
    del patients[identifiant]["operations"][id - 1]

    # Met a jour les id des opérations
    for i in range (len(patients[identifiant]["operations"])):
        patients[identifiant]["operations"][i]["id"] = i + 1


    # Sauvegarder les données mises à jour
    with open('./assets/json/patients.json', mode='w') as fichier:
        json.dump(patients, fichier, indent=4)
    return "L'opération à bien été supprimée !" 


def get_all_ids():
    try:
        with open('./assets/json/patients.json', mode='r') as fichier:
                patients = json.load(fichier)
                identifiants = list(patients.keys())
                return identifiants
    except FileNotFoundError:
        return []
    

def get_patient_infos(identifiant: str):
    try:
        with open('./assets/json/patients.json', mode='r') as fichier:
            patients = json.load(fichier)
    except FileNotFoundError:
        patients = {}

    return patients[identifiant]


#if __name__ == '__main__' : 
