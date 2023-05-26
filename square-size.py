
import os, sys, time, traceback
from math import hypot

import numpy as np
import cv2

import frame_capture
import frame_draw
from subprocess import call


def square_rejected():
    call(["python", "square_rejected.py"])


def square_accepted():
    call(["python", "square_accepted.py"])


# camera values
camera_id = 0
camera_width = 1920
camera_height = 1080
camera_frame_rate = 30
camera_fourcc = cv2.VideoWriter_fourcc(*"MJPG")

auto_percent = 0.2
auto_threshold = 127
auto_blur = 5

norm_alpha = 0
norm_beta = 255

configfile = 'camruler_config.csv'
if os.path.isfile(configfile):
    with open(configfile) as f:
        for line in f:
            line = line.strip()
            if line and line[0] != '#' and (',' in line or '=' in line):
                if ',' in line:
                    item, value = [x.strip() for x in line.split(',', 1)]
                elif '=' in line:
                    item, value = [x.strip() for x in line.split('=', 1)]
                else:
                    continue
                if item in 'camera_id camera_width camera_height camera_frame_rate camera_fourcc auto_percent auto_threshold auto_blur norm_alpha norm_beta'.split():
                    try:
                        exec(f'{item}={value}')
                        print('CONFIG:', (item, value))
                    except:
                        print('CONFIG ERROR:', (item, value))


if len(sys.argv) > 1:
    camera_id = sys.argv[1]
    if camera_id.isdigit():
        camera_id = int(camera_id)

camera = frame_capture.Camera_Thread()
camera.camera_source = camera_id  # SET THE CORRECT CAMERA NUMBER
camera.camera_width = camera_width
camera.camera_height = camera_height
camera.camera_frame_rate = camera_frame_rate
camera.camera_fourcc = camera_fourcc

camera.start()

width = camera.camera_width
height = camera.camera_height
area = width * height
cx = int(width / 2)
cy = int(height / 2)
dm = hypot(cx, cy)  # max pixel distance
frate = camera.camera_frame_rate
print('CAMERA:', [camera.camera_source, width, height, area, frate])


draw = frame_draw.DRAW()
draw.width = width
draw.height = height
unit_suffix = 'mm'
pixel_base = 10
cal_range = 63
cal = dict([(x, cal_range / dm) for x in range(0, int(dm) + 1, pixel_base)])
cal_base = 5
cal_last = None


def cal_update(x, y, unit_distance):

    pixel_distance = hypot(x, y)
    scale = abs(unit_distance / pixel_distance)
    target = baseround(abs(pixel_distance), pixel_base)

    low = target * scale - (cal_base / 2)
    high = target * scale + (cal_base / 2)

    # get low start point in pixels
    start = target
    if unit_distance <= cal_base:
        start = 0
    else:
        while start * scale > low:
            start -= pixel_base

    # get high stop point in pixels
    stop = target
    if unit_distance >= baseround(cal_range, pixel_base):
        high = max(cal.keys())
    else:
        while stop * scale < high:
            stop += pixel_base

    # set scale
    for x in range(start, stop + 1, pixel_base):
        cal[x] = scale
        print(f'CAL: {x} {scale}')


# read local calibration data
calfile = 'camruler_cal.csv'
if os.path.isfile(calfile):
    with open(calfile) as f:
        for line in f:
            line = line.strip()
            if line and line[0] in ('d',):
                axis, pixels, scale = [_.strip() for _ in line.split(',', 2)]
                if axis == 'd':
                    print(f'LOAD: {pixels} {scale}')
                    cal[int(pixels)] = float(scale)


def conv(x, y):
    d = distance(0, 0, x, y)

    scale = cal[baseround(d, pixel_base)]

    return x * scale, y * scale


def baseround(x, base=1):
    return int(base * round(float(x) / base))


def distance(x1, y1, x2, y2):
    return hypot(x1 - x2, y1 - y2)


framename = "CamRuler"
cv2.namedWindow(framename, flags=cv2.WINDOW_NORMAL | cv2.WINDOW_GUI_NORMAL)


key_last = 0
key_flags = {'config': False,  # c key
             'auto': False,  # a key
             'thresh': False,  # t key
             'percent': False,  # p key
             'norms': False,  # n key
             'rotate': False,  # r key
             'lock': False,  #
             }


def key_flags_clear():
    global key_flags

    for key in list(key_flags.keys()):
        if key not in ('rotate',):
            key_flags[key] = False


def key_event(key):
    global key_last
    global key_flags
    global mouse_mark
    global cal_last


    if key == 99:
        if key_flags['config']:
            key_flags['config'] = False
        else:
            key_flags_clear()
            key_flags['config'] = True
            cal_last, mouse_mark = 0, None


    elif key == 110:
        if key_flags['norms']:
            key_flags['norms'] = False
        else:
            key_flags['thresh'] = False
            key_flags['percent'] = False
            key_flags['lock'] = False
            key_flags['norms'] = True
            mouse_mark = None


    elif key == 114:
        if key_flags['rotate']:
            key_flags['rotate'] = False
        else:
            key_flags['rotate'] = True


    elif key == 97:
        if key_flags['auto']:
            key_flags['auto'] = False
        else:
            key_flags_clear()
            key_flags['auto'] = True
            mouse_mark = None


    elif key == 112 and key_flags['auto']:
        key_flags['percent'] = not key_flags['percent']
        key_flags['thresh'] = False
        key_flags['lock'] = False


    elif key == 116 and key_flags['auto']:
        key_flags['thresh'] = not key_flags['thresh']
        key_flags['percent'] = False
        key_flags['lock'] = False


    print('key:', [key, chr(key)])
    key_last = key


mouse_raw = (0, 0)
mouse_now = (0, 0)
mouse_mark = None


# mouse callback
def mouse_event(event, x, y, flags, parameters):

    global mouse_raw
    global mouse_now
    global mouse_mark
    global key_last
    global auto_percent
    global auto_threshold
    global auto_blur
    global norm_alpha
    global norm_beta

    # update percent
    if key_flags['percent']:
        auto_percent = 5 * (x / width) * (y / height)

    # update threshold
    elif key_flags['thresh']:
        auto_threshold = int(255 * x / width)
        auto_blur = int(20 * y / height) | 1  # insure it is odd and at least 1

    # update normalization
    elif key_flags['norms']:
        norm_alpha = int(64 * x / width)
        norm_beta = min(255, int(128 + (128 * y / height)))

    # update mouse location
    mouse_raw = (x, y)

    # offset from center
    # invert y to standard quadrants
    ox = x - cx
    oy = (y - cy) * -1

    # update mouse location
    mouse_raw = (x, y)
    if not key_flags['lock']:
        mouse_now = (ox, oy)

    # left click event
    if event == 1:

        if key_flags['config']:
            key_flags['lock'] = False
            mouse_mark = (ox, oy)

        elif key_flags['auto']:
            key_flags['lock'] = False
            mouse_mark = (ox, oy)

        if key_flags['percent']:
            key_flags['percent'] = False
            mouse_mark = (ox, oy)

        elif key_flags['thresh']:
            key_flags['thresh'] = False
            mouse_mark = (ox, oy)

        elif key_flags['norms']:
            key_flags['norms'] = False
            mouse_mark = (ox, oy)

        elif not key_flags['lock']:
            if mouse_mark:
                key_flags['lock'] = True
            else:
                mouse_mark = (ox, oy)
        else:
            key_flags['lock'] = False
            mouse_now = (ox, oy)
            mouse_mark = (ox, oy)

        key_last = 0

    # right click event
    elif event == 2:
        key_flags_clear()
        mouse_mark = None
        key_last = 0


# register mouse callback
cv2.setMouseCallback(framename, mouse_event)

# -------------------------------
# main loop
# -------------------------------

# loop
while 1:

    # get frame
    frame0 = camera.next(wait=1)
    if frame0 is None:
        time.sleep(0.1)
        continue

    # normalize
    cv2.normalize(frame0, frame0, norm_alpha, norm_beta, cv2.NORM_MINMAX)

    # rotate 180
    if key_flags['rotate']:
        frame0 = cv2.rotate(frame0, cv2.ROTATE_180)

    text = []


    fps = camera.current_frame_rate

    if key_flags['norms']:
        # print
        text.append('')
        text.append(f'NORMILIZE MODE')
        text.append(f'ALPHA (min): {norm_alpha}')
        text.append(f'BETA (max): {norm_beta}')

    if key_flags['config']:


        draw.crosshairs(frame0, 5, weight=2, color='red', invert=True)


        draw.line(frame0, cx, cy, cx + cx, cy + cy, weight=1, color='red')
        draw.line(frame0, cx, cy, cx + cy, cy - cx, weight=1, color='red')
        draw.line(frame0, cx, cy, -cx + cx, -cy + cy, weight=1, color='red')
        draw.line(frame0, cx, cy, cx - cy, cy + cx, weight=1, color='red')


        mx, my = mouse_raw
        draw.line(frame0, mx, my, mx + dm, my + (dm * (cy / cx)), weight=1, color='green')
        draw.line(frame0, mx, my, mx - dm, my - (dm * (cy / cx)), weight=1, color='green')
        draw.line(frame0, mx, my, mx + dm, my + (dm * (-cx / cy)), weight=1, color='green')
        draw.line(frame0, mx, my, mx - dm, my - (dm * (-cx / cy)), weight=1, color='green')


        text.append('')
        text.append(f'CONFIG MODE')


        if not cal_last:
            cal_last = cal_base
            caltext = f'CONFIG: Click on D = {cal_last}'


        elif cal_last <= cal_range:
            if mouse_mark:
                cal_update(*mouse_mark, cal_last)
                cal_last += cal_base
            caltext = f'CONFIG: Click on D = {cal_last}'


        else:
            key_flags_clear()
            cal_last == None
            with open(calfile, 'w') as f:
                data = list(cal.items())
                data.sort()
                for key, value in data:
                    f.write(f'd,{key},{value}\n')
                f.close()
            caltext = f'CONFIG: Complete.'


        draw.add_text(frame0, caltext, (cx) + 100, (cy) + 30, color='red')


        mouse_mark = None

    elif key_flags['auto']:

        mouse_mark = None

        text.append(f'UNITS: {unit_suffix}')
        text.append(f'MIN PERCENT: {auto_percent:.2f}')
        text.append(f'THRESHOLD: {auto_threshold}')



        frame1 = cv2.cvtColor(frame0, cv2.COLOR_BGR2GRAY)


        frame1 = cv2.GaussianBlur(frame1, (auto_blur, auto_blur), 0)


        frame1 = cv2.threshold(frame1, auto_threshold, 255, cv2.THRESH_BINARY)[1]


        frame1 = ~frame1


        contours, nada = cv2.findContours(frame1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


        draw.crosshairs(frame0, 5, weight=2, color='green')


        for c in contours:


            x1, y1, w, h = cv2.boundingRect(c)
            x2, y2 = x1 + w, y1 + h
            x3, y3 = x1 + (w / 2), y1 + (h / 2)


            percent = 100 * w * h / area


            if percent < auto_percent:
                continue

            # if the contour is too large, ignore it
            elif percent > 60:
                continue

            # convert to center, then distance
            x1c, y1c = conv(x1 - (cx), y1 - (cy))
            x2c, y2c = conv(x2 - (cx), y2 - (cy))
            xlen = abs(x1c - x2c)
            ylen = abs(y1c - y2c)
            alen = 0
            if max(xlen, ylen) > 0 and min(xlen, ylen) / max(xlen, ylen) >= 0.95:
                alen = (xlen + ylen) / 2
            carea = xlen * ylen

            # if (xlen<56 and xlen>53 and ylen>53 and ylen<56):
            #     draw.add_text(frame0, f'Accept', x3 +10,  y2-40, center=True, color='green')
            #     draw.rect(frame0, x1, y1, x2, y2, weight=2, color='green')
            if(xlen<54 and xlen>49 and ylen>49 and ylen<54):
                draw.add_text(frame0, f'Accept', x3 +10,  y2-40, center=True, color='green')
                draw.rect(frame0, x1, y1, x2, y2, weight=2, color='green')
                square_accepted()
            # elif (xlen<45 and xlen>39 and ylen>39 and ylen<45):
            #     draw.add_text(frame0, f'Accept', x3 +10,  y2-40, center=True, color='green')
            #     draw.rect(frame0, x1, y1, x2, y2, weight=2, color='green')
            else:
                draw.add_text(frame0, f'Reject', x3 + 15,  y2-50, center=True, color='red')
                draw.rect(frame0, x1, y1, x2, y2, weight=2, color='red')
                square_rejected()
            # plot


            # add dimensions
            draw.add_text(frame0, f'{xlen:.2f}', x1 - ((x1 - x2) / 2), min(y1, y2) - 8, center=True, color='red')
            draw.add_text(frame0, f'Area: {carea:.2f}', x3, y2 + 8, center=True, top=True, color='red')
            if alen:
                draw.add_text(frame0, f'Avg: {alen:.2f}', x3, y2 + 34, center=True, top=True, color='green')
            if x1 < width - x2:
                draw.add_text(frame0, f'{ylen:.2f}', x2 + 4, (y1 + y2) / 2, middle=True, color='red')
            else:
                draw.add_text(frame0, f'{ylen:.2f}', x1 - 4, (y1 + y2) / 2, middle=True, right=True, color='red')


    else:

        # small crosshairs
        draw.crosshairs(frame0, 5, weight=2, color='green')

        # mouse cursor lines
        draw.vline(frame0, mouse_raw[0], weight=1, color='green')
        draw.hline(frame0, mouse_raw[1], weight=1, color='green')

        # draw
        if mouse_mark:

            # locations
            x1, y1 = mouse_mark
            x2, y2 = mouse_now

            # convert to distance
            x1c, y1c = conv(x1, y1)
            x2c, y2c = conv(x2, y2)
            xlen = abs(x1c - x2c)
            ylen = abs(y1c - y2c)
            llen = hypot(xlen, ylen)
            alen = 0
            if max(xlen, ylen) > 0 and min(xlen, ylen) / max(xlen, ylen) >= 0.95:
                alen = (xlen + ylen) / 2
            carea = xlen * ylen

            # print distances
            text.append('')
            text.append(f'X LEN: {xlen:.2f}{unit_suffix}')
            text.append(f'Y LEN: {ylen:.2f}{unit_suffix}')
            text.append(f'L LEN: {llen:.2f}{unit_suffix}')

            # convert to plot locations
            x1 += cx
            x2 += cx
            y1 *= -1
            y2 *= -1
            y1 += cy
            y2 += cy
            x3 = x1 + ((x2 - x1) / 2)
            y3 = max(y1, y2)

            # line weight
            weight = 1
            if key_flags['lock']:
                weight = 2


            # plot
            draw.rect(frame0, x1, y1, x2, y2, weight=weight, color='red')
            draw.line(frame0, x1, y1, x2, y2, weight=weight, color='green')

            # add dimensions
            draw.add_text(frame0, f'{xlen:.3f}', x1 - ((x1 - x2) / 2), min(y1, y2) - 8, center=True, color='red')
            draw.add_text(frame0, f'Area: {carea:.2f}', x3, y3 + 8, center=True, top=True, color='red')
            if alen:
                draw.add_text(frame0, f'Avg: {alen:.2f}', x3, y3 + 34, center=True, top=True, color='green')
            if x2 <= x1:
                draw.add_text(frame0, f'{ylen:.2f}', x1 + 4, (y1 + y2) / 2, middle=True, color='red')
                draw.add_text(frame0, f'{llen:.2f}', x2 - 4, y2 - 4, right=True, color='green')
            else:
                draw.add_text(frame0, f'{ylen:.2f}', x1 - 4, (y1 + y2) / 2, middle=True, right=True, color='red')
                draw.add_text(frame0, f'{llen:.2f}', x2 + 8, y2 - 4, color='green')

    draw.add_text_top_left(frame0, text)

    cv2.imshow(framename, frame0)

    key = cv2.waitKey(1) & 0xFF

    if key in (27, 113):
        break
    elif key not in (-1, 255):
        key_event(key)

camera.stop()

cv2.destroyAllWindows()

exit()

