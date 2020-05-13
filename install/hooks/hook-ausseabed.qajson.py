from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('ausseabed.qajson')

print("**********")
print(datas)
print()
