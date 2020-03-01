import pandas as pd

df = pd.read_csv('ExperimentResults/light_g35_r13_fpoint1_a6.csv')

N14E_car_arrivals = df["Num Cars N14E"].mean()
S14E_car_arrivals = df["Num Cars S14E"].mean()
EN14W_car_arrivals = df["Num Cars EN14W"].mean()
ES14W_car_arrivals = df["Num Cars ES14W"].mean()
NAtlanticS_car_arrivals = df["Num Cars N Atlantic S"].mean()
SAtlanticN_car_arrivals = df["Num Cars S Atlantic N"].mean()

import matplotlib.pyplot as plt

averaged_arrivals = pd.Series([N14E_car_arrivals, S14E_car_arrivals, EN14W_car_arrivals, 
                                ES14W_car_arrivals, NAtlanticS_car_arrivals, SAtlanticN_car_arrivals],
                                index=['N14E', 'S14E', 'EN14W', 'ES14W', 'N Atlantic S', 'S Atlantic N']).transpose()

my_colors = 'bmrcgk'
#plt.title('Total Number of Car Arrivals for Each Street Resource\n\
#Traffic Light: True; Green Light: 45; Red Light: 20\n\
#14th St Arrival Rate: 0.5; Atlantic Dr Arrival Rate: 6')
#plt.ylabel('Average Number of Car Arrivals')
#plt.xlabel('Street Resources')
ax = averaged_arrivals.plot(kind='bar', color = my_colors)

ax.set_title('Total Number of Car Arrivals for Each Street Resource\n\
Traffic Light: True; Green Light: 35; Red Light: 13\n\
14th St Arrival Rate: 0.1; Atlantic Dr Arrival Rate: 6')

#ax.set_title('Total Number of Car Arrivals for Each Street Resource\n\
#Traffic Light: False\n\
#14th St Arrival Rate: 0.5; Atlantic Dr Arrival Rate: 6')

ax.set_xlabel('Street Resources')
ax.set_ylabel('Average Number of Car Arrivals')
rects = ax.patches
# For each bar: Place a label
for rect in rects:
    # Get X and Y placement of label from rect
    y_value = rect.get_height()
    x_value = rect.get_x() + rect.get_width() / 2

    # Number of points between bar and label. Change to your liking.
    space = 0
    # Vertical alignment for positive values
    va = 'bottom'

    # Use Y value as label and format number with one decimal place
    label = "{:.1f}".format(y_value)

    # Create annotation
    plt.annotate(
        label,                      # Use `label` as label
        (x_value, y_value),         # Place label at end of the bar
        xytext=(0, space),          # Vertically shift label by `space`
        textcoords="offset points", # Interpret `xytext` as offset in points
        ha='center',                # Horizontally center label
        va=va)                      # Vertically align label differently for
                                    # positive and negative values.
plt.ylim(0, 200)
plt.tight_layout()
plt.savefig('Graphs/arrivals_light_g35_r13_fpoint1_a6.png')





# Generate chart for wait times
import matplotlib.pyplot as plt

N14E_wait_time = df["Avg Wait N14E"].mean()
S14E_wait_time = df["Avg Wait S14E"].mean()
EN14W_wait_time = df["Avg Wait EN14W"].mean()
ES14W_wait_time = df["Avg Wait ES14W"].mean()
NAtlanticS_wait_time = df["Avg Wait N Atlantic S"].mean()
SAtlanticN_wait_time = df["Avg Wait S Atlantic N"].mean()

averaged_wait_times = pd.Series([N14E_wait_time, S14E_wait_time, EN14W_wait_time, 
                                ES14W_wait_time, NAtlanticS_wait_time, SAtlanticN_wait_time],
                                index=['N14E', 'S14E', 'EN14W', 'ES14W', 'N Atlantic S', 'S Atlantic N']).transpose()

my_colors = 'bmrcgk'
#plt.title('Total Number of Car Arrivals for Each Street Resource\n\
#Traffic Light: True; Green Light: 45; Red Light: 20\n\
#14th St Arrival Rate: 0.5; Atlantic Dr Arrival Rate: 6')
#plt.ylabel('Average Number of Car Arrivals')
#plt.xlabel('Street Resources')
ax = averaged_wait_times.plot(kind='bar', color = my_colors)

ax.set_title('Average Wait Time Each Street Resource\n\
Traffic Light: True; Green Light: 35; Red Light: 13\n\
14th St Arrival Rate: 0.1; Atlantic Dr Arrival Rate: 6')

#ax.set_title('Average Wait Time Each Street Resource\n\
#Traffic Light: False\n\
#14th St Arrival Rate: 0.5; Atlantic Dr Arrival Rate: 6')

ax.set_xlabel('Street Resources')
ax.set_ylabel('Average Wait Time')
rects = ax.patches
# For each bar: Place a label
for rect in rects:
    # Get X and Y placement of label from rect
    y_value = rect.get_height()
    x_value = rect.get_x() + rect.get_width() / 2

    # Number of points between bar and label. Change to your liking.
    space = 0
    # Vertical alignment for positive values
    va = 'bottom'

    # Use Y value as label and format number with one decimal place
    label = "{:.1f}".format(y_value)

    # Create annotation
    plt.annotate(
        label,                      # Use `label` as label
        (x_value, y_value),         # Place label at end of the bar
        xytext=(0, space),          # Vertically shift label by `space`
        textcoords="offset points", # Interpret `xytext` as offset in points
        ha='center',                # Horizontally center label
        va=va)                      # Vertically align label differently for
                                    # positive and negative values.
plt.ylim(0, 30)
plt.tight_layout()
plt.savefig('Graphs/wait_light_g35_r13_fpoint1_a6.png')
