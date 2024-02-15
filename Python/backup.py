import os
from tkinter import messagebox
import subprocess
import settings

def startBackup():
    try:
        subprocess.run(["adb", "kill-server"])
    except FileNotFoundError:
        messagebox.showerror("Dépendance manquante", 'La dépendance "adb" est manquante.')
        return
    subprocess.run(["adb", "start-server"])

    # Créé le dossier par défaut s'il n'a pas été changé
    if not os.path.exists(settings.settings["backup_dir"]):
        os.mkdir(settings.settings["backup_dir"])
    # Ouvrir liste de fichiers déjà traités
    if not os.path.exists(settings.settings["backup_dir"] + "/backup_list"):
        print("Première sauvegarde")
        old_list = {}
    else:
        file = open(settings.settings["backup_dir"] + "/backup_list", "r")
        old_list = file.read()
    file = open(settings.settings["backup_dir"] + "/backup_list", "w")
    if not old_list == {}:
        file.write(old_list)
        print('A CHANGER')
        #try:
            #old_list = ast.literal_eval(old_list)
        #except SyntaxError:
            #old_list = ast.literal_eval(old_list + "}")
    else:
        file.write("{")
    actual_folder = ""
    recent_file = ""
    first_round = True
    found_folder = False
    for backup_folder in range(len(settings.settings["target_dirs"])):
        backup_list = subprocess.run(['adb', 'shell', 'ls', '-R1tr', '"/storage/' + settings.settings["target_dirs"][backup_folder] + '"'], capture_output=True, encoding="utf-8").stdout.split()
        print(backup_list)
        # Liste chaque ligne une par une
        for line in range(len(backup_list)):
            # Regarde si l'élément actuel est une image / vidéo
            if any(substring in backup_list[line] for substring in settings.settings["extension_list"]):
                # Si ce dossier a été copié précédement
                if actual_folder[:len(actual_folder) - 1] in old_list:
                    # Attend de trouver les images plus récentes que la dernière sauvegarde
                    if not found_folder:
                        if recent_file == old_list[actual_folder[:len(actual_folder) - 1]]:
                            found_folder = True
                            continue
                        else:
                            print("Skipping until new files")
                            continue
                recent_file = backup_list[line]
                # Regarde si le répertoire est interdit
                if actual_folder[9:len(actual_folder) - 1] in settings.settings["forbidden_dirs"]:
                    print("Skipping until valid directory")
                    continue
                # Fichier valide -> copie
                print("copying", actual_folder[:len(actual_folder) - 1] + "/" + recent_file)
                subprocess.run(['adb', 'pull', '-a', f'{actual_folder[:len(actual_folder) - 1]}/{recent_file}', f'{settings.settings["backup_dir"]}/{recent_file}'])
            else:
                temp = str(backup_list[line]) + " "
                # Regarde si l'élément actuel est un dossier
                if temp[0] == "/":
                    print("changing folder :", backup_list[line])
                    found_folder = False
                    if not first_round and not recent_file == "":
                        file.write("'" + actual_folder[:len(actual_folder) - 1] + "':'" + recent_file + "',")
                    else:
                        first_round = False
                    actual_folder = backup_list[line]
                    recent_file = ""
    file.close()
    subprocess.run(["adb", "kill-server"])
    print("-----------------------------------------------\nOpération terminée.")

