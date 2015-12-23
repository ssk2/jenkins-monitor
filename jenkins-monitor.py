#!/usr/bin/python

import Image, ImageDraw, ImageFont
import ast, time, random, sys, urllib
from adafruit.rgbmatrix import Adafruit_RGBmatrix
from collections import namedtuple
from enum import Enum
import Queue
from threading import Thread

JENKINS_URL='http://ma.dcos.ca1.mesosphere.com/service/jenkins/view/Monitor%20View/api/python'
ASSETS_PATH='/home/pi/jenkins-monitor/assets/'
JENKINS_LOGO='jenkins.png'
BAD_IMAGES=['bad/' + s for s in ['awesomeface-angry.png', 'awesomeface-sad.png', 'awesomeface-unhappy.png']]
GOOD_IMAGES=['good/' + s for s in ['awesomeface-chin.jpg', 'awesomeface-crazy.png', 'awesomeface-happy.png', 'awesomeface-sunglasses.jpg', 'awesomeface.jpg']]
NEUTRAL_IMAGES=['neutral/' + s for s in ['awesomeface-anxious.gif', 'awesomeface-eyebrow-raised.jpg', 'awesomeface-pensive.png', 'awesomeface-skeptical.jpg']]
FONT_PATH='/usr/share/fonts/truetype/droid/DroidSansMono.ttf'
FONT_SIZE=10
UPDATE_INTERVAL=5
REDRAW_INTERVAL=0.3
OFFSET_STEP=8
SHUTDOWN_TIME_UTC=3 #7pm in California

class Status(Enum):
    bad = 1,
    good = 2,
    neutral = 3,
    loading = 4

Build = namedtuple('Build', 'name status')

Update = namedtuple('Update', 'status text')

def bootstrap(queue, matrix):
    queue.put(Update(status=Status.loading, text='Loading'))
    draw_screen_thread = Thread(target = update_screen, args = (queue, matrix))
    draw_screen_thread.daemon = True
    draw_screen_thread.start()
    return draw_screen_thread

def update_screen(queue, matrix):
    last_update = Update(0, "")
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    image = None
    text = None
    offset = 31
    while (True):
        matrix.Clear()
        try:
            latest_update = queue.get_nowait()
            if last_update.status != latest_update.status:
                image = get_image(latest_update.status)
            if last_update.text != latest_update.text:
                ((text_width, text_height), text) = get_text(latest_update.text, font)
                offset = 31
            last_update = latest_update
        except Queue.Empty:
            pass
	draw_image(matrix, image, 4, 0)
	draw_image(matrix, text, offset, 24)
	if offset < -text_width:
	    offset = 31
	else:
            offset = offset - OFFSET_STEP
    	time.sleep(REDRAW_INTERVAL)

def draw_image(matrix, image, x, y):
    matrix.SetImage(image.im.id, x, y)

def get_image(status):
    if status is Status.bad:
        filename = random.choice(BAD_IMAGES)
    elif status is Status.good:
        filename = random.choice(GOOD_IMAGES)
    elif status is Status.neutral:
        filename = random.choice(NEUTRAL_IMAGES)
    else:
        filename = JENKINS_LOGO
    image = Image.open(ASSETS_PATH + filename)
    return image.resize((24,24))

def get_text(text, font):
    image = Image.new('1', (1, 1))
    draw = ImageDraw.Draw(image)
    textsize = draw.textsize(text, font=font)
    image = Image.new('1', textsize)
    draw = ImageDraw.Draw(image)
    draw.text((0,-1), text, font=font, fill=255)
    return (textsize, image)

def parse_build_status(job_color):
    if job_color.startswith('blue') or job_color.startswith('notbuilt'):
        return Status.good
    elif job_color.startswith('red'):
        return Status.bad
    else:
        return Status.neutral

def fetch_builds(url):
    current_builds = list()
    try:
        tree = ast.literal_eval(urllib.urlopen(url).read());
        for job in tree["jobs"]:
            build = Build(name=job['name'], status=parse_build_status(job['color']))
            current_builds.append(build)
    except Exception as e:
        print e
        pass
    return current_builds

def update_monitor(builds):
    build_status = Status.good
    text = ''
    for build in builds:
        if build.status is Status.bad:
            if build_status is Status.good:
                build_status = Status.bad
                text = "Failed:"
            text = text + " " + build.name
        elif build.status is Status.neutral:
            if build_status is not Status.neutral:
                build_status = Status.neutral
                text = "Building:"
            text = text + " " + build.name
    print("Updating build status to: " + str(build_status) + " for builds: " + text)
    return Update(build_status, text)

def main():
    matrix = Adafruit_RGBmatrix(32, 1)
    queue = Queue.Queue()
    bootstrap(queue, matrix)
    while time.gmtime().tm_hour != SHUTDOWN_TIME_UTC:
        time.sleep(UPDATE_INTERVAL)
        builds = fetch_builds(JENKINS_URL)
        update = update_monitor(builds)
        queue.put(update)
    matrix.Clear()

if __name__ == "__main__": main()
