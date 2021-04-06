import tkinter as tk
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror
from tkinter.font import Font
from tkinter import scrolledtext
import os, csv, re, time, sys

# To DO: Make output text uneditable, method call needed for writing
#        Help button/version #
#        Standalone work
#        taskbar icon
#        Multithreaded: update display, progress bar, interrupted run message
#        OutputText font and color changes
#        option to select (default) .835 or contains a string in filename
#        Progress bar
#        Make Input labels aligned
#        Allow app to be reset/restarted for multiple runs
# Assumptions: Standard Format, segment delimiter is '*'

class App(tk.Frame):

    def __init__(self, master):
        self.master = master
        # self.master.resizable(width=False,height=False)
        path = self.resource_path('835.ico')
        self.master.iconbitmap(path)

        self.outfile_path = ""
        self.source_dir = ""

        inputsFrame = tk.LabelFrame(root, text="1. Enter File Details: ")
        inputsFrame.grid(row=0, columnspan=10, sticky='WE', padx=5, pady=5, ipadx=5, ipady=5)
        inputsFrame.columnconfigure(1,weight=1)  # ok

        outputFrame = tk.Label(root)
        outputFrame.grid(row=1, columnspan=10, sticky='NSEW', padx=5, pady=5, ipadx=5, ipady=5)
        outputFrame.columnconfigure(1,weight=1)  # ok
        outputFrame.rowconfigure(0,weight=1)  # ok
        
        footerFrame = tk.Label(root)
        footerFrame.grid(row=2, columnspan=10, sticky='EW', padx=5, pady=1)
        footerFrame.columnconfigure(1, weight=1)  # ok
        footerFrame.rowconfigure(1,weight=1)  # ok, no change?
        
         # File Pattern Input
        filePatternLbl = tk.Label(inputsFrame, text="File Pattern:")
        filePatternLbl.grid(row=0, column=0, sticky='WE', padx=5, pady=2)

        self.filePatternTxt = tk.Entry(inputsFrame, state="normal")
        self.filePatternTxt.grid(row=0, column=1, columnspan=7, sticky="WE", padx=5, pady=2)
        self.filePatternTxt.insert(0, str(file_pattern))

        # Source Directory Prompt
        inFolderLbl = tk.Label(inputsFrame, text="Folder with 835s:")
        inFolderLbl.grid(row=1, column=0, sticky='WE', padx=5, pady=2)
        
        self.inFolderTxt = tk.Entry(inputsFrame, state="disabled")
        self.inFolderTxt.grid(row=1, column=1, columnspan=7, sticky="WE", padx=5, pady=2)
        
        self.inFolderBtn = tk.Button(inputsFrame, text="Browse ...", command=self.browse_for_open_loc)
        self.inFolderBtn.grid(row=1, column=10, sticky='E', padx=5, pady=2)
        
        # Save Results Prompt
        outFolderLbl = tk.Label(inputsFrame, text="Save Results to:")
        outFolderLbl.grid(row=2, column=0, sticky='WE', padx=5, pady=2)
  
        self.outFolderTxt = tk.Entry(inputsFrame, state="disabled")
        self.outFolderTxt.grid(row=2, column=1, columnspan=7, sticky="WE", padx=5, pady=2)       

        self.outFolderBtn = tk.Button(inputsFrame, text="Browse ...", command=self.browse_for_save_loc)
        self.outFolderBtn.grid(row=2, column=10, sticky='E', padx=5, pady=2)
        
        # Results Output Display
        self.outputText = tk.scrolledtext.ScrolledText(outputFrame, wrap='word', height=5, width=10, font=('',8), fg="#333333")
        self.outputText.grid(row=0, column=1, sticky="NSEW", padx=5, pady=2)

        self.xscrollbar = tk.Scrollbar(outputFrame, orient='horizontal', command=self.outputText.xview)
        self.outputText.configure(xscrollcommand=self.xscrollbar.set)
        self.xscrollbar.grid(row=2, column=1, sticky="EW")

        # Run and Close
        self.okBtn = tk.Button(footerFrame, text="Run", command=self.parse_835)
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
        self.outfile_path = os.path.join(save_loc,outfile_name)

    def write_to_csv(self, *args):
        with open(self.outfile_path, newline='', mode='a') as outcsv:
            csv_writer = csv.writer(outcsv, delimiter=',', quotechar='"', quoting = csv.QUOTE_MINIMAL)
            data= []
            for x in args:
                data.append(x)
            csv_writer.writerow(data)

    def warn_missing_loc(self):
        tk.messagebox.showerror(title="Error- Did you forget??",message="Please specify both an input and output folder location")

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

    def parse_835(self):
        if len(self.filePatternTxt.get()) > 0:
            file_pattern = self.filePatternTxt.get()
            self.print_output(str(f'Pattern used: {file_pattern}\n'))
        self.disable_widgets()
        if len(self.outputText.index(tk.END)) != 0:
            self.print_output(str(f'\n\n'))
        if len(self.inFolderTxt.get()) == 0 or len(self.outFolderTxt.get()) == 0:
            self.warn_missing_loc()
        else:
            # Write out Headers if output file is being newly created in current directory
            with open(self.outfile_path, newline='', mode='a') as outcsv:
                csv_writer = csv.writer(outcsv, delimiter=',', quotechar='"', quoting = csv.QUOTE_MINIMAL)
                if not file_exists:
                    csv_writer.writerow(outfile_headers)
            self.print_output(str(f'Beginning processing...\n'))
            self.print_output(str(f'Parsing with file pattern: {file_pattern}\n'))
            # Iterate through each '835' file in current directory and parse out desired values
            # Consider if file is split across lines (standard) or all in 1 line (uncommon)
            # Write desired values out as each CLP segment is found
            for root, dirs, files in os.walk(self.source_dir):
                for file in files:
                    if file.endswith(file_pattern) or (file_pattern in file):
                        self.print_output(str(f'Reading file: {file}\n'))
                        file_trn02, file_trn03, file_payer, file_payee, file_npi = "", "", "", "", ""
                        num_lines_in_file = len(open(os.path.join(self.source_dir,file)).readlines())
                        # One Line 835
                        if num_lines_in_file == 1:
                            for line in open(os.path.join(self.source_dir,file),'r'):
                                one_line_data = line.split(sep="~")
                                for i in range(len(one_line_data)):
                                    if (one_line_data[i].startswith("TRN")):
                                         file_trn02 = re.sub('~','',one_line_data[i].split('*')[2])           # TRN;02
                                         file_trn03 = re.sub('~','',one_line_data[i].split('*')[3])           # TRN;03
                                    if (one_line_data[i].startswith("N1*PR")):
                                         file_payer = re.sub('~','',one_line_data[i].split('*')[2]).rstrip()  # N1;02
                                    if (one_line_data[i].startswith("N1*PE")):
                                         file_payee = re.sub('~','',one_line_data[i].split('*')[2]).rstrip()  # N1;02
                                         file_npi = re.sub('~','',one_line_data[i].split('*')[4])             # N1;04
                                    if (one_line_data[i].startswith("CLP")):
                                         claim = re.sub('~','',one_line_data[i].split('*')[1])                # CLP;01
                                         clp02 = re.sub('~','',one_line_data[i].split('*')[2])                # CLP;02
                                         self.write_to_csv(file, file_trn02, file_trn03, file_payer, file_payee, file_npi, claim, clp02)
                        else:
                            for line in open(os.path.join(self.source_dir,file),'r'):
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
                                    self.write_to_csv(file, file_trn02, file_trn03, file_payer, file_payee, file_npi, claim, clp02)
            self.print_output(str(f'Completed stripping 835s in: {self.source_dir} to {outfile_name}'))


        self.enable_widgets()

    # def refresh(self):
    #     self.root.update()
    #     self.root.after(1000,self.refresh)

    # def start(self):
    #     self.refresh()
    #     threading.Thread(target=doingALotOfStuff).start()

if __name__ == "__main__":
    outfile_name = "Parsed835Goodies" +" " + time.strftime("%Y-%m-%d-%H%M%S") + ".csv"
    outfile_headers = ['FILENAME', 'TRN02', 'TRN03', 'PAYER', 'PAYEE', 'NPI', 'CLAIM', 'CLP02']
    file_exists = os.path.isfile(outfile_name)
    file_pattern = ".835"

    root = tk.Tk()
    root.wm_title('835 File Parser')
    # root.iconphoto(False, tk.PhotoImage(file='./835.png'))
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

   pysinstaller --onefile --windowed --icon/??? 835Parser.spec
   else debug mode, onefolder, and no windowed
   for output and trace back if debug enabled:
    pyinstaller file.py 2> build.txt
"""
