import matplotlib.pyplot as plt
import pandas as pd
import pandas_ta as ta
import datetime
import keyboard


# Turn on interactive mode
plt.ion()

# Create a sample DataFrame
data = {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 6, 80, 100]}
df = pd.DataFrame(data)

# Plot the DataFrame
df.plot(x='x', y='y', kind='line', marker='o')

# No need to use plt.show() in interactive mode

# Keep the plot window open for a while (optional)
plt.pause(5)  # This will keep the plot window open for 5 seconds

# Turn off interactive mode (optional)
plt.ioff()

# Display the plot (optional)
plt.show()