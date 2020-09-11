import socketserver
import queue


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

class QueueReplenisher:
    def __init__(self, requests_queue: queue.Queue):
        self._requests_queue = requests_queue

    def handle(self):
        self._requests_queue.put(self.request)
        return