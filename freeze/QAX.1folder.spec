# Builds a single-folder EXE for distribution.
# Note that an "unbundled" distribution launches much more quickly, but
# requires an installer program to distribute.
#
# To compile, execute the following within the source directory:
#
# pyinstaller --clean -y freeze/QCTools.1folder.spec
#
# The resulting .exe file is placed in the dist/QCTools folder.
#
#
# - It may require to manually copy DLL libraries.
# - Uninstall PyQt and sip
# - For QtWebEngine:
#   . copy QtWebEngineProcess.exe in the root
#   . copy in PySide2 both "resources" and "translations" folder
# - For PyProj:
#   . copy Share folder

from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT, TOC
from PyInstaller.utils.hooks import get_package_paths, remove_prefix, PY_IGNORE_EXTENSIONS
from PyInstaller.compat import is_darwin

import os
import sys
sys.modules['FixTk'] = None

from hyo2.qc import __version__ as qc_version


def collect_pkg_data(package, include_py_files=False, subdir=None):

    # Accept only strings as packages.
    if type(package) is not str:
        raise ValueError

    pkg_base, pkg_dir = get_package_paths(package)
    if subdir:
        pkg_dir = os.path.join(pkg_dir, subdir)
    # Walk through all file in the given package, looking for data files.
    data_toc = TOC()
    for dir_path, dir_names, files in os.walk(pkg_dir):

        copy_root_token = os.path.split(dir_path)[-1]
        copy_root = copy_root_token in ["support", "configdata"]
        # if copy_root:
        #     print("- %s" % dir_path)

        for f in files:
            extension = os.path.splitext(f)[1]
            if include_py_files or (extension not in PY_IGNORE_EXTENSIONS):
                source_file = os.path.join(dir_path, f)
                dest_folder = remove_prefix(dir_path, os.path.dirname(pkg_base) + os.sep)
                dest_file = os.path.join(dest_folder, f)
                data_toc.append((dest_file, source_file, 'DATA'))

                if copy_root:
                    source_file = os.path.join(dir_path, f)
                    root_path = os.path.join(os.path.dirname(pkg_base), "hyo2", "grids") + os.sep
                    dest_folder = remove_prefix(dir_path, root_path)
                    dest_file = os.path.join(dest_folder, f)
                    # print("%s -> %s" % (dest_file, source_file))
                    data_toc.append((dest_file, source_file, 'DATA'))

    return data_toc


def collect_folder_data(folder: str, visit_sub_folders=True, include_py_files=False,):

    interpreter_path = os.path.dirname(sys.executable)
    folder_path = os.path.join(interpreter_path, folder)
    print("folder path: %s" % folder_path)
    # Walk through all file in the given package, looking for data files.
    data_toc = TOC()
    for dir_path, dir_names, files in os.walk(folder_path):

        for f in files:
            extension = os.path.splitext(f)[1]
            # print(f)
            if not include_py_files and (extension in PY_IGNORE_EXTENSIONS):
                continue

            source_file = os.path.join(dir_path, f)
            dest_folder = remove_prefix(dir_path, interpreter_path + os.sep)
            dest_file = os.path.join(dest_folder, f)
            data_toc.append((dest_file, source_file, 'DATA'))

        if not visit_sub_folders:
            break

    return data_toc


qc_data = collect_pkg_data('hyo2.qc')
grids_data = collect_pkg_data('hyo2.grids')
rori_data = collect_pkg_data('hyo2.rori')
unc_data = collect_pkg_data('hyo2.unccalc')
proj4_data = collect_folder_data(folder=os.path.join("Library", "share"))
pyside2_data = collect_pkg_data('PySide2')

icon_file = 'freeze\QCTools.ico'
if is_darwin:
    icon_file = 'freeze\QCTools.icns'

a = Analysis(['QCTools.py'],
             pathex=[],
             hiddenimports=["PIL", "scipy.linalg", "hyo2.grids._gappy", "scipy._lib.messagestream",
             "PySide2.QtPrintSupport"],
             excludes=["IPython", "PyQt4", "PyQt5", "pandas", "sphinx", "sphinx_rtd_theme", "OpenGL_accelerate",
                       "FixTk", "tcl", "tk", "_tkinter", "tkinter", "Tkinter",
                       "wx"],
             hookspath=None,
             runtime_hooks=None)

pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='QCTools.%s' % qc_version,
          debug=False,
          strip=None,
          upx=True,
          console=True,
          icon=icon_file)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               qc_data,
               grids_data,
               rori_data,
               unc_data,
               proj4_data,
               pyside2_data,
               strip=None,
               upx=True,
               name='QCTools.%s' % qc_version)
