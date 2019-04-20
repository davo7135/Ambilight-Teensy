
import mss.tools

import numpy as np

import time

import signal

import serial

COM_PORT = "/dev/ttyACM0"
MONITOR_NUM = 1
PIXEL_DENSITY = 60
TOP_LENGTH = 71.3

running = 1

def signal_handler(sig, frame):
    global running
    print('You pressed Ctrl+C!')
    running = 0


signal.signal(signal.SIGINT, signal_handler)


with mss.mss() as sct:

    mons = sct.monitors

    mon = mons[MONITOR_NUM]

    monitor = {
        "top": 120,  # 100px from the top
        "left": 0,  # 100px from the left
        "width": mon["width"],
        "height": 1,
        "mon": MONITOR_NUM,
    }

    pixels = int((PIXEL_DENSITY/100)*TOP_LENGTH)

    chunk_size = int(mon["width"]/pixels)

    pixel_pos = [int(i*chunk_size+chunk_size) for i in range(pixels)]

    ser = serial.Serial(COM_PORT, 57600, timeout=0, rtscts=1) # , writeTimeout=0
    ser.write(bytes("@"+chr(pixels)+"$", "UTF-8"))

    bytes_arr = bytearray(pixels * 3)

    loops = 0
    stime = time.time()

    while running:

        time.sleep(.03)

        sct_img = sct.grab(monitor)
        sct_arr = np.array(sct_img)[:,:,:3]

        pixel_data = sct_arr[:,pixel_pos,:]
        pixel_data = np.uint8(pixel_data.reshape(-1, 3))

        bytes_arr_len = 0

        for p in pixel_data:

            avg_rgb = np.average(p)
            if avg_rgb > 245:
                p = p / 3

            p[0] *= 0.35
            p[1] *= 0.6
            p[2] *= 1.0

            bytes_arr[bytes_arr_len+0] = int(p[2])
            bytes_arr[bytes_arr_len+1] = int(p[1])
            bytes_arr[bytes_arr_len+2] = int(p[0])
            bytes_arr_len += 3

        ser.write(bytes_arr)

        loops += 1

    etime = time.time()
    dtime = etime - stime
    fps = loops/dtime

    print("Ran for: {0} with an average fps: {1}".format(dtime, fps))

    ser.close()


