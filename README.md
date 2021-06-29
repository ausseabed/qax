<img src ="/resources/Website_banner.png" alt="MATE" height=200 >
# QAX
### AusSeabed Quality Assurance Tool for Multibeam Echosounder (MBES) data
Visit ausseabed.gov.au/qax for training resources, download information and more. 

QAX provides an efficient workflow for checking multibeam echosounder data. The tool standardises quality assurance (QA) outputs and assists the technician to perform a robust QA of data.
Three plug-in tools are available through the QAX user interface that facilitate the QA checks.


### <img src ="/resources/logos/MATE.png" alt="MATE" height=50 > MATE
-	Raw data checks for unprocessed MBES data
-	Runs QA checks on .all, .kmall and .gsf files
-	Can be used for near-real time decision making
-	Matadata and messages are generated to aid downstream processing

### <img src ="/resources/logos/MBESGC.png" alt="MATE" height=50 > MBESGC
-	Grid checks for processed MBES data
-	Runs QA checks on multiband geotiff files
-	Checks data against IHO or HIPP standards

### <img src ="/resources/logos/FinderGC.png" alt="MATE" height=50 > FinderGC
-	Flags erroneous and missing data present in processed MBES data
-	Runs QA checks on multiband geotiff files
-	Identifies holidays (missing data or holes)
-	Identifies erroneous data (fliers or outliers)

![QAX_diagram](/resources/diagrams/qax_and_others.png)

QAX runs the three QA plug-ins based on user-defined input parameters and input files. After the checks are run, a check results table, QAJSON output and output files are created. The check results table provides near real time decision support QAJSON output contains the provenance and metadata on the check that was run.  Additional output files are also created for use in external software packages and enable further analysis of processed multibeam data check results.

Do you need more checks? Tell us what you think of QAX via GitHub issues or using our feedback form at ausseabed.gov.au/qax.

