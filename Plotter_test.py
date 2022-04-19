#!/usr/bin/env python3
import serial
import matplotlib.pyplot as plt
import numpy as np
import sys
import time

print(len(sys.argv))
print(sys.argv[0])
if len(sys.argv) == 1:
	arduino_port = "/dev/cu.usbmodem47110001"
else:
	arduino_port = sys.argv[1]
baud = 115200;
samples = 4000 #how many samples to collect
line = 0 #start at 0 because our header is 0 (not real data)

ser = serial.Serial(arduino_port, baud)
print ("Connected to Arduino port: " + arduino_port) 
print("Created file")

initialString=str(ser.readline())[0:][2:-3]

print(initialString)

initialStringList = initialString.split(sep=',')
channels = int(initialStringList[-1])
print(channels)

color_array = ['Violet', 'Blue', 'Cyan', 'Green', 'Yellow', 'Orange', 'Red', 'Off']
colorNum = int(initialStringList[-2])
colorHolder = colorNum
print(color_array[colorNum])

initialTime = int(initialStringList[-3])
print(initialTime)

time.sleep(5)

line = 0
spec_data = np.zeros([samples, channels+1])

points = np.linspace(340, 850, num=channels)

plt.plot(points, spec_data[0,:-1])

getData=str(ser.readline())
spec_line_str = getData[0:][2:-4]
print(spec_line_str)

plt.title(color_array[colorNum])

change_array = list(range(1, channels+1))

while line < samples:
	getData=str(ser.readline())
	spec_line_str = getData[0:][2:-4]
	spec_line_data = []
	
	data_dummy = '0'
	
	spec_line_str_list = spec_line_str.split(',')
	
	for i in spec_line_str_list[:-4]: # Make the spectrometer data array. Leave the last two out.
		if i == '':
			i = '0'
		spec_line_data.append(int(i))
		
	integral = float(spec_line_str_list[-4])
	arduino_time = float((int(spec_line_str_list[-3]) - initialTime)/1000)
	colorNum = int(spec_line_str_list[-2])
	if (colorNum != colorHolder):
		plt.title(color_array[colorNum])
	colorHolder = colorNum
	print(integral, arduino_time, color_array[colorNum])
		
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