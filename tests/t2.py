import plotly.io as pio

# Get the list of available renderers
available_renderers = pio.renderers

# Print the list of available renderers
print("Available Plotly Renderers:")
for renderer in available_renderers:
    print(renderer)