 #!/usr/bin/env python3
import serial
import matplotlib.pyplot as plt
import numpy as np
import sys
import time
import pickle
from datetime import datetime
from datetime import date

today = date.today()
today = today.strftime("%m_%d_%y")

#plt.switch_backend('TkAgg')

now = datetime.now()
current_time = now.strftime("%H:%M:%S")

def save_object(obj, lines):
	try:
		with open("Pickles/data_{}_{}_{}.pickle".format(lines, today, current_time), "wb") as f:
			pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
	except Exception as ex:
		print("Error during pickling object (Possibly unsupported):", ex)
		
def maximize():
	plot_backend = plt.get_backend()
	mng = plt.get_current_fig_manager()
	if plot_backend == 'TkAgg':
		mng.resize(*mng.window.maxsize())
	elif plot_backend == 'wxAgg':
		mng.frame.Maximize(True)
	elif plot_backend == 'Qt4Agg':
		mng.window.showMaximized()

if len(sys.argv) == 1:
	arduino_port = "/dev/cu.usbmodem47110001"
else:
	arduino_port = sys.argv[1]
baud = 115200;
samples = 2000 #how many samples to collect

ser = serial.Serial(arduino_port, baud)
print ("Connected to Arduino port: " + arduino_port) 
print("Created file")

initialString = str(ser.readline())[0:][2:-3] # Grab an initial line from the arduino to define some stuff

initialStringList = initialString.split(sep=',')
channels = int(initialStringList[-6]) # Define the number of channels

initialTime = int(initialStringList[-7]) # Define the current time
time_array = []
time_array.append(0.0)

left_temp = float(initialStringList[-5])
left_temp_array = [];
left_temp_array.append(left_temp)
right_temp = float(initialStringList[-4])
right_temp_array = [];
right_temp_array.append(right_temp)

x_accel = float(initialStringList[-1])
x_accel_array = [];
x_accel_array.append(x_accel)
y_accel = float(initialStringList[-2])
y_accel_array = [];
y_accel_array.append(y_accel)
z_accel = float(initialStringList[-3])
z_accel_array = [];
z_accel_array.append(z_accel)

time.sleep(1) # Pause 1 second for suspense

line = 0
spec_data = np.zeros([samples, channels+channels+9])  # Create a numpy array to store the spectrometer data, the integral result, and left and right temperatures

points = np.linspace(340, 850, num=channels) # Create an array for all the wavelengths

fig, axd = plt.subplot_mosaic([['upper','upper'],['lower left','lower right']])
spec_plot = axd['upper']
temp_plot = axd['lower left']
accel_plot = axd['lower right']

spec_plot.plot(points, spec_data[0,:channels], points, spec_data[channels:2*channels]) 
spec_plot.set_title('Spectrometer Data')
spec_plot.legend(['Spectrometer 1','Spectrometer 2'])

temp_plot.plot(time_array, left_temp_array, time_array, right_temp_array)
temp_plot.set_title('Temperature Readings')
temp_plot.legend(['Left Sensor', 'Right Sensor'])

accel_plot.plot(time_array, x_accel_array, \
				time_array, y_accel_array, \
				time_array, z_accel_array )
accel_plot.set_title('Accelerometer Readings')
accel_plot.legend(['X acceleration', 'Y acceleration', 'Z acceleration'])

getData=str(ser.readline())
spec_line_str = getData[0:][2:-4]

mng = plt.get_current_fig_manager()
mng.resize(1400,800)

#mng = plt.get_current_fig_manager()
#mng.full_screen_toggle()

plt.tight_layout()

while line < samples:
	getData=str(ser.readline())
	spec_line_str = getData[0:][2:-4]
	spec_line_data = []
	
	spec_line_str_list = spec_line_str.split(',')
	
	for i in spec_line_str_list[:-9]: # Make the spectrometer data array. Leave the last six out (right temperature, left temperature, number of channels, time, integral result)
		if i == '':
			i = '0'
		spec_line_data.append(int(i))
		
	integral_1 = float(spec_line_str_list[-9])
	integral_2 = float(spec_line_str_list[-8])
	arduino_time = float((int(spec_line_str_list[-7]) - initialTime)/1000)
	time_array.append(arduino_time)
	left_temp = float(spec_line_str_list[-5])
	left_temp_array.append(left_temp)
	right_temp = float(spec_line_str_list[-4])
	right_temp_array.append(right_temp)
	x_accel = float(spec_line_str_list[-3])
	x_accel_array.append(x_accel)
	y_accel = float(spec_line_str_list[-2])
	y_accel_array.append(y_accel)
	z_accel = float(spec_line_str_list[-1])
	z_accel_array.append(z_accel)
		
	print(arduino_time, integral_1, integral_2) 
	
	spec_line_data_left = spec_line_data[0:channels]
	spec_line_data_right = spec_line_data[channels:2*channels]
		
	spec_data[line,:-9] = spec_line_data # Add the current data to the array of all data
	
	spec_data[line, -9] = integral_1
	spec_data[line, -8] = integral_2
	spec_data[line, -7] = arduino_time
	
	spec_data[line, -5] = left_temp
	spec_data[line, -4] = right_temp
	spec_data[line, -3] = x_accel
	spec_data[line, -2] = y_accel
	spec_data[line, -1] = z_accel
	
	spec_plot.lines[0].set_ydata(spec_line_data_left)
	spec_plot.lines[1].set_ydata(spec_line_data_right)
	spec_plot.relim() 
	spec_plot.autoscale_view()
	
	temp_plot.lines[0].set_ydata(left_temp_array)
	temp_plot.lines[0].set_xdata(time_array)
	temp_plot.lines[1].set_ydata(right_temp_array)
	temp_plot.lines[1].set_xdata(time_array)
	temp_plot.relim() 
	temp_plot.autoscale_view()
	
	accel_plot.lines[0].set_ydata(x_accel_array)
	accel_plot.lines[0].set_xdata(time_array)
	accel_plot.lines[1].set_ydata(y_accel_array)
	accel_plot.lines[1].set_xdata(time_array)
	accel_plot.lines[2].set_ydata(z_accel_array)
	accel_plot.lines[2].set_xdata(time_array)
	accel_plot.relim()
	accel_plot.autoscale_view()
	
	plt.pause(0.05);
	
	line += 1 # Update current line
	
	if (line % 50) == 0: # Print total lines every 50 lines
		print(line)
		save_object(spec_data, line)
	
	
filename = 'data_no_led_temp_' + str(channels) + '.csv'

np.savetxt(filename, spec_data, delimiter=',')
	
print("Data collection complete!")

