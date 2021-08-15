from itertools import count
import sys
import tkinter as tk
import tkinter.messagebox as tkMessageBox
import threading
import time
from random import randint
import queue

# Based on example Dialog 
# http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
class InfoMessage(tk.Toplevel):
    def __init__(self, parent, info, title=None, modal=True):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent

        body = tk.Frame(self)
        self.initial_focus = self.body(body, info)
        body.pack(padx=5, pady=5)

        self.buttonbox()

        if modal:
            self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        self.initial_focus.focus_set()

        if modal:
            self.wait_window(self)  # Wait until this window is destroyed.

    def body(self, parent, info):
        label = tk.Label(parent, text=info)
        label.pack()
        return label  # Initial focus.

    def buttonbox(self):
        box = tk.Frame(self)
        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        self.bind("<Return>", self.ok)
        box.pack()

    def ok(self, event=None):
        self.withdraw()
        self.update_idletasks()
        self.cancel()

    def cancel(self, event=None):
        # Put focus back to the parent window.
        self.parent.focus_set()
        self.destroy()


class GuiPart:
    TIME_INTERVAL = 0.1

    def __init__(self, master, queue, end_command):
        self.queue = queue
        self.master = master
        console = tk.Button(master, text='Done', command=end_command)
        console.pack(expand=True)
        self.update_gui()  # Start periodic GUI updating.

    def update_gui(self):
        try:
            self.master.update_idletasks()
            threading.Timer(self.TIME_INTERVAL, self.update_gui).start()
        except RuntimeError:  # mainloop no longer running.
            pass

    def process_incoming(self):
        """ Handle all messages currently in the queue. """
        while self.queue.qsize():
            try:
                info = self.queue.get_nowait()
                InfoMessage(self.master, info, "Status", modal=False)
            except queue.Empty:  # Shouldn't happen.
                pass


class ThreadedClient:
    """ Launch the main part of the GUI and the worker thread. periodic_call()
        and end_application() could reside in the GUI part, but putting them
        here means all the thread controls are in a single place.
    """
    def __init__(self, master):
        self.master = master
        self.count = count(start=1)
        self.queue = queue.Queue()

        # Set up the GUI part.
        self.gui = GuiPart(master, self.queue, self.end_application)

        # Set up the background processing thread.
        self.running = True
        self.thread = threading.Thread(target=self.workerthread)
        self.thread.start()

        # Start periodic checking of the queue.
        self.periodic_call(200)  # Every 200 ms.

    def periodic_call(self, delay):
        """ Every delay ms process everything new in the queue. """
        self.gui.process_incoming()
        if not self.running:
            sys.exit(1)
        self.master.after(delay, self.periodic_call, delay)

    # Runs in separate thread - NO tkinter calls allowed.
    def workerthread(self):
        while self.running:
            time.sleep(randint(1, 10))  # Time-consuming processing.
            count = next(self.count)
            info = 'Report #{} created'.format(count)
            self.queue.put(info)

    def end_application(self):
        self.running = False  # Stop queue checking.
        self.master.quit()


if __name__ == '__main__':  # Needed to support multiprocessing.
    root = tk.Tk()
    root.title('Report Generator')
    root.minsize(300, 100)
    client = ThreadedClient(root)
    root.mainloop()  # Display application window and start tkinter event loop.