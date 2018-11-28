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
import math

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
       self.norm_f1 = ''
       self.norm_f2 = ''
       self.norm_f3 = ''
       self.stress = '' 
       self.glide = ''
       self.cd = "" 
       self.fm = ''
       self.ps = ''
 
    def GetF1(self):
       return self.fifty_percent[0]
    
    def GetF2(self):
       return self.fifty_percent[1]

    def GetF3(self):
       return self.fifty_percent[2]

    def GetSpeakerName(self):
       return os.path.dirname(self.speaker).split("/")[-1] 
     
    def MeasurementDistance50(self,other):
       value = 0
       for i in range(3):#f1,f2,f3
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


def lobanovN(value, mean, stdv):
    """converts a value into its corresponding z-score"""

    if value and mean and stdv:
        return (value - mean) / stdv
    else:  # not enough tokens for normalization, or no mean to normalize
        return ''


class VowelMean2:

    """represents the mean and standard deviation for a given vowel class"""

    def __init__(self):
        self.pc = ''  # Plotnik vowel class
        self.means = ['', '', '']  # means for F1, F2, F3
        self.stdvs = ['', '', '']  # standard deviations for F1, F2, F3
        self.n = [0, 0, 0]
            # number of tokens used to calculate means and standard deviations
        self.values = [[], [], []]  # formant values from individual tokens
        self.norm_means = ['', '', '']  # normalized means
        self.norm_stdvs = ['', '', '']  # normalized standard deviations
        self.trackvalues = []
            # formant "tracks" (5 measurement points) from individual tokens
        self.trackmeans = []  # means values for formant "tracks"
        self.trackmeans_norm = []  # normalized mean formant "tracks"

    def __str__(self):
        return '<Means for vowel class %s:  means=%s, stdvs=%s, tokens=%s,\nnormalized:  means=%s, stdvs=%s, values:\n\tF1:  %s,\n\tF2:  %s,\n\tF3:  %s>' % (self.pc, self.means, self.stdvs, self.n, self.norm_means, self.norm_stdvs, self.values[0], self.values[1], self.values[2])


def mean_stdv2(valuelist):
    """returns the arithmetic mean and sample standard deviation (N-1 in the denominator) of a list of values"""

    n = len(valuelist)
    if n > 0:
        if n == 1:
            mean = valuelist[0]
            stdv = 0
        else:
            sum_i = 0
            for i in range(n):
                sum_i += valuelist[i]
            mean = sum_i / n
            diffsum_i = 0
            for i in range(n):
                diffsum_i += (valuelist[i] - mean) ** 2
            stdv = math.sqrt(diffsum_i / (n - 1))

    else:  # empty list
        mean = None
        stdv = None

    return mean, stdv


def NormalizeManualMeasurements(manualMeasurements, m_means, measurementType):
    
    values = [[], [], []]
    grand_means = [0, 0, 0]
    grand_stdvs = [0, 0, 0]
    # collect measurement values for each formant
    for m in manualMeasurements:
        if len(m.fifty_percent) > 0:
            values[0].append(m.GetF1())
        if len(m.fifty_percent) > 0:
            values[1].append(m.GetF2()) 
        if len(m.fifty_percent) > 0:
            values[2].append(m.GetF3())
    # get overall means and standard deviations for each formant
    for i in range(3):
        grand_means[i], grand_stdvs[i] = mean_stdv2(values[i])
   
    for m in manualMeasurements:
        try:
            m.norm_f1 = round(650 + 150 * (lobanovN(m.GetF1(), grand_means[0], grand_stdvs[0])), 0)
        except TypeError:
            m.norm_f1 = ''
        try:
            m.norm_f2 = round(1700 + 420 * (lobanovN(m.GetF2(), grand_means[1], grand_stdvs[1])), 0)
        except TypeError:
            m.norm_f2 = ''
# try:
##            m.norm_f3 = round(lobanov(m.f3, grand_means[2], grand_stdvs[2]), 0)
# except TypeError:
##            m.norm_f3 = None
        m.norm_f3 = ''  # don't normalize F3 right now - we don't have any reasonable scaling factors
    
    key_array = plotnik.PLOTNIKCODES
    if measurementType == "lexical":
        key_array = list(set(lexical.LEX_DICT.values()))    
    if measurementType == "arpabet":
        key_array = plotnik.VOWELS

    # normalize the means and standard deviations for F1 and F2
    for p in key_array:
        # F1 mean
        try:
            m_means[p].norm_means[0] = round(650 + 150 * (lobanovN(m_means[p].means[0], grand_means[0], grand_stdvs[0])), 0)
        except TypeError:
# print "No F1 normalized mean for vowel class %s:  value = %s, mean = %s,
# stdv = %s." % (p, m_means[p].means[0], grand_means[0], grand_stdvs[0])
            m_means[p].norm_means[0] = ''
        # F1 standard deviation
        try:
            m_means[p].norm_stdvs[0] = round(150 * (m_means[p].stdvs[0] / grand_stdvs[0]), 0)
        except TypeError:
# print "No F1 normalized standard deviation for vowel class %s:  value =
# %s, stdv = %s." % (p, m_means[p].stdvs[0], grand_stdvs[0])
            m_means[p].norm_stdvs[0] = ''
        # F2 mean
        try:
            m_means[p].norm_means[1] = round(1700 + 420 * (lobanovN(m_means[p].means[1], grand_means[1], grand_stdvs[1])), 0)
        except TypeError:
# print "No F2 normalized mean for vowel class %s:  value = %s, mean = %s,
# stdv = %s." % (p, m_means[p].means[1], grand_means[1], grand_stdvs[1])
            m_means[p].norm_means[1] = ''
        # F2 standard deviation
        try:
            m_means[p].norm_stdvs[1] = round(420 * (m_means[p].stdvs[1] / grand_stdvs[1]), 0)
        except TypeError:
# print "No F2 normalized standard deviation for vowel class %s:  value =
# %s, stdv = %s." % (p, m_means[p].stdvs[1], grand_stdvs[1])
            m_means[p].norm_stdvs[1] = ''


    return manualMeasurements, m_means





def calculateMeans2(measurements, measurementType):
    """takes a list of vowel measurements and calculates the means for each vowel class"""

    # initialize vowel means
    means = {}

    key_array = plotnik.PLOTNIKCODES
    if measurementType == "lexical":
        key_array = list(set(lexical.LEX_DICT.values()))    
    if measurementType == "arpabet":
        key_array = plotnik.VOWELS
   
    for p in key_array:
        newmean = VowelMean2()
        newmean.pc = p
        means[p] = newmean


    # process measurements
    for m in measurements:
        # only include tokens with primary stress
        if m.stress != '1':
            continue
        # exclude tokens with F1 < 200 Hz
        if m.GetF1() < 200:
            continue
        # exclude glide measurements
        if m.glide == 'g':
            continue
        # exclude function words
        if m.word.upper() in ['A', 'AH', 'AM', "AN'", 'AN', 'AND', 'ARE', "AREN'T", 'AS', 'AT', 'AW', 'BECAUSE', 'BUT', 'COULD',
              'EH', 'FOR', 'FROM', 'GET', 'GONNA', 'GOT', 'GOTTA', 'GOTTEN',
              'HAD', 'HAS', 'HAVE', 'HE', "HE'S", 'HIGH', 'HUH',
              'I', "I'LL", "I'M", "I'VE", "I'D", 'IN', 'IS', 'IT', "IT'S", 'ITS', 'JUST', 'MEAN', 'MY',
              'NAH', 'NOT', 'OF', 'OH', 'ON', 'OR', 'OUR', 'SAYS', 'SHE', "SHE'S", 'SHOULD', 'SO',
              'THAN', 'THAT', "THAT'S", 'THE', 'THEM', 'THERE', "THERE'S", 'THEY', 'TO', 'UH', 'UM', 'UP',
              'WAS', "WASN'T", 'WE', 'WERE', 'WHAT', 'WHEN', 'WHICH', 'WHO', 'WITH', 'WOULD',
              'YEAH', 'YOU', "YOU'VE"]:
            continue
        # exclude /ae, e, i, aw/ before nasals
        if m.cd in ['3', '2', '1', '42'] and m.fm == '4':
            continue
        # exclude vowels before /l/
        if m.fm == '5' and not m.cd == '39':
            continue
        # exclude vowels after /w, y/
        if m.ps == '9':
            continue
        # exclude vowels after obstruent + liquid clusters
        if m.ps == '8':
            continue
        # add measurements to means object
        
        key = m.cd
        if measurementType == "arpabet":
           key = m.phone
        if measurementType == "lexical":
           key = m.lexical_set

        if len(m.fifty_percent) > 0:
            means[key].values[0].append(m.GetF1())
        if len(m.fifty_percent) > 0:
            means[key].values[1].append(m.GetF2())
        if len(m.fifty_percent) > 0:
            means[key].values[2].append(m.GetF3())

    # calculate means and standard deviations
    for p in key_array:
        for i in range(3):
            means[p].n[i] = len(means[p].values[i])
                                # number of tokens for formant i
            mean, stdv = mean_stdv2(means[p].values[i])
                                   # mean and standard deviation for formant i
            if mean:
                means[p].means[i] = round(mean, 0)
            if stdv:
                means[p].stdvs[i] = round(stdv, 0)


    return means






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
       #    Glide
       measurement.cd = measurement.plotnik_code
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
  
       measurement.stress = dataLine[28]
       measurement.lexical_set = dataLine[13]
       measurement.age = dataLine[15]
       measurement.speaker = dataLine[21]
       #27 Vowel
       measurement.vowel = dataLine[27]
       #30 Word
       measurement.word = dataLine[30]
       #32-37 F1%50-> B350
       measurement.glide = dataLine[49]
       #cd
       measurement.cd = measurement.plotnik_code
       
       measurement.fifty_percent = [float(x) if x != "" else 0 for x in dataLine[32:38]]
       measurement.fifty_percent[3] = math.log(measurement.fifty_percent[3])
       measurement.fifty_percent[4] = math.log(measurement.fifty_percent[4])

       #52,53 F1,F2 20%
       measurement.twenty_percent = [float(x) if x != "" else 0 for x in dataLine[57:59]]
       #60,61 F1,F2,80%
       measurement.eighty_percent= [float(x) if x != "" else 0 for x in dataLine[65:67]]
       manualMeasurements.append(measurement) 
    return manualMeasurements       
 


def calculateMeansAndCovariances(keys, actualManualMeasurements, typeOfOutput, normalize):
    m_means = calculateMeans2(actualManualMeasurements, typeOfOutput)
    measurements, m_means = NormalizeManualMeasurements(actualManualMeasurements, m_means, typeOfOutput)
    
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
    normalize = True
    means, covariances = calculateMeansAndCovariances(keys, actualManualMeasurements, typeOfOutput, normalize)
	
    
    SaveToPath(outputName,means, covariances)



