import threading
import os
import time
from time import process_time_ns
from tkinter import Tk, ttk, Frame, Button as Bt, Label, Entry, Menu, BOTH, StringVar
from pynput import mouse as mo
from pynput import keyboard as ke
from pynput.keyboard import Controller as Controller_k
from pynput.mouse import Controller as Controller_m
import key_dict


class Record:
    def __init__(self):
        self.history = []
        self.k_listener = ke.Listener(on_press=self.press, on_release=self.release)
        self.m_listener = mo.Listener(on_click=self.click, on_scroll=self.scroll)

    def click(self, x, y, button, pressed):
        self.history.append((time.time_ns() - self.st_tm, "{0}".format(button), pressed, x, y))

    def scroll(self, x, y, dx, dy):
        self.history.append((time.time_ns() - self.st_tm, "scroll", dy, x, y))

    def press(self, key):
        try:
            self.history.append((time.time_ns() - self.st_tm, "key", key.char, True, True))
        except AttributeError:
            self.history.append((time.time_ns() - self.st_tm, "key", str(key), True, False))

    def release(self, key):
        try:
            self.history.append((time.time_ns() - self.st_tm, "key", key.char, False, True))
        except AttributeError:
            self.history.append((time.time_ns() - self.st_tm, "key", str(key), False, False))

    def record_start(self):
        self.st_tm = time.time_ns()
        self.m_listener.start()
        self.k_listener.start()

    def record_stop(self):
        self.m_listener.stop()
        self.k_listener.stop()
        self.history.pop()  # deletes last clicks
        self.history.pop()

        x = 0
        y = 1
        le = len(self.history)
        for z in range(le):
            if z != 0:
                if self.history[x][1:] == self.history[y][1:]:
                    self.history.pop(x)  # delete duplicate clicks
                else:
                    x += 1
                    y += 1
        return self.history


class Replay(threading.Thread):
    def __init__(self, path):
        threading.Thread.__init__(self)

        file = open(path, "r")
        self.recording = eval(file.read())

        self.length = len(self.recording)
        self.dic = key_dict.dic
        self.keyboard = Controller_k()
        self.mouse = Controller_m()

    def run(self):
        st_tm = process_time_ns()

        for z in range(self.length):
            action = self.recording[z]

            tm = st_tm + action[0]
            x = action[3]
            y = action[4]

            while process_time_ns() < tm:
                pass

            if action[1][:7] == "Button.":
                self.mouse.position = (x, y)
                try:
                    if action[2]:
                        self.mouse.press(self.dic[action[1]])
                    else:
                        self.mouse.release(self.dic[action[1]])
                except KeyError:
                    print("ERROR: unknown key " + str(action[2]))

            elif action[1] == "scroll":
                self.mouse.position = (x, y)
                self.mouse.scroll(None, action[2])

            elif action[1] == "key":
                if action[3]:
                    try:
                        if action[4]:
                            self.keyboard.press(action[2])
                        else:
                            self.keyboard.press(self.dic[action[2]])
                    except KeyError:
                        print("ERROR: unknown key " + str(action[2]))

                else:
                    try:
                        if action[4]:
                            self.keyboard.release(action[2])
                        else:
                            self.keyboard.release(self.dic[action[2]])
                    except KeyError:
                        print("ERROR: unknown key " + str(action[2]))

            else:
                print("ERROR: unknown action")


class GUI(Frame):
    def __init__(self, big_fungus):
        Frame.__init__(self, big_fungus, background="white")
        self.big_fungus = big_fungus
        self.info = StringVar()
        self.file_name = StringVar()
        self.recording = []
        self.started = False

        self.big_fungus.title("MOUSE RECORD")
        self.centre_window()
        self.pack(fill=BOTH, expand=1)

        menubar = Menu(self.big_fungus)
        self.big_fungus.config(menu=menubar)
        file_menu = Menu(menubar)

        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Settings")  # add page
        file_menu.add_command(label="Help")  # add page
        file_menu.add_command(label="DEBUGGING", command=self.bug)

        start_button = Bt(self, text="Start", width=7, command=self.start)
        start_button.grid(row=0, column=0, padx=5, pady=5)

        stop_button = Bt(self, text="Stop", width=7, command=self.stop)
        stop_button.grid(row=1, column=0, padx=5, pady=5)

        info_lable = Label(self, textvariable=self.info, width=30)
        info_lable.grid(row=0, column=1, rowspan=2, sticky="news", padx=5, pady=5)

        save_as_button = Bt(self, text="Save as:", width=7, command=self.save_as)
        save_as_button.grid(row=3, column=0, padx=5, pady=5)

        save_as_entry = Entry(self, textvariable=self.file_name)
        save_as_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        replay_button = Bt(self, text="Replay", width=7, command=self.replay)
        replay_button.grid(row=4, column=0, padx=5, pady=5)

        self.dir_var = StringVar()
        self.dir_combo = ttk.Combobox(self, textvariable=self.dir_var)
        self.check_folder()
        self.dir_combo.bind("<<ComboboxSelected>>")
        self.dir_combo.grid(row=4, column=1, padx=5, pady=5, sticky="ew")

    def bug(self):
        print(self.dir_var.get())

    def check_folder(self):
        lt = []
        for p in os.listdir("saved"):
            if p[-3:] == "txt":
                lt.append(p)
        self.dir_combo["values"] = lt
        if len(lt) > 0:
            self.dir_combo.current(0)

    def save_as(self):
        if len(self.recording) != 0:
            if os.path.exists("saved/" + self.file_name.get() + ".txt"):
                self.info.set("ERROR: filename already taken")
            else:
                f = open("saved/" + self.file_name.get() + ".txt", "x")
                f.write(str(self.recording))
                self.check_folder()
                self.info.set("Saved as: {0}".format(self.file_name.get() + ".txt"))
        else:
            self.info.set("ERROR: nothing recorded yet")

    def centre_window(self):
        w = 300
        h = 150
        sw = self.big_fungus.winfo_screenwidth()
        sh = self.big_fungus.winfo_screenheight()
        x = sw - w - 8
        y = 0
        self.big_fungus.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def start(self):
        self.record = Record()
        self.record.record_start()
        self.info.set("Recording...")
        self.started = True

    def stop(self):
        if self.started:
            self.recording = self.record.record_stop()
            self.info.set("Recording stopped")
            self.started = False
        else:
            self.info.set("ERROR: nothing to stop")

    def replay(self):
        try:
            r = Replay("saved/" + self.dir_var.get())
            r.start()
            self.info.set("Replaying...")
        except SyntaxError:
            self.info.set("ERROR: wrong file")
        except FileNotFoundError:
            self.info.set("ERROR: file not found")


def main():
    if not os.path.exists("saved"):
        os.makedirs("saved")
    root = Tk()
    root.resizable(width=False, height=False)
    app = GUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
