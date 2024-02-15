import os
from shutil import move, copy
from exif import Image
from geopy.geocoders import Nominatim
from datetime import date
import math
import settings

if "Google" in  settings.settings["birthdays_services"]:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

def start_classifying():
    global settings
    global infos

    # Si le dossier de classement n'existe pas, le créé
    if not os.path.exists(settings.settings["class_dir"]):
        os.mkdir(settings.settings["class_dir"])

    # Si annuaire, ouvrir annuaire
    if os.path.exists(settings.settings["class_dir"]+"registry.json"):
        file = open(settings.settings["class_dir"]+"registry.json", "r")
        infos = json.load(file)
    # Sinon créer annuaire vide
    else:
        infos = {"registry":{}, "coordinates":{}}

    # Si l'utilisateur veut ajouter anniversaires Google:
    birthdates = None
    if len(settings.settings["birthdays_services"]) > 0:
        birthdates = {}
        if "Google" in settings.settings["birthdays_services"]:
            birthdates.update(get_google_birthdates())

    print("Démarrage...")
    known_distances = {}
    # Pour chaque fichier :
    for path, dirs, files in os.walk(settings.settings["backup_dir"]):
        for filename in files:
            if any(extension in filename for extension in settings.settings["extension_list"]):
                # Ouverture image
                img_path = path + "/" + filename
                with open(img_path, 'rb') as src:
                    date = None
                    coordinates = None, None
                    exif_enabled = True
                    location = ""
                    events = []
                    try:
                        img = Image(src)
                    except:
                        exif_enabled = False

                    if exif_enabled and "datetime_original" in img.list_all():
                        # Récupération date par Exif
                        #print("Date obtenue par exif")
                        date = get_date_exif(img)
                    else:
                        # Récupération date par date de modification
                        #print("Date obtenue par explorateur")
                        date = get_explorer_date(img_path)

                    # Si on a bien une date
                    if date is not None:
                        if exif_enabled and "gps_latitude" in img.list_all():
                            # Récupération localisation par Exif
                            #print("Localisation obtenue par exif")
                            coordinates = get_location_exif(img)
                        else:
                            # Récupération localisation par Ffprobe
                            #print("Tentative de localisation par FFprobe")
                            coordinates = get_location_ffprobe(img_path)

                        # Si Coordonnées:
                        if coordinates[0] is not None:
                            # Calculer différence avec domicile
                            home_distance = get_distance(settings.settings["home_coordinates"], coordinates)
                            # Si distance > 50km:
                            if home_distance > 50:
                                # Si lieu existe dans l'annuaire à cette date:
                                if date[0] in infos["registry"] and date[1] in infos["registry"][date[0]] and date[2] in infos["registry"][date[0]][date[1]] and "location" in infos["registry"][date[0]][date[1]][date[2]]:
                                    # Si distance annuaire <> lieu < 10km:
                                    registry_location = infos["registry"][date[0]][date[1]][date[2]]["location"]
                                    registry_coordinates = infos["coordinates"][registry_location]
                                    registry_distance = get_distance(registry_coordinates, coordinates)
                                    if registry_distance < 10:
                                        # Reprendre ville annuaire
                                        location = registry_location
                                    # Sinon, obtenir nom
                                    else:
                                        location = get_location_registry(coordinates, date)

                                # Si lieu n'est pas dans l'annuaire:
                                else:
                                    location = get_location_registry(coordinates, date)

                        # Pas coordonnées:
                        else:
                            # Si lieu existe dans l'annuaire:
                            if date[0] in infos["registry"] and date[1] in infos["registry"][date[0]] and date[2] in infos["registry"][date[0]][date[1]] and "location" in infos["registry"][date[0]][date[1]][date[2]]:
                                # Reprend ville annuaire
                                location = infos["registry"][date[0]][date[1]][date[2]]["location"]
                                #print("Localisation obtenue par annuaire")

                        # Dossier de sortie
                        target_folder = f'{settings.settings["class_dir"]}/{date[0]}/{date[0]} {date[1]} {date[2]}'

                    # Si la date correspond à un évènement
                    if date[2] + date[1] in settings.settings["important_dates"]:
                        events.append(settings.settings["important_dates"][date[2] + date[1]])

                    # Si la date correspond à un anniversaire
                    if birthdates is not None:
                        for name, birthday in birthdates.items():
                            if birthday[1:3] == date[1:3]:
                                text = f"Anniversaire {nom}"
                                if birthday[0] is not None:
                                    text += f" {calculate_age(date(birthday[0], birthday[1], birthday[2]))} ans"
                                events.append(text)

                    # Pas de date :
                    else:
                        target_folder = f'{settings.settings["class_dir"]}/0 - Unknown'

                # Créer nom dossier
                target_folder_final = target_folder
                if events != [] or location != "":
                    target_folder_final += " - "
                    if events != []:
                        target_folder_final += string_list(events)
                        if location != "":
                            target_folder_final += " à "
                    if location != "":
                        target_folder_final += location

                # Rajouter le lieu au dossier ayant la même date
                if os.path.exists(target_folder) and location != "":
                    # Supprimer le dossier sans géolocalisation
                    for file in os.scandir(target_folder):
                        # Déplacer les fichiers, et non dossiers
                        if file.is_file():
                            if not os.path.exists(target_folder_final):
                                os.makedirs(target_folder_final)
                            move(f"{target_folder}/{file.name}", f"{target_folder_final}/{file.name}")
                    # Si le dossier est vide, le supprime
                    if not os.listdir(target_folder):
                        os.rmdir(target_folder)

                # Créer dossier de sortie s'il n'existe pas
                elif not os.path.exists(target_folder_final):
                    os.makedirs(target_folder_final)

                # Déplacer / Copier image dans le dossier de sortie
                if settings.settings["class_method"] == "move":
                    print("Déplacement de", end="")
                    move(img_path, target_folder_final)
                else:
                    print("Copie de", end="")
                    copy(img_path, target_folder_final)
                print(f' {img_path} vers {target_folder_final}')

                # Ajouter à l'annuaire
                if not (date[0] in infos["registry"] and date[1] in infos["registry"][date[0]] and date[2] in infos["registry"][date[0]][date[1]] and "files" in infos["registry"][date[0]][date[1]][date[2]]):
                    infos = merge(infos, {"registry": {date[0]: {date[1]: {date[2]: {"files": [filename]}}}}})
                else:
                    infos["registry"][date[0]][date[1]][date[2]]["files"].append(filename)

                if location != "" and not "location" in infos["registry"][date[0]][date[1]][date[2]]:
                    infos = merge(infos, {"registry": {date[0]: {date[1]: {date[2]: {"location": location}}}}})

    # Si l'annuaire doit être créé :
    if settings.settings["keep_registry"]:
        file = open(settings.settings["class_dir"]+"/registry.json", "w")
        json.dump(infos, file)
    print("-----------------------------------------------\nOpération terminée.")












def get_date_exif(file):
    date = file.datetime_original.split(":")
    return date[0], date[1], date[2].split(" ")[0]


def get_explorer_date(path):
    timestamp = min(os.path.getctime(path), os.path.getmtime(path))
    date_string = date.fromtimestamp(timestamp).strftime('%Y-%m-%d')
    return date_string.split('-')


def get_location_exif(file):
    latitude = decimal_coords(file.gps_latitude, file.gps_latitude_ref)
    longitude = decimal_coords(file.gps_longitude, file.gps_longitude_ref)
    return latitude, longitude


def get_location_ffprobe(path):
    try:
        output = os.popen(f'ffprobe -v quiet -of json -show_entries format_tags "{path}"').read()
        output = json.loads(output)
        location = output["format"]["tags"]["location"]
        latitude = float(location[0:8])
        longitude = float(location[8:17])
        return latitude, longitude
    except KeyError:
        return None, None

def get_location_registry(coordinates, date):
    global infos
    # Tenter de trouver le nom de la ville parmi les coordonnées déjà connues
    location = None
    for city in reversed(infos["coordinates"]):
        if get_distance(coordinates, infos["coordinates"][city]) < 5:
            return city
    # Si distance toujours inconnue :
    # Obtenir nom du lieu
    location = get_location_name(coordinates)
    # Inscrire coordonnées lieu et lieu du dossier dans l'annuaire
    infos = merge(infos, {"registry": {date[0]: {date[1]: {date[2]: {"location": location}}}}, "coordinates": {location: coordinates}})
    return location


def get_location_name(location):
    global settings
    print(f"!!! Demande nom des coordonnées {location}")
    geolocator = Nominatim(user_agent="PhoneBackup")
    location = geolocator.reverse(f"{location[0]},{location[1]}")
    address = location.raw['address']
    if "town" in address:
        location = address["town"]
    elif "village" in address:
        location =  address["village"]
    elif "city" in address:
        location =  address["city"]
    return location


def get_location_coordinates(town):
    print(f"!!! Demande coordonnées de {town}")
    geolocator = Nominatim(user_agent='PhoneBackup')
    location = geolocator.geocode(town)
    return location.latitude, location.longitude


def get_distance(town1_coords, town2_coords):
    R = 6371
    phi1 = math.radians(town1_coords[0])
    phi2 = math.radians(town2_coords[0])
    delta_phi = math.radians(town2_coords[0] - town1_coords[0])
    delta_lambda = math.radians(town2_coords[1] - town1_coords[1])

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    #print(f"La distance est de {distance}km")
    return distance


def decimal_coords(coords, ref):
    decimal_degrees = coords[0] + coords[1] / 60 + coords[2] / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees


def merge(dict1, dict2):
    if not isinstance(dict1, dict) or not isinstance(dict2, dict):
        return dict2
    for key, value in dict2.items():
        if key in dict1:
            dict1[key] = merge(dict1[key], value)
        else:
            dict1[key] = value
    return dict1


def string_list(elements):
    text = ""
    for index in range(len(elements)):
        text += elements[index]
        if index == len(elements)-1:
            break
        if len(elements) > 1 and index < len(elements)-2:
            text += ", "
        else:
            text += " et "
    return text


def get_google_birthdates():
    SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        try:
            service = build('people', 'v1', credentials=creds)

            # Call the People API
            result = service.people().connections().list(resourceName='people/me', personFields='names,birthdays').execute()
            connections = result.get('connections', [])
            birthdates = {}
            for person in connections:
                names = person.get('names', [])
                if len(names) > 0:
                    name = names[0]['displayName']
                else:
                    continue
                birthdays = person.get('birthdays', [])
                if len(birthdays) > 0:
                    print(birthdays)
                    birthday = (birthdays[0].get('date').get('year'), birthdays[0].get('date').get('month'), birthdays[0].get('date').get('day'))
                else:
                    continue
                birthdates.update({name: birthday})
            print(birthdates)
            return birthdates
        except HttpError as err:
            print(err)
    else:
        print("Fichier token introuvable !")

def calculate_age(birthdate):
    today = date.today()
    age = today.year - birthdate.year
    if today.month < birthdate.month or (today.month == birthdate.month and today.day < birthdate.day):
        age -= 1
    return age
