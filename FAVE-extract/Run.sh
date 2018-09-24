#!/bin/sh

#This is a script to Run extract formants given the speakers file for the 
#reading passages and the wordlist...

#the start of the line... and this will add the option of the fave extract run.
#For the speakers files and gender info, only modify the speakersdata.csv included 

echo $SCRIPT_METHOD
echo $MEAN_FILE
echo $COV_FILE

OPTIONS=""

#If the option does not need an input, then just put the pound symbol infront of the line to disable
#that option
OPTIONS="${OPTIONS} --candidates"


#if it receives an input then just change the value at that location
CASE=lower
OPTIONS="${OPTIONS} --case ${CASE}"

#############################################################
#TYPE=plotnik  
TYPE=$SCRIPT_METHOD
# possible types are plotnik, lexical, arpabet... the means and covariances
# are dependent on this value so make sure means and covariance file relate to it
OPTIONS="${OPTIONS} --vowelMeasurementType ${TYPE}"


###############################################################

#MEANSFILE=plotnik_without_frederik_means.txt 
#MEANSFILE=means.txt
MEANSFILE=$MEAN_FILE 
OPTIONS="${OPTIONS} --means ${MEANSFILE}"

#########################################################################
#COVARIANCESFILE=covs.txt
#COVARIANCESFILE=plotnik_without_frederik_covs.txt
COVARIANCESFILE=$COV_FILE  #lexical_without_frederik_covs.txt
OPTIONS="${OPTIONS} --covariances ${COVARIANCESFILE}"


#########################################################################
PREDICTIONMETHOD=mahalanobis
#PREDICTIONMETHOD=default
OPTIONS="${OPTIONS} --formantPredictionMethod ${PREDICTIONMETHOD}"

#########################################################################
MAXFORMANT=5000
OPTIONS="${OPTIONS} --maxFormant ${MAXFORMANT}"

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
NSMOOTHING=0
OPTIONS="${OPTIONS} --nSmoothing ${NSMOOTHING}"

#########################################################################
OPTIONS="${OPTIONS} --removeStopWords"

#########################################################################
OPTIONS="${OPTIONS} --onlyMeasureStressed"
#OPTIONS="${OPTIONS} --measureStressed"

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

##########################################################################
OPTIONS="${OPTIONS} --padding" # Remove to not apply padding when getting formant tracks

#########################################################################
#OPTIONS="${OPTIONS} --keep"    #Keep the old formants 

#########################################################################
NUMTOKENS=7
OPTIONS="${OPTIONS} --minAmountTokens ${NUMTOKENS}"

#########################################################################
WINDOWSIZE=0.025
OPTIONS="${OPTIONS} --windowSize ${WINDOWSIZE}"

echo $OPTIONS
python bin/extractFormants.py ${OPTIONS} SpeakersData.csv 
