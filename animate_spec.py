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

index_nums = list(range(1,293))
index = [num_hash(n) for n in index_nums ]
df2.set_axis(index, axis=1, inplace=True)
df2.head(20)

wavelengths = np.linspace(340, 850, 289)

time = np.array(df2.loc[:,'A']).reshape(-1,1)
left_temp = np.array(df2.loc[:,'B']).reshape(-1,1)
right_temp = np.array(df2.loc[:,'C']).reshape(-1,1)

spec_data = np.array(df2.loc[:, 'D':])

fig, (spec_plot, temp_plot) = plt.subplots(1,2)

spec_plot.plot(wavelengths, spec_data[0,:]) 
spec_plot.set_title('Spectrometer Data')
spec_plot.set_xlabel('Wavelengths [nm]')
spec_plot.set_ylabel('Intensity')
temp_plot.plot(time[0], left_temp[0], time[0], right_temp[0])
temp_plot.set_title('Temperature Readings')
temp_plot.set_xlabel('Time [s]')
temp_plot.set_ylabel('Temperature [ºC]')
temp_plot.legend(['Window Sensor', 'Spectrometer Sensor'])
plt.tight_layout()


def animate(i):
    spec_plot.lines[0].set_ydata(spec_data[i+1,:])
    spec_plot.relim() 
    spec_plot.autoscale_view()
    
    temp_plot.lines[0].set_ydata(left_temp[0:i+1])
    temp_plot.lines[0].set_xdata(time[0:i+1])
    temp_plot.lines[1].set_ydata(right_temp[0:i+1])
    temp_plot.lines[1].set_xdata(time[0:i+1])
    temp_plot.relim() 
    temp_plot.autoscale_view()

ani = animation.FuncAnimation(fig, animate, frames=num_frames, interval=40)
#plt.show()

ani.save('spec_plot_{}.mp4'.format(excel_title), fps=40, dpi=200)
    