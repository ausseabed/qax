.. _qax-MBESGC:

MBESGC
============

.. index::
    single: MBESGC

Inputs
-----------------------------------------
Processed multibeam grid files can be used as input to the MBESGC plugin in QAX
File type supported by the current version:

#. Mutiband GeoTIFF (.tiff, .tif)

+-------------------+
|**Bands Required** |
+-------------------+
| Depth             |
+-------------------+
| Density           |
+-------------------+
| Uncertainty       |
+-------------------+

    .. note::
        The bands required in order to perform the check are Depth, Density and Uncertainty. \
        These need to be named as above and need to be contained within \
        the one file.

#. Bathymetric Attributed Grid (.bag)

+-------------------+
|**Bands Required** |
+-------------------+
| Depth             |
+-------------------+
| Density           |
+-------------------+
| Uncertainty       |
+-------------------+

    .. note::
        The bands required in order to perform the check are Depth, Density and Uncertainty. \
        Due to current bag file specification limitations the following is required \
        Two bag files are needed.  One must contain Depth as the primary layer while \
        the other must contain Density as the primary layer.  Because of this \
        it is recommended to use Geotiff files until these limitations are rectified. 

Checks
-----------------------------------------


Density grid check
^^^^^^^^^^^^^^^^^^^^^^

Use the mbesgridcheck library to provide information to the user about if the \
survey grid input adheres to specific requirement

.. autoclass:: ausseabed.mbesgc.lib.mbesgridcheck.DensityCheck

There are three parameters that can be changed to modify the Density Grid check

================================================  ====================================
Parameter                                         Description
================================================  ====================================
Minimum Soundings per node (mspn)                 Value of density node threshold
Minimum Soundings per node at percentage (mspna)  Percentage of nodes required to fail
Minimum Soundings per node percentage (mspp)      Percentage of nodes required to pass
================================================  ====================================

Using an example of how to set these parameters based on an IHO Order 1a survey \
which requires 9 soundings to contribute to each grid node across 100% of the \
grid nodes.  In this example the settings required are:

================================================  ====================================
Parameter                                         Value
================================================  ====================================
Minimum Soundings per node (mspn)                 9
Minimum Soundings per node at percentage (mspna)  100
Minimum Soundings per node percentage (mspp)      0
================================================  ====================================

The Density layer from your grid is then compared to the minimum sounding \
per node value with 100% of nodes required to have >9 soundings in order to pass

Total Vertical Uncertainty grid check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the mbesgridcheck library to provide information to the user about if the \
survey grid input adheres to specific requirement

.. autoclass:: ausseabed.mbesgc.lib.mbesgridcheck.TvuCheck

TVU check calculates the error limits using the formula

.. math:: TVU Error Limit = sqrt[a^2+(b*d)^2]

Where

=========================================  ====================================
Parameter                                  Description
=========================================  ====================================
Constant Depth Error (a)                   Sum of all constant errors in meters
Factor of Depth Dependant Errors (b)       multiplied by depth layer and is the \
                                           sum of all depth dependant errors
Depth (d)                                  Obtained from input Depth layer
=========================================  ====================================

Using an example of how to set these parameters based on an IHO Order 1a survey \
which requires a=0.5m and b=0.013

=========================================  ====================================
Parameter                                  Description
=========================================  ====================================
Constant Depth Error (a)                   0.5
Factor of Depth Dependant Errors (b)       0.013
=========================================  ====================================

The resulting calculated values would then be compared to he Uncertainty layer \
from your grid and if all Uncertainty nodes are less than the TVU error limit \
the check will pass

Resolution of grid check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use the mbesgridcheck library to provide information to the user about if the \
survey grid input adheres to specific requirement

.. autoclass:: ausseabed.mbesgc.lib.mbesgridcheck.ResolutionCheck

Resolution check calculates the required resolution of the input grid surface \
where a number of parameters are used to create linear equations for both above \
and below a particular threshold depth

.. math:: Resolution requirement for < threshold depth
.. math:: DSM * (ADM * Depth + ADC)
.. math:: Resolution requirement for > threshold depth
.. math:: DSM * (BDM * Depth + BDC)

==========================================  ======================================
Parameter                                   Description
==========================================  ======================================
Feature Detection Size Multiplier (DSM)     Multiplier for feature detection size
Threshold Depth                             Depth threshold for linear equations
Above Threshold FDS Depth Multiplier (ADM)  Above threshold depth depth multiplier                                   
Above Threshold FDS Depth Constant (ADC)    Above threshold depth depth constant
Below Threshold FDS Depth Multiplier (BDM)  Below threshold depth depth multiplier
Below Threshold FDS Depth Constant (BDC)    Below threshold depth depth constant                       
==========================================  ======================================

Using an example of how to get these parameters to work for an IHO Order 1a survey 
which requires:
Half the feature detection size
Shallower than a threshold depth of 40m a constant 2m feature detection size
Deeper than a threshold depth of 40m 5% of depth feature detection size is as follows

.. math:: Resolution requirement for < threshold depth
.. math:: 0.5 * (0 * Depth + 2)
.. math:: Resolution requirement for > threshold depth
.. math:: 0.5 * (0.05 * Depth + 0)

Outputs
-----------------------------------------

The outputs vary depending on the grid check that is run

Density grid check
^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: ausseabed.mbesgc.lib.mbesgridcheck.DensityCheck.get_outputs

QAJSON output object that contains:

+------------------+--------------------------+
|**Parameter**     |**Description**           |
+------------------+--------------------------+
|execution         |- Start time of execution |
|                  |- End time of execution   |
|                  |- Execution status        |
|                  |- Execution error         |
+------------------+--------------------------+
|**messages**      |Output messages describing|
|                  |the results of the check  |
|                  |(see below for detail)    |
+------------------+--------------------------+                     
|**data**          |Data output for the check |
|                  |(see below for detail)    |
+------------------+--------------------------+
|check_state       |- pass                    |
|                  |- warning                 |
|                  |- fail                    |
+------------------+--------------------------+

| **messages**:
| For this check the messages can be one of:
| **?** nodes were found to be under the Minimum Soundings per node setting (**mspn**)
| where the **?** is a count of the nodes that were under the threshold and **mspn** is minimum soundings per node parameter setup by the user
| 
| **?**\% of nodes were found to have a sounding count above **mspna**. This is required to be **mspp**\% of all nodes
| where the **?** is a percentage of the  total nodes that were under the threshold and **mspna** entered by the user.  **mspp** is the required percentage entered by the user
| 
| **data**:
| For this check the data is a dictionary containing the keys:
| 1. chart: for future use contains dictionary of type and data.  in this case type is histogram with data containing counts of density values in the nodes in the input data
| 2. map: geographic tiles for the map widget display


Total Vertical Uncertainty grid check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: ausseabed.mbesgc.lib.mbesgridcheck.TvuCheck.get_outputs

QAJSON output object that contains:

+------------------+--------------------------+
|**Parameter**     |**Description**           |
+------------------+--------------------------+
|execution         |- Start time of execution |
|                  |- End time of execution   |
|                  |- Execution status        |
|                  |- Execution error         |
+------------------+--------------------------+
|**messages**      |Output messages describing|
|                  |the results of the check  |
|                  |(see below for detail)    |
+------------------+--------------------------+                     
|**data**          |Data output for the check |
|                  |(see below for detail)    |
+------------------+--------------------------+
|check_state       |- pass                    |
|                  |- warning                 |
|                  |- fail                    |
+------------------+--------------------------+

| **messages**:
| For this check the messages is:
| **?** nodes failed the TVU check this represents **x**\% of all nodes within data.
| where the **?** is a count of the nodes that failed to meet the calculated TVU threshold which is **x** percent of the overall nodes in the input data
| 
| **data**:
| For this check the data is a dictionary containing the keys:
| 1. failed_cell_count: count of failed nodes in the input data
| 2. total_cell_count: total number of nodes in the input data
| 3. fraction_failed: failed_cell_count \\ total_cell_count
| 4. map: geographic tiles for the map widget display

Resolution of grid check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: ausseabed.mbesgc.lib.mbesgridcheck.ResolutionCheck.get_outputs

QAJSON output object that contains:

+------------------+--------------------------+
|**Parameter**     |**Description**           |
+------------------+--------------------------+
|execution         |- Start time of execution |
|                  |- End time of execution   |
|                  |- Execution status        |
|                  |- Execution error         |
+------------------+--------------------------+
|**messages**      |Output messages describing|
|                  |the results of the check  |
|                  |(see below for detail)    |
+------------------+--------------------------+                     
|**data**          |Data output for the check |
|                  |(see below for detail)    |
+------------------+--------------------------+
|check_state       |- pass                    |
|                  |- warning                 |
|                  |- fail                    |
+------------------+--------------------------+

| **messages**:
| For this check the messages can be one of:
| **?** nodes failed the resolution check this represents **x**\% of all nodes within data.
| where the **?** is a count of the nodes that failed to meet the calculated resolution threshold which is **x** percent of the overall nodes in the input data
| 
| **data**:
| For this check the data is a dictionary containing the keys:
| For this check the data is a dictionary containing the keys:
| 1. failed_cell_count: count of failed nodes in the input data
| 2. total_cell_count: total number of nodes in the input data
| 3. fraction_failed: failed_cell_count \\ total_cell_count
| 4. map: geographic tiles for the map widget display

   .. note::
        If the checks pass no messages will be created

Interface
-----------------------------------------
Upon initial opening of the QAX interface two windows will open.  One is a console window that provides 
extra information and assists with debugging, the other is the main graphical user interface (GUI).

.. _console:
.. figure:: _static/console_qax.png
    :width: 1000px
    :align: center
    :alt: console
    :figclass: align-center

    Console window

.. _QAX_Interface:
.. figure:: _static/interface_qax.png
    :width: 1000px
    :align: center
    :alt: initial interface
    :figclass: align-center

    Initial QAX GUI interface
    
The initial tab that is opened when QAX is started in the input tab.  A breakdown of the tab is explained
below

.. _QAX_input_breakdown:
.. figure:: _static/mbesgc_qax.png
    :width: 1000px
    :align: center
    :alt: input breakdown
    :figclass: align-center

    QAX GUI input breakdown
    
When the MBES Grid Checks plugin is selected, the QAX interface will change to show the inputs
that work with the plugin.  As shown in the screenshot, it is Survey DTM's.

#. Check tools - Used to select the plugin you want to run in this case MBES Grid Checks
#. Folder icon - Used to select the surface files you want to check.  Will open independent popup for selection
#. Remove file - you can remove files and of the x buttons not highlighted or the clear all files button
    .. note::
        Profile selection is not implemented in the current version of QAX
        
After the gridded files have been added into the QAX interface navigate to the plugins tab

.. _QAX_plugins_breakdown:
.. figure:: _static/mbesgc_parameters_qax.png
    :width: 1000px
    :align: center
    :alt: plugins breakdown
    :figclass: align-center

    QAX GUI parameters breakdown
    
The parameters are as follows:

Density Check

#. Minimum Soundings per node - Minimum number required in density layer of density layer of gridded surface
#. Minimum Soundings per node at percentage - Minimum number required in density layer of density layer of gridded surface linked with the percentage below
#. Minimum Soundings per node percentage - Percentage of cells required to pass with the minimum number from above

Resolution Check

#. Feature detection size multiplier - Multiplier to scale the feature detection size
#. Threshold depth - Depth threshold to dictate when to use above and below parameters below
#. Above threshold FDS depth multiplier - Multiplier of depth to calculate feature detection size above threshold depth
#. Above threshold FDS depth constant - Constant added to above to calculate feature detection size above threshold depth
#. Below threshold FDS depth multiplier - Multiplier of depth to calculate feature detection size below threshold depth
#. Below threshold FDS depth constant - Constant added to above to calculate feature detection size above threshold depth

Total Vertical Uncertainty Check

#. Constant depth error - Constant depth error (a) for total vertical uncertainty check
#. Factor of depth dependant errors - Factor of depth dependant errors (b) for total vertical uncertainty check
    
.. _QAX_run_checks_breakdown:
.. figure:: _static/mbesgc_runchecks_breakdown_qax.png
    :width: 1000px
    :align: center
    :alt: run checks breakdown
    :figclass: align-center

    QAX GUI run checks breakdown

To run the QAX checks on your data files press the play button.  The check that is being
run will be shown on the display as well as the status.  Logging messages will provide
further information and time taken to run the checks.

#. Check outputs - The two checkboxes enable different outputs from QAX on MBES grid checks
    - Include summary spatial output in QAJSON - enables visualisations within the QAX GUI.  This can be used with all plugins
    - Export detailed spatial outputs to file - enables GeoTIFF and shapefile output able to be ingested into other geospatial applications
        * These outputs include different outputs for each different check which includes areas that have failed checks
        * Raster data containing the calculation results for comparison and analysis in other geospatial applications

.. _External_application_example:
.. figure:: _static/allowable_uncertainty_comparison.png
    :width: 500px
    :align: center
    :alt: external_app
    :figclass: align-center

    Example of TVU check comparison in external application.  This example was inverted by the external application.  \
    In this case the cell would pass the check with Uncertainty of 0.506 being less than the absolute value of -1.040

.. _QAX_view_results_breakdown:
.. figure:: _static/mbesgc_checkresults_breakdown_qax.png
    :width: 1000px
    :align: center
    :alt: view checks breakdown
    :figclass: align-center

    QAX GUI view results breakdown
    
#. View Selection - Choose between a summary of all data, score board view to look at the individual line level or QAJSON output
    - Summary gives a summary of the overall check results, i.e. a count of the lines pass, fail or warning
    - Scoreboard enables viewing of results per file
    - JSON text is a raw printout of the QAJSON created after running the checks
#. Data Level - Automatically updates on summary view but is selectable on scoreboard view.  Options are:
    - raw_data
    - survey_products
#. Check Selection - Choose the check you want to view in the details view
#. Details - Details is a subsection of the view part of the window.  It will change depending on what you select within the view pane
    - As an example selecting the summary view --> summary item for density check will display a geographic map of where this check has failed
    - If you then select the scoreboard view of the same check you will then be able to see the total number of cells, \
      number of cells failing, percentage of cells failing and the resolution of the surface
