from flask import Flask, render_template, Response,render_template_string
import pyautogui
import cv2
import numpy as np
import subprocess
import time

app = Flask(__name__)

@app.route('/')
def index():
    tmp  = open("./index.html").read()
    return render_template_string(tmp)


@app.route('/video_feed')
def video_feed():
    while 1:
        image = pyautogui.screenshot()
        image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        ret, jpeg = cv2.imencode('.jpg', image)
        return Response(b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n',
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def video_pyautogui():
    while True:
        frame = pyautogui.screenshot()
        frame = cv2.cvtColor(np.array(frame), cv2.COLOR_RGB2BGR)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

w,h = 1920,1080

def video_ffmpeg():
    """Generator to read frames from ffmpeg subprocess"""
    cmd = [
        'ffmpeg',
        '-video_size', '1920x1080',  # Specify the video size directly
        '-framerate', '20',
        '-f', 'x11grab',  # Use x11grab for screen capture on Linux
        '-i', ':0.0',  # Display index; use ':0.0' for the primary display
        '-vf', 'scale=1920:1080',  # Video filter for scaling
        '-f', 'rawvideo',
        'pipe:1'
    ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        frame = proc.stdout.read(w*h*4)
        # yield np.frombuffer(frame, dtype=np.uint8).reshape((h,w,4))
        frame = np.frombuffer(frame, dtype=np.uint8).reshape((h,w,4))
        ret, jpeg = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        


@app.route('/video_feed2')
def video_feed2():
    return Response(video_ffmpeg(), mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    PORT = 8000
    app.run(port=PORT, debug=True)

