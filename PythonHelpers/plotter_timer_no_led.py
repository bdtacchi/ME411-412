#!/usr/bin/env python3
import serial
import matplotlib.pyplot as plt
import numpy as np
import sys
import time

if len(sys.argv) == 1:
	arduino_port = "/dev/cu.usbmodem47110001"
else:
	arduino_port = sys.argv[1]
baud = 115200;
samples = 4000 #how many samples to collect

ser = serial.Serial(arduino_port, baud)
print ("Connected to Arduino port: " + arduino_port) 
print("Created file")

initialString = str(ser.readline())[0:][2:-3] # Grab an initial line from the arduino to define some stuff

initialStringList = initialString.split(sep=',')
channels = int(initialStringList[-4]) # Define the number of channels

initialTime = int(initialStringList[-5]) # Define the current time

time.sleep(1) # Pause 1 second for suspense

line = 0
spec_data = np.zeros([samples, channels+2])  # Create a numpy array to store the spectrometer data and the integral result

points = np.linspace(340, 850, num=channels) # Create an array for all the wavelengths

plt.plot(points, spec_data[0,:-2]) 

getData=str(ser.readline())
spec_line_str = getData[0:][2:-4]

while line < samples:
	getData=str(ser.readline())
	spec_line_str = getData[0:][2:-4]
	spec_line_data = []
	
	spec_line_str_list = spec_line_str.split(',')
	
	for i in spec_line_str_list[:-6]: # Make the spectrometer data array. Leave the last six out (integral, time, color, and number of channels)
		if i == '':
			i = '0'
		spec_line_data.append(i)
		
	integral = float(spec_line_str_list[-6])
	arduino_time = float((int(spec_line_str_list[-5]) - initialTime)/1000)
	timeSpec = int(spec_line_str_list[-3])
	timeIntegral = int(spec_line_str_list[-2])
	timePrint = int(spec_line_str_list[-1])
		
	print(integral, arduino_time, timeSpec, timeIntegral, timePrint) 
	
	if len(spec_line_data) < channels: # In case the output is smaller than the number of channels, add some zeroes at the end.
		for i in range(channels - len(spec_line_data)):
			spec_line_data.append(0) 
			
	if len(spec_line_data) > channels: # If bigger, trim it
		spec_line_data = spec_line_data[0:channels]
		
	spec_data[line,:-2] = spec_line_data # Add the current data to the array of all data
	spec_data[line, -2] = integral
	spec_data[line, -1] = arduino_time
	
	plt.gca().lines[0].set_ydata(spec_line_data) # Update the plot
	plt.gca().relim() 
	plt.gca().autoscale_view()
	plt.pause(0.05);
	
	line += 1 # Update current line
	
	if (line % 50) == 0: # Print total lines every 50 lines
		print(line)
	
	
filename = 'data_timer_no_led' + str(channels) + '.csv'

np.savetxt(filename, spec_data, delimiter=',')
	
print("Data collection complete!")