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

index_nums = list(range(1,292))
index = [num_hash(n) for n in index_nums ]
df2.set_axis(index, axis=1, inplace=True)
df2.head(20)

wavelengths = np.linspace(340, 850, 289)

time = np.array(df2.loc[:,'KE']).reshape(-1,1)

spec_data = np.array(df2.loc[:, :'KC'])

fig, ax = plt.subplots()

ax.plot(wavelengths, spec_data[0,:]) 
ax.set_title('Spectrometer Data')
ax.set_xlabel('Wavelengths [nm]')
ax.set_ylabel('Intensity')

def animate(i):
    plt.gca().lines[0].set_ydata(spec_data[i+1,:]) # Update the plot
    plt.gca().relim() 
    plt.gca().autoscale_view()

ani = animation.FuncAnimation(fig, animate, frames=num_frames, interval=40)
#plt.show()

ani.save('spec_plot_{}.mp4'.format(excel_title), fps=24, dpi=200)
    