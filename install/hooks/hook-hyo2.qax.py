from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('hyo2.qax')

print("**********")
print(datas)
print()
