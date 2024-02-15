import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QRadialGradient, QColor, QFont, QIcon, QPalette, QBrush, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QStackedWidget, QFileDialog, QLineEdit
import settings
import classify
import backup

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Outil de sauvegarde")
        self.setMinimumSize(800, 600)

        # Appliquer un dégradé bleu léger en diagonale à la fenêtre et à la barre latérale
        p = QPalette()
        print(self.width())
        gradient = QRadialGradient(self.width()/2, self.height()/2, (self.width()**2 + self.height()**2)**0.5/2)

        gradient.setColorAt(0, QColor('#0D47A1'))
        gradient.setColorAt(1, QColor('#1a2f4c'))
        p.setBrush(QPalette.ColorRole.Window, QBrush(gradient))
        self.setPalette(p)


        # Ajouter la barre latérale
        self.sidebar = QFrame()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(int(0.15*self.width()))
        self.sidebarLayout = QVBoxLayout(self.sidebar)
        self.sidebarLayout.setContentsMargins(0,0,0,0)
        self.sidebarLayout.setSpacing(0)
        self.sidebar.setStyleSheet("background-color: rgba(0, 0, 0, 51);"
                           "border-radius: 25px;"
                           "border: 1px solid rgba(255, 255, 255, 0.2);")

        # Ajouter les icônes cliquables
        self.iconHome = QPushButton()
        self.iconHome.setObjectName("iconHome")
        self.iconHome.setFixedSize(int(0.15*self.width()), int(0.15*self.width()))
        self.iconHome.clicked.connect(self.showHome)

        self.iconBackup = QPushButton()
        self.iconBackup.setObjectName("iconBackup")
        self.iconBackup.setFixedSize(int(0.15*self.width()), int(0.15*self.width()))
        self.iconBackup.clicked.connect(self.showBackup)

        self.iconClassify = QPushButton()
        self.iconClassify.setObjectName("iconClassify")
        self.iconClassify.setFixedSize(int(0.15*self.width()), int(0.15*self.width()))
        self.iconClassify.clicked.connect(self.showClassify)

        self.iconSettings = QPushButton()
        self.iconSettings.setObjectName("iconSettings")
        self.iconSettings.setFixedSize(int(0.15*self.width()), int(0.15*self.width()))
        self.iconSettings.clicked.connect(self.showSettings)

        self.iconInfos = QPushButton()
        self.iconInfos.setObjectName("iconInfos")
        self.iconInfos.setFixedSize(int(0.15*self.width()), int(0.15*self.width()))
        self.iconInfos.clicked.connect(self.showInfos)

        # Ajouter les icônes cliquables dans la barre latérale
        self.sidebarLayout.addWidget(self.iconHome)
        self.sidebarLayout.addWidget(self.iconBackup)
        self.sidebarLayout.addWidget(self.iconClassify)
        self.sidebarLayout.addWidget(self.iconSettings)
        self.sidebarLayout.addWidget(self.iconInfos)
        self.sidebarLayout.addStretch()

        # Créer les pages
        self.pages = QStackedWidget()

        # Page d'accueil
        self.pageHome = QWidget()
        self.pageHomeLayout = QVBoxLayout(self.pageHome)
        self.pageHomeLayout.setContentsMargins(50, 50, 50, 50)
        self.pageHomeTitle = QLabel("Accueil")
        self.pageHomeTitle.setObjectName("pageHomeTitle")
        self.pageHomeLayout.addWidget(self.pageHomeTitle, alignment=Qt.AlignmentFlag.AlignTop)

        self.pageHomeText = QLabel("Bienvenue dans l'Outil de sauvegarde.\nCe logiciel de sauvegarde vous permet de sauvegarder facilement des images et des vidéos depuis votre téléphone ou votre ordinateur, puis de les classer automatiquement par date et lieu dans des dossiers dédiés. Vous pouvez également ajouter des tags personnalisés pour une organisation encore plus précise. Grâce à cet outil, vous pouvez vous assurer que vos précieux souvenirs numériques sont en sécurité et faciles à retrouver.")
        self.pageHomeText.setObjectName("pageHomeText")
        self.pageHomeText.setAlignment(Qt.AlignmentFlag.AlignJustify)
        self.pageHomeText.setWordWrap(True)
        self.pageHomeLayout.addWidget(self.pageHomeText, alignment=Qt.AlignmentFlag.AlignCenter)

        self.pageHomeLayout.addWidget(self.pageHomeTitle)
        self.pageHomeLayout.addWidget(self.pageHomeText)
        self.pages.addWidget(self.pageHome)

        # Page de sauvegarde
        self.pageBackup = QWidget()
        self.pageBackupLayout = QVBoxLayout(self.pageBackup)
        self.pageBackupLayout.setContentsMargins(50,50,50,50)

        self.pageBackupTitle = QLabel("Sauvegarde du téléphone")
        self.pageBackupTitle.setObjectName("pageBackupTitle")
        self.pageBackupLayout.addWidget(self.pageBackupTitle, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Ajouter les icônes
        phone_image = QPixmap("icons/smartphone.png")
        usb_image = QPixmap("icons/usb_off.png")

        self.phone_label = QLabel()
        self.phone_label.setPixmap(phone_image.scaled(self.width() // 3 * 2, self.height() // 3 * 2, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.pageBackupLayout.addWidget(self.phone_label, alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignLeft)

        self.usb_label = QLabel()
        self.usb_label.setPixmap(usb_image.scaled(self.width() // 3, self.height() // 3, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        self.pageBackupLayout.addWidget(self.usb_label, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)

        # Ajouter le chemin d'accès, le label et le bouton Parcourir
        self.OpenFolderLayout = QHBoxLayout()
        self.pageBackupLayout.addLayout(self.OpenFolderLayout)

        path_label = QLabel('Chemin de sauvegarde :')
        self.OpenFolderLayout.addWidget(path_label)

        self.path_text = QLineEdit(settings.settings["backup_dir"])
        self.path_text.setMaximumWidth(self.width() // 3)
        self.OpenFolderLayout.addWidget(self.path_text)

        self.browse_button = QPushButton('Parcourir')
        self.browse_button.setMaximumWidth(self.width() // 8)
        self.browse_button.clicked.connect(self.selectBackup)
        self.OpenFolderLayout.addWidget(self.browse_button)

        # Ajouter le bouton pour démarrer la sauvegarde
        self.pageBackupButtonStart = QPushButton("Démarrer la sauvegarde")
        self.pageBackupButtonStart.setObjectName("pageBackupButtonStart")
        self.pageBackupButtonStart.setMaximumWidth(self.width() // 2)
        self.pageBackupButtonStart.clicked.connect(backup.startBackup)
        self.OpenFolderLayout.addWidget(self.pageBackupButtonStart, alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        self.pageBackupLayout.addLayout(self.OpenFolderLayout)

        self.pages.addWidget(self.pageBackup)

        # Page de classement des images
        self.pageClassify = QWidget()
        self.pageClassifyLayout = QVBoxLayout(self.pageClassify)
        self.pageClassifyLayout.setContentsMargins(50,50,50,50)
        self.pageClassifyTitle = QLabel("Classement des images")
        self.pageClassifyTitle.setObjectName("pageClassifyTitle")
        self.pageClassifyLayout.addWidget(self.pageClassifyTitle, alignment=Qt.AlignmentFlag.AlignTop)
        self.pageClassifyButtonSource = QPushButton("Sélectionner le dossier source")
        self.pageClassifyButtonSource.setObjectName("pageClassifyButtonSource")
        self.pageClassifyButtonSource.clicked.connect(self.selectBackup)
        self.pageClassifyLayout.addWidget(self.pageClassifyButtonSource)
        self.pageClassifyButtonDest = QPushButton("Sélectionner le dossier de destination")
        self.pageClassifyButtonDest.setObjectName("pageClassifyButtonDest")
        self.pageClassifyButtonDest.clicked.connect(self.selectClassify)

        # Ajouter le bouton pour démarrer le classement
        self.pageClassifyButtonStart = QPushButton("Démarrer le classement")
        self.pageClassifyButtonStart.setObjectName("pageClassifyButtonStart")
        self.pageClassifyButtonStart.clicked.connect(classify.start_classifying)
        self.pageClassifyLayout.addWidget(self.pageClassifyButtonDest)
        self.pageClassifyLayout.addWidget(self.pageClassifyButtonStart)
        self.pages.addWidget(self.pageClassify)

        # Paramètres
        self.pageSettings = QWidget()
        self.pageSettingsLayout = QVBoxLayout(self.pageSettings)
        self.pageSettingsLayout.setContentsMargins(50,50,50,50)
        self.pageSettingsLabel = QLabel("Paramètres")
        self.pageSettingsLabel.setObjectName("pageSettingsLabel")
        self.pageSettingsLayout.addWidget(self.pageSettingsLabel)
        self.pages.addWidget(self.pageSettings)

        # Informations
        self.pageInfos = QWidget()
        self.pageInfosLayout = QVBoxLayout(self.pageSettings)
        self.pageInfosLayout.setContentsMargins(50,50,50,50)
        self.pageInfosLabel = QLabel("Informations")
        self.pageInfosLabel.setObjectName("pageInfosLabel")
        self.pageInfosLayout.addWidget(self.pageInfosLabel)
        self.pages.addWidget(self.pageInfos)

        # Ajouter la barre latérale et les pages à la fenêtre principale
        self.mainWidget = QWidget()
        self.mainLayout = QHBoxLayout(self.mainWidget)
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)
        self.mainLayout.addWidget(self.sidebar)
        self.mainLayout.addWidget(self.pages)
        self.setCentralWidget(self.mainWidget)

        # Définir le style avec une feuille de style CSS
        self.setStyleSheet("""
        #sidebar {
            background-color: #EEE;
        }
        #iconHome {
            background-image: url(icons/home.png);
            background-repeat: no-repeat;
            background-position: center;
        }
        #iconBackup {
            background-image: url(icons/backup.png);
            background-repeat: no-repeat;
            background-position: center;
        }
        #iconClassify {
            background-image: url(icons/classify.png);
            background-repeat: no-repeat;
            background-position: center;
        }
        #iconSettings {
            background-image: url(icons/settings.png);
            background-repeat: no-repeat;
            background-position: center;
        }
        #iconInfos {
            background-image: url(icons/infos.png);
            background-repeat: no-repeat;
            background-position: center;
        }

        #pageHomeTitle, #pageBackupTitle {
            font-size: 36px;
            font-weight: bold;
            margin-bottom: 30px;
        }
        #pageHomeText, #pageBackupText {
            font-size: 18px;
            line-height: 1.5;
            margin-bottom: 20px;
        }

        #pageClassifyLabel, #pageSettingsLabel {
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        #pageBackupButtonStart, #pageClassifyButtonSource, #pageClassifyButtonDest, #pageClassifyButtonStart {
            padding: 10px;
            font-size: 18px;
            font-weight: bold;
            border: 2px solid #999;
            border-radius: 10px;
            background-color: #EEE;
            color: #333;
        }
        #pageBackupButtonStart, #pageClassifyButtonSource:hover, #pageClassifyButtonDest:hover, #pageClassifyButtonStart:hover {
            background-color: #DDD;
            cursor: pointer;
        }
        """)

    def showHome(self):
        self.pages.setCurrentWidget(self.pageHome)

    def showBackup(self):
        self.pages.setCurrentWidget(self.pageBackup)

    def showClassify(self):
        self.pages.setCurrentWidget(self.pageClassify)

    def showSettings(self):
        self.pages.setCurrentWidget(self.pageSettings)

    def showInfos(self):
        self.pages.setCurrentWidget(self.pageInfos)

    def selectBackup(self):
        # Afficher une boîte de dialogue pour sélectionner le dossier de sauvegarde
        folder_path = QFileDialog.getExistingDirectory(self, "Ouvrir un dossier de sauvegarde")
        if folder_path:
            settings.settings["backup_dir"] = folder_path
            settings.write_settings()

    def selectClassify(self):
        # Afficher une boîte de dialogue pour sélectionner le dossier de classification
        folder_path = QFileDialog.getExistingDirectory(self, "Ouvrir un dossier de classification")
        if folder_path:
            settings.settings["class_dir"] = folder_path
            settings.write_settings()

    def startClassify(self):
        # Code pour démarrer le classement des images
        pass

# Credits
# Icônes de catégories par Icones 8 : https://icones8.fr/icons/3d-fluency
app = QApplication(sys.argv)
mainWindow = MainWindow()
mainWindow.show()
sys.exit(app.exec())



"""
Intégrer toutes les options dans l'appli
Changer fichier de base
GUI faire un bouton undo qui récup tous les fichiers d'une liste et les replace à leur ancien emplacement et qui supprime les dossiers vides
Option pour mettre en pause
Désactiver GPS si hors ligne
Vérifier dépendency ffprobe, adb
Désactiver ADB si aucun appareil connecté
Nouvelle page copie fichiers
Temps restant, fichiers copiés, restants, barre de progression
Calculer coordonnées au changement de domicile
Lors de la première config, demander ville
Virer tkinter
"""
# Rendre fonctions async
# Réécrire partie json startBackup
# Classer distances par popularité
# Ajouter dates importantes
# Trouver bottleneck
# Scinder fichiers
# Fusionner dossiers 7j diff ayant le même lieu
# Rendre caché fichier registry
# Ne pas prendre en compte tous les contacts
# Utiliser module adb ?
# Enlever "/" après dossiers si déjà dans settings.json