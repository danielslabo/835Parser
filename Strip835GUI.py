import os
import csv
import sys
import re
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox, END
from tkinter.filedialog import askdirectory


class App(tk.Frame):
    __OUTFILE_PREFIX = "ParsedFileResults"
    __OUTFILE_HEADERS = ['FILENAME', 'TRN02', 'TRN03', 'PAYER', 'PAYEE', 'NPI',
                         'CLAIM', 'CLP02', 'PLB_DATA']
    __OUTFILE_HEADERS_271 = ['FILENAME', 'LASTNAME', 'FIRSTNAME', 'MIDINITIAL',
                             'SUBSCRIBERID', 'INSTYPECODE']
    __DEFAULT_FILE_PATTERN = ".835"
    __DEFAULT_PARSE_MODE = "835"
    __HELPFILE = 'help.txt'
    __CHANGELOG = 'changelog.txt'
    __ICONFILE = '835_icon.ico'

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
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
        self.__parse_271 = tk.BooleanVar()
        self.__parse_271.set(False)
        self.__run_counter = 1
        self.__outfile_name = self.get_new_outfile_name()
        self.__file_exists = self.check_outfile_exists(self.__outfile_name)
        self.__parse_mode = self.__DEFAULT_PARSE_MODE
        self.__headers = self.__OUTFILE_HEADERS

        self.__init_widgets_menu()
        self.__init_widgets_other()

    def __init_widgets_menu(self):
        """Sets up menu related widgets."""
        # Menu Bar
        menu_bar = tk.Menu(self.master)
        self.master.config(menu=menu_bar)

        # File
        self.file_menu = tk.Menu(menu_bar, tearoff=0)
        self.file_menu.add_command(label="Open",
                                   command=self.browse_for_open_loc)
        self.file_menu.add_command(label="Save",
                                   command=self.browse_for_save_loc)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.quit)
        menu_bar.add_cascade(label='File', menu=self.file_menu)

        # Settings
        self.settings_menu = tk.Menu(menu_bar, tearoff=0)
        self.settings_menu.add_checkbutton(
            label="Append subsequent runs", onvalue=1, offvalue=0,
            variable=self.__append_runs, command=None)
        self.settings_menu.add_checkbutton(
            label="Search in subdirectories", onvalue=1, offvalue=0,
            variable=self.__traverse_subdir, command=None)
        self.settings_menu.add_checkbutton(
            label="Use for 271 parsing", onvalue=1, offvalue=0,
            variable=self.__parse_271, command=self.update_widgets_271_toggle)
        menu_bar.add_cascade(label='Settings', menu=self.settings_menu)

        # Help
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Help", command=self.open_help)
        help_menu.add_command(label="Change Log", command=self.open_changelog)
        menu_bar.add_cascade(label="Help", menu=help_menu)

    def __init_widgets_other(self):
        """Sets up non-menu widgets. """
        # Frame Setup
        inputs_frame = tk.LabelFrame(root, text="1. Enter File Details: ")
        inputs_frame.grid(row=0, columnspan=10, sticky='WE', padx=5, pady=5,
                          ipadx=5, ipady=5)
        inputs_frame.columnconfigure(1, weight=1)

        output_frame = tk.Label(root)
        output_frame.grid(row=1, columnspan=10, sticky='NSEW', padx=5, pady=5,
                          ipadx=5, ipady=5)
        output_frame.columnconfigure(1, weight=1)
        output_frame.rowconfigure(0, weight=1)

        progress_frame = tk.Frame(root)
        progress_frame.grid(row=2, columnspan=10, sticky='WE', padx=5, pady=5)
        progress_frame.columnconfigure(1, weight=1)
        progress_frame.rowconfigure(1, weight=1)

        footer_frame = tk.Label(root)
        footer_frame.grid(row=3, columnspan=10, sticky='EW', padx=5, pady=1)
        footer_frame.columnconfigure(1, weight=1)
        footer_frame.rowconfigure(2, weight=1)

        # File Pattern Input
        file_pattern_lbl = tk.Label(inputs_frame, text="File Pattern", anchor='w')
        file_pattern_lbl.grid(row=0, column=0, sticky='WE', padx=5, pady=2)

        self.file_pattern_txt = tk.Entry(inputs_frame, state="normal")
        self.file_pattern_txt.grid(row=0, column=1, columnspan=7,
                                   sticky="WE", padx=5, pady=2)
        self.file_pattern_txt.insert(0, str(self.__DEFAULT_FILE_PATTERN))

        # Source Directory Prompt
        self.in_folder_lbl = tk.Label(inputs_frame, text="Folder with 835s:", anchor='w')
        self.in_folder_lbl.grid(row=1, column=0, sticky='WE', padx=5, pady=2)

        self.in_folder_txt = tk.Entry(inputs_frame, state="disabled")
        self.in_folder_txt.grid(row=1, column=1, columnspan=7,
                                sticky="WE", padx=5, pady=2)

        self.in_folder_btn = tk.Button(inputs_frame, text="Browse ...",
                                       command=self.browse_for_open_loc)
        self.in_folder_btn.grid(row=1, column=10, sticky='E', padx=5, pady=2)

        # Save Results Prompt
        out_folder_lbl = tk.Label(inputs_frame, text="Save Results to:",
                                  anchor='w')
        out_folder_lbl.grid(row=2, column=0, sticky='WE', padx=5, pady=2)

        self.out_folder_txt = tk.Entry(inputs_frame, state="disabled")
        self.out_folder_txt.grid(row=2, column=1, columnspan=7, sticky="WE",
                                 padx=5, pady=2)

        self.out_folder_btn = tk.Button(inputs_frame, text="Browse ...",
                                        command=self.browse_for_save_loc)
        self.out_folder_btn.grid(row=2, column=10, sticky='E', padx=5, pady=2)

        # Results Output Display
        self.output_text = tk.scrolledtext.ScrolledText(
            output_frame, wrap='word', height=5, width=10,
            font=('', 8), fg="#333333")
        self.output_text.grid(row=0, column=1, sticky="NSEW", padx=5, pady=2)

        self.xscroll_bar = tk.Scrollbar(output_frame, orient='horizontal',
                                        command=self.output_text.xview)
        self.output_text.configure(xscrollcommand=self.xscroll_bar.set)
        self.xscroll_bar.grid(row=2, column=1, sticky='EW')

        # Progress Bar
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal",
                                            length=200, mode="determinate")

        # Run and Close       
        self.ok_btn = tk.Button(footer_frame, text="Run",
                                command=self.setup_processing)
        self.ok_btn.grid(row=2, column=2, sticky='SE', padx=5, pady=2, ipadx=27)

        close_btn = tk.Button(footer_frame, text="Close", command=self.quit)
        close_btn.grid(row=2, column=3, sticky='SE', padx=5, pady=2, ipadx=20)

    def update_widgets_271_toggle(self):
        if self.__parse_271.get():
            self.__parse_mode = "271"
            self.__file_pattern = ".txt"
            self.in_folder_lbl.config(text = "Folder with 271s:")
            self.file_pattern_txt.delete(0,END)
            self.file_pattern_txt.insert(0, str(self.__file_pattern))
            self.__headers = self.__OUTFILE_HEADERS_271
        else:
            self.__parse_mode = "835"
            self.__file_pattern = self.__DEFAULT_FILE_PATTERN
            self.in_folder_lbl.config(text = "Folder with 835s:")
            self.file_pattern_txt.delete(0,END)
            self.file_pattern_txt.insert(0, str(self.__file_pattern))
            self.__headers = self.__OUTFILE_HEADERS




    def open_changelog(self):
        """Opens changelog file for user in new window."""
        try:
            with open(self.resource_path(self.__CHANGELOG),
                      mode='r') as changelogfile:
                msg = changelogfile.read()
            new_window = tk.Toplevel(self.master)
            new_window.title('Change Log')
            new_window.resizable(width=False, height=False)
            new_window.iconbitmap(self.icon_path)

            changelog_frame = tk.Frame(new_window)
            changelog_frame.pack()

            txt_widget = tk.scrolledtext.ScrolledText(changelog_frame,
                                                      wrap='none',
                                                      state='disabled')
            txt_widget.configure(state='normal', font='TkFixedFont')
            txt_widget.insert(tk.END, str(msg))
            txt_widget.configure(state='disabled')

            xscroll_bar = tk.Scrollbar(changelog_frame, orient='horizontal',
                                       command=txt_widget.xview)
            txt_widget.configure(xscrollcommand=xscroll_bar.set)

            txt_widget.grid(row=0, column=0, sticky='EW')
            xscroll_bar.grid(row=1, column=0, sticky='EW')
        except IOError:
            tk.messagebox.showerror(title="Error",
                                    message='Error opening changelog')

    def open_help(self):
        """Opens help file for user in new window."""
        try:
            with open(self.resource_path(self.__HELPFILE), mode='r') as helpfile:
                msg = helpfile.read()
            tk.messagebox.showinfo('Help', message=msg, icon='question')
        except IOError:
            tk.messagebox.showerror(title="Error",
                                    message='Error opening help file')

    def quit(self):
        """Closes app."""
        root.destroy()

    def update_outfile_path(self, save_loc, filename):
        """Updates outfile to specified save_loc and filename."""
        self.__outfile_path = os.path.join(save_loc, filename)

    def browse_for_open_loc(self):
        """Opens window for user to navigate and select input folder location."""
        msg = "Browse for Folder containing {ext}s to parse...".format(ext = self.__parse_mode)
        open_loc = os.path.normpath(askdirectory(title=msg))
        self.in_folder_txt.configure(state='normal')
        self.in_folder_txt.delete(0, tk.END)
        self.in_folder_txt.insert(0, str(open_loc))
        self.in_folder_txt.configure(state='disabled')
        self.__source_dir = os.path.normpath(open_loc)

    def browse_for_save_loc(self):
        """Opens window for user to navigate and select output folder location."""
        save_loc = os.path.normpath(askdirectory(
            # initialdir=expanduser(pathvar.get()), # used for debugging
            title="Browse for where to save output results..."))
        self.out_folder_txt.configure(state='normal')
        self.out_folder_txt.delete(0, tk.END)
        self.out_folder_txt.insert(0, str(save_loc))
        self.out_folder_txt.configure(state='disabled')
        self.update_outfile_path(save_loc, self.__outfile_name)

    def write_to_csv(self, *args):
        """Appends input args to outfile."""
        with open(self.__outfile_path, newline='', mode='a') as outcsv:
            csv_writer = csv.writer(outcsv, delimiter=',',
                                    quotechar='"', quoting=csv.QUOTE_MINIMAL)
            data = []
            for x in args:
                data.append(x)
            csv_writer.writerow(data)

    @staticmethod
    def warn_missing_loc():
        """Shows user warning of missing input and/or output values"""
        msg = "Please specify an input and output folder location"
        tk.messagebox.showerror(title="Error- Did you forget??", message=msg)

    def print_output(self, text):
        """Adds parameter text at bottom of output text widget for user to see."""
        self.output_text.configure(state='normal')
        self.output_text.insert(tk.END, str(text))
        self.output_text.see(tk.END)
        self.output_text.configure(state='disabled')

    @staticmethod
    def resource_path(relative_path):
        # Get absolute path to resource, works for dev and for PyInstaller
        base_path = getattr(sys, '_MEIPASS',
                            os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def disable_widgets(self):
        """
        Disables certain widgets from user interaction while program is parsing
        files to prevent unexpected issues."""
        self.ok_btn.configure(state='disabled')
        self.in_folder_btn.configure(state='disabled')
        self.out_folder_btn.configure(state='disabled')
        self.file_pattern_txt.configure(state='disabled')
        self.file_menu.entryconfigure(0, state='disabled')
        self.file_menu.entryconfigure(1, state='disabled')
        self.settings_menu.entryconfigure(0, state='disabled')
        self.settings_menu.entryconfigure(1, state='disabled')

    def enable_widgets(self):
        """Re-enables user interaction with certain widgets previously disabled. """
        self.ok_btn.configure(state='normal')
        self.in_folder_btn.configure(state='normal')
        self.out_folder_btn.configure(state='normal')
        self.file_pattern_txt.configure(state='normal')
        self.file_menu.entryconfigure(0, state='normal')
        self.file_menu.entryconfigure(1, state='normal')
        self.settings_menu.entryconfigure(0, state='normal')
        self.settings_menu.entryconfigure(1, state='normal')

    @staticmethod
    def check_outfile_exists(outfile_name):
        """Returns if outfile_name param is an existing file."""
        return os.path.isfile(outfile_name)

    def get_new_outfile_name(self):
        """Returns new filename affixed with current time-related elements."""
        return (self.__OUTFILE_PREFIX + " " +
                time.strftime("%Y-%m-%d-%H%M%S") + ".csv")

    def begin_progressbar(self):
        """
        Disable widgets that affect input values used when processing and
        make progress bar visible.
        """
        self.disable_widgets()
        self.progress_bar.grid(row=2, column=1, stick='EW')

    def update_progressbar(self, amount):
        """Update progress bar to specified amount value."""
        self.progress_bar['value'] = amount
        self.master.update_idletasks()

    def end_progressbar(self):
        """ Set progress bar to 0 value and hide it from user."""
        self.update_progressbar(int(0))
        self.enable_widgets()
        self.progress_bar.grid_forget()

    def process_queue(self):
        """ Unused. Potentially use when implementing a Queue. """
        pass
        # try:
        #     msg = self.queue.get(0)
        #     # Show result of the task if needed
        #     print(msg)
        #     self.progressBar.stop()
        # except queue.Empty:
        #     self.master.after(100, self.process_queue)

    def get_files_list(self, source_dir):
        """Returns a list of files in specified source_dir."""
        if self.__traverse_subdir.get():
            files = [os.path.join(root, f) for root, dirs, files
                     in os.walk(source_dir) for f in files]
            # files = [f for root,dirs,files in os.walk(source_dir) for f in files]
        else:
            files = [f for f in os.listdir(source_dir)
                     if os.path.isfile(os.path.join(source_dir, f))]
        return files

    def parse_271(self, full_file_path, filename):
        """TODO Document parse_271 function."""
        with open(full_file_path, 'r') as file:
            file_data = file.readlines()
            num_lines_in_file = len(file_data)
            if num_lines_in_file == 1:
                file_content = file_data[0].split(sep="\n")
            else:
                file_content = file_data
            for line in file_content:
                lname, fname, midin, subid, instype = "", "", "", "", ""
                idxA1 = ("EB", line.find("EB*R**30*"))
                idxB1 = ("SUB", line.find("NM1*IL*1*"))
                indexes = sorted([idxA1, idxB1])
                for start_index in indexes:
                    idx_white_space = line[start_index[1]:].find(" ")
                    data = line[start_index[1]:start_index[1] + idx_white_space]
                    if start_index[0] == "SUB":
                        lname = data.split('*')[3]
                        fname = data.split('*')[4]
                        midin = data.split('*')[7]
                        subid = data.split('*')[9]
                    elif start_index[0] == "EB":
                        instype = data.split('*')[4]
                parsed_line = [filename, lname, fname, midin, subid, instype]
                # print(parsed_line)
                self.write_to_csv(*parsed_line)

    def parse_835(self, full_file_path, filename):
        """
        Consider if filename in specified full_file_path  is split across
        multiple lines (standard) or all in 1 line (less common). Write desired
        values out as each CLP or PLB segment is found.
        Note: Currently will update TRN and N1* as the respective segment
        occurs in a file, but in the future it may be desired to clear values
        if a new one occurs, so as not to mix.
        """
        file_trn02 = file_trn03 = file_payer = file_payee = file_npi = ""
        with open(full_file_path, 'r') as file:
            file_data = file.readlines()
            num_lines_in_file = len(file_data)
            if num_lines_in_file == 1:
                file_content = file_data[0].split(sep="~")
            else:
                file_content = file_data
            for line in file_content:
                claim, clp02, plb = "", "", ""  # reset values
                if line.startswith("TRN"):
                    file_trn02 = re.sub('~', '', line.split('*')[2])  # TRN;02
                    file_trn03 = re.sub('~', '', line.split('*')[3])  # TRN;03
                if line.startswith("N1*PR"):
                    file_payer = re.sub('~', '', line.split('*')[2]).rstrip()  # N1;02
                if line.startswith("N1*PE"):
                    file_payee = re.sub('~', '', line.split('*')[2]).rstrip()  # N1;02
                    file_npi = re.sub('~', '', line.split('*')[4])  # N1;04
                if line.startswith("CLP"):
                    claim = re.sub('~', '', line.split('*')[1])  # CLP;01
                    clp02 = re.sub('~', '', line.split('*')[2])  # CLP;02
                    parsed_line = [filename, file_trn02, file_trn03,
                                   file_payer, file_payee, file_npi, claim,
                                   clp02, plb]
                    self.write_to_csv(*parsed_line)
                elif line.startswith("PLB"):  # PLB;*
                    plb = re.sub('~', '', line.rstrip())
                    parsed_line = [filename, file_trn02, file_trn03,
                                   file_payer, file_payee, file_npi, claim,
                                   clp02, plb]
                    self.write_to_csv(*parsed_line)

    def process_files(self, file_pattern, source_dir):
        """
        Get number of files in specified source_dir and iterate through each file of
        specified file_pattern in source_dir and call function to parse the file. Increment
        files parsed and update progress bar with each 1% change in progress.
        """
        files = self.get_files_list(source_dir)
        # total_file_count = sum(len(files) for _, _, files in os.walk(source_dir)) # for debugging
        total_file_count = len(files)
        processed_file_count = 0
        for file in files:
            processed_file_count += 1
            if file.endswith(file_pattern) or (file_pattern in file):
                self.print_output(f'Reading file: {file}\n')
                full_file_path = os.path.abspath(os.path.join(source_dir, file))
                # Check what we're parsing
                if self.__parse_271.get():
                    self.parse_271(full_file_path, file)
                else:
                    self.parse_835(full_file_path, file)
            progress = int(100 * (processed_file_count / total_file_count))
            if self.progress_bar['value'] < progress:
                self.update_progressbar(progress)
        self.end_progressbar()

    def begin_processing(self):
        """
        Creates with headers or opens existing outfile and calls function to
        process files in source dir with set file pattern. Will increment run
        counter.
        """
        with open(self.__outfile_path, newline='', mode='a') as outcsv:
            csv_writer = csv.writer(outcsv, delimiter=',', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
            if not self.__file_exists:
                csv_writer.writerow(self.__headers)
        self.print_output(f'Beginning processing...\n')
        self.print_output(f'Parsing with file pattern: {self.__file_pattern}\n')
        self.process_files(self.__file_pattern, self.__source_dir)
        self.print_output(f'Completed stripping {self.__parse_mode}s in: {self.__source_dir}\n')
        self.print_output(f'Results saved to: {self.__outfile_path}')
        self.__run_counter += 1

    def setup_processing(self):
        """
        Checks if file pattern and in/out folder values have been specified else stops
        and warns user to specify them. If user re-running program, prompts if re-run
        is desired to avoid accidental re-runs on large amounts of files. If re-running,
        will reset output filename if setting set to NOT append results to initial run's
        file.
        """
        if len(self.file_pattern_txt.get()) > 0:
            self.__file_pattern = self.file_pattern_txt.get()
        if (len(self.in_folder_txt.get()) == 0 or
                len(self.out_folder_txt.get()) == 0):
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
                        self.update_outfile_path(self.out_folder_txt.get(),
                                                 self.__outfile_name)
                    ok_to_run = True
                    self.print_output(f'\n\n\n*****Starting Run #{self.__run_counter} *****\n')
            else:
                ok_to_run = True
            if ok_to_run:
                self.begin_progressbar()
                # self.queue = queue.Queue()                  # Implement with Queues potentially
                # ThreadedTask(self.queue).start()            # Implement with Queues potentially
                threading.Thread(target=self.begin_processing,
                                 daemon=True).start()
                # self.master.after(100, self.process_queue)  # Implement with Queues potentially


class ThreadedTask(threading.Thread):
    """ Unused. Potentially use when implementing a Queue. """
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
