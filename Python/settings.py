import os
import json

def load_settings():
	global settings
	file = open("settings.json", "r")
	settings = json.load(file)
	print(settings)

def write_settings():
	global settings
	file = open("settings.json", "w")
	file.write(str(shared_variables.settings))
	file.close()

def write_default_settings():
	global settings
	settings["backup_dir"] = os.getcwd() + "/Backup/"
	settings["class_dir"] = os.getcwd() + "/Sorted/"
	settings["class_method"] = "copy"
	settings["extension_list"] = [".jpg", ".png", ".mp4"]
	settings["target_dirs"] = ["emulated/0/DCIM/","emulated/0/Pictures","emulated/0/Snapchat","sdcard/DCIM"]
	settings["forbidden_dirs"] = ["emulated/0/DCIM/Screenshots","emulated/0/DCIM/ScreenRecorder","sdcard/DCIM/Screenshots"]
	settings["home_coordinates"] = None
	settings["keep_registry"] = True
	settings["birthdays_services"] = ["Google"]
	write_settings()

def add_home_coordinates(town):
	global settings
	settings["home_coordinates"] = classify.get_location_coordinates(town)

if not os.path.exists("settings.json"):
	write_default_settings()
try:
	load_settings()
except:
	write_default_settings()