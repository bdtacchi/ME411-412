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
samples = 10000 #how many samples to collect

ser = serial.Serial(arduino_port, baud)
print ("Connected to Arduino port: " + arduino_port) 
print("Created file")

initialString = str(ser.readline())[0:][2:-3] # Grab an initial line from the arduino to define some stuff

initialStringList = initialString.split(sep=',')
channels = int(initialStringList[-3]) # Define the number of channels

initialTime = int(initialStringList[-4]) # Define the current time
time_array = []
time_array.append(0.0)

left_temp = float(initialStringList[-2])
left_temp_array = [];
left_temp_array.append(left_temp)
right_temp = float(initialStringList[-1])
right_temp_array = [];
right_temp_array.append(right_temp)

time.sleep(1) # Pause 1 second for suspense

line = 0
spec_data = np.zeros([samples, channels+4])  # Create a numpy array to store the spectrometer data, the integral result, and left and right temperatures

points = np.linspace(340, 850, num=channels) # Create an array for all the wavelengths

fig, (spec_plot, temp_plot) = plt.subplots(1,2)

mng = plt.get_current_fig_manager()
mng.resize(1400,800)

spec_plot.plot(points, spec_data[0,:-4]) 
spec_plot.set_title('Spectrometer Data')
temp_plot.plot(time_array, left_temp_array, time_array, right_temp_array)
temp_plot.set_title('Temperature Readings')
temp_plot.legend(['Left Sensor', 'Right Sensor'])

getData=str(ser.readline())
spec_line_str = getData[0:][2:-4]

while line < samples:
	getData=str(ser.readline())
	spec_line_str = getData[0:][2:-4]
	spec_line_data = []
	
	spec_line_str_list = spec_line_str.split(',')
	
	for i in spec_line_str_list[:-5]: # Make the spectrometer data array. Leave the last six out (right temperature, left temperature, number of channels, time, and integral result)
		if i == '':
			i = '0'
		spec_line_data.append(int(i))
		
	integral = float(spec_line_str_list[-5])
	arduino_time = float((int(spec_line_str_list[-4]) - initialTime)/1000)
	time_array.append(arduino_time)
	left_temp = float(spec_line_str_list[-2])
	left_temp_array.append(left_temp)
	right_temp = float(spec_line_str_list[-1])
	right_temp_array.append(right_temp)
		
	print(integral, arduino_time, left_temp, right_temp) 
	
	if len(spec_line_data) < channels: # In case the output is smaller than the number of channels, add some zeroes at the end.
		for i in range(channels - len(spec_line_data)):
			spec_line_data.append(0) 
			
	if len(spec_line_data) > channels: # If bigger, trim it
		spec_line_data = spec_line_data[0:channels]
		
	spec_data[line,:-4] = spec_line_data # Add the current data to the array of all data
	spec_data[line, -4] = integral
	spec_data[line, -3] = arduino_time
	spec_data[line, -2] = left_temp
	spec_data[line, -1] = right_temp
	
	spec_plot.lines[0].set_ydata(spec_line_data)
	spec_plot.relim() 
	spec_plot.autoscale_view()
	
	temp_plot.lines[0].set_ydata(left_temp_array)
	temp_plot.lines[0].set_xdata(time_array)
	temp_plot.lines[1].set_ydata(right_temp_array)
	temp_plot.lines[1].set_xdata(time_array)
	temp_plot.relim() 
	temp_plot.autoscale_view()
	plt.pause(0.05);
	
	line += 1 # Update current line
	
	if (line % 50) == 0: # Print total lines every 50 lines
		print(line)
		pickles_list = save_object(spec_data, line, pickles_list)
		print(pickles_list)
	
	if (line % 1000) == 0:
		print(pickles_list)
		pickles_list = delete_stuff(pickles_list)
		
	
	
filename = 'data_no_led_temp_' + str(channels) + '.csv'

np.savetxt(filename, spec_data, delimiter=',')
	
print("Data collection complete!")

