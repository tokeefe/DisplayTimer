#!/usr/bin/env python
'''
DisplayTimer host application

Captures light level from Arduino Uno
and optionally plots in a [near] real-
time viewer.

:version: 0.1
'''
import os
import sys
import time
import argparse
import serial
import numpy as np
import collections
import matplotlib.pyplot as plt

def main():
	parser = argparse.ArgumentParser(description='Data Collector')
	parser.add_argument('-d', '--block-device', required=True, help='Block device')
	parser.add_argument('-b', '--baud', required=True, type=int, help='Baud rate')
	parser.add_argument('-x', '--x-length', required=True, type=int, help='Length of X axis')
	parser.add_argument('-p', '--plot', action='store_true', help='Plot data in [near] real-time')
	parser.add_argument('-s', '--sampling-rate', action='store_true', help='Display sampling rate')
	parser.add_argument('--y-min', type=int, default=0, help='Minimum y value')
	parser.add_argument('--y-max', type=int, default=1024, help='Maximum y value')
	parser.add_argument('-o', '--output-file', help='Save data to file')
	args = parser.parse_args()
	
	y_lim = [args.y_min, args.y_max]

	## --- expand output file
	if args.output_file:
		args.output_file = os.path.expanduser(args.output_file)

	## --- initialize plot
	if args.plot:
		plt.ion()
		fig = plt.figure(figsize=(10,6), facecolor='white')
		ax = fig.add_subplot(111, axisbg='#000000')
		x = np.arange(args.x_length)
		y = np.zeros(args.x_length)
		line, = plt.plot(x, y, color='#FA2D89')
		plt.grid(color='#FFFFFF')
		plt.ylim(y_lim)
		plt.ylabel('light level', color='0.5')
	
	## --- initialize DAQ
	dev = serial.Serial(port=args.block_device, baudrate=args.baud, timeout=.5)
	dev.nonblocking()
	stack = collections.deque(maxlen=args.x_length)
	daq = DAQ(device=dev, buff=stack, sampling_rate=args.sampling_rate, 
		  outfile=args.output_file)

	## --- create y buffer
	for i in range(args.x_length):
		stack.append(0)

	## --- begin data acquisition thread
	daq.daemon = True
	daq.start()

	## --- plot data
	while 1:
		## --- provoke context switch
		if args.plot:
			line.set_ydata(stack)
			plt.draw()
		## --- instigate context switch
		time.sleep(0)

import sys
import time
import select
import threading

class DAQ(threading.Thread):
	'''
	Data Acquisition thread
	'''
	def __init__(self, device, buff, sampling_rate=False, outfile=None):
		threading.Thread.__init__(self)
		self.buff = buff
		self.device = device
		self.sampling_rate = sampling_rate
		self.outfile = outfile
	
	def run(self):
		## --- open handle on output fiile
		if self.outfile:
			self.outfile = open(self.outfile, 'wb')

		## --- sync with device
		self.handshake()
	
		## --- we want to collect data as fast as possible
		t0 = time.time()
		counter = 1
		while 1:
			## --- if user asks for sampling rate
			if self.sampling_rate:
				if time.time() - t0 >= 1:
					t0 = time.time()
					sys.stdout.write('\rSampling rate = %dHz' % counter)
					sys.stdout.flush()
					counter = 1
				counter += 1
			try:
				## --- read from serial port and store on stack
				readables,_,_ = select.select([self.device], [], [])
				if readables:
					data = self.device.readline()
					level,ms = data.split(",")
					self.buff.appendleft(int(level))

				## --- if user asks for logging
				if self.outfile:
					self.outfile.write(data)
			except ValueError, e:
				print(e)
				pass
	def handshake(self):
		while 1:
			readables,writables,_ = select.select([self.device], [self.device], [])
			if writables:
				self.device.write(chr(255))
			if readables:
				try:
					val = self.device.readline()
					if int(val) == 255:
						print('ACK')
						return True
				except ValueError, e:
					pass
	
if __name__ == '__main__':
	main()
