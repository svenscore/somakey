import board
import busio
import time
import usb_hid
import neopixel

from adafruit_neokey.neokey1x4 import NeoKey1x4
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode

from stream_data import stream_data

i2c_bus = busio.I2C(board.SCL1, board.SDA1)
neokey = NeoKey1x4(i2c_bus, addr=0x30)
keyboard = Keyboard(usb_hid.devices)

pixels = neopixel.NeoPixel(board.NEOPIXEL, 4)
NUM_PIXELS = 4
BRIGHTNESS = 0.6
FADE_DELAY = 0.02

print("somakey")

key_0_state = False
key_1_state = False
key_2_state = False
key_3_state = False

def neo_reset():
	neokey.pixels[0] = 0x0
	neokey.pixels[1] = 0x0
	neokey.pixels[2] = 0x0
	neokey.pixels[3] = 0x0

while True:
	if not neokey[0] and key_0_state:
		key_0_state = False
	if not neokey[1] and key_1_state:
		key_1_state = False
	if not neokey[2] and key_2_state:
		key_2_state = False
	if not neokey[3] and key_3_state:
		key_3_state = False

	if neokey[0] and not key_0_state:
		neo_reset()
		print("key 1")
		neokey.pixels[0] = stream_data['stream_1']['color']
		pixels.fill(stream_data['stream_1']['color'])
		pixels.show()
		keyboard.send(Keycode.F16)
		time.sleep(.2)
		key_0_state = True

	if neokey[1] and not key_1_state:
		neo_reset()
		print("key 2")
		neokey.pixels[1] = stream_data['stream_2']['color']
		pixels.fill(stream_data['stream_2']['color'])
		pixels.show()
		keyboard.send(Keycode.F17)
		time.sleep(.2)
		key_1_state = True

	if neokey[2] and not key_2_state:
		neo_reset()
		print("key 3")
		neokey.pixels[2] = stream_data['stream_3']['color']
		pixels.fill(stream_data['stream_3']['color'])
		pixels.show()
		keyboard.send(Keycode.F18)
		time.sleep(.2)
		key_2_state = True

	if neokey[3] and not key_3_state:
		neo_reset()
		print("key 4")
		neokey.pixels[3] = stream_data['stream_4']['color']
		pixels.fill(stream_data['stream_4']['color'])
		pixels.show()
		keyboard.send(Keycode.F19)
		time.sleep(.2)
		key_3_state = True
