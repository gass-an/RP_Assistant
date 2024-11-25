import json


def create_patient(prenom: str, nom: str, age: int, sexe: str, creator: str):
    try:
        with open('./json/patients.json', mode='r') as fichier:
            patients = json.load(fichier)
    except FileNotFoundError:
        patients = {}

    identifiant = f"{prenom.lower()}_{nom.lower()}"

    if identifiant not in patients:
        patients[identifiant] = {
            "id_patient":len(patients),
            "prenom": prenom.capitalize(),
            "nom": nom.capitalize(), 
            "age": age,
            "sexe": sexe,
            "enregistre_par": creator, 
            "operations": []
            }

        with open('./json/patients.json', mode='w') as fichier:
            json.dump(patients, fichier, indent=4)
    
    return identifiant


def ajouter_operation(identifiant_patient: str, nouvelle_date: str, causes: str, consequenses: str, medecin: str, editor: str, discord_name: str):
    try:
        with open('./json/patients.json', mode='r') as fichier:
            patients = json.load(fichier)
    except FileNotFoundError:
        patients = {}
        
    if identifiant_patient not in patients : 
        return "Patient non touvé !"

    # Ajouter la nouvelle opération
    patients[identifiant_patient]["operations"].append({
        "id" : len(patients[identifiant_patient]["operations"]) + 1,
        "date": nouvelle_date,
        "causes": causes,
        "consequences" : consequenses,
        "medecin" : medecin,
        "editor" : editor,
        "discord_name": discord_name
    })

    # Sauvegarder les données mises à jour
    with open('./json/patients.json', mode='w') as fichier:
        json.dump(patients, fichier, indent=4)
    return "L'opération à bien été ajoutée !" 


def supprimer_operation(identifiant_patient: str, id: int):
    try:
        with open('./json/patients.json', mode='r') as fichier:
            patients = json.load(fichier)
    except FileNotFoundError:
        patients = {}

    if identifiant_patient not in patients : 
        return "Patient non touvé !"
    
    # Supprimer la nouvelle opération
    del patients[identifiant_patient]["operations"][id - 1]

    # Met a jour les id des opérations
    for i in range (len(patients[identifiant_patient]["operations"])):
        patients[identifiant_patient]["operations"][i]["id"] = i + 1


    # Sauvegarder les données mises à jour
    with open('./json/patients.json', mode='w') as fichier:
        json.dump(patients, fichier, indent=4)
    return "L'opération à bien été supprimée !" 


def get_all_ids():
    try:
        with open('./json/patients.json', mode='r') as fichier:
                patients = json.load(fichier)
                identifiants = list(patients.keys())
                return identifiants
    except FileNotFoundError:
        return []
    

def get_patient_infos(identifiant: str):
    try:
        with open('./json/patients.json', mode='r') as fichier:
            patients = json.load(fichier)
    except FileNotFoundError:
        patients = {}

    return patients[identifiant]


def load_medic_json():
    try:
        with open('./json/roles.json', mode='r') as fichier:
            return json.load(fichier)
    except FileNotFoundError:
        return []


def save_medic_json(data):
    with open('./json/roles.json', mode='w') as fichier:
        json.dump(data, fichier, indent=4)


def get_medics_display_name():
    json_data = load_medic_json()
    medics = json_data.get("medic",[])
    display_names = [medic["display"] for medic in medics]
    return display_names


if __name__ == '__main__' : 
    create_patient("John","Doe",35,"Homme")
    ajouter_operation("john_doe","10-10-2024","Accident de voiture", "Emoragie interne", "Faucon", "Faucon")
    ajouter_operation("john_doe","11-10-2024","Accident de vélo", "Plaies superficielles","Faucon", "Faucon")
    ajouter_operation("john_doe","12-10-2024","Blessure par balle", "Poumon gauche perforé","Faucon", "Faucon")
    ajouter_operation("john_doe","13-10-2024","Greffe", "Greffe Poumon gauche","Faucon", "Faucon")
    ajouter_operation("john_doe","14-10-2024","Rejet Greffe", "Retrait du poumon greffé","Faucon", "Faucon")
    ajouter_operation("john_doe","15-10-2024","Greffe", "Nouvelle greffe du Poumon gauche","Faucon", "Faucon")
    create_patient("stéphane","plaza",40,"Homme")
    print(get_patient_infos("john_doe"))
    create_patient("arTHUR", "cuiLLERE", 50, "Homme")
    get_medics_display_name()
    pass
