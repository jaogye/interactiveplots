import sqlite3
import numpy as np 
import matplotlib.pyplot as plt 
import pandas as pd 
import matplotlib
from sklearn.decomposition import PCA 
import wx 
import wx.lib.mixins.listctrl as listmix
from wx.lib.agw import ultimatelistctrl as ULC
import statistics 
import math
import csv
from scipy import stats


APPNAME='First Version'
APPVERSION='1.0'
MAIN_WIDTH=600
MAIN_HEIGHT=600
THRESHOLD = 20



class ExamplePanel(wx.Panel, listmix.ColumnSorterMixin):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS, size=(MAIN_WIDTH,MAIN_HEIGHT))
        # create some sizers        
        mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        hSizer = wx.BoxSizer(wx.HORIZONTAL)
        vSizer = wx.BoxSizer(wx.VERTICAL)
        vSizer2 = wx.BoxSizer(wx.VERTICAL)

        LevelList = ["0.1%", "1%","2%","5%", "10¨%"]
        self.LevelList = [26.1, 20.09,18.16,15.51, 13.36 ]
        self.lblInd = wx.StaticText(self, label="Significance:")
        self.cmbInd = wx.ComboBox(self, size=(300, -1), choices= LevelList, style=wx.CB_DROPDOWN)
        self.cmbInd.SetSelection(1)

        self.list = ULC.UltimateListCtrl(self, -1, pos=(300,20), size=(400,600), agwStyle=ULC.ULC_REPORT|ULC.ULC_HAS_VARIABLE_ROW_HEIGHT)
        self.list.InsertColumn(0, "C1")
        self.list.InsertColumn(1, "C2")
        self.list.InsertColumn(2, "C3")

        self.Bind(wx.EVT_LIST_COL_CLICK,      self.OnColClick, self.list)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED,  self.OnItemClick, self.list)

        self.pathname = ""
        self.ind = -1
        self.fig = ""
        self.ax = ""
        
        # Plot button
        self.bopen =wx.Button(self, label="Open")
        self.Bind(wx.EVT_BUTTON, self.OnClickOpen,self.bopen)

        # clear button
        self.bplot =wx.Button(self, label="Plot")
        self.Bind(wx.EVT_BUTTON, self.OnClickPlot,self.bplot)

        # clear button
        self.babout =wx.Button(self, label="About")
        self.Bind(wx.EVT_BUTTON, self.OnClickAbout,self.babout)

        hSizer.Add(self.lblInd)
        hSizer.Add(self.cmbInd)
        vSizer.Add(self.bopen)
        vSizer.Add(self.bplot)
        vSizer.Add(self.babout)
        vSizer2.Add(hSizer)
        vSizer2.Add(self.list)
        mainSizer.Add(vSizer, 0, wx.ALL, 5)
        mainSizer.Add(vSizer2, 0, wx.ALL)

        self.SetSizerAndFit(mainSizer)
        
    def OnClickPlot(self,event):
        if self.pathname != "":
            self.plot()
        else:
           wx.LogError("First, must open a file")

    def OnClickOpen(self,event):

      # otherwise ask the user what new file to open
      with wx.FileDialog(self, "Open csv file", wildcard="XYZ files (*.csv)|*.csv",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

        if fileDialog.ShowModal() == wx.ID_CANCEL:
            return     # the user changed their mind

        # Proceed loading the file chosen by the user
        self.pathname = fileDialog.GetPath()
        self.list.DeleteAllItems()
        self.loadData()

    def OnClickAbout(self, event):

        wx.MessageBox('Window Information', 'About',
            wx.OK | wx.ICON_INFORMATION)
        

    def loadData(self):

       self.data = {}
       line2 = ""
       try:
          with open(self.pathname, 'r') as file1:
              # 1-stats.chi2.cdf(23, 8)
                            
              count = 0
              line = file1.readline()   
              header = True
              tokens = line.split(";")
              # if the second column is numeric then there is no header
              if len(tokens) ==1: 
                 wx.LogError("Invalid file. The file must be separated by ;.")
                 return
              if tokens[1].replace('.','',1).isdigit():
                 header = False
              line = file1.readline()   
              while line: 
                 # Get next line from file 
                 tokens = line.split(";")    
                 if line != line2:
                    number = tokens[1].strip().replace(',','.',1)                              
                    if number.replace('.','',1).isdigit():                        
                        digit = int(tokens[1][0].strip() )
                        if not (tokens[0] in self.data):
                           self.data[tokens[0]]=[0 for col in range(9)]        
                        self.data[tokens[0]][digit-1]=self.data[tokens[0]][digit-1]+1
                    else:
                       if line:  
                          s = "Error in line "+str(count-1)+" . The second column must be numeric "
                          s = s + line + "."
                          wx.LogError(s) 
                          self.pathname = ""
                          file1.close()
                          self.list.DeleteAllItems()
                          return 
                 line2 = line     
                 line = file1.readline() 
                 count = count + 1
          file1.close() 

       except IOError:
            wx.LogError("Cannot open file '%s'." % self.pathname)
            return

       L = 50
       self.data = np.random.rand(L,5)
       self.X = np.random.rand(L,2)
       self.rows = [('','','') for y in range(L)]  
       for i in range(L):
           self.rows[i]=(str(i), str(int(100*self.X[i,0])/100), str(int(100*self.X[i,1])/100) ) 

       self.SetForegroundColour(wx.RED)
       for rowIndex, data in enumerate(self.rows):
            for colIndex, coldata in enumerate(data):
                if colIndex == 0:
                    self.list.InsertStringItem(rowIndex, coldata)
                else:
                    self.list.SetStringItem(rowIndex, colIndex, coldata)
            self.list.SetItemData(rowIndex, data)

       self.itemDataMap = {data : data for data in self.rows} 

       listmix.ColumnSorterMixin.__init__(self, len(self.data))     

    def plot(self):

       n = self.cmbInd.GetSelection()
       THRESHOLD= self.LevelList[ n ] 
       L = len(self.X) 

       self.fig = plt.figure()
       ax = self.fig.add_subplot(111)
       self.ax = ax
       ax.set_title('First Version.' )

       self.line, = ax.plot(self.X[0:12,0], self.X[0:12,1], 'o', c='b' , picker=5, label='A')  
       ax.plot(self.X[12:L,0], self.X[12:L,1], 'o', c='r' , picker=5,  label='B') 

       ax.legend()      
       self.fig.canvas.mpl_connect('pick_event', self.onpick)
       self.fig.canvas.mpl_connect('close_event', self.handle_close)

       plt.show()

    def handle_close(self,evt):
       self.fig= ""
       self.ind = -1

    def onpick(self, event):

       N = len(event.ind)
       if not N: return True

       # fig = plt.figure()
       for subplotnum, dataind in enumerate(event.ind):
           #ax.set_ylim(-0.5, 1.5)

          labels = ['1', '2', '3', '4', '5']

          k = list(self.data)[dataind]
         
          x1 = self.data[dataind,:]
          x2 = self.data[dataind,:]
          
          x = np.arange(len(labels))  # the label locations
          width = 0.35  # the width of the bars

          figi, ax = plt.subplots()
          ax.bar(x - width/2, x1, width, label='A')
          ax.bar(x + width/2, x2, width, label='B')

          # Add some text for labels, title and custom x-axis tick labels, etc.
          ax.set_ylabel('Frequency')
          ax.set_title('Index: ' + str(dataind) + ' THRESHOLD:' + str(THRESHOLD))
          ax.set_xticks(x)
          ax.set_xticklabels(labels)
          ax.legend()      
          figi.canvas.manager.window.move(100,400)

          figi.tight_layout()

          plt.subplots_adjust(left = 0.125, bottom = 0.1, right = 0.9, top = 0.9, wspace = 0.2, hspace = 0.2)
          plt.show()

          return True

    def GetListCtrl(self):
        return self.list

    def OnColClick(self, event):
        pass

    def OnItemClick(self, event): 
        ind = event.GetIndex()
        item = self.list.GetItem(ind,0)
        code = item.GetText()
        if self.fig != "":
           ind = self.ind 
           #ax = self.fig.add_subplot(111)

           if self.ind > 0: 
              if ind > 12:
                 self.ax.plot(self.X[ind,0], self.X[ind,1], 'o', c='r' , picker=5) 
              else:
                 self.ax.plot(self.X[ind,0], self.X[ind,1], 'o', c='b' , picker=5) 
              plt.draw()
               
           self.ind = int(code)
           ind=self.ind 

           self.ax.plot(self.X[ind,0], self.X[ind,1], 'o', c='k' , picker=5) 
           #self.ax.draw()
           plt.draw()

           
class MyForm(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self,None,wx.ID_ANY,'%s v%s' % (APPNAME,APPVERSION),size=(MAIN_WIDTH,MAIN_HEIGHT),style=wx.MINIMIZE_BOX | wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX | wx.CLIP_CHILDREN)
        panel = ExamplePanel(self)

if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.SetSize((600,600))
    frame.Show()
    app.MainLoop()
    