#!/usr/bin/env python
# Read a manual CSV file with speakers
# Create means and covariances matrices with
# plotnik codes, arpabet symbols, or lexical sets

import sys
import plotnik
import cmu
import extractFormants
import os
from math import sqrt

class ManualMeasurement:
    """ represent a manual measurement value """

    def __init__(self):
       self.lexical_set = ""
       self.vowel = ""
       self.word = ""
       self.speaker = ""
       self.age = ""
       self.speaker_id = ""
       self.plotnik_code = ""
       self.fifty_percent = []
       self.twenty_percent = []
       self.eighty_percent = []
    
    def GetSpeakerName(self):
       return os.path.dirname(self.speaker).split("/")[-1] 
     
    def MeasurementDistance50(self,other):
       value = 0
       for i in range(len(self.fifty_percent)):
          v1 = self.fifty_percent[i]
          v2 = other.fifty_percent[i]
          value = (v1-v2)*(v1-v2)
       return sqrt(value)

def SaveToPath(filePath, means, covs):
    keys = list(means.keys())
    f1Name = filePath + "_means.txt"
    f2Name = filePath + "_covs.txt"

    with open(f1Name,"w") as f:
      
      for key in keys:
         mean = "\t".join(map(lambda x:str(x),means[key]))
         line = key + "\t" + mean + "\r\n"
         f.write(line)
    
    with open(f2Name,"w") as f:
      
      for key in keys:
         mean = "\t".join(map(lambda x:str(x),covs[key]))
         line = key + "\t" + mean + "\r\n"
         f.write(line)

 
    
def GetPlotnikCode(line):
    """ Call arpabet2plotnik -> in oder to get the plotnik vowel classes """
    phoneset = cmu.read_phoneset("../cmu_phoneset.txt")
    vowelSystem="NorthAmerican"
    trans = line[30]
    ac = line[27]
    stress = line[28]
    phone = extractFormants.Phone()
    xmin = float(line[38])
    xmax = float(line[39])    
    phone.label = ac + stress
    phone.xmin = xmin 
    phone.xmax = xmax
    i = 0
    phones = [phone]
    speaker = extractFormants.Speaker()

    code, prec_p = plotnik.cmu2plotnik_code(i, phones, trans, phoneset, speaker, vowelSystem) 
    return code.split('.')[0]    



def LoadDataFave(filePath):
    dataFile = open(filePath, "r")
    lines = dataFile.readlines()
    lines = lines[1:]
    manualMeasurements = []

    for line in lines:
       dataLine = line.split("\t")
       measurement = ManualMeasurement() 
       measurement.speaker_id = ""
       # 
       measurement.plotnik_code = dataLine[12] + dataLine[13]
       #13 Lexical Set 
       measurement.lexical_set = dataLine[14]
       measurement.age = dataLine[0]
       measurement.speaker = dataLine[6]
       #27 Vowel
       measurement.vowel = dataLine[12]
       #30 Word
       measurement.word = dataLine[16]
       #32-37 F1%50-> B350
       measurement.fifty_percent = [float(x) if x != "" else 0 for x in dataLine[18:24]]
       #52,53 F1,F2 20%
       measurement.twenty_percent = [float(x) if x != "" else 0 for x in dataLine[43:45]]
       #60,61 F1,F2,80%
       measurement.eighty_percent= [float(x) if x != "" else 0 for x in dataLine[51:52]]
       manualMeasurements.append(measurement) 
    return manualMeasurements       



def LoadData(filePath):
    """Load the data from the file, things to store: 
       %50 > F1,F2,F3, B1,B2,B3 ,
       VOWEL, LEXICAL SET
       %20 > F1,F2
       %80 > F1,F2
       Speaker Id... 
       """
    dataFile = open(filePath, "r")
    lines = dataFile.readlines()
    lines = lines[1:]
    manualMeasurements = []

    for line in lines:
       dataLine = line.split("\t")
       measurement = ManualMeasurement() 
       measurement.speaker_id = dataLine[1]
       # 
       measurement.plotnik_code = GetPlotnikCode(dataLine)
       #13 Lexical Set 
       measurement.lexical_set = dataLine[13]
       measurement.age = dataLine[15]
       measurement.speaker = dataLine[21]
       #27 Vowel
       measurement.vowel = dataLine[27]
       #30 Word
       measurement.word = dataLine[30]
       #32-37 F1%50-> B350
       measurement.fifty_percent = [float(x) if x != "" else 0 for x in dataLine[32:38]]
       #52,53 F1,F2 20%
       measurement.twenty_percent = [float(x) if x != "" else 0 for x in dataLine[57:59]]
       #60,61 F1,F2,80%
       measurement.eighty_percent= [float(x) if x != "" else 0 for x in dataLine[65:67]]
       manualMeasurements.append(measurement) 
    return manualMeasurements       
 


def calculateMeansAndCovariances(keys, actualManualMeasurements, typeOfOutput, normalize):
    means = {}
    covariances = {}
    for key in keys:
       values = []
       if typeOfOutput== "A":
          values = filter(lambda x: x.vowel == key, actualManualMeasurements)
       elif typeOfOutput== "L":
          values = filter(lambda x: x.lexical_set == key, actualManualMeasurements)
       elif typeOfOutput== "P":
          values = filter(lambda x: x.plotnik_code == key, actualManualMeasurements)
 
       v_means = [0,0,0,0]
       for element in values:
           v_means[0] += element.fifty_percent[0]
           v_means[1] += element.fifty_percent[1]
           v_means[2] += element.fifty_percent[3]
           v_means[3] += element.fifty_percent[4]
       v_means = [ x/len(values) for x in v_means ]
       means[key] = v_means

    for key in keys:
        mean = means[key]
        if typeOfOutput== "A":
           v = filter(lambda x: x.vowel == key, actualManualMeasurements)
        elif typeOfOutput== "L":
           v = filter(lambda x: x.lexical_set == key, actualManualMeasurements)
        elif typeOfOutput== "P":
           v = filter(lambda x: x.plotnik_code == key, actualManualMeasurements)
         
        cov = [0 for i in range(16)]

        for e1 in v:
            vF1 = e1.fifty_percent[0] - mean[0]
            vF2 = e1.fifty_percent[1] - mean[1]
            vB1 = e1.fifty_percent[3] - mean[2]
            vB2 = e1.fifty_percent[4] - mean[3]

            vals = [vF1,vF2,vB1,vB2]
            for i in range(16):
               row = i/4
               col = i%4
               cov[i] += vals[row]*vals[col]
              
        for i in range(16):
           cov[i] /= (len(v))
        covariances[key] = cov
    return means, covariances




if  __name__ == "__main__":
    manualMeasurements = LoadData(sys.argv[1])
    typeOfOutput = sys.argv[2] # Either Arpabet, Plotnick, Lexical
    outputName = sys.argv[3]
 
    filterOut = []
    if len(sys.argv) > 4:
        filterOut = sys.argv[4:]
    print  "Total Measurements ", len(manualMeasurements)
    
    actualManualMeasurements = filter( lambda x: x.speaker_id not in filterOut, manualMeasurements) 

    print  "Total Measurements Filtered", len(actualManualMeasurements)

    keys = []

    if typeOfOutput == "A": # apply arpabet
       keys = set([x.vowel for x in actualManualMeasurements])
    elif typeOfOutput == "L": # apply arpabet
       keys = set([x.lexical_set for x in actualManualMeasurements])
    elif typeOfOutput == "P": # apply arpabet
       keys = set([x.plotnik_code for x in actualManualMeasurements])
    means, covariances = calculateMeansAndCovariances(keys, actualManualMeasurements, typeOfOutput, normalize)
    SaveToPath(outputName,means, covariances)





