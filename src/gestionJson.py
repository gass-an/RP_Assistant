import json

# ------ Patients ---------
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


def get_all_patient_ids():
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

# ------ Formation ---------
def ajouter_formation(identifiant_formation: str, prenom_nom: str, date: str, valideur: str, editor: str, discord_name: str):
    try:
        with open('./json/formation.json', mode='r') as fichier:
            formations = json.load(fichier)
    except FileNotFoundError:
        formations = {}

    if identifiant_formation not in formations:
        formations[identifiant_formation] = []


    formations[identifiant_formation].append({
        "id" : len(formations[identifiant_formation]) + 1,
        "nom_prenom": prenom_nom,
        "date": date,
        "valideur" : valideur,
        "editor" : editor,
        "discord_name": discord_name
    })

    with open('./json/formation.json', mode='w') as fichier:
        json.dump(formations, fichier, indent=4)
    return "La formation à bien été ajoutée !"


def supprimer_formation(identifiant_formation: str, id: int):
    try:
        with open('./json/formation.json', mode='r') as fichier:
            formations = json.load(fichier)
    except FileNotFoundError:
        formations = {}

    # Supprimer la nouvelle opération
    del formations[identifiant_formation][id - 1]

    # Met a jour les id des formations
    for i in range (len(formations[identifiant_formation])):
        formations[identifiant_formation][i]["id"] = i + 1


    # Sauvegarder les données mises à jour
    with open('./json/formation.json', mode='w') as fichier:
        json.dump(formations, fichier, indent=4)
    return "L'opération à bien été supprimée !"


def get_infos_formations(identifiant_formation: str):
    try:
        with open('./json/formation.json', mode='r') as fichier:
            formations = json.load(fichier)
    except FileNotFoundError:
        formations = {}
    return formations[identifiant_formation]

# ------ Factures ---------
def ajouter_facture(identifiant_facture: str, montant: int, date: str):
    try:
        with open('./json/factures.json', mode='r') as fichier:
            factures = json.load(fichier)
    except FileNotFoundError:
        factures = {
            "Police" : {
                "total" : 0,
                "details" : {}
            },
            "Gouvernement" : {
                "total" : 0,
                "details" : {}
            }
        }

    if identifiant_facture not in factures:
        return

    detail_facture = factures[identifiant_facture]["details"]

    factures[identifiant_facture]["total"] += montant
    if f"{date}" not in detail_facture:
        detail_facture[f"{date}"] = []

    detail_facture[f"{date}"].append(montant)


    with open('./json/factures.json', mode='w') as fichier:
        json.dump(factures, fichier, indent=4)
    return "La formation à bien été ajoutée !"


def supprimer_facture(identifiant_facture: str):
    try:
        with open('./json/factures.json', mode='r') as fichier:
            factures = json.load(fichier)
    except FileNotFoundError:
        factures = {
            "Police" : {
                "total" : 0,
                "details" : {}
            },
            "Gouvernement" : {
                "total" : 0,
                "details" : {}
            }
        }
    if identifiant_facture not in factures:
        return

    factures[identifiant_facture] = {
        "total" : 0,
        "details" : {}
    }
    with open('./json/factures.json', mode='w') as fichier:
        json.dump(factures, fichier, indent=4)
    return "La formation à bien été supprimée !"


def get_infos_factures(identifiant_factures: str):
    try:
        with open('./json/factures.json', mode='r') as fichier:
            factures = json.load(fichier)
    except FileNotFoundError:
        factures = {}
    return factures[identifiant_factures]

# ------ Roles ---------
def load_roles_json():
    try:
        with open('./json/roles.json', mode='r') as fichier:
            return json.load(fichier)
    except FileNotFoundError:
        return []


def save_roles_json(data):
    with open('./json/roles.json', mode='w') as fichier:
        json.dump(data, fichier, indent=4)


def get_medics_display_name():
    json_data = load_roles_json()
    medics = json_data.get("medic",[])
    display_names = [medic["display"] for medic in medics]
    return display_names


def get_chirurgien_display_name():
    json_data = load_roles_json()
    chirurgiens = json_data.get("chirurgien",[])
    display_names = [chirurgien["display"] for chirurgien in chirurgiens]
    return display_names


def get_team_display_name():
    json_data = load_roles_json()
    teams = json_data.get("team",[])
    display_names = [team["display"] for team in teams]
    return display_names


# ------ User Embed ---------

def get_infos_message():
    try:
        with open('./json/message.json', mode='r') as fichier:
            return json.load(fichier)
    except FileNotFoundError:
        return 




if __name__ == '__main__' :
    ajouter_facture("Gouvernement", 1, "19/12/2026")
    ajouter_facture("Gouvernement", 2, "19/12/2026")
    ajouter_facture("Gouvernement", 3, "19/12/2026")
    ajouter_facture("Gouvernement", 4, "19/12/2026")
    ajouter_facture("Gouvernement", 5, "20/12/2026")
    ajouter_facture("Gouvernement", 6, "20/12/2026")
    ajouter_facture("Gouvernement", 7, "20/12/2026")
    ajouter_facture("Gouvernement", 9, "21/12/2026")
    

