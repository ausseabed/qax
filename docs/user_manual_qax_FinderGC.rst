.. _qax-FinderGC:

FinderGC
============

.. index::
    single: FinderGC

Inputs
-----------------------------------------
Processed multibeam grid files can be used as input to the FinderGC plugin in QAX
File type supported by the current version:

#. Mutiband Geotiff (.tiff, .tif)

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


Fliers grid check
^^^^^^^^^^^^^^^^^^^^^^

Fliers grid checks are based off original code created by NOAA Coast Survey Development Laboratory, \
leveraging logic from hydroffice package QCTools.  Original documentation can be found \
at `QCTools <https://www.hydroffice.org/qctools/>`_ and the user manual downloaded at \
best describes the function of these checks.  The online help can be found at \
`QCTools online help <https://www.hydroffice.org/manuals/qctools/index.html>`_. For QAX there are 9 parameters \
that need to be set:

#. Laplacian Operator - threshold
#. Gaussian Curvature - threshold
#. Noisy Edges - dist
#. Noisy Edges - cf
#. Adjacent Cells - threshold
#. Adjacent Cells - percent 1
#. Adjacent Cells - percent 2
#. Small Groups - threshold
#. Small Groups - area limit

There are also two check boxes:

#. Small Groups - check slivers
#. Small Groups - check isolated

Holes grid check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Holes grid check takes the survey grid input and checks for no data pixels using \
the numpy.ma module.

The workflow is:

#. Take the input survey grid and run numpy.ma.getmask mask that identifies \
   all no data areas within the survey grid
#. If the ignore edge holes is checked the check will work through the mask \
   and idenfify holes that are conneced to the edge of the survey grid.  It \
   will remove those holes that are connected to the edge of the survey grid


Outputs
-----------------------------------------

The outputs vary depending on the grid check that is run

Fliers grid check
^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: ausseabed.findergc.lib.fliersgridcheck.FliersCheck.get_outputs

QAJson output object that contains:

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
| For this check the messages are:
| Outputs an overall failure metric of the check **?** nodes failed the flier finders check, this represents **%** of all nodes.
| Then, for each of the checks Laplacian Operator, Gaussian Curvature, Noisy Edges, Adjacent Cells, Edge Slivers and Isolated Nodes the check will output a the message:
| **?** nodes failed **check** (**%**)
| where the **?** is a count of the nodes that failed and **%** is the number of percentage of the total nodes that represents
|
| **data**:
| For this check the data is a dictionary containing the keys:
| 1. failed_cell_laplacian_operator: count of cells failing laplacian operation
| 2. failed_cell_gaussian_curvaturer: count of cells failing gaussian curvature operation
| 3. failed_cell_adjacent_cells: count of cells failing adjacent cells operation
| 4. failed_cell_sliver: count of cells failing adjacent sliver operation
| 5. failed_cell_isolated_group: count of cells failing adjacent isolated group operation
| 6. failed_cell_count_noisy_edges: count of cells failing noisy edges operation
|
| The numbers above will be the flag value associated with a data point in the map view
|
| 7. Total_cell_count: The total number of cells in the survey
| 8. map: geographic tiles for the map widget display


Holes grid check
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automethod:: ausseabed.findergc.lib.holesgridcheck.HolesCheck.get_outputs

QAJson output object that contains:

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
| A total of **?** holes were found. The total area of these holes was **x** px.
| where the **?** is a count of the no data areas in the grid and **x** is the number of pixels those holes span
|
| or
|
| No holes found
| 
| **data**:
| For this check the data is a dictionary containing the keys:
| 1. total_hole_count: count of no data areas identified by the check
| 2. total_hole_cell_count: total number of pixels or cells of no data based on the holes identified
| 3. total_cell_count: total cell count within the survey input
| 4. map: geographic tiles for the map widget display

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
.. figure:: _static/fliersgc_QAX.png
    :width: 1000px
    :align: center
    :alt: input breakdown
    :figclass: align-center

    QAX GUI input breakdown
    
When the MBES Grid Checks plugin is selected the the QAX interface will change to show the inputs
that work with the plugin.  As shown in the screenshot it is Survey DTM's.

#. Check tools - Used to select the plugin you want to run in this case mbesgc
#. Folder icon - Used to select the surface files you want to check.  Will open independant popup for selection
#. Remove file - you can remove files and of the x buttons not highlighted or the clear all files button
    .. note::
        Profile selection is not implemented in the current version of QAX
        
After the gridded files have been added into the QAX interface navigate to the plugins tab

.. _QAX_plugins_breakdown:
.. figure:: _static/findergc_parameters_qax.png
    :width: 1000px
    :align: center
    :alt: plugins breakdown
    :figclass: align-center

    QAX GUI parameters breakdown
    
The parameters are as follows:

Flier Finder Check

#. Laplacian Operator - threshold: 
#. Guassian Curvature - threshold: 
#. Noisy Edges - dist: 
#. Noisy Edges - cf: 
#. Adjacent Cells - threshold: 
#. Adjacent Cells - percent 1: 
#. Adjacent Cells - percent 2: 
#. Small Groups - threshold: 
#. Small Groups - area limit: 

Hole Finder Check

#. Ignore edge holes checkbox: Ignores a hole found if it connects to the edge of the input grid
    
.. _QAX_run_checks_breakdown:
.. figure:: _static/findergc_runchecks_breakdown_qax.png
    :width: 1000px
    :align: center
    :alt: run checks breakdown
    :figclass: align-center

    QAX GUI run checks breakdown

To run the QAX checks on your data files press the play button.  The check that is being
run will be shown on the display as well as the status.  Logging messages will provide
further information and time taken to run the checks.

#. Check outputs - The two checkboxes enable different outputs from QAX on MBES grid checks
    - Include summary spatial output in QAJSON - enables visualisations within the QAX gui.  This can be used with all plugins
    - Export detailed spatial outputs to file - enables geotiff and shapefile output able to be ingested into other geospatial applications
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
.. figure:: _static/findergc_checkresults_breakdown_qax.png
    :width: 1000px
    :align: center
    :alt: view checks breakdown
    :figclass: align-center

    QAX GUI view results breakdown
    
#. View Selection - Choose between a summary of all data, score board view to look at the individual line level or qajson output
    - Summary gives a summary of the overall check results, i.e. a count of the lines pass, fail or warning
    - Scoreboard enables viewing of results per file
    - json text is a raw printout of the QAJson created after running the checks
#. Data Level - Automatically updates on summary view but is selectable on scoreboard view.  Options are:
    - raw_data
    - survey_products
#. Check Selection - Choose the check you want to view in the details view
#. Details - Details is a subsection of the view part of the window.  It will change depending on what you select within the view pane
    - As an example selecting the summary view --> summary item for density check will display a geographic map of where this check has failed
    - If you then select the scoreboard view of the same check you will then be able to see the total number of cells, \
      number of cells failing, percentage of cells failing and the resolution of the surface