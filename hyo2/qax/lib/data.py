from osgeo import gdal
from typing import List
import os


class RasterBandInfo():

    def __init__(self, index: int, name: str, data_type: str):
        self.index: int = index
        self.name: str = name
        self.data_type: str = data_type

    @property
    def display_name(self) -> str:
        if self.name is None:
            return str(self.index)
        else:
            return f"{self.index} ({self.name})"


class RasterFileInfo():

    def __init__(self):
        # is a valid raster input file
        self.valid = False
        self.bands: List[RasterBandInfo] = []
        self.filename = None

    def open(self, filename):
        self.bands = []
        self.filename = filename

        f: gdal.Dataset = gdal.Open(filename)
        if f is None:
            self.valid = False
            return
        self.valid = True

        self.size_x = f.RasterXSize
        self.size_y = f.RasterYSize

        self.projection = f.GetProjection()
        self.geotransform = f.GetGeoTransform()

        for band_index in range(1, f.RasterCount + 1):
            band: gdal.Band = f.GetRasterBand(band_index)

            band_name = band.GetDescription()
            band_data_type = gdal.GetDataTypeName(band.DataType)

            band_info = RasterBandInfo(band_index, band_name, band_data_type)
            self.bands.append(band_info)

    def __repr__(self) -> str:
        band_details = []
        for band in self.bands:
            band_details.append(
                f"  Band {band.index}\n"
                f"    Name: {band.name}\n"
                f"    Data type: {band.data_type}"
            )
        band_details_str = "\n".join(band_details)

        _, fn = os.path.split(self.filename)
        msg = (
            f"Filename: {fn}\n"
            f"  Size: {self.size_x}, {self.size_y}\n"
        )
        msg += band_details_str

        return msg
