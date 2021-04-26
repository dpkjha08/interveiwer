from flask import Flask, render_template, Response, request, url_for, jsonify
from camera import VideoCamera
import socket,struct, pickle,json
from cv2 import cv2
#######################
# import sys,os
# import operator
# from tensorflow.keras.models import model_from_json
# import numpy as np 

app = Flask(__name__,static_url_path='/static')

client_address = "192.168.0.106"

@app.route('/',methods = ['POST', 'GET'])
def index():
    return  render_template('index.html')


def clientSide():
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    global client_address
    print("client-1",client_address)
    host_ip = str(client_address) # paste your server ip address here
    port = 9999
    client_socket.connect((host_ip,port)) # a tuple
    data = b""
    payload_size = struct.calcsize("Q")
    while True:
        while len(data) < payload_size:
            packet = client_socket.recv(4*1024) # 4K
            if not packet: break
            data+=packet
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("Q",packed_msg_size)[0]
        
        while len(data) < msg_size:
            data += client_socket.recv(4*1024)
        frame_data = data[:msg_size]
        data  = data[msg_size:]
        frame = pickle.loads(frame_data)
        ret,jpeg = cv2.imencode('.jpg',frame)
        frame = jpeg.tobytes()

        yield(b'--frame\r\n'
                                b'Content-Type: image/jpeg\r\n\n'+frame+b'\r\n\r\n')


@app.route('/client_video',methods = ['POST', 'GET'])
def client_video():
    print("Deepak Jha -1")
    return Response(clientSide(),mimetype='multipart/x-mixed-replace; boundary=frame')

def serverSide():
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    host_name  = socket.gethostname()
    host_ip = socket.gethostbyname(host_name)
    print('HOST IP:',host_ip)
    port = 9999
    socket_address = (host_ip,port)
    server_socket.bind((host_ip,port))
    server_socket.listen(5)
    print("LISTENING AT:",socket_address)
    while True:
            client_socket,addr = server_socket.accept()
            print('GOT CONNECTION FROM:',addr)
            if client_socket:
                cap = cv2.VideoCapture(0)
                xd = {"0":0,"1":0,"2":0,"3":0,"4":0,"5":0,"6":0,"7":0,"8":0,"9":0}
                count = 0
                while(cap.isOpened()):
                    _, frame = cap.read()
                    frame = cv2.flip(frame, 1)
                    a = pickle.dumps(frame)
                    message = struct.pack("Q",len(a))+a
                    client_socket.sendall(message)
                    ret,jpeg = cv2.imencode('.jpg',frame)
                    frame = jpeg.tobytes()

                    yield(b'--frame\r\n'
                                b'Content-Type: image/jpeg\r\n\n'+frame+b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(serverSide(),mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__=="__main__":
    # client_socket.close()
    app.run(debug=True,port=3000)