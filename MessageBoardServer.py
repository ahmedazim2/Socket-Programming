import time
from socketserver import BaseRequestHandler, ThreadingTCPServer
import datetime as dt
from collections import OrderedDict

SENDING_COOLDOWN = 0.3
BUFFER_SIZE = 4096

class EchoHandler(BaseRequestHandler):
    ok_str = 'OK' # Response string for success

    def __init__(self, *args, **kwargs):
        #Intialize instance variables 
        self.content = ""
        self.content_idx = 0
        self.contents = OrderedDict()
        super().__init__(*args, **kwargs)

    def send_str(self, string):
        # Sending string to client
        self.request.send(bytes(string, encoding='utf-8'))
        time.sleep(SENDING_COOLDOWN)

    def recv_str(self):
        # Receiving string from client
        post_msg = self.request.recv(BUFFER_SIZE)
        return str(post_msg, encoding='utf-8')

    def handle_post(self):
        # Handling the post command
        in_post = True
        while in_post:
            post_msg_str = self.recv_str().strip()
            if post_msg_str == "#":
                in_post = False
                self.send_str(self.ok_str)
            else:
                print(f"Added: {post_msg_str}")
                self.content += "\n" + post_msg_str
        self.contents[str(self.content_idx).zfill(4)] = {
            "content": self.content.strip(),
            "datetime": dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        }
        self.content_idx += 1
        self.content = ""

    def handle_get(self):
        # Handling the get command

        self.send_str('Happy Socket Programming')
        for key in self.contents:
            content = self.contents[key]["content"]
            datetime = self.contents[key]["datetime"]
            self.send_str(f"MESSAGE ID: {key}, RECEIVED DATETIME: {datetime}")
            for line in content.strip().split("\n"):
                if line:
                    self.send_str(f"{line}")
        self.send_str('#')

    def handle_delete(self):
        # Handling the delete command

        ids = []
        in_delete = True
        while in_delete:
            delete_msg_str = self.recv_str().strip()
            if delete_msg_str == "#":
                in_delete = False
            else:
                print(f"Message ID for deletion: {delete_msg_str}")
                ids.append(delete_msg_str)
        # For checking if all IDs are valid
        fail_deletion = False
        for id in ids:
            if id not in self.contents:
                fail_deletion = True
                break
        if fail_deletion:
            self.send_str("ERROR - Wrong ID")
        else:
            # To delete all messages with the given files
            for id in ids:
                del self.contents[id]
            self.send_str(self.ok_str)

    def handle(self):
        # Handle client connections
        print('Got connection from', self.client_address)
        while True:
            msg = ""
            try:
                msg = self.recv_str()
            except Exception as e:
                print("Disconnected from", self.client_address, "due to", e)
                break
            if not msg:
                break
            msg_str = msg.strip().upper()
            print('Message string is:', msg_str)

            if msg_str not in ['POST', 'GET', 'QUIT', 'DELETE']:
                self.send_str('ERROR - Command not understood')
            else:
                command = msg_str
                print('Command is: ', command)
                if command == 'POST':
                    self.handle_post()
                elif command == 'GET':
                    self.handle_get()
                elif command == 'DELETE':
                    self.handle_delete()
                elif command == 'QUIT':
                    self.send_str(self.ok_str)
                    break

if __name__ == '__main__':
    # Starting server
    serv = ThreadingTCPServer(('0.0.0.0', 16111), EchoHandler)
    print("Listening...")
    serv.serve_forever()