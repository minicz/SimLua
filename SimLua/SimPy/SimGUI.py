#!/usr/bin/env python
# $Revision: 1.1.1.12 $ $Date: 2008/03/03 13:56:37 $ kgm
"""SimGUI 1.9.1  Provides a Tk/Tkinter-based framework for SimPy simulation
models.

LICENSE:
Copyright (C) 2002,2003,2004,2005,2006,2007  Klaus G. Muller, Tony Vignaux
mailto: kgmuller@xs4all.nl and Tony.Vignaux@vuw.ac.nz

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
END OF LICENSE

SimGUI uses a Tkinter-based console for conversing with the Python interpreter,
developed by Ka-Ping Yee, <ping@lfw.org>.


**Change history:**
    October through December 2003:
                   Development of SimGUI, with outstanding support by
                   Prof. Simon Frost of University of California, San Diego
                   as co-designer/co-implementor.
                   Simon also contributed the idea of using Ka-Ping Yee's
                   Python interpreter console.
                   
    December 16, 2003:   Completion of 1.4alpha version (fully compatible with
                   SimPy 1.4alpha).

    February 2004: Release as part of SimPy 1.4
    
"""

from Tkinter import *
from tkMessageBox import *
from Canvas import Line, CanvasText, Rectangle
import tkconsole as tkcons

__version__ = '1.9.1 $Revision: 1.1.1.12 $ $Date: 2008/03/03 13:56:37 $'

class SimGUI(object):
    def __init__(self,win,title="SimGUI",doc="No doc string found",consoleHeight=50):
        self.root=win
        self.doc=doc
        self.title=title
        win.title(title)
        self.win=self.root
        self.noRunYet=True
        self.makeMenu()
        self.makeConsole(consoleHeight)

    def mainloop(self):
        self.root.mainloop()
        
    def makeMenu(self):
        self.top = Menu(self.win)                 #win = top-level window
        self.win.config(menu=self.top)
        self.makeFileMenu()
        self.makeEditMenu()
        self.makeRunMenu()
        self.makeViewMenu()
        self.makeHelpMenu()
    def makeFileMenu(self):
        self.file = Menu(self.top)
        self.file.add_command(label='Save console content',
                              command=self.saveConsole, underline=0)
        self.file.add_command(label='Quit',
                         command=self.win.quit,underline=0)
        self.top.add_cascade(label='File',menu=self.file,underline=0)
    def makeEditMenu(self):
        self.edit = Menu(self.top)
        self.edit.add_command(label='Change parameters',
                              command=self.changeParameters, underline=0)
        self.edit.add_command(label='Clear console',
                              command=self.clearConsole, underline=1)
        self.top.add_cascade(label='Edit',
                        menu=self.edit, underline=0)
    def makeRunMenu(self):
        self.run = Menu(self.top)
        self.top.add_cascade(label='Run',
                         menu=self.run, underline=0)
    def makeViewMenu(self):
        self.view = Menu(self.top)
        self.view.add_command(label="Collected data",
                              command=self.showMonitors, underline=0)
        self.top.add_cascade(label='View',
                        menu=self.view, underline=0)
    def makeHelpMenu(self):
        self.help = Menu(self.top)
        self.help.add_command(label='About SimGUI',
                         command=self._aboutSimGUI,underline=6)
        self.help.add_command(label='Model description',
                         command=self.about,underline=6)
        self.help.add_command(label='Model code',
                         command=self.showcode,underline=6)
        self.help.add_command(label='Python interpreter',
                         command=self.makeInterpreter,underline=0)
        self.top.add_cascade(label='Help',menu=self.help,underline=0)

    def makeConsole(self,height):
        scrollbar=Scrollbar(self.root)
        scrollbar.pack(side=RIGHT,fill=Y)
        textOutput=Frame(self.root)
        # the status-line
        self.topconsole=Label(textOutput,text="")
        self.topconsole.pack()
        # the console
        self.console=Text(textOutput,height=height,wrap=WORD,yscrollcommand=scrollbar.set)
        self.console.pack()
        scrollbar.config(command=self.console.yview)
        textOutput.pack()

    def writeConsole(self,text=' '):
        self.console.insert(END,"%s\n"%text)
        self.root.update()

    def writeStatusLine(self,text=''):
        self.topconsole.config(text=text)
        self.root.update()        

    def saveConsole(self):
        from tkFileDialog import asksaveasfilename
        #get the Console content
        content=self.console.get('1.0',END+'-1c')
        #get a file name to save to
        filename=asksaveasfilename()
        if not filename[-4:] == '.txt':
             filename+=".txt"
        fi=open(filename,'wb')
        fi.write(content)
        fi.close()
        
    def clearConsole(self):
        self.console.delete('1.0',END)

    def showcode(self):
        "Show SimPy/Python code of this program"
        import sys
        tl=Toplevel()
        tl.title(self.title+" - Code")
        t=Text(tl,width=80)
        scroll=Scrollbar(tl,command=t.yview)
        t.configure(yscrollcommand=scroll.set)
        sourcefile= sys.argv[0]
        source=""
        for i in open(sourcefile).readlines():
            source=source+i
        t.insert(END,source)
        t.pack(side=LEFT)
        scroll.pack(side=RIGHT,fill=Y)

    def about(self):
        self.showTextBox(width=80,height=30,text=self.doc,
                         title=self.title+" - Model information")

    def _aboutSimGUI(self):
        t=Toplevel()
        t.title("About SimGUI")
        tx=Text(t,width=60,height=7)
        txt="SimGUI version %s\n\nSimGUI is a framework for SimPy-based simulations. "%__version__+\
        "It has been developed by Klaus Muller, Simon Frost and Tony Vignaux. \n"+\
        "\n\nHomepage and download: simpy.sourceforge.net\n"
        tx.insert(END,txt)
        tx.pack()

    def notdone(self):
        showerror('Not implemented','Not yet available')

    def showTextBox(self,width=60,height=10,text=" ",title=" "):
        tl=Toplevel()
        tl.title(title)
        txt=text
        t=Text(tl,width=width,height=height,wrap=WORD)
        t.insert(END,txt)
        t.pack()

    def findMonitors(self):
        self._monitors=[]
        for k in self.__dict__.keys():
            a =self.__dict__[k]
            if isinstance(a,list) and hasattr(a,'tseries') and hasattr(a,'yseries'):                                 
                self._monitors.append(a)
                    
    def showMonitors(self):
        if self.noRunYet:
            showwarning('SimGUI warning','Run simulation first!')
            return
        self.findMonitors()
        if not self._monitors:
            showwarning("SimGUI warning","No Monitor instances found")
        for m in self._monitors:
            self.writeConsole("\nMonitor '%s':\n"%m.name)
            dat=m
            try:
                xlab=m.tlab
            except:
                xlab='x'
            try:
                ylab=m.ylab
            except:
                ylab='y'
            sep=",\t"
            self.writeConsole("%s%s%s"%(xlab,sep,ylab))
            for this in dat:
                self.writeConsole("%s%s%s"%(this[0],sep,this[1]))
            self.writeConsole()
            
    def findParameters(self):
        """Finds the instance of Parameters (there may only be one)
        and associates it with self._parameters"""
        self._parameters=None
        for k in self.__dict__.keys():
            a=self.__dict__[k]
            if isinstance(a,Parameters):
                self._parameters=a
            
    def changeParameters(self):
        """Offers entry fields for parameter change"""
        
        self.findParameters()
        if not self._parameters:
            showwarning("SimGUI warning","No Parameters instance found.") 
            return
        t1=Toplevel(self.root)
        top=Frame(t1)
        self.lbl={}
        self.ent={}
        i=1
        for p in self._parameters.__dict__.keys():
            self.lbl[p]=Label(top,text=p)
            self.lbl[p].grid(row=i,column=0)
            self.ent[p]=Entry(top)
            self.ent[p].grid(row=i,column=1)
            self.ent[p].insert(0,self._parameters.__dict__[p])
            i+=1
        top.pack(side=TOP,fill=BOTH,expand=YES)
        commitBut=Button(top,text='Change parameters',command=self.commit)
        commitBut.grid(row=i,column=1)
        
    def commit(self):
        """Commits parameter changes, i.e. updates self._parameters"""
        for p in self._parameters.__dict__.keys():
            this=self._parameters.__dict__
            tipo=type(this[p])
            if tipo==type(1):
                try:
                    this[p]=int(self.ent[p].get())
                except:
                    showerror(title="Input error",
                        message="Type Error; correct parameter '%s' to %s"%(p,tipo))
            elif tipo==type(1.1):
                try:
                    this[p]=float(self.ent[p].get())
                except:
                    showerror(title="Input error",
                        message="Type Error; correct parameter '%s' to %s"%(p,tipo))
            elif this==type("abc"):
                try:
                    this[p]=self.ent[p].get()
                except:
                    showerror(title="Input error",
                        message="Type Error; correct parameter '%s' to %s"%(p,tipo))
            elif tipo==type([]):
                try:
                    a=eval(self.ent[p].get())
                    if type(a)==type([]):
                        this[p]=a
                except:
                    showerror(title="Input error",
                        message="Type Error; correct parameter '%s' to %s"%(p,tipo))
            else:
                showerror(title="Application program error",
                          message="Parameter %s has unsupported type"%p)
        self.noRunYet=True

    def makeInterpreter(self):
        i=Toplevel(self.root)
        interpreter=tkcons.Console(parent=i)
        interpreter.dict['SimPy']=self
        interpreter.pack(fill=BOTH,expand=1)        

class Parameters:
    def __init__(self,**kwds):
        self.__dict__.update(kwds)
    def __repr__(self):
        return str(self.__dict__)
    def __str__(self):
        return str(self.__dict__)
    def show(self):
        res=[]
        for i in self.__dict__.keys():
            res.append("%s : %s\n"%(i,self.__dict__[i]))
        return "".join(res)

if __name__ == '__main__':
    print "SimGUI.py %s"%__version__
    from SimPy.Simulation import *
    from SimPy.Monitor import *
    from random import Random

    class Source(Process):
        """ Source generates customers randomly"""
        def __init__(self,seed=333):
            Process.__init__(self)
            self.SEED = seed

        def generate(self,number,interval):       
            rv = Random(self.SEED)
            for i in range(number):
                c = Customer(name = "Customer%02d"%(i,))
                activate(c,c.visit(timeInBank=12.0))
                t = rv.expovariate(1.0/interval)
                yield hold,self,t

    def NoInSystem(R):
        """ The number of customers in the resource R
        in waitQ and active Q"""
        return (len(R.waitQ)+len(R.activeQ))

    class Customer(Process):
        """ Customer arrives, is served and leaves """
        def __init__(self,name):
            Process.__init__(self)
            self.name = name
            
        def visit(self,timeInBank=0):       
            arrive=now()
            Qlength = [NoInSystem(counter[i]) for i in range(Nc)]
            ##print "%7.4f %s: Here I am. %s   "%(now(),self.name,Qlength)
            for i in range(Nc):
                if Qlength[i] ==0 or Qlength[i]==min(Qlength): join =i ; break
            yield request,self,counter[join]
            wait=now()-arrive
            waitMonitor.observe(wait,t=now())
            ##print "%7.4f %s: Waited %6.3f"%(now(),self.name,wait)
            tib = counterRV.expovariate(1.0/timeInBank)
            yield hold,self,tib
            yield release,self,counter[join]
            serviceMonitor.observe(now()-arrive,t=now())
            if trace:
                gui.writeConsole("Customer leaves at %.1d"%now())

    def model():
        global Nc,counter,counterRV,waitMonitor,serviceMonitor,trace,lastLeave,noRunYet,initialized
        counterRV = Random(gui.params.counterseed)
        sourceseed = gui.params.sourceseed
        nrRuns=gui.params.nrRuns
        lastLeave=0
        gui.noRunYet=True
        for runNr in range(nrRuns):
            gui.noRunYet=False
            trace=gui.params.trace
            if trace:
                gui.writeConsole(text='\n** Run %s'%(runNr+1))
            Nc = 2
            counter = [Resource(name="Clerk0"),Resource(name="Clerk1")]
            gui.waitMon=waitMonitor = Monitor(name='Waiting Times')
            waitMonitor.tlab='Time'
            waitMonitor.ylab='Customer waiting time'
            gui.serviceMon=serviceMonitor = Monitor(name='Service Times')
            serviceMonitor.xlab='Time'
            serviceMonitor.ylab='Total service time = wait+service'
            initialize()
            source = Source(seed = sourceseed)
            activate(source,source.generate(gui.params.numberCustomers,gui.params.interval),0.0)
            result=simulate(until=gui.params.endtime)
            lastLeave+=now()
        gui.writeConsole("%s simulation run(s) completed\n"%nrRuns)
        gui.writeConsole("Parameters:\n%s"%gui.params.show())
        gui.writeStatusLine("Time: %.2f "%now())
     
    def statistics():
        if gui.noRunYet:
            showwarning(title='Model warning',
                      message="Run simulation first -- no data available.")
            return
        aver=lastLeave/gui.params.nrRuns
        gui.writeConsole(text="Average time for %s customers to get through bank: %.1f\n(%s runs)\n"\
                          %(gui.params.numberCustomers,aver,gui.params.nrRuns))

    __doc__="""
Modified bank11.py (from Bank Tutorial) with GUI.

Model: Simulate customers arriving at random, using a Source, requesting service
from two counters each with their own queue with random servicetime.

Uses Monitor objects to record waiting times and total service times."""
    
    def showAuthors():
        gui.showTextBox(text="Tony Vignaux\nKlaus Muller",title="Author information")
    class MyGUI(SimGUI):
        def __init__(self,win,**p):
            SimGUI.__init__(self,win,**p)
            self.help.add_command(label="Author(s)",
                                  command=showAuthors,underline=0)
            self.view.add_command(label="Statistics",
                                  command=statistics,underline=0)
            self.run.add_command(label="Run",
                                 command=model,underline=0)
            


    root=Tk()
    gui=MyGUI(root,title="SimPy GUI example",doc=__doc__,consoleHeight=40)
    gui.params=Parameters(endtime=2000,
       sourceseed=1133,
       counterseed=3939393,
       numberCustomers=50,
       interval=10.0,
       trace=0,
       nrRuns=1)
    gui.mainloop()

