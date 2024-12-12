'''
 sproutGrowthStatistics.py  is a Python script to calculate linear regression parameters (a,b) in  y = a * t + b for growth of young sprout of the 
 Camellia Sinensis plant. 'a' is the growth rate in mm/day, 'b' the start length as the (random) zero time reference, 
 'y' the length of the sprout in mm  and 't' the time in days.
 
 version: 20211021
 author: Maarten Roos

'''


import numpy as np
import matplotlib.pyplot as plt 
from scipy import stats

from HandyTools import HandyTools as ht

from readGrowthTable import readGrowthTable


# The string set to use in this run
iFileNamesAndStrings = 0

# Boolean to produce figures as png files or not
saveFigures = False


# The first string is the file name of a "download as cvs" from a Google Sheet, found in this Google folder:
#  https://drive.google.com/drive/folders/1QKy8gKy13t4JcW88e84t-2N_utGdjZH2?usp=sharing
fileNamesAndStrings = [

# iFileNamesAndStrings = 0
['Camelia Sinensis Plants Growth Record - Sprout Development 20210317-20210419 Table.dat',
'some text'],

# iFileNamesAndStrings = 1
['Camelia Sinensis Plants Growth Record - Sprout Development 20210701-20210901 Table.dat',
'some text'],

]



plantIDsMap = {'Ichi' : 1, 'Ni' : 2, 'San' : 3, 'Yon' : 4, 'Go' : 5, 'Ruku' : 6}
plantIDStrings = ['Ichi', 'Ni', 'San', 'Yon', 'Go', 'Ruku']
plantColours = ['red', 'green', 'blue', 'cyan', 'black', 'darkorange']


table1Content = readGrowthTable (fileNamesAndStrings [0][0])

sproutID1Map = []
for sproutIDString in table1Content.sproutIDStrings:

    for sproutID in plantIDsMap: 
    
        if sproutID in sproutIDString: sproutID1Map.append ( plantIDsMap [sproutID] )


sproutID1Map = np.asarray (sproutID1Map)
                

table2Content = readGrowthTable (fileNamesAndStrings [1][0])

sproutID2Map = []
for sproutIDString in table2Content.sproutIDStrings:

    for sproutID in plantIDsMap: 
    
        if sproutID in sproutIDString: sproutID2Map.append ( plantIDsMap [sproutID] )


sproutID2Map = np.asarray (sproutID2Map)


plt.figure (1)
plt.clf ()

for sproutIDFromMap in plantIDsMap:

    iPoints = np.where ( sproutID1Map == plantIDsMap [sproutIDFromMap] )[0]

    if len (iPoints):

        plt.scatter ( sproutID1Map [iPoints], table1Content.data [iPoints,1], 
                      marker = 'o' , color = plantColours [plantIDsMap [sproutIDFromMap] - 1] )

 
    iPoints = np.where ( sproutID2Map == plantIDsMap [sproutIDFromMap] )[0]

    if len (iPoints):

        plt.scatter ( sproutID2Map [iPoints], table2Content.data [iPoints,1], 
                      marker = 'o' , color = plantColours [plantIDsMap [sproutIDFromMap] - 1] )

    plt.title ( ' Spread of Growth Rates per Plant ' )
    plt.xticks ( [1,2,3,4,5,6], plantIDStrings )

    
    plt.xlabel ( 'Plant ID' )
    plt.ylabel ( 'Growth Rate (mm/day)')


if saveFigures: plt.savefig ( 'GrowthRatePerPlant.png' )



plt.figure (2)
plt.clf ()

for sproutIDFromMap in plantIDsMap:

    iPoints = np.where ( sproutID1Map == plantIDsMap [sproutIDFromMap] )[0]

    if len (iPoints):

        plt.errorbar ( sproutID1Map [iPoints], table1Content.data [iPoints,6], yerr = 2, ls = 'none',
                      marker = 'o' , color = plantColours [plantIDsMap [sproutIDFromMap] - 1] )

 
    iPoints = np.where ( sproutID2Map == plantIDsMap [sproutIDFromMap] )[0]

    if len (iPoints):

        plt.errorbar ( sproutID2Map [iPoints], table2Content.data [iPoints,6], yerr = 2, ls = 'none',
                      marker = 'o' , color = plantColours [plantIDsMap [sproutIDFromMap] - 1] )

    plt.title ( ' Maximum Sprout Length Measured per Plant ' )
    plt.xticks ( [1,2,3,4,5,6], plantIDStrings )

    
    plt.xlabel ( 'Plant ID' )
    plt.ylabel ( 'Maxmimum Sprout Length Measured (mm)')


if saveFigures: plt.savefig ( 'MaximumSproutLengthMeasuredPerPlant.png' )


plt.figure (3)
plt.clf ()    

for sproutIDFromMap in plantIDsMap:

    iPoints = np.where ( sproutID1Map == plantIDsMap [sproutIDFromMap] )[0]

    if len (iPoints):

        plt.errorbar ( table1Content.data [iPoints,1], table1Content.data [iPoints,6], xerr = table1Content.data [iPoints,2], 
                       yerr = 2, ls = 'none',
                       marker = 'o' , color = plantColours [plantIDsMap [sproutIDFromMap] - 1] )

 
    iPoints = np.where ( sproutID2Map == plantIDsMap [sproutIDFromMap] )[0]

    if len (iPoints):

        plt.errorbar ( table2Content.data [iPoints,1], table2Content.data [iPoints,6], xerr = table2Content.data [iPoints,2], 
                       yerr = 2, ls = 'none',
                       marker = 'o' , color = plantColours [plantIDsMap [sproutIDFromMap] - 1] )

    plt.title ( 'Maximum Sprout Length Measured vs Growth Rate' )
    
    plt.xlabel ( 'Growth Rate (mm/day)' )
    plt.ylabel ( 'Maxmimum Sprout Length (mm)')

    for iPlant, plantIDString in enumerate (plantIDStrings):
        
        plt.text (-0.75, 75 - iPlant*5, plantIDString, color = plantColours [iPlant])


if saveFigures: plt.savefig ( 'GrowthRate-MaximumSproutLengthMeasured.png' )


plt.figure (4)
plt.clf ()    

for sproutIDFromMap in plantIDsMap:

    iPoints = np.where ( sproutID1Map == plantIDsMap [sproutIDFromMap] )[0]

    if len (iPoints):

        plt.errorbar ( table1Content.data [iPoints,1], table1Content.data [iPoints,5], xerr = table1Content.data [iPoints,2], 
                       yerr = 2, ls = 'none', 
                       marker = 'o' , color = plantColours [plantIDsMap [sproutIDFromMap] - 1] )

 
    iPoints = np.where ( sproutID2Map == plantIDsMap [sproutIDFromMap] )[0]

    if len (iPoints):

        plt.errorbar ( table2Content.data [iPoints,1], table2Content.data [iPoints,5], xerr = table2Content.data [iPoints,2], 
                       yerr = 2, ls = 'none',
                       marker = 'o' , color = plantColours [plantIDsMap [sproutIDFromMap] - 1] )

    plt.title ( 'Minimum Sprout Length Measured vs Growth Rate' )
    
    plt.xlabel ( 'Growth Rate (mm/day)' )
    plt.ylabel ( 'Minimum Sprout Length (mm)')

    for iPlant, plantIDString in enumerate (plantIDStrings):
        
        plt.text (-0.75, 30 - iPlant*2, plantIDString, color = plantColours [iPlant])






if saveFigures: plt.savefig ( 'GrowthRate-MinimumSproutLengthMeasured.png' )

growthRates = np.concatenate ( (table1Content.data [:,1], table2Content.data [:,1]) )
minimumLengths = np.concatenate ( (table1Content.data [:,5], table2Content.data [:,5]) )
maximumLengths = np.concatenate ( (table1Content.data [:,6], table2Content.data [:,6]) )

print ('')
a, b, uncertaintyA, uncertaintyB = ht.linearLeastSquare (growthRates, minimumLengths)
print ('Minimum length - growth rate: a, b, da, db', a, b, uncertaintyA, uncertaintyB)

c = stats.pearsonr (growthRates, minimumLengths)
print ('p-value', c)


a, b, uncertaintyA, uncertaintyB = ht.linearLeastSquare (growthRates, maximumLengths)
print ('Maximum - growth rate: a, b, da, db', a, b, uncertaintyA, uncertaintyB)

c = stats.pearsonr (growthRates, maximumLengths)
print ('p-value', c)


ht.QQPlot (minimumLengths, xlabelToPrint = 'Minimum Sprout Lengths', ylabelToPrint = 'z (sigma)',
           QQTitleToPrint = 'QQ-plot of Minimum Sprout Lengths',
           HistTitleToPrint = 'Histogram of Minimum Sprout Lengths',
           plotTextAverageMedian = False)


if saveFigures: 

    plt.figure (1)

    plt.text (-2.8,2.6, 'average: {:4.1f} +/- {:5.2f}mm'.format (np.mean (minimumLengths), np.std (minimumLengths)), color = 'green')
    plt.text (-2.8,2.3, 'median: {:4.1f}mm  (p15 = {:4.1f}, p85 = {:4.1f})'.
                         format (np.percentile (minimumLengths, 50), np.percentile (minimumLengths, 15), np.percentile (minimumLengths, 85)), 
                         color = 'green')


    plt.savefig ( 'QQPlot minimumSproutLengths.png' )

    plt.figure (2)

    plt.text (2,4.4, 'average: {:4.1f} +/- {:5.2f}mm'.format (np.mean (minimumLengths), np.std (minimumLengths)), color = 'green')
    plt.text (2,4.15, 'median: {:4.1f}mm  (p15 = {:4.1f}, p85 = {:4.1f})'.
                         format (np.percentile (minimumLengths, 50), np.percentile (minimumLengths, 15), np.percentile (minimumLengths, 85)), 
                         color = 'green')

    plt.savefig ( 'Histogram minimumSproutLengths.png' )




iType1 = np.where ( growthRates <= 0.75 )
print ( '({}) Type 1 maximum length: median (p15, p85) - {:4.1f} ({:4.1f}, {:4.1f})'.
         format (len (iType1 [0]), np.percentile (maximumLengths [iType1], 50), 
                 np.percentile (maximumLengths [iType1], 15),
                 np.percentile (maximumLengths [iType1], 85)) 
)


iType2 = np.where ( (growthRates > 0.75) & (growthRates <= 2) )
print ( '({}) Type 2 maximum length median: (p15, p85) - {:4.1f} ({:4.1f}, {:4.1f})'.
         format (len (iType2 [0]), np.percentile (maximumLengths [iType2], 50), 
                 np.percentile (maximumLengths [iType2], 15),
                 np.percentile (maximumLengths [iType2], 85)) 
)

iType3 = np.where ( growthRates > 2)
print ( '({}) Type 3 maximum length median:  (p15, p85) - {:4.1f} ({:4.1f}, {:4.1f})'.
         format (len (iType3 [0]), np.percentile (maximumLengths [iType3], 50), 
                 np.percentile (maximumLengths [iType3], 15),
                 np.percentile (maximumLengths [iType3], 85)) 
)











