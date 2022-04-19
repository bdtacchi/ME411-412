#!/usr/bin/env python3
import serial
import matplotlib.pyplot as plt
import numpy as np
import sys
import time
import pickle
from datetime import datetime
from datetime import date
import os

today = date.today()
today = today.strftime("%m_%d_%y")

now = datetime.now()
current_time = now.strftime("%H_%M_%S")

pickles_list=[]

def delete_stuff(pickles_list):
	for i in range(len(pickles_list)-1):
		if os.path.exists(pickles_list[i]):
			print(pickles_list[i])
			os.remove(pickles_list[i])
		else:
			print("The file does not exist")
	pickle_copy = pickles_list[-1]
	pickles_list=[pickle_copy]
	return pickles_list

def save_object(obj, lines, pickles_list):
	try:
		with open("Pickles/data_{}_{}_{}.pickle".format(lines, today, current_time), "wb") as f:
			pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
			pickles_list.append("Pickles/data_{}_{}_{}.pickle".format(lines, today, current_time))
	except Exception as ex:
		print("Error during pickling object (Possibly unsupported):", ex)
	return pickles_list

if len(sys.argv) == 1:
	arduino_port = "/dev/cu.usbmodem47110001"
else:
	arduino_port = sys.argv[1]
baud = 115200;
samples = 1000 #how many samples to collect

ser = serial.Serial(arduino_port, baud)
print ("Connected to Arduino port: " + arduino_port) 
print("Created file")

initialString = str(ser.readline())[0:][2:-3] # Grab an initial line from the arduino to define some stuff

initialStringList = initialString.split(sep=',')
channels = int(initialStringList[-1]) # Define the number of channels

initialTime = int(initialStringList[-2]) # Define the current time

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
	
	for i in spec_line_str_list[:-3]: # Make the spectrometer data array. Leave the last for out (integral, time, color, and number of channels)
		if i == '':
			i = '0'
		spec_line_data.append(int(i))
		
	integral = float(spec_line_str_list[-3])
	arduino_time = float((int(spec_line_str_list[-2]) - initialTime)/1000)
	
		
	print(integral, arduino_time) 
	
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
		pickles_list = save_object(spec_data, line, pickles_list)
		print(pickles_list)
	
	if (line % 200) == 0:
		print(pickles_list)
		pickles_list = delete_stuff(pickles_list)
	
		
filename = 'data_no_led_{}'.format(current_time) + str(channels) + '.csv'

np.savetxt(filename, spec_data, delimiter=',')
	
print("Data collection complete!")
