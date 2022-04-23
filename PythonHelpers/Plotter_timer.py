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
channels = int(initialStringList[-5]) # Define the number of channels

color_array = ['Violet', 'Blue', 'Cyan', 'Green', 'Yellow', 'Orange', 'Red', 'Off']
colorNum = int(initialStringList[-6]) # Define the current color
colorHolder = colorNum # Define a previous color to change the title of the plot once the color changes

initialTime = int(initialStringList[-7]) # Define the current time

time.sleep(1) # Pause 1 second for suspense

line = 0
spec_data = np.zeros([samples, channels+1])  # Create a numpy array to store the spectrometer data and the integral result

points = np.linspace(340, 850, num=channels) # Create an array for all the wavelengths

plt.plot(points, spec_data[0,:-1]) 

getData=str(ser.readline())
spec_line_str = getData[0:][2:-4]

plt.title(color_array[colorNum])

while line < samples:
	getData=str(ser.readline())
	spec_line_str = getData[0:][2:-4]
	spec_line_data = []
	
	spec_line_str_list = spec_line_str.split(',')
	
	for i in spec_line_str_list[:-8]: # Make the spectrometer data array. Leave the last for out (integral, time, color, and number of channels)
		if i == '':
			i = '0'
		spec_line_data.append(int(i)-155)
		
	integral = float(spec_line_str_list[-8])
	arduino_time = float((int(spec_line_str_list[-7]) - initialTime)/1000)
	colorNum = int(spec_line_str_list[-6])
	timeColor = int(spec_line_str_list[-4])
	timeSpec = int(spec_line_str_list[-3])
	timeIntegral = int(spec_line_str_list[-2])
	timePrint = int(spec_line_str_list[-1])
	
	if (colorNum != colorHolder): # Change the plot title if the color has changed
		plt.title(color_array[colorNum])
		colorHolder = colorNum
		
	print(integral, arduino_time, color_array[colorNum], timeColor, timeSpec, timeIntegral, timePrint) 
	
	if len(spec_line_data) < channels: # In case the output is smaller than the number of channels, add some zeroes at the end.
		for i in range(channels - len(spec_line_data)):
			spec_line_data.append(0) 
			
	if len(spec_line_data) > channels: # If bigger, trim it
		spec_line_data = spec_line_data[0:channels]
		
	spec_data[line,:-1] = spec_line_data # Add the current data to the array of all data
	spec_data[line, -1] = integral
	
	plt.gca().lines[0].set_ydata(spec_line_data) # Update the plot
	plt.gca().relim() 
	plt.gca().autoscale_view()
	plt.pause(0.05);
	
	line += 1 # Update current line
	
	if (line % 50) == 0: # Print total lines every 50 lines
		print(line)
	
	
filename = 'data_' + str(channels) + '.csv'

np.savetxt(filename, spec_data, delimiter=',')
	
print("Data collection complete!")