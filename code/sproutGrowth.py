'''
 sproutGrowth.py  is a Python script to calculate linear regression parameters (a,b) in  y = a * t + b for growth of young sprout of the 
 Camellia Sinensis plant. 'a' is the growth rate in mm/day, 'b' the start length as the (random) zero time reference, 
 'y' the length of the sprout in mm  and 't' the time in days.
 
 version: 20211021
 author: Maarten Roos

'''


import numpy as np
from scipy import stats
import matplotlib.pyplot as plt 
import re

from HandyTools import HandyTools as ht


# The string set to use in this run
# iFileNamesAndStrings = 0
iFileNamesAndStrings = 1

# Boolean to produce figures as png files or not
produceFigures = False


# The first string is the file name of a "download as cvs" from a Google Sheet, found in this Google folder:
#  https://drive.google.com/drive/folders/1QKy8gKy13t4JcW88e84t-2N_utGdjZH2?usp=sharing
fileNamesAndStrings = [

# iFileNamesAndStrings = 0
['Camelia Sinensis Plants Growth Record - Sprout Development 20210317-20210419.csv',
'Camelia Sinensis Plants Growth Record - Sprout Development 20210317-20210419 Table.csv',
'Camelia Sinensis Plants Growth Record - Sprout Development 20210317-20210419 Parameters.csv',
'Time (days relative to 17 March 2021 at 15h UTC)'],

# iFileNamesAndStrings = 1
['Camelia Sinensis Plants Growth Record - Sprout Development 20210701-20210901.csv',
'Camelia Sinensis Plants Growth Record - Sprout Development 20210701-20210901 Table.csv',
'Camelia Sinensis Plants Growth Record - Sprout Development 20210701-20210901 Parameters.csv',
'Time (days relative to 01 July 2021 at 18h UTC)'],

]



def uncertaintyEstimator (relativeDates, recordedLengths, uncertaintyRecordedLengths, numberOfTrials = 1000):
    '''
    In this function the uncertainty in the derived regression parameters (a,b) in y = a * x + b, is determined using a
     Monte Carlos type of approach: new data sets (numberOfTrials times) are created by randomly adding a Gaussian distribution 
     with a standard deviation of  uncertaintyRecordedLengths  and new regression parameters are determined for each set. 
     The standard deviation of all sets is a good indication for the uncertainty in the parameters  a  and  b.
    '''

    numberOfRecordings = len (recordedLengths)

    randomLengths = []        
    for recordedLength in recordedLengths:
    
        randomLengths.append ( np.random.normal (recordedLength, uncertaintyRecordedLengths, numberOfTrials) )  
    
    
    growthRateTrials = []
    startLengthTrials = []    
    for iTrial in range (numberOfTrials):
    
        randomLength = [ randomLengths [iRecording][iTrial]  for iRecording in range (numberOfRecordings) ]
    
        a, b, da, db = ht.linearLeastSquare (relativeDates, randomLength)
                   
        growthRateTrials.append (a)
        startLengthTrials.append (b) 
        
    
    averageGrowthRate = np.mean (growthRateTrials)
    uncertaintyGrowthRate = np.std (growthRateTrials)
    
    averageStartLength = np.mean (startLengthTrials)
    uncertaintyStartLength = np.std (startLengthTrials)
        
    return averageGrowthRate, averageStartLength, uncertaintyGrowthRate, uncertaintyStartLength
                          


# fileCSVOpen = open (r'Camelia Sinensis Plants Growth Record - Sprout Development 20210317-20210419.csv')
fileCSVOpen = open ( fileNamesAndStrings [iFileNamesAndStrings][0] )

recordedData = fileCSVOpen.readlines ()
fileCSVOpen.close ()

dateStrings = []
julianDates = []
numberOfSprouts = len (recordedData [2].split (',')) - 2
sprouts = [ [] for _ in range (numberOfSprouts) ]

sproutNames = recordedData [0].split (',')

# The last item in the cvs list is followed by the  '\n'  character, which should not be taken with the sproutNames string
if '\n' in sproutNames [-1]: sproutNames [-1] = sproutNames [-1][:-1]

del sproutNames [0:2]


# Determine the indices of the linear section of the growth curve: [0:-1] means include all indices
unravelledLine = recordedData [1].split (',')
indicesLinearRangePerSprout = []
for iSprout in range (numberOfSprouts):

    indicesLinearRangePerSprout.append ([0,-1])
    if unravelledLine [iSprout + 2] != '' and unravelledLine [iSprout + 2] != '\n': 
        
        indicesForRange = re.findall (r'-?\d+\.?\d*', unravelledLine [iSprout + 2])

        firstIndex = int (indicesForRange [0])
        lastIndex = -1  if len (indicesForRange) == 1  else  int (indicesForRange [1])
               
        indicesLinearRangePerSprout [-1] = [firstIndex,lastIndex]



for iData in range (2,len (recordedData)):

    unravelledLine = recordedData [iData].split (',')
    
    dateStrings.append (unravelledLine [0])
    julianDates.append (float (unravelledLine [1]))
    for iSprout in range (numberOfSprouts):
    
        sprouts [iSprout].append (np.nan)
        if unravelledLine [iSprout + 2] != '' and unravelledLine [iSprout + 2] != '\n': 
            
            sprouts [iSprout][-1] = float (unravelledLine [iSprout + 2])



        
julianDates = np.asarray (julianDates)
sprouts = np.asarray (sprouts)
relativeDate = julianDates - julianDates [0] 
uncertaintyRecordedLength = 2  # mm

growthRateList = []
growthRateUncertaintyList = []

startLengthList = []
startLengthUncertaintyList = []


# This array contains for each valid measurement set the spout ID, the number of measurement points, 
#  the start length, the start length uncertainty, the growth rate and growth rate uncertainty.
sproutGrowthParameters = []
for iSprout in range (numberOfSprouts):
    
    iValid = np.isfinite ( sprouts [iSprout] )

    growthRateList.append (np.nan)
    growthRateUncertaintyList.append (np.nan)
    
    startLengthList.append (np.nan)
    startLengthUncertaintyList.append (np.nan)


    # Only consider sprouts for which more than two measurements have been made
    if len (np.where (iValid) [0]) > 2:

        print ('   ', iSprout, sproutNames [iSprout])

        startIndexLinearRange = indicesLinearRangePerSprout [iSprout][0]
        endIndexLinearRange = indicesLinearRangePerSprout [iSprout][1]

        # All data points are in the linear range
        if indicesLinearRangePerSprout [iSprout] == [0,-1]:

            growthRate, startLength, growthRateUncertainty, startLengthUncertainty = \
                ht.linearLeastSquare (relativeDate [iValid], sprouts [iSprout][iValid])
                
            pearsonsRpValue = stats.pearsonr (relativeDate [iValid], sprouts [iSprout][iValid])

 
        # Linear range starts at data point with  startIndexLinearRange
        elif endIndexLinearRange == -1:
        
            growthRate, startLength, growthRateUncertainty, startLengthUncertainty = \
                ht.linearLeastSquare ( relativeDate [iValid][startIndexLinearRange:], 
                                       sprouts [iSprout][iValid][startIndexLinearRange:] )

            pearsonsRpValue = stats.pearsonr ( relativeDate [iValid][startIndexLinearRange:], 
                                 sprouts [iSprout][iValid][startIndexLinearRange:] )


        # Linear range is between  startIndexLinearRange  and  endIndexLinearRange - 1
        else:
        
            growthRate, startLength, growthRateUncertainty, startLengthUncertainty = \
                ht.linearLeastSquare ( relativeDate [iValid][startIndexLinearRange:endIndexLinearRange], 
                                       sprouts [iSprout][iValid][startIndexLinearRange:endIndexLinearRange] )

            pearsonsRpValue = stats.pearsonr ( relativeDate [iValid][startIndexLinearRange:endIndexLinearRange], 
                                 sprouts [iSprout][iValid][startIndexLinearRange:endIndexLinearRange] )

        
        
        print ('growthRate, startLength, growthRateUncertainty, startLengthUncertainty from Least Square:')
        print (growthRate, startLength, growthRateUncertainty, startLengthUncertainty)
        print (' PearsonsR p-value = ', pearsonsRpValue)


        # All data points are in the linear range
        if indicesLinearRangePerSprout [iSprout] == [0,-1]:

            averageGrowthRate, averageStartLength, growthRateUncertainty, startLengthUncertainty = \
                uncertaintyEstimator (relativeDate [iValid], sprouts [iSprout][iValid], 
                                      uncertaintyRecordedLength, numberOfTrials = 1000)

            rangeOfLinearGrowth = relativeDate [iValid][-1] - relativeDate [iValid][0]
            numberOfPoints = len ( sprouts [iSprout][iValid] )

 
        # Linear range starts at data point with  startIndexLinearRange
        elif endIndexLinearRange == -1:

            averageGrowthRate, averageStartLength, growthRateUncertainty, startLengthUncertainty = \
                uncertaintyEstimator (relativeDate [iValid][startIndexLinearRange:],
                                      sprouts [iSprout][iValid][startIndexLinearRange:], 
                                      uncertaintyRecordedLength, numberOfTrials = 1000)

            rangeOfLinearGrowth = relativeDate [iValid][-1] - relativeDate [iValid][startIndexLinearRange]        
            numberOfPoints = len ( sprouts [iSprout][iValid][startIndexLinearRange:] )


        # Linear range is between  startIndexLinearRange  and  endIndexLinearRange - 1
        else:

            averageGrowthRate, averageStartLength, growthRateUncertainty, startLengthUncertainty = \
                uncertaintyEstimator (relativeDate [iValid][startIndexLinearRange:endIndexLinearRange], 
                                      sprouts [iSprout][iValid][startIndexLinearRange:endIndexLinearRange],
                                      uncertaintyRecordedLength, numberOfTrials = 1000)
       
            rangeOfLinearGrowth = relativeDate [iValid][endIndexLinearRange] - relativeDate [iValid][startIndexLinearRange]
            numberOfPoints = len ( sprouts [iSprout][iValid][startIndexLinearRange:endIndexLinearRange] )



        print ('averageGrowthRate, averageStartLength, growthRateUncertainty, startLengthUncertainty from Monte Carlo:')
        print (averageGrowthRate, averageStartLength, growthRateUncertainty, startLengthUncertainty)
        print ('')
        print ('')

        sproutGrowthParameters.append (
            [sproutNames [iSprout], numberOfPoints, growthRate, growthRateUncertainty, startLength, startLengthUncertainty,
             np.min (sprouts [iSprout][iValid]), np.max (sprouts [iSprout][iValid]) , rangeOfLinearGrowth, pearsonsRpValue [0]
            ]
        )



        # The reported growth rate and start length are the values calculated from the Least Square method
        #  the reported uncertainties from the Monte Carlo method
        growthRateList [-1] = growthRate
        growthRateUncertaintyList [-1] = growthRateUncertainty
        
        startLengthList [-1] = startLength
        startLengthUncertaintyList [-1] = startLengthUncertainty
        
            

        if produceFigures:
        
            plt.figure (1)
            plt.clf ()

            plt.title ( sproutNames [iSprout] + '  -  growth rate = {:4.1f} +/- {:4.2f} mm/day'.format (growthRate, growthRateUncertainty) )
            plt.xlabel (fileNamesAndStrings [iFileNamesAndStrings][3])
            plt.ylabel ('Leaf length (mm)')
        

            plt.xlim (0 - 1, relativeDate [-1] + 2)


            # Plot all the data points in blue
            plt.errorbar (relativeDate [iValid], sprouts [iSprout][iValid], 
                          yerr = 2, ls = 'none', marker = 'o')

        
            # Plot green the data point in the linear range
            # Linear range starts at data point with  startIndexLinearRange
            if indicesLinearRangePerSprout [iSprout] == [0,-1]:
            
            
                plt.errorbar (relativeDate [iValid], sprouts [iSprout][iValid], 
                              yerr = 2, ls = 'none', marker = 'o', color = 'green')
            

                # The fitted line
                fittedLength = np.polyval ([growthRate, startLength], relativeDate [iValid])
                plt.plot (relativeDate [iValid], fittedLength, color = 'red')

            

            else:
        
                if endIndexLinearRange == -1:
            
                    plt.errorbar (relativeDate [iValid][startIndexLinearRange:], 
                                  sprouts [iSprout][iValid][startIndexLinearRange:], 
                                  yerr = 2, ls = 'none', marker = 'o', color = 'green')

                    # The fitted line
                    fittedLength = np.polyval ([growthRate, startLength], relativeDate [iValid][startIndexLinearRange:])
                    plt.plot (relativeDate [iValid][startIndexLinearRange:], fittedLength, color = 'red')

        

                # Linear range is between  startIndexLinearRange  and  endIndexLinearRange - 1
                else:

                    plt.errorbar (relativeDate [iValid][startIndexLinearRange:endIndexLinearRange], 
                                  sprouts [iSprout][iValid][startIndexLinearRange:endIndexLinearRange], 
                              yerr = 2, ls = 'none', marker = 'o', color ='green')

                    # The fitted line
                    fittedLength = np.polyval ([growthRate, startLength], relativeDate [iValid][startIndexLinearRange:endIndexLinearRange])
                    plt.plot (relativeDate [iValid][startIndexLinearRange:endIndexLinearRange], fittedLength, color = 'red')



            plt.savefig ( sproutNames [iSprout] + '.png' )
    


# Export the results to a table with six columns: Sprout ID, number of point, growth rate and uncertainty, start length and uncertainty 
fileCVSResultsOpen = open (fileNamesAndStrings [iFileNamesAndStrings][1], 'w')


# Export to a properly formatted C_END-type table (human readable and readable with readGrowthTable.py, adapted from readTable.py)
fileCVSResultsC_ENDTableOpen = open (fileNamesAndStrings [iFileNamesAndStrings][1][:-3] + 'dat', 'w')

# Header of the C_END file
print ( '',  file = fileCVSResultsC_ENDTableOpen )
print ( ' File: {}'.format (fileNamesAndStrings [iFileNamesAndStrings][1][:-3] + 'dat'),  file = fileCVSResultsC_ENDTableOpen )
print ( ' Dates: {}  -  {}'.format (dateStrings [0], dateStrings [-1]),  file = fileCVSResultsC_ENDTableOpen )
print ( '',  file = fileCVSResultsC_ENDTableOpen )

print ( '  # Points: number of points of the linear section of the growth curve',  file = fileCVSResultsC_ENDTableOpen )
print ( '  Growth Rate: linear section of the growth curve ',  file = fileCVSResultsC_ENDTableOpen )
print ( '  Min. / Max. Length: minimum and maximum lengths of all the points of the growth curve (uncertainty = 2mm)',  file = fileCVSResultsC_ENDTableOpen )
print ( '  p-value: Pearsons-R value for the linear section of the growth curve')
print ( '',  file = fileCVSResultsC_ENDTableOpen )

print ( 'Sprout ID             # Points   Growth Rate  Growth Rate  Start Length   Start Length  Min. Length   Max. Length      # Days        p-value', file = fileCVSResultsC_ENDTableOpen )
print ( '                                              Uncertainty                 Uncertainty                               Linear Growth', file = fileCVSResultsC_ENDTableOpen )
print ( '                                    (mm/day)    (mm/day)       (mm)           (mm)         (mm)          (mm)           (days)', file = fileCVSResultsC_ENDTableOpen )
print ( 'C_END',  file = fileCVSResultsC_ENDTableOpen )


for iLine in range (len (sproutGrowthParameters)):


    print ( ''.join ( " {} , {:2d} , {:5.3f} , {:5.3f} , {:5.3f} , {:5.3f},  {:5.1f} , {:5.1f} , {:6.3f}".format ( 
        sproutGrowthParameters [iLine][0] ,
        sproutGrowthParameters [iLine][1] ,
        sproutGrowthParameters [iLine][2] ,
        sproutGrowthParameters [iLine][3] ,
        sproutGrowthParameters [iLine][4] ,
        sproutGrowthParameters [iLine][5] ,
        sproutGrowthParameters [iLine][6] ,
        sproutGrowthParameters [iLine][7] ,
        sproutGrowthParameters [iLine][9]

         ) 
        ), file = fileCVSResultsOpen )

    
    print ( ''.join ( " {:<20}   {:3d}         {:6.3f}      {:6.3f}        {:7.3f}        {:6.3f}       {:5.1f}         {:5.1f}         {:9.5f}      {:6.3f}".format ( 
        sproutGrowthParameters [iLine][0] ,
        sproutGrowthParameters [iLine][1] ,
        sproutGrowthParameters [iLine][2] ,
        sproutGrowthParameters [iLine][3] ,
        sproutGrowthParameters [iLine][4] ,
        sproutGrowthParameters [iLine][5] ,
        sproutGrowthParameters [iLine][6] ,
        sproutGrowthParameters [iLine][7] ,
        sproutGrowthParameters [iLine][8] ,
        sproutGrowthParameters [iLine][9]       
         ) 
        ), file = fileCVSResultsC_ENDTableOpen )



            
fileCVSResultsOpen.close ()            
fileCVSResultsC_ENDTableOpen.close ()

# I still need to import this .cvs into a Google Sheet, 
#  and then export (download) it as .cvs again for Apple Numbers to read it correctly!!





# Transpose the list and export to (a horizontal) table
sproutGrowthParameters = list (map ( list, zip (*sproutGrowthParameters ) ) )

fileCVSResultsOpen = open (fileNamesAndStrings [iFileNamesAndStrings][2], 'w')

for iLine in range (len (sproutGrowthParameters)):

    if iLine == 0:

        print ( ','.join ( " {} ".format ( sproutID ) for sproutID in sproutGrowthParameters [iLine] ), 
            file = fileCVSResultsOpen )



    elif iLine == 1:
    
        print ( ','.join (" {:2d} ".format ( value )  for value in sproutGrowthParameters [iLine] ), 
            file = fileCVSResultsOpen )


    else:

        print ( ','.join (" {:5.3f} ".format ( value ) for value in sproutGrowthParameters [iLine] ), 
            file = fileCVSResultsOpen )
    
            
fileCVSResultsOpen.close ()            


 
  


