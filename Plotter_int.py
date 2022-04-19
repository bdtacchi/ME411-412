#!/usr/bin/env python3
import serial
import matplotlib.pyplot as plt
import numpy as np
import sys
import time



arduino_port = "/dev/cu.usbmodem47110001"
baud = 115200;
samples = 40000 #how many samples to collect
print_labels = False
line = 0 #start at 0 because our header is 0 (not real data)

ser = serial.Serial(arduino_port, baud)
print ("Connected to Arduino port: " + arduino_port) 
print("Created file")

ser.setDTR(False)
time.sleep(1)
# toss any data already received, see
# http://pyserial.sourceforge.net/pyserial_api.html#serial.Serial.flushInput
ser.flushInput()
ser.setDTR(True)

channels_str = str(ser.readline())[0:][2:-5]

print(channels_str)

channels = int(channels_str)

line = 0
spec_data = np.zeros([samples, channels+1])

points = np.linspace(340, 850, num=channels)

plt.plot(points, spec_data[0,:-1])

t = 0

color = 'Violet'    

color_array = ['Violet', 'Blue', 'Cyan', 'Green', 'Yellow', 'Orange', 'Red']

color_num = 0

getData=str(ser.readline())
spec_line_str = getData[0:][2:-4]
print(spec_line_str)

def nextColor(color_num):
	color_num = color_num + 1
	if color_num > 6:
		color_num = 0
	return color_num

plt.title(color)

change_array = list(range(1, channels+1))

# initial_time = timer.perf_counter()

while line < samples:
	getData=str(ser.readline())
	spec_line_str = getData[0:][2:-4]
	spec_line_data = []
	
	data_dummy = '0'
	
#	for i in spec_line_str:
#		if i == ',':
#			spec_line_data.append(int(data_dummy))
#			data_dummy = ''
#		else:
#			if i == '':
#				i = '0'
#			data_dummy = data_dummy + i
	
	spec_line_str_list = spec_line_str.split(',')
	
	for i in spec_line_str_list[:-1]:
		if i == '':
			i = '0'
		spec_line_data.append(int(i))
		
	integral = float(spec_line_str_list[-1])
	print(integral)
		
#	spec_line_data.append(int(data_dummy))
	
	if len(spec_line_data) < channels:
		for i in range(channels - len(spec_line_data)):
			spec_line_data.append(0) 
			
	if len(spec_line_data) > channels:
		spec_line_data = spec_line_data[0:channels]
	
	if spec_line_data == change_array:
		color_num = nextColor(color_num)
		color = color_array[color_num]
		plt.title(color)
		
	
	spec_data[line,:-1] = spec_line_data
	spec_data[line, -1] = integral
	
	plt.gca().lines[0].set_ydata(spec_line_data)
	plt.gca().relim() 
	plt.gca().autoscale_view()
	plt.pause(0.05);
	
	line = line + 1
	
	if (line % 50) == 0:
		print(line)
	
	
filename = 'data_' + str(channels) + '.csv'

np.savetxt(filename, spec_data, delimiter=',')
	
	
print("Data collection complete!")