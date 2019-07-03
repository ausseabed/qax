"""Script to download data files from the BitBucket repository"""
import sys
import os.path
import shutil
import zipfile
try:
    import wget
except ImportError as e:
    print("> missing wget, trying to install it: %s" % e)
    try:
        import pip
        pip.main(['install', 'wget'])
        import wget
    except Exception as e:
        print("  - unable to install wget: %s" % e)
        sys.exit(1)

# list of archives to download
data_files = [
    'bag.zip',
    'csar.zip',
    's57.zip',
]

# actually downloading the file with wget
for fid in data_files:
    uri = 'https://bitbucket.org/ccomjhc/hyo_base/downloads/' + fid
    print("> downloading %s" % uri)
    if os.path.isfile(fid):
        print("  - already downloaded: skipping!")
    else:
        wget.download(uri, bar=wget.bar_thermometer)
        print("  - OK")

# create an empty `download` folder
downloaded_folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), "download")
if os.path.exists(downloaded_folder):
    shutil.rmtree(downloaded_folder)
os.makedirs(downloaded_folder)

# actually unzipping the archives (then delete them)
for fid in data_files:
    with zipfile.ZipFile(fid) as zf:
        zf.extractall(downloaded_folder)
    os.remove(fid)

print("--- DONE")
