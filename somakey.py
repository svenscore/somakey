#!/usr/bin/env python3

import getpass
import os
import platform
import re
import shutil
import subprocess
import threading
import time

from datetime import datetime
from threading import Thread

from stream_data import stream_data
from prompt_toolkit import Application
from prompt_toolkit.application import get_app
from prompt_toolkit.formatted_text import ANSI, FormattedText
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import VSplit, Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.styles import Style
from prompt_toolkit.widgets import Frame, TextArea, Dialog, Label

import keyboard

# change to possible mount paths for os
data_paths = [
	'/media/' + getpass.getuser() + '/CIRCUITPY/img/',
	'/Volumes/CIRCUITPY/img/'
]

# preferred stream player
player_bin = 'mpv'

# preferred stream player options
player_cmd = [player_bin, '--display-tags=icy-title', '--quiet']

# border of ui
color_border = '#FFFFFF'

# find logo locations, assuming one circuitpy mounted at a time
for d in data_paths:
	if os.path.isdir(d):
		data_path = d

# override autodiscovered path
# data_path = "/media/user/CIRCUITPY/img/"

# location of first logo
soma_fm = data_path + 'somafm.jpg'

columns, rows = shutil.get_terminal_size()
catimg_res = str(int(columns - 6))
ansi_width = int((int(catimg_res)/ 2) + 2)

# import all image graphics
catimg_cmd = ["catimg", "-H", catimg_res, soma_fm]
catimg_somafm = subprocess.run(catimg_cmd, capture_output=True, text=True)
img_somafm = catimg_somafm.stdout.strip()
remove_extra = re.compile(r'25l|25h|\n')

for i in stream_data:
	stream_data[i]['image'] = data_path + stream_data[i]['image']
	catimg_cmd = ["catimg", "-w", catimg_res, stream_data[i]['image']]
	catimg_out = subprocess.run(catimg_cmd, capture_output=True, text=True)
	cleaned_output = remove_extra.sub('', catimg_out.stdout.strip())
	stream_data[i]['catimg'] = cleaned_output
# END: import all image graphics

tracks_title = f"[{stream_data['stream_1']['name']}] [{stream_data['stream_2']['name']}] [{stream_data['stream_3']['name']}] [{stream_data['stream_4']['name']}]"
default_title = "stopped. press neokey corresponding to above stations to begin playing"
current_title = default_title

# ANSi codes to hide and display cursor
def cursor_hide():
	print('\033[?25l', end='')

def cursor_show():
	print('\033[?25h', end='')

# setup the correct neokey mappings in linux
if platform.system() == 'Linux':
	subprocess.run("xmodmap -e 'keycode 194 = F16' -e 'keycode 195 = F17' -e 'keycode 196 = F18' -e 'keycode 197 = F19'", shell=True)

def kill_stream():
	subprocess.run(["pkill", "-f", player_bin])

def play_stream(stream_url, title_color):
	global current_title
	kill_stream()
	time.sleep(1)

	player_cmd_with_url = player_cmd + [stream_url]

	process = subprocess.Popen(player_cmd_with_url, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

	def process_output():
		global current_title
		while True:
			line = process.stdout.readline()
			if 'icy-title:' in line:
				title = line.split('icy-title:', 1)[1].strip()
				current_title = current_title + datetime.now().strftime("%H:%M") + ' ' + title + '\n'

				# ensure title only stores number of played songs equal to the space it has available
				if current_title.count('\n') > int(rows - 2):
					current_title = re.sub(r'^.*?\n', '', current_title, 1)

				update_now_playing(current_title, title_color)
				get_app().invalidate()
				cursor_hide()
			elif line == '' and process.poll() is not None:
				break

	threading.Thread(target=process_output, daemon=True).start()

def on_fkey(event, stream):
	global current_title
	current_title = ''
	update_ansi_area(stream_data[stream]['catimg'])
	cursor_hide()
	play_stream(stream_data[stream]['url'], stream_data[stream]['text_color'])

def on_f19(event):
	update_ansi_area(stream_data['stream_4']['catimg'])
	current_title = default_title
	update_text_area(current_title)
	cursor_hide()
	kill_stream()

def update_ansi_area(new_art):
	new_label = Label(ANSI(new_art))
	ansi_frame.body = new_label

def update_text_area(new_text):
	formatted_text = FormattedText([
		('fg:white bold', new_text)
	])
	text_label.text = formatted_text

def update_now_playing(title, title_color='#FFFFFF'):
	title = title.rstrip('\n')
	f_color = f'fg:{title_color}' # optionally add ' bold' to end
	formatted_text = FormattedText([
		(f_color, title)
	])
	text_label.text = formatted_text

def exit_app(event):
	kill_stream()
	event.app.exit()
	cursor_show()

# ansi frame
ansi_area = Label(ANSI(stream_data['stream_4']['catimg']))
initial_ansi_label = Label(ANSI(stream_data['stream_4']['catimg']))

frame_width = Dimension.exact(ansi_width)
ansi_frame = Frame(initial_ansi_label, title="station", width=frame_width, style=color_border)
formatted_text = FormattedText([
	('fg:white bold', current_title)
])

# text frame
text_label = Label(formatted_text)
frame_height = Dimension.exact(int(ansi_width - 2))
text_frame = Frame(text_label, title=tracks_title, height=frame_height, style=color_border)

root_container = VSplit([
  ansi_frame,
  text_frame
])

layout = Layout(root_container)

key_bindings = KeyBindings()

key_bindings.add('f16')(lambda event: on_fkey(event, 'stream_1'))
key_bindings.add('f17')(lambda event: on_fkey(event, 'stream_2'))
key_bindings.add('f18')(lambda event: on_fkey(event, 'stream_3'))
key_bindings.add('f19')(on_f19)
key_bindings.add('c-c')(exit_app)

app = Application(layout=layout, full_screen=True, key_bindings=key_bindings)

current_title = ''

# hide cursor
cursor_hide()

app.run()
