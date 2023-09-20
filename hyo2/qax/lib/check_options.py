from enum import Enum


class CheckOption(Enum):
    spatial_output_qajson = 'spatial_output_qajson'
    spatial_output_export = 'spatial_output_export'
    spatial_output_export_location = 'spatial_output_export_location'

    gridprocessing_tile_x = 'gridprocessing_tile_x'
    gridprocessing_tile_y = 'gridprocessing_tile_y'
