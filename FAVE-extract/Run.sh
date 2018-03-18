#!/bin/sh

#This is a script to Run extract formants given the speakers file for the 
#reading passages and the wordlist...

#the start of the line... and this will add the option of the fave extract run.
#For the speakers files and gender info, only modify the speakersdata.csv included 

OPTIONS=""


#If the option does not need an input, then just put the pound symbol infront of the line to disable
#that option
OPTIONS="${OPTIONS} --candidates"


#if it receives an input then just change the value at that location
CASE=lower
OPTIONS="${OPTIONS} --case ${CASE}"


#########################################################################
COVARIANCESFILE=covs.txt
OPTIONS="${OPTIONS} --covariances ${COVARIANCESFILE}"


#########################################################################
PREDICTIONMETHOD=mahalanobis
OPTIONS="${OPTIONS} --formantPredictionMethod ${PREDICTIONMETHOD}"

#########################################################################
MAXFORMANT=5000
OPTIONS="${OPTIONS} --maxFormant ${MAXFORMANT}"

#########################################################################
MEANSFILE=means.txt
OPTIONS="${OPTIONS} --means ${MEANSFILE}"

#########################################################################
MEASUREMENTPOINT=mid
OPTIONS="${OPTIONS} --measurementPointMethod ${MEASUREMENTPOINT}"

#########################################################################
MINVOWELDURATION=0.001
OPTIONS="${OPTIONS} --minVowelDuration ${MINVOWELDURATION}"


#########################################################################
NFORMANTS=5
OPTIONS="${OPTIONS} --nFormants ${NFORMANTS}"

#########################################################################
NSMOOTHING=12
OPTIONS="${OPTIONS} --nSmoothing ${NSMOOTHING}"

#########################################################################
OPTIONS="${OPTIONS} --removeStopWords"

#########################################################################
OPTIONS="${OPTIONS} --onlyMeasureStressed"

#########################################################################
OUTPUTFORMAT=txt
OPTIONS="${OPTIONS} --outputFormat ${OUTPUTFORMAT}"

#########################################################################
PREEMPHASIS=50
OPTIONS="${OPTIONS} --preEmphasis ${PREEMPHASIS}"

#########################################################################
PHONESET=cmu_phoneset.txt
OPTIONS="${OPTIONS} --phoneset ${PHONESET}"

#########################################################################
OPTIONS="${OPTIONS} --remeasurement"

#########################################################################
SPEECHSOFTWARE=praat
OPTIONS="${OPTIONS} --speechSoftware ${SPEECHSOFTWARE}"

#########################################################################
OPTIONS="${OPTIONS} --tracks"

#########################################################################
VSYSTEM=NorthAmerican
OPTIONS="${OPTIONS} --vowelSystem ${VSYSTEM}"

#########################################################################
STOPWORDLIST="./stoplist_capitals_ut.txt"
OPTIONS="${OPTIONS} --stopWordsFile ${STOPWORDLIST}"

#########################################################################
OPTIONS="${OPTIONS} --verbose"

#########################################################################
WINDOWSIZE=0.025
OPTIONS="${OPTIONS} --windowSize ${WINDOWSIZE}"

echo $OPTIONS
python bin/extractFormants.py ${OPTIONS} SpeakersData.csv 
