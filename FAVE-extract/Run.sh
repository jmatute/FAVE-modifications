#!/bin/sh

#This is a script to Run extract formants given the speakers file for the 
#reading passages and the wordlist...in order to add the options 
#just uncomment each of the group of 3 lines  ( remove the pound symbol from 
#the start of the line... and this will add the option of the fave extract run.
#For the speakers files and gender info, only modify the speakersdata.csv included 

OPTIONS=""

#CANDIDATES=True
#OPTIONS="${OPTIONS} --candidates ${CANDIDATES}"

#CASE=upper
#OPTIONS="${OPTIONS} --case ${CASE}"

OPTIONS="${OPTIONS} --removeStopWords"


STOPWORDLIST="./stoplist_capitals_ut.txt"
OPTIONS="${OPTIONS} --stopWordsFile ${STOPWORDLIST}"

OPTIONS="${OPTIONS} --verbose"


python bin/extractFormants.py ${OPTIONS} SpeakersData.csv 
