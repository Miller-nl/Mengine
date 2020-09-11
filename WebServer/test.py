import threading

import time
import queue

lock = threading.RLock()
event = threading.Event()
event.clear()
Q = queue.Queue()



def get():
    while True:
        print(Q.get())

    return


t1 = threading.Thread(target=get, args=())
t1.start()


