import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import sys
#
#print('Number of arguments:', len(sys.argv), 'arguments.')
#print('Argument List:', str(sys.argv))

book_choice = int(sys.argv[1])

alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
# defined a recursive function here.
# if number is less than "26", simply hash out (index-1)
# There are sub possibilities in possibilities,
# 1.if remainder is zero(if quotient is 1 or not 1) and
# 2. if remainder is not zero
 
def num_hash(num):
    if num < 26:
        return alpha[num-1]
    else:
        q, r = num//26, num % 26
        if r == 0:
            if q == 1:
                return alpha[r-1]
            else:
                return num_hash(q-1) + alpha[r-1]
        else:
            return num_hash(q) + alpha[r-1]

excel_title = 'Book{}'.format(book_choice)

df2 = pd.read_excel('{}.xlsx'.format(excel_title))
num_frames = len(df2.index) - 1

index_nums = list(range(1,588))
index = [num_hash(n) for n in index_nums ]
df2.set_axis(index, axis=1, inplace=True)
df2.head(20)

wavelengths = np.linspace(340, 850, 289)

time = np.array(df2.loc[:,'VI']).reshape(-1,1)
left_temp = np.array(df2.loc[:,'VK']).reshape(-1,1)
right_temp = np.array(df2.loc[:,'VL']).reshape(-1,1)
x_accel = np.array(df2.loc[:,'VM']).reshape(-1,1)
y_accel = np.array(df2.loc[:,'VN']).reshape(-1,1)
z_accel = np.array(df2.loc[:,'VO']).reshape(-1,1)

spec_data_1 = np.array(df2.loc[:, :'KC'])
spec_data_2 = np.array(df2.loc[:, 'KD':'VF'])
wavelengths = np.linspace(340, 850, 289)

fig, (spec_plot, temp_plot) = plt.subplots(1,2)

fig, axd = plt.subplot_mosaic([['upper','upper'],['lower left','lower right']])
spec_plot = axd['upper']
temp_plot = axd['lower left']
accel_plot = axd['lower right']

spec_plot.plot(wavelengths, spec_data_1[0,:], wavelengths, spec_data_2[0,:]) 
spec_plot.set_title('Spectrometer Data')
spec_plot.axis([340, 850, 0, 1050])

temp_plot.plot(time[0], left_temp[0], time[0], right_temp[0])
temp_plot.axis([None, None, 20, 30])
temp_plot.set_title('Temperature Readings')

accel_plot.plot(time[0], x_accel[0], \
                time[0], y_accel[0], \
                time[0], z_accel[0] )
accel_plot.set_title('Accelerometer Readings')
accel_plot.legend(['X acceleration', 'Y acceleration', 'Z acceleration'])
accel_plot.axis([None, None, -10, 10])

plt.tight_layout()

def animate(i):
    spec_plot.lines[0].set_ydata(spec_data_1[i+1,:])
    spec_plot.lines[1].set_ydata(spec_data_2[i+1,:])
    spec_plot.relim() 
    spec_plot.autoscale_view()
    
    temp_plot.lines[0].set_ydata(left_temp[0:i+1])
    temp_plot.lines[0].set_xdata(time[0:i+1])
    temp_plot.lines[1].set_ydata(right_temp[0:i+1])
    temp_plot.lines[1].set_xdata(time[0:i+1])
    temp_plot.relim() 
    temp_plot.autoscale_view()
    
    accel_plot.lines[0].set_ydata(x_accel[0:i+1])
    accel_plot.lines[0].set_xdata(time[0:i+1])
    accel_plot.lines[1].set_ydata(y_accel[0:i+1])
    accel_plot.lines[1].set_xdata(time[0:i+1])
    accel_plot.lines[2].set_ydata(z_accel[0:i+1])
    accel_plot.lines[2].set_xdata(time[0:i+1])
    accel_plot.relim() 
    accel_plot.autoscale_view()

fps = int(sys.argv[2])

ani = animation.FuncAnimation(fig, animate, frames=num_frames, interval=40)
#plt.show()

ani.save('elec_plot_{}_fps.mp4'.format(fps), fps=fps, dpi=200)
    