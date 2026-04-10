# hack to workaround missing rasterio imports
# https://stackoverflow.com/a/69376916

import pkgutil
import rasterio

hiddenimports = [
    package.name
    for package in pkgutil.iter_modules(rasterio.__path__, prefix="rasterio.")
]
