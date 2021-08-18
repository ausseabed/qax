# <img src ="/resources/logos/qax_original_logo.png" alt="QAX Logo" height=50 > QAX
### Quality Assurance Tool for Multibeam Echosounder (MBES) data
Visit the [AusSeabed Website](ausseabed.gov.au/qax) for training resources, download information and more. 

### About QAX
QAX is an open-source project, jointly steered by AusSeabed, and the United States of America National Oceanic and Atmospheric Administration’s Office of Coast Survey (NOAA OCS), and the University of New Hampshire’s Center for Coastal and Ocean Mapping (UNH CCOM) that facilitates quality assurance of Multibeam Echosounder (MBES) data.

QAX provides an efficient workflow for checking multibeam echosounder data. The tool standardises quality assurance (QA) outputs and assists the technician to perform a robust QA of data.
Three plug-in tools are available through the QAX user interface that facilitate the QA checks.

### <img src ="/resources/logos/MATE.png" alt="MATE" height=50 > MATE
-	Raw data checks for unprocessed MBES data
-	Runs QA checks on .all, .kmall and .gsf files
-	Can be used for near-real time decision making
-	Matadata and messages are generated to aid downstream processing

### <img src ="/resources/logos/MBESGC.png" alt="MBESGC" height=50 > MBESGC
-	Grid checks for processed MBES data
-	Runs QA checks on multiband geotiff files
-	Checks data against IHO or HIPP standards

### <img src ="/resources/logos/FinderGC.png" alt="FinderGC" height=50 > FinderGC
-	Flags erroneous and missing data present in processed MBES data
-	Runs QA checks on multiband geotiff files
-	Identifies holidays (missing data or holes)
-	Identifies erroneous data (fliers or outliers)

### <img src ="/resources/logos/qcTools_logo.png" alt="QC Tools Logo" height=50 > QC Tools
- Coming in future release
- QA checks on MBES saved in a BAG file format

Do you need more checks? Tell us what you think of QAX using our [feedback form](https://www.ausseabed.gov.au/QAX/feedback-form).

### How QAX works
QAX runs the three QA plug-ins based on user-defined input parameters and input files. After the checks are run, a check results table, QAJSON output and output files are created. The check results table provides near real time decision support QAJSON output contains the provenance and metadata on the check that was run.  Additional output files are also created for use in external software packages and enable further analysis of processed multibeam data check results.

![QAX_diagram](/resources/diagrams/qax_and_others.png)

Do you need more checks? Tell us what you think of QAX via GitHub issues or using our feedback form on the [AusSeabed Website](ausseabed.gov.au/qax).

### QAX was born from collaboration
QAX was born from a collaboration between AusSeabed and the Center for Coastal and Ocean Mapping/Joint Hydrographic Centre (CCOM/JHC) at the University of New Hampshire and the NOAA Office of Coast Survey. QAX leverages an existing [QC Tools suite](https://www.hydroffice.org/qctools), which is part of an open research framework named [HydrOffice](https://www.hydroffice.org/) and that was developed by CCOM/JHC and NOAA. The QAX collaboration led to AusSeabed creating the first version of the QAX tool to meet the needs of the AusSeabed community. Under the hood AusSeabed developers have built QAX, only QAX itself and the FinderGC component still contain HydrOffice source code. In the future, AusSeabed aims to continue to provide updates to QAX according to its needs.

<img src ="/resources/logos/AusSeabed logo_stacked_CMYK.png" alt="ASB" height=150> <img src ="/resources/logos/CCOM.jfif" alt="CCOM" height=150> <img src ="/resources/logos/noaa-logo-no-ring-70.png" alt="NOAA" height=150>
