# WINDOW SETTINGS
# ---------------
# Screen resolution
resolution = [960, 720]

# Window sizes (Currently buggy if you change these non-uniformly)
x_min, x_max = -1, 1
y_min, y_max = -1, 1

# Window size scaling
window_scale = 10

# HELPERS FOR GRAPHING
# --------------------
x_min, x_max = x_min * window_scale, x_max * window_scale
y_min, y_max = y_min * window_scale, y_max * window_scale

# Convert from world space to NDC [-1, 1]
def to_ndc_x(val):
    # Get the distance from the left edge of the screen (minimum x)
    distance = (val - x_min)
    # Get the ratio of how far the value is across the x-axis
    pos = distance / (x_max - x_min)
    return 2 * pos - 1

def to_ndc_y(val):
    # Get the distance from the bottom edge of the screen (minimum y)
    distance = (val - y_min)
    # Get the ratio of how far the value is across the y-axis
    pos = distance / (y_max - y_min)
    return 2 * pos - 1
