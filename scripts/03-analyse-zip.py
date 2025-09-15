import glob
import io
import zipfile
import re
import json

def extract_between(text, start, end):
    pattern = fr'(?<={re.escape(start)})(.*?)(?={re.escape(end)})'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def analyse_zip(zip_path, search_text):
	"""
	Öffnet eine ZIP-Datei in-memory und sucht nach 'search_text' in allen enthaltenen Dateien.
	
	:param zip_path: Pfad zur ZIP-Datei
	:param search_text: Der zu suchende String
	:return: Liste der Dateinamen, die den Suchstring enthalten
	"""
	results = []

	with open(zip_path, "rb") as f:
		zip_bytes = f.read()  # ZIP-Datei als Bytes laden

	try:
		with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zip_file:
			for file_name in zip_file.namelist():
				# Nur lesbare Textdateien prüfen
				with zip_file.open(file_name) as file:
					try:
						content = file.read().decode(errors='ignore')  # Dekodierung ignoriert fehlerhafte Zeichen
						if search_text in content:
							results.append(file_name)
					except Exception as e:
						print(f"⚠ Fehler beim Lesen von {file_name}: {e}")
	except Exception as e:
		print(zip_path, e)
	return results

zip_files = glob.glob("./plugins/*.zip")
print("I will analyze that many plugins: ", len(zip_files))

plugins_with_is_admin = {}
for i,p_path in enumerate(zip_files):
	is_admin_files = analyse_zip(p_path,"is_admin")
	wp_ajax_files = analyse_zip(p_path, "wp_ajax_")
	if not is_admin_files or not wp_ajax_files:
		continue
	p_slug = extract_between(p_path, "./plugins/", ".zip")
	print("Found is_admin in: ", p_slug, len(is_admin_files))
	print("Found wp_ajax in: ", p_slug, len(wp_ajax_files))
	plugins_with_is_admin[p_slug] = list(set(is_admin_files + wp_ajax_files))
	if i % 100 == 0:
		json.dump(plugins_with_is_admin, open("03-plugins_with_is_admin.json","w"))
json.dump(plugins_with_is_admin, open("03-plugins_with_is_admin.json","w"))

