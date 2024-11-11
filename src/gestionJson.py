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


def ajouter_operation(identifiant: str, nouvelle_date: str, nouvelle_operation: str):
    try:
        with open('./assets/json/patients.json', mode='r') as fichier:
            patients = json.load(fichier)
    except FileNotFoundError:
        patients = {}
    
    # Ajouter la nouvelle opération
    patients[identifiant]["operations"].append({
        "date": nouvelle_date,
        "operation": nouvelle_operation
    })

    # Sauvegarder les données mises à jour
    with open('./assets/json/patients.json', mode='w') as fichier:
        json.dump(patients, fichier, indent=4)
    return "L'opération à bien été ajoutée !" 


def supprimer_operation(identifiant: str, nouvelle_date: str, nouvelle_operation: str):
    try:
        with open('./assets/json/patients.json', mode='r') as fichier:
            patients = json.load(fichier)
    except FileNotFoundError:
        patients = {}


    # Supprimer la nouvelle opération
    patients[identifiant]["operations"].remove({
        "date": nouvelle_date,
        "operation": nouvelle_operation
    })

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

