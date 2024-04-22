import logging

"""
These constants are used to persist values within the gui_settings config
"""

# names used in config file to remember locations user last opened file
# from the grid transformer dialog
input_folder_settings = 'grid_transformer_input_folder'
output_folder_settings = 'grid_transformer_output_folder'

# checkbox values
spatial_outputs_qajson = 'spatial_outputs_qajson'
spatial_outputs_detailed = 'spatial_outputs_detailed'
# folder detailed spatial outputs are saved to (specified on Run tab)
spatial_outputs_folder = 'spatial_outputs'

# settings UI variables
## Grid processing
gridprocessing_tile_x = 'gridprocessing_tile_x'
gridprocessing_tile_y = 'gridprocessing_tile_y'

## Log settings
logging_qax = 'logging_qax'
logging_qt = 'logging_qt'
logging_other = 'logging_other'
logging_qax_default = 'INFO'
logging_qt_default = 'ERROR'
logging_other_default = 'WARN'

LOG_LEVELS = [
    ("DEBUG", logging.DEBUG),
    ("INFO", logging.INFO),
    ("WARN", logging.WARN),
    ("ERROR", logging.ERROR),
    ("CRITICAL", logging.CRITICAL),
]
