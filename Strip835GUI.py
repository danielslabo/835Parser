import os
import csv
import sys
import re
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
from tkinter.filedialog import askdirectory
from tkinter.messagebox import showerror, askyesno
from tkinter.font import Font

'''
Program parses an 835 file.
    Assumptions: end of line delimiter is '~', segment delimiter is '*'
'''


class App(tk.Frame):
    __OUTFILE_PREFIX = "Parsed835Results"
    __OUTFILE_HEADERS = ['FILENAME', 'TRN02', 'TRN03', 'PAYER', 'PAYEE', 'NPI',
                         'CLAIM', 'CLP02', 'PLB_DATA']
    __DEFAULT_FILE_PATTERN = ".835"
    __HELPFILE = 'help.txt'
    __CHANGELOG = 'changelog.txt'
    __ICONFILE = '835_icon.ico'

    def __init__(self, master):
        self.master = master
        self.icon_path = self.resource_path(self.__ICONFILE)
        self.master.iconbitmap(self.icon_path)
        self.__outfile_path = ""
        self.__source_dir = ""
        self.__file_pattern = ""
        self.__append_runs = tk.BooleanVar()
        self.__append_runs.set(True)
        self.__traverse_subdir = tk.BooleanVar()
        self.__traverse_subdir.set(False)
        self.__run_counter = 1
        self.__outfile_name = self.get_new_outfile_name()
        self.__file_exists = self.check_outfile_exists(self.__outfile_name)

        self.init_widgets_menu()
        self.init_widgets_other()

    def init_widgets_menu(self):
        # Menu Bar
        menubar = tk.Menu(self.master)
        self.master.config(menu=menubar)

        # File
        self.filemenu = tk.Menu(menubar, tearoff=0)
        self.filemenu.add_command(label="Open", 
                                  command=self.browse_for_open_loc)
        self.filemenu.add_command(label="Save", 
                                  command=self.browse_for_save_loc)
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label='File', menu=self.filemenu)

        # Settings
        self.settingsmenu = tk.Menu(menubar, tearoff=0)
        self.settingsmenu.add_checkbutton(
            label="Append subsequent runs", onvalue=1, offvalue=0, 
            variable=self.__append_runs, command=None)
        self.settingsmenu.add_checkbutton(
            label="Search in subdirectories", onvalue=1, offvalue=0, 
            variable=self.__traverse_subdir, command=None)
        menubar.add_cascade(label='Settings', menu=self.settingsmenu)

        # Help
        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Help", command=self.open_help)
        helpmenu.add_command(label="Change Log", command=self.open_changelog)
        menubar.add_cascade(label="Help", menu=helpmenu)

    def init_widgets_other(self):
        # Frame Setup
        inputsFrame = tk.LabelFrame(root, text="1. Enter File Details: ")
        inputsFrame.grid(row=0, columnspan=10, sticky='WE', padx=5, pady=5, 
                         ipadx=5, ipady=5)
        inputsFrame.columnconfigure(1, weight=1)

        outputFrame = tk.Label(root)
        outputFrame.grid(row=1, columnspan=10, sticky='NSEW', padx=5, pady=5, 
                         ipadx=5, ipady=5)
        outputFrame.columnconfigure(1, weight=1)
        outputFrame.rowconfigure(0, weight=1)

        progressFrame = tk.Frame(root)
        progressFrame.grid(row=2, columnspan=10, sticky='WE', padx=5, pady=5)
        progressFrame.columnconfigure(1, weight=1)
        progressFrame.rowconfigure(1, weight=1)
        
        footerFrame = tk.Label(root)
        footerFrame.grid(row=3, columnspan=10, sticky='EW', padx=5, pady=1)
        footerFrame.columnconfigure(1, weight=1)
        footerFrame.rowconfigure(2, weight=1)
        
        # File Pattern Input
        filePatternLbl = tk.Label(inputsFrame, text="File Pattern", anchor='w')
        filePatternLbl.grid(row=0, column=0, sticky='WE', padx=5, pady=2)

        self.filePatternTxt = tk.Entry(inputsFrame, state="normal")
        self.filePatternTxt.grid(row=0, column=1, columnspan=7, 
                                 sticky="WE", padx=5, pady=2)
        self.filePatternTxt.insert(0, str(self.__DEFAULT_FILE_PATTERN))

        # Source Directory Prompt
        inFolderLbl = tk.Label(inputsFrame, text="Folder with 835s:", 
                               anchor='w')
        inFolderLbl.grid(row=1, column=0, sticky='WE', padx=5, pady=2)
        
        self.inFolderTxt = tk.Entry(inputsFrame, state="disabled")
        self.inFolderTxt.grid(row=1, column=1, columnspan=7, 
                              sticky="WE", padx=5, pady=2)
        
        self.inFolderBtn = tk.Button(inputsFrame, text="Browse ...", 
                                     command=self.browse_for_open_loc)
        self.inFolderBtn.grid(row=1, column=10, sticky='E', padx=5, pady=2)
        
        # Save Results Prompt
        outFolderLbl = tk.Label(inputsFrame, text="Save Results to:", 
                                anchor='w')
        outFolderLbl.grid(row=2, column=0, sticky='WE', padx=5, pady=2)
  
        self.outFolderTxt = tk.Entry(inputsFrame, state="disabled")
        self.outFolderTxt.grid(row=2, column=1, columnspan=7, sticky="WE", 
                               padx=5, pady=2)

        self.outFolderBtn = tk.Button(inputsFrame, text="Browse ...", 
                                      command=self.browse_for_save_loc)
        self.outFolderBtn.grid(row=2, column=10, sticky='E', padx=5, pady=2)
        
        # Results Output Display
        self.outputText = tk.scrolledtext.ScrolledText(
            outputFrame, wrap='word', height=5, width=10, 
            font=('', 8), fg="#333333")
        self.outputText.grid(row=0, column=1, sticky="NSEW", padx=5, pady=2)

        self.xscrollbar = tk.Scrollbar(outputFrame, orient='horizontal', 
                                       command=self.outputText.xview)
        self.outputText.configure(xscrollcommand=self.xscrollbar.set)
        self.xscrollbar.grid(row=2, column=1, sticky='EW')

        # Progress Bar
        self.progressBar = ttk.Progressbar(progressFrame, orient="horizontal", 
                                           length=200, mode="determinate")

        # Run and Close       
        self.okBtn = tk.Button(footerFrame, text="Run", 
                               command=self.setup_processing)
        self.okBtn.grid(row=2, column=2, sticky='SE', padx=5, pady=2, ipadx=27)
        
        closeBtn = tk.Button(footerFrame, text="Close", command=self.quit)
        closeBtn.grid(row=2, column=3, sticky='SE', padx=5, pady=2, ipadx=20)

    def open_changelog(self):
        try:
            with open(self.resource_path(self.__CHANGELOG), 
                      mode='r') as changelogfile:
                msg = changelogfile.read()
            newWindow = tk.Toplevel(self.master)
            newWindow.title('Change Log')
            newWindow.resizable(width=False, height=False)
            newWindow.iconbitmap(self.icon_path)

            changelogFrame = tk.Frame(newWindow)
            changelogFrame.pack()
            
            txtWidget = tk.scrolledtext.ScrolledText(changelogFrame, 
                                                     wrap='none', 
                                                     state='disabled')
            txtWidget.configure(state='normal', font='TkFixedFont')
            txtWidget.insert(tk.END, str(msg))
            txtWidget.configure(state='disabled')

            xscrollbar = tk.Scrollbar(changelogFrame, orient='horizontal', 
                                      command=txtWidget.xview)
            txtWidget.configure(xscrollcommand=xscrollbar.set)

            txtWidget.grid(row=0, column=0, sticky='EW')
            xscrollbar.grid(row=1, column=0, sticky='EW')
        except IOError:
            tk.messagebox.showerror(title="Error", 
                                    message='Error opening changelog')

    def open_help(self):
        try:
            with open(self.resource_path(self.__HELPFILE), mode='r') as helpfile:
                msg = helpfile.read()
            tk.messagebox.showinfo('Help', message=msg, icon='question')
        except IOError:
            tk.messagebox.showerror(title="Error", 
                                    message='Error opening help file')

    def quit(self):
        root.destroy()

    def update_outfile_path(self, save_loc, filename):
        self.__outfile_path = os.path.join(save_loc, filename)

    def browse_for_open_loc(self):
        msg = "Browse for Folder containing 835s to parse..."
        open_loc = os.path.normpath(askdirectory(title=msg))
        self.inFolderTxt.configure(state='normal')
        self.inFolderTxt.delete(0, tk.END)
        self.inFolderTxt.insert(0, str(open_loc))
        self.inFolderTxt.configure(state='disabled')
        self.__source_dir = os.path.normpath(open_loc)
    
    def browse_for_save_loc(self):
        save_loc = os.path.normpath(askdirectory(
            # initialdir=expanduser(pathvar.get()),
            title="Browse for where to save output results..."))
        self.outFolderTxt.configure(state='normal')
        self.outFolderTxt.delete(0, tk.END)
        self.outFolderTxt.insert(0, str(save_loc))
        self.outFolderTxt.configure(state='disabled')
        self.update_outfile_path(save_loc, self.__outfile_name)

    def write_to_csv(self, *args):
        with open(self.__outfile_path, newline='', mode='a') as outcsv:
            csv_writer = csv.writer(outcsv, delimiter=',', 
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            data = []
            for x in args:
                data.append(x)
            csv_writer.writerow(data)

    def warn_missing_loc(self):
        msg = "Please specify an input and output folder location"
        tk.messagebox.showerror(title="Error- Did you forget??", message=msg)

    def print_output(self, text):
        self.outputText.configure(state='normal')
        self.outputText.insert(tk.END, str(text))
        self.outputText.see(tk.END)
        self.outputText.configure(state='disabled')

    def resource_path(self, relative_path):
        # Get absolute path to resource, works for dev and for PyInstaller
        base_path = getattr(sys, '_MEIPASS', 
                            os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def disable_widgets(self):
        self.okBtn.configure(state='disabled')
        self.inFolderBtn.configure(state='disabled')
        self.outFolderBtn.configure(state='disabled')
        self.filePatternTxt.configure(state='disabled')
        self.filemenu.entryconfigure(0, state='disabled')
        self.filemenu.entryconfigure(1, state='disabled')
        self.settingsmenu.entryconfigure(0, state='disabled')
        self.settingsmenu.entryconfigure(1, state='disabled')

    def enable_widgets(self):
        self.okBtn.configure(state='normal')
        self.inFolderBtn.configure(state='normal')
        self.outFolderBtn.configure(state='normal')
        self.filePatternTxt.configure(state='normal')
        self.filemenu.entryconfigure(0, state='normal')
        self.filemenu.entryconfigure(1, state='normal')
        self.settingsmenu.entryconfigure(0, state='normal')
        self.settingsmenu.entryconfigure(1, state='normal')

    def check_outfile_exists(self, outfile_name):
        return os.path.isfile(self.__outfile_name)

    def get_new_outfile_name(self):
        return (self.__OUTFILE_PREFIX + " " + 
                time.strftime("%Y-%m-%d-%H%M%S") + ".csv")

    def begin_progressbar(self):
        self.disable_widgets()
        self.progressBar.grid(row=2, column=1, stick='EW')

    def update_progressbar(self, amount):
        self.progressBar['value'] = amount
        self.master.update_idletasks()

    def end_progressbar(self):
        self.update_progressbar(int(0))
        self.enable_widgets()
        self.progressBar.grid_forget()

    def process_queue(self):  # Unused
        # Potentially use when implementing a Queue
        pass
        # try:
        #     msg = self.queue.get(0)
        #     # Show result of the task if needed
        #     print(msg)
        #     self.progressBar.stop()
        # except queue.Empty:
        #     self.master.after(100, self.process_queue)

    def get_files_list(self, source_dir):
        if self.__traverse_subdir.get():
            files = [os.path.join(root, f) for root, dirs, files 
                     in os.walk(source_dir) for f in files]
            # files = [f for root,dirs,files in os.walk(source_dir) for f in files]
        else:
            files = [f for f in os.listdir(source_dir) 
                     if os.path.isfile(os.path.join(source_dir, f))]
        return files

    def parse_835(self, full_file_path, filename):
        # Consider if file is split across lines (standard) or all in 1 line 
        # (uncommon). Write desired values out as each CLP or PLB segment is 
        # found. Currently will update TRN and N1* as the respective segment 
        # occurs in a file,but may want to clear values if a new one occurs,
        # so as not to mix. TBD
        file_trn02 = file_trn03 = file_payer = file_payee = file_npi = ""
        num_lines_in_file = 0
        with open(full_file_path, 'r') as file:
            file_data = file.readlines()
            num_lines_in_file = len(file_data)
            file_content = []
            if num_lines_in_file == 1:
                file_content = file_data[0].split(sep="~")
            else:
                file_content = file_data
            for line in file_content:
                claim, clp02, plb = "", "", ""  # reset values
                if (line.startswith("TRN")):
                    file_trn02 = re.sub('~', '', line.split('*')[2])           # TRN;02
                    file_trn03 = re.sub('~', '', line.split('*')[3])           # TRN;03
                if (line.startswith("N1*PR")):
                    file_payer = re.sub('~', '', line.split('*')[2]).rstrip()  # N1;02
                if (line.startswith("N1*PE")):
                    file_payee = re.sub('~', '', line.split('*')[2]).rstrip()  # N1;02
                    file_npi = re.sub('~', '', line.split('*')[4])             # N1;04
                if (line.startswith("CLP")):
                    claim = re.sub('~', '', line.split('*')[1])                # CLP;01
                    clp02 = re.sub('~', '', line.split('*')[2])                # CLP;02
                    parsed_line = [filename, file_trn02, file_trn03, 
                                   file_payer, file_payee, file_npi, claim, 
                                   clp02, plb]
                    self.write_to_csv(*parsed_line)
                elif (line.startswith("PLB")):                               # PLB;*
                    plb = re.sub('~', '', line.rstrip())
                    parsed_line = [filename, file_trn02, file_trn03, 
                                   file_payer, file_payee, file_npi, claim, 
                                   clp02, plb]
                    self.write_to_csv(*parsed_line)

    def process_835s(self, file_pattern, source_dir):
        # Iterate through each '835' files in current directory and parse out desired values  
        files = self.get_files_list(source_dir)
        # total_file_count = sum(len(files) for _, _, files in os.walk(source_dir))
        total_file_count = len(files)
        processed_file_count = 0
        files = self.get_files_list(source_dir)
        for file in files:
            processed_file_count += 1
            if file.endswith(file_pattern) or (file_pattern in file):
                self.print_output(str(f'Reading file: {file}\n'))
                full_file_path = os.path.abspath(os.path.join(source_dir, file))
                self.parse_835(full_file_path, file)
            progress = int(100 * (processed_file_count / total_file_count))
            if self.progressBar['value'] < progress:
                self.update_progressbar(progress)
        self.end_progressbar()

    def begin_processing(self):
        # Write out Headers if output file is being newly created
        with open(self.__outfile_path, newline='', mode='a') as outcsv:
            csv_writer = csv.writer(outcsv, delimiter=',', quotechar='"', 
                                    quoting=csv.QUOTE_MINIMAL)
            if not self.__file_exists:
                csv_writer.writerow(self.__OUTFILE_HEADERS)
        self.print_output(str('Beginning processing...\n'))
        self.print_output(str(f'Parsing with file pattern: {self.__file_pattern}\n'))
        self.process_835s(self.__file_pattern, self.__source_dir)
        self.print_output(str(f'Completed stripping 835s in: {self.__source_dir}\n'))
        self.print_output(str(f'Results saved to: {self.__outfile_path}'))
        self.__run_counter += 1

    def setup_processing(self):
        if len(self.filePatternTxt.get()) > 0:
            self.__file_pattern = self.filePatternTxt.get()
        if (len(self.inFolderTxt.get()) == 0 or 
                len(self.outFolderTxt.get()) == 0):
            self.warn_missing_loc()
        else:
            ok_to_run = False
            if self.__run_counter != 1:
                if tk.messagebox.askyesno(
                        "Confirm Run", "Are you sure you want to run again?"):
                    if not self.__append_runs.get():
                        self.__outfile_name = self.get_new_outfile_name()
                        self.__file_exists = self.check_outfile_exists(
                                self.__outfile_name)
                        self.update_outfile_path(self.outFolderTxt.get(), 
                                                 self.__outfile_name)
                    ok_to_run = True
                    self.print_output(f'\n\n\n*****Starting Run #{self.__run_counter} *****\n')
            else:
                ok_to_run = True
            if ok_to_run:
                self.begin_progressbar()
                # self.queue = queue.Queue()
                # ThreadedTask(self.queue).start()
                threading.Thread(target=self.begin_processing, 
                                 daemon=True).start()
                # self.master.after(100, self.process_queue)


class ThreadedTask(threading.Thread):  # Unused
    # Potentially use when implementing a Queue
    pass
    # def __init__(self, queue):
    #     threading.Thread.__init__(self)
    #     self.queue = queue
    # def run(self):
    #     print("running thread")
    #     #self.begin_processing()
    #     time.sleep(1)  # Simulate long running process
    #     self.queue.put("Task finished")


if __name__ == "__main__":
    root = tk.Tk()
    root.wm_title('835 File Parser')
    root.minsize(450, 265)
    root.columnconfigure(2, weight=1)
    root.rowconfigure(1, weight=1)
    myapp = App(root)
    root.mainloop()

"""
Unreleased Items Notes
    https://stackoverflow.com/questions/25753632/tkinter-how-to-use-after-method
    https://stackoverflow.com/questions/36516497/how-to-update-a-progress-bar-in-a-loop
    https://stackoverflow.com/questions/13318742/python-logging-to-tkinter-text-widget
    https://beenje.github.io/blog/posts/logging-to-a-tkinter-scrolledtext-widget/
    https://stackoverflow.com/questions/6893968/how-to-get-the-return-value-from-a-thread-in-python
    https://stackoverflow.com/questions/39061265/how-to-get-a-working-progress-bar-in-python-using-multi-process-or-multi-threade

    import queue as queue
    pyinstaller --onefile --windowed --icon=835_icon.ico --version-file=version.txt Strip835GUI.spec
    pyinstaller -F -w -- clean --exclude-module=pyinstaller Strip835GUI.spec
    for output and trace back if debug enabled: pyinstaller file.py 2> build.txt
"""
