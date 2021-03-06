# opiateDashboard

The University of Washington Department of Laboratory Medicine and Pathology
uses mass spectrometry for therapeutic drug monitoring for patients undergoing
opioid therapy. This project provides a dashboard used to monitor quality 
assurance parameters and liquid-chromatography tandem mass-spectrometer
 (LC-MS/MS) instrument performance.

https://desolate-citadel-06032.herokuapp.com/

This dashboard is part of a larger toolkit that involves an XML parser and 
a relational database management system which stores the metadata. The 
dashboard imports data from the database and presents the data to the user.  
The dashboard possesses 5 different graphical visualizations that summarize 
the metadata in different manners.

The assay measures 12 opioids and 11 metabolites plus ethyl glucuronide, 
performed on one of two Waters Xevo TQS instruments. Pathologists on our 
Clinical Chemistry service then integrate results from the assay with 
information from the patient’s chart to provide interpretations for the 
results. These results and interpretations are used to support decisions to 
continue or discontinue patient opioid therapy, and therefore robust quality 
control metrics are critical to the assay's clinical utility.

The folder "dashboard_files" holds a file, "qa", that holds the quality control
cutoff values and ranges for each compound of the assay. Additionally, the
file "sample_data" holds data collected from the LCMS test after being
parsed and formatted in a data table.

### Histogram
The histogram visualization displays the cumulative data based on the 
instrument, parameter, compound, sample type, and date range. The 
visualization helps identify overall instrument performance across a wide 
time range.

### Averages
The averages visualization displays the average measured parameter values per 
compound, instrument, and sample type for a given day, week, or month.  The
visualization provides a graphical and table display of the same data. 

### Batch
The batch visualization displays the plotted summary of a given batch for a 
given instrument, batch, compound, and parameter. The value of each injection is 
plotted for the chosen parameter and compound. The graphical summary is plotted 
with the QA parameter cutoff of the assay. The table summary displays the 
calculated average and standard deviation along with the number/percentage of 
samples that were out of or below the range.

### Standard-A
The standard-a visualization displays the plotted peak area signal of the first
calibrator (standard-a) for each compound and by instrument. The graph displays 
either the last 10 batches, or the data collected in the last month. The 
visualization helps identify any potential MS issues.

### Absolute RT
The absolute retention time (aRT) visualization displays the average aRT of each 
internal standard across the calibrator set for a given run against the monthly 
calculated average +/- 2 standard deviations. The running average is calculated 
from all the calibrator sets ran in the listed date range for the selected 
instrument. This visualization helps to identify any potential chromatography 
issues that need to be addressed.

#### Database
The XML parser repository can be found at https://github.com/pablouw/opiateDatabase.
For the mock-dashboard linked above which is created by the code in this repository,
the data is provided the CSV file in the folder
opiateDashboard/dashboard_files/sample_data.csv. In order for the dashboard to
obtain data from the dashboard the user would have to connect to the database
and collect the necessary information. In process_data.py, line 92 should be
changed to ```df, compound_dict = read_sql_results(db)``` to read the result
data from the database result table where db is either 'sqlite' or 'postgresql'.
Additionally, in the read_sql_results function, the path should be edited
to the appropriate location of the database.

