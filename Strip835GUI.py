import os, csv, re, time,sys
import queue as queue
import threading
import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror, askyesno
from tkinter.font import Font
from tkinter import scrolledtext, ttk
import time #pause
'''
To DO: 
       Make output text uneditable, method call needed for writing
       Help button/version #
       Standalone work and taskbar icon
       Multithreaded: update display, progress bar, interrupted run message
       OutputText font and color changes
       Progress bar
       Assumptions: Standard Format, segment delimiter is '*'
'''

class App(tk.Frame):
    __OUTFILE_PREFIX = "Parsed835Goodies"
    __OUTFILE_HEADERS = ['FILENAME', 'TRN02', 'TRN03', 'PAYER', 'PAYEE', 'NPI', 'CLAIM', 'CLP02']
    __DEFAULT_FILE_PATTERN = ".835"

    def __init__(self, master):
        self.master = master
        # self.master.resizable(width=False,height=False)
        path = self.resource_path('835.ico')
        self.master.iconbitmap(path)

        self.outfile_path = ""
        self.source_dir = ""
        self.file_pattern = ""
        self.__run_counter = 1
        self.__outfile_name = self.get_new_outfile_name()
        self.__file_exists = os.path.isfile(self.__outfile_name)

        # Frame Setup
        inputsFrame = tk.LabelFrame(root, text="1. Enter File Details: ")
        inputsFrame.grid(row=0, columnspan=10, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        inputsFrame.columnconfigure(1,weight=1)

        outputFrame = tk.Label(root)
        outputFrame.grid(row=1, columnspan=10, sticky='NSEW', padx=5, pady=5, ipadx=5, ipady=5)
        outputFrame.columnconfigure(1,weight=1)
        outputFrame.rowconfigure(0,weight=1)

        progressFrame = tk.Frame(root)
        progressFrame.grid(row=2, columnspan=10, sticky='WE', padx=5, pady=5)
        progressFrame.columnconfigure(1, weight=1)
        progressFrame.rowconfigure(1,weight=1)
        
        footerFrame = tk.Label(root)
        footerFrame.grid(row=3, columnspan=10, sticky='EW', padx=5, pady=1)
        footerFrame.columnconfigure(1, weight=1)
        footerFrame.rowconfigure(2,weight=1)
        
         # File Pattern Input
        filePatternLbl = tk.Label(inputsFrame, text="File Pattern", anchor = 'w')
        filePatternLbl.grid(row=0, column=0, sticky='WE', padx=5, pady=2)

        self.filePatternTxt = tk.Entry(inputsFrame, state="normal")
        self.filePatternTxt.grid(row=0, column=1, columnspan=7, sticky="WE", padx=5, pady=2)
        self.filePatternTxt.insert(0, str(self.__DEFAULT_FILE_PATTERN))

        # Source Directory Prompt
        inFolderLbl = tk.Label(inputsFrame, text="Folder with 835s:", anchor = 'w')
        inFolderLbl.grid(row=1, column=0, sticky='WE', padx=5, pady=2)
        
        self.inFolderTxt = tk.Entry(inputsFrame, state="disabled")
        self.inFolderTxt.grid(row=1, column=1, columnspan=7, sticky="WE", padx=5, pady=2)
        
        self.inFolderBtn = tk.Button(inputsFrame, text="Browse ...", command=self.browse_for_open_loc)
        self.inFolderBtn.grid(row=1, column=10, sticky='E', padx=5, pady=2)
        
        # Save Results Prompt
        outFolderLbl = tk.Label(inputsFrame, text="Save Results to:", anchor = 'w')
        outFolderLbl.grid(row=2, column=0, sticky='WE', padx=5, pady=2)
  
        self.outFolderTxt = tk.Entry(inputsFrame, state="disabled")
        self.outFolderTxt.grid(row=2, column=1, columnspan=7, sticky="WE", padx=5, pady=2)       

        self.outFolderBtn = tk.Button(inputsFrame, text="Browse ...", command=self.browse_for_save_loc)
        self.outFolderBtn.grid(row=2, column=10, sticky='E', padx=5, pady=2)
        
        # Results Output Display
        self.outputText = tk.scrolledtext.ScrolledText(outputFrame, wrap='word'
            , height=5, width=10, font=('',8), fg="#333333")
        self.outputText.grid(row=0, column=1, sticky="NSEW", padx=5, pady=2)

        self.xscrollbar = tk.Scrollbar(outputFrame, orient='horizontal', command=self.outputText.xview)
        self.outputText.configure(xscrollcommand=self.xscrollbar.set)
        self.xscrollbar.grid(row=2, column=1, sticky='EW')

        # Progress Bar
        self.progressBar = ttk.Progressbar(progressFrame, orient="horizontal", length=200, mode="determinate")
        # self.progressBar.grid(row=2, column=1, stick='EW') # Hide to start

        # Run and Close       
        self.okBtn = tk.Button(footerFrame, text="Run", command=self.process_run)
        self.okBtn.grid(row=2, column=2, sticky='SE', padx=5, pady=2, ipadx=27)
        
        closeBtn = tk.Button(footerFrame, text="Close", command=self.quit)
        closeBtn.grid(row=2, column=3, sticky='SE', padx=5, pady=2, ipadx=20)

    def quit(self):
        root.destroy()

    def browse_for_open_loc(self):
        open_loc = os.path.normpath(askdirectory(title="Browse for Folder containing 835s to parse..."))
        self.inFolderTxt.configure(state='normal')
        self.inFolderTxt.delete(0,tk.END)
        self.inFolderTxt.insert(0, str(open_loc))
        self.inFolderTxt.configure(state='disabled')
        self.source_dir = os.path.normpath(open_loc)
    
    def browse_for_save_loc(self):
        save_loc = os.path.normpath(askdirectory(
            # initialdir=expanduser(pathvar.get()),
            title="Browse for where to save output results..."))
        self.outFolderTxt.configure(state='normal')
        self.outFolderTxt.delete(0,tk.END)
        self.outFolderTxt.insert(0, str(save_loc))
        self.outFolderTxt.configure(state='disabled')
        self.outfile_path = os.path.join(save_loc,self.__outfile_name)

    def write_to_csv(self, *args):
        with open(self.outfile_path, newline='', mode='a') as outcsv:
            csv_writer = csv.writer(outcsv, delimiter=',', quotechar='"', quoting = csv.QUOTE_MINIMAL)
            data= []
            for x in args:
                data.append(x)
            csv_writer.writerow(data)

    def warn_missing_loc(self):
        tk.messagebox.showerror(title="Error- Did you forget??"
            ,message="Please specify an input and output folder location")

    def print_output(self,text):
        self.outputText.configure(state='normal')
        self.outputText.insert(tk.END, str(text))
        self.outputText.see(tk.END)
        self.outputText.configure(state='disabled')

    def resource_path(self, relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def disable_widgets(self):
        self.okBtn.configure(state='disabled')
        self.inFolderBtn.configure(state='disabled')
        self.outFolderBtn.configure(state='disabled')
        self.filePatternTxt.configure(state = 'disabled')

    def enable_widgets(self):
        self.okBtn.configure(state='normal')
        self.inFolderBtn.configure(state='normal')
        self.outFolderBtn.configure(state='normal')
        self.filePatternTxt.configure(state = 'normal')

    def get_new_outfile_name(self):
        return self.__OUTFILE_PREFIX + " " + time.strftime("%Y-%m-%d-%H%M%S") + ".csv"

    def begin_progressbar(self):
        self.disable_widgets()
        self.progressBar.grid(row=2, column=1, stick='EW')
        self.progressBar.start()

    def update_progressbar(self, amount):
        self.progressBar['value'] = amount
        self.master.update_idletasks()

    def end_progressbar(self):
        self.enable_widgets()
        self.progressBar.stop()
        self.progressBar.grid_forget()

    # def process_queue(self):
    #     try:
    #         msg = self.queue.get(0)
    #         # Show result of the task if needed
    #         print(msg)
    #         self.progressBar.stop()
    #     except queue.Empty:
    #         self.master.after(100, self.process_queue)

    def process_run(self):
        ok_to_run = False
        if self.__run_counter != 1:
            if tk.messagebox.askyesno("Confirm Run", "Are you sure you want to run again?"):
                self.print_output(f'\n\n\n*****Starting Run #{self.__run_counter} *****\n')
                self.__outfile_name = self.get_new_outfile_name()
                ok_to_run = True
        else: ok_to_run = True
        if ok_to_run:
            if len(self.filePatternTxt.get()) > 0:
                self.file_pattern = self.filePatternTxt.get()
            if len(self.inFolderTxt.get()) == 0 or len(self.outFolderTxt.get()) == 0:
                self.warn_missing_loc()
            else:
                self.begin_progressbar()
                #self.queue = queue.Queue()
                #ThreadedTask(self.queue).start()
                threading.Thread(target=self.process_835s).start()
                #self.master.after(100, self.process_queue)


    def parse_line(self, file, line):
        file_trn02, file_trn03, file_payer, file_payee, file_npi = "", "", "", "", ""
        claim, clp02 = "", ""
        if (line.startswith("TRN")):
            file_trn02 = re.sub('~','',line.split('*')[2])           # TRN;02
            file_trn03 = re.sub('~','',line.split('*')[3])           # TRN;03
        if (line.startswith("N1*PR")):
            file_payer = re.sub('~','',line.split('*')[2]).rstrip()  # N1;02
        if (line.startswith("N1*PE")):
            file_payee = re.sub('~','',line.split('*')[2]).rstrip()  # N1;02
            file_npi = re.sub('~','',line.split('*')[4])             # N1;04
        if (line.startswith("CLP")):
            claim = re.sub('~','',line.split('*')[1])                # CLP;01
            clp02 = re.sub('~','',line.split('*')[2])                # CLP;02
            return [file, file_trn02, file_trn03, file_payer, file_payee, file_npi, claim, clp02]
            # self.write_to_csv(file
            #     , file_trn02
            #     , file_trn03
            #     , file_payer
            #     , file_payee
            #     , file_npi
            #     , claim
            #     , clp02)

    def parse_835(self, file_pattern):
        # Iterate through each '835' file in current directory and parse out desired values
        # Consider if file is split across lines (standard) or all in 1 line (uncommon)
        # Write desired values out as each CLP segment is found
        #print("gets to parse_835")
        file_count = sum(len(files) for _, _, files in os.walk(self.source_dir))
        count = 0
        for root, dirs, files in os.walk(self.source_dir):
            for file in files:
                count = count + 1
                if file.endswith(file_pattern) or (file_pattern in file):
                    self.print_output(str(f'Reading file: {file}\n'))
                    num_lines_in_file = len(open(os.path.join(self.source_dir,file)).readlines())
                    if num_lines_in_file == 1:      # One Line 835
                        for line in open(os.path.join(self.source_dir,file),'r'):
                            one_line_data = line.split(sep="~")
                            for i in range(len(one_line_data)):
                                arg_list = self.parse_line(file, one_line_data[i])
                                self.write_to_csv(*arg_list)
                    else:                           # Normal Multi-line 835 file
                        for line in open(os.path.join(self.source_dir,file),'r'):
                            arg_list = self.parse_line(file, line)
                            self.write_to_csv(*arg_list)
                    time.sleep(1)
                self.update_progressbar(100 * (count / file_count))
        self.end_progressbar()

    def process_835s(self):
        #print("gets to process_835s")
        # Write out Headers if output file is being newly created in current directory
        with open(self.outfile_path, newline='', mode='a') as outcsv:
            csv_writer = csv.writer(outcsv, delimiter=',', quotechar='"', quoting = csv.QUOTE_MINIMAL)
            if not self.__file_exists: csv_writer.writerow(self.__OUTFILE_HEADERS)

        self.print_output(str(f'Beginning processing...\n'))
        self.print_output(str(f'Parsing with file pattern: {self.file_pattern}\n'))
        self.parse_835(self.file_pattern)
        self.print_output(str(f'Completed stripping 835s in: {self.source_dir}\n'))
        self.print_output(str(f'Results saved to: {self.__outfile_name}'))
        self.__run_counter += 1

# class ThreadedTask(threading.Thread):
#     def __init__(self, queue):
#         threading.Thread.__init__(self)
#         self.queue = queue
#     def run(self):
#         print("running thread")
#         #self.process_835s()
#         time.sleep(1)  # Simulate long running process
#         self.queue.put("Task finished")

if __name__ == "__main__":
    root = tk.Tk()
    root.wm_title('835 File Parser')
    #root.iconphoto(False, tk.PhotoImage(file='./835.png'))
    root.minsize(450,265)
    root.columnconfigure(2, weight=1)  # ok
    root.rowconfigure(1, weight=1)  # ok
    myapp = App(root)
    root.mainloop()

"""
Helpful Sites along the way
   https://mborgerson.com/creating-an-executable-from-a-python-script/
   https://stupidpythonideas.blogspot.com/2013/10/why-your-gui-app-freezes.html
   https://stackoverflow.com/questions/16745507/tkinter-how-to-use-threads-to-preventing-main-event-loop-from-freezing
   https://stackoverflow.com/questions/42422139/how-to-easily-avoid-tkinter-freezing
   Lot more in depth: https://pymotw.com/2/threading/

   pysinstaller --onefile --windowed --icon=835.ico 835Parser.spec
   else debug mode, onefolder, and no windowed
   for output and trace back if debug enabled:
    pyinstaller file.py 2> build.txt
"""

