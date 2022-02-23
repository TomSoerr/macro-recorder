import threading
from time import process_time_ns
from pynput.mouse import Controller as Controller_m
from pynput.keyboard import Controller as Controller_k
import key_dict


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

