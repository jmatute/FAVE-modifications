from Tkinter import *
import ttk
from priorsGen import *
import tkFileDialog
import os
import subprocess
from math import sqrt

class Application(Frame):

    def loadManualData(self):
        self.manualPath = tkFileDialog.askopenfilename(initialdir = "../",title = "Select manual file")
        if self.manualPath is not None:
          self.filterSpeakerIds = []
          self.manualDataPathEntry.insert(0,self.manualPath)
          self.manualMeasurements = LoadData(self.manualPath)
          self.dataSummary.delete(0, END)
          self.users = list(set(map(lambda x: (x.speaker_id, x.age, x.speaker), self.manualMeasurements ) )) 
          self.dataSummary.insert(END, "Id  Age      Name") 
          for user in self.users:
            summary = user[0] + " "  + user[1] + "   "+user[2]
            self.dataSummary.insert(END, summary)
           
    def addToFilterOut(self):
        selection = self.dataSummary.curselection()
        for index in selection:
           if index > 0:
             user = self.users[index-1]
             summary = user[0] + " "  + user[1] + "   "+user[2]
             self.filterOutUsers.insert(END, summary)
             self.filterSpeakerIds.append(user[0])

    def generatePriors(self):
        actualManualMeasurements = filter( lambda x: x.speaker_id not in self.filterSpeakerIds, self.manualMeasurements)       
        indexMethod = self.methodPriors.current()
        methods = ["A","P","L"]
        typeOfOutput = methods[indexMethod]
        keys = []
        if typeOfOutput == "A": # apply arpabet
          keys = set([x.vowel for x in actualManualMeasurements])
        elif typeOfOutput == "L": # apply arpabet
          keys = set([x.lexical_set for x in actualManualMeasurements])
        elif typeOfOutput == "P": # apply arpabet
          keys = set([x.plotnik_code for x in actualManualMeasurements])
        # directory & apply the measurements
        folder_selected = tkFileDialog.askdirectory()
        if folder_selected is not None:
          outputName = os.path.join(folder_selected, self.baseName.get())
          normalize = self.norm.get()
          means, covariances = calculateMeansAndCovariances(keys, actualManualMeasurements, typeOfOutput, normalize)
          SaveToPath(outputName,means, covariances)

 
    def addToSelection(self):
        selection = self.filterOutUsers.curselection()
        self.filterOutUsers.delete(selection[0])
        value = self.filterSpeakerIds[selection[0]]
        self.filterSpeakerIds = filter(lambda x: x != value, self.filterSpeakerIds )
        #we have to remove from the list as well

    def priorsGenArea(self):
        Label(text="Priors Gen", font="bold").grid(row=0, column=0, columnspan=3)
        Label(text="Manual Data").grid(row=1, column=0)
        self.manualDataPathEntry = Entry()
        self.manualDataPathEntry.grid(row=1, column=1)
        Button(text="Load Path",command=self.loadManualData).grid(row=1, column=2)
        #Loading the data 
        Label(text="Data Summary").grid(row=2, column=0)        
        self.dataSummary = Listbox()
        self.dataSummary.grid(row=2, column=1)

        Button(text="Filter out Selection", command= self.addToFilterOut).grid(row=2, column=2)

        Label(text="Method").grid(row=5, column=0)
        self.methodPriors = ttk.Combobox(state="readonly")
        self.methodPriors.grid(row=5, column=1)
        self.methodPriors["values"] = ["Arpabet","Plotnik","Lexical"] 
    
        self.methodPriors.current(1)
        self.norm = IntVar()
        self.normalizeButton = Checkbutton(text="Normalize Measurements", variable=self.norm)
        self.normalizeButton.grid(row=6,column=1)
       
        Label(text="Filtered Out").grid(row=7, column=0)
        self.filterOutUsers = Listbox()
        self.filterOutUsers.grid(row=7, column=1) 
       
        Button(text="add to Selection", command= self.addToSelection).grid(row=7, column=2)        
       
        Label(text="Base Name").grid(row=9, column=0)
        self.baseName = Entry()
        self.baseName.grid(row=9, column=1)
         
        Button(text="Generate Priors", command=self.generatePriors).grid(row=11, column=2)


    def CallRun(self):
        indexMethod = self.methodAnalysis.current()
        methods = ["arpabet","plotnik","lexical"]
        typeOfOutput = methods[indexMethod]
        os.environ["SCRIPT_METHOD"] = typeOfOutput
        os.environ["MEAN_FILE"] = self.meanPath.get()
        os.environ["COV_FILE"] = self.covPath.get()
       
        os.chdir("../")
        subprocess.call(["./Run.sh"])
        

    def ChangeMeanPath(self):
        newPath = tkFileDialog.askopenfilename(initialdir = "../",title = "Select means file")
        if newPath is not None:
           self.meanPath.insert(0,newPath)
        
    
    def ChangeCovPath(self):
        newPath = tkFileDialog.askopenfilename(initialdir = "../",title = "Select covs file")
        if newPath is not None:
           self.covPath.insert(0,newPath)

    def FaveExtractArea(self):
        Label(text="Fave Extract",font="bold").grid(row=0, column=3, columnspan=3)
        Label(text="Analysis Method", font="bold").grid(row=1, column=3)
  
        self.methodAnalysis = ttk.Combobox(state="readonly")
        self.methodAnalysis.grid(row=1, column=4)
        self.methodAnalysis["values"] = ["arpabet","plotnik","lexical"] 
        self.methodAnalysis.current(1)
        
        Label(text="Means", font="bold").grid(row=2, column=3)
        Label(text="Covs" , font="bold").grid(row=3, column=3)

        self.meanPath = Entry()
        self.meanPath.grid(row=2, column=4)
        
        self.covPath = Entry()
        self.covPath.grid(row=3, column=4)

        os.environ["SCRIPT_METHOD"] = "plotnik"
        os.environ["MEAN_FILE"] = "means.txt"
        os.environ["COV_FILE"] = "covs.txt"
        
        Button(text="Load Means", command = self.ChangeMeanPath).grid(row=2, column=5)
        Button(text="Load Covs", command = self.ChangeCovPath).grid(row=3, column=5)
        Button(text="Run Script", command = self.CallRun).grid(row=11, column = 4)
       

    def CreateComparison(self):
        manualComparisonMeasurements = LoadData(self.manualResult.get())
        faveMeasurements = LoadDataFave(self.faveResult.get())
        speakers = set(map(lambda x:x.GetSpeakerName(), faveMeasurements))
        txt = ""
        for speaker in speakers:
           print speaker
           txt += speaker + "\r\n"
           filteredFave = filter(lambda x:x.GetSpeakerName() == speaker, faveMeasurements)
           filteredManual = filter(lambda x:x.GetSpeakerName() == speaker, manualComparisonMeasurements)
           avg_dist = 0.0
           totalMeasurement = 0
           for measurement in filteredFave:
              #now find the equivalent measure 
              otherFilter = filter( lambda x: x.word == measurement.word, filteredManual)

              #get the minimum distance to the other measurement
              distances = []
              for other in otherFilter:
                 distance = measurement.MeasurementDistance50(other)
                 distances.append(distance)
                 print  measurement.lexical_set, measurement.vowel, measurement.plotnik_code, distance
              value = min(distances)
              txt += measurement.lexical_set +"\t"+ measurement.vowel +"\t" + measurement.plotnik_code + "\t"+  str(value) + "\r\n" 
              totalMeasurement += 1
              avg_dist += value
           avg_dist /= totalMeasurement
           txt += "avg dist" + str(avg_dist)

        with open(self.summaryResult.get(),"w") as f:
           f.write(txt)
 

    def ChangeManualPath(self):
        newPath = tkFileDialog.askopenfilename(initialdir = "../",title = "Select manual file")
        if newPath is not None:
           self.manualResult.insert(0,newPath)
    

    def ChangeResultPath(self):
        newPath = tkFileDialog.askopenfilename(initialdir = "../",title = "Select fave output file")
        if newPath is not None:
           self.faveResult.insert(0,newPath)
    


    def ChangeSummaryPath(self):
        newPath = tkFileDialog.asksaveasfilename(initialdir = "../",title = "Save To")
        if newPath is not None:
           self.summaryResult.insert(0,newPath)

    def ComparisonArea(self):
        Label(text="Comparison",font="bold").grid(row=0, column=6, columnspan=3)

        Label(text="Manual File").grid(row=1, column=6)
        Label(text="Fave Extract Output").grid(row=2, column=6)
        Label(text="Summary Output").grid(row=3, column=6)

        self.manualResult = Entry()
        self.faveResult = Entry()
        self.summaryResult = Entry()
        
        self.manualResult.grid(row=1, column=7)
        self.faveResult.grid(row=2, column=7)
        self.summaryResult.grid(row=3, column=7)       
        
        Button(text="Get File", command= self.ChangeManualPath).grid(row=1, column=8)
        Button(text="Get File", command= self.ChangeResultPath).grid(row=2, column=8)
        Button(text="Set File", command= self.ChangeSummaryPath).grid(row=3, column=8)
        
        Button(text="Create Comparison", command= self.CreateComparison).grid(row=11, column=7)

    def initUI(self):
        self.master.title("FAVE-extract")
        self.priorsGenArea()
        self.FaveExtractArea()
        self.ComparisonArea()
       
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.initUI()
        self.filterSpeakerIds = []

root = Tk()
app = Application(master=root)
app.mainloop()
#root.destroy()
