# WINDOW SETTINGS
# ---------------
# Screen resolution
resolution = [960, 720]

# Window sizes (Currently buggy if you change these non-uniformly)
DEFAULT_X_MIN, DEFAULT_X_MAX = -1, 1
DEFAULT_Y_MIN, DEFAULT_Y_MAX = -1, 1

# Window size scaling
DEFAULT_WINDOW_SCALE = 10

# Graph settings
# --------------
# Type of integration estimation method drawn
# (LRAM, RRAM, MRAM, TRAP)
DEFAULT_INTEGRATION_TYPE = "LRAM"
# Number of samples used for integration under the graph
DEFAULT_INTEGRATION_SAMPLES = 8192
# Number of samples used to draw the graph
# Note: There is no option to change this during runtime
GRAPH_SAMPLES = 8192
# Default bounds of integration
DEFAULT_LOWER_BOUND = -5
DEFAULT_UPPER_BOUND = 5
# How fast the bounds expand/shrink/shifts when pressing associated keys during runtime
BOUND_EXP_FACTOR = 0.5

FPS = 60
MIN_INTEGRATION_SAMPLES = 1
MAX_INTEGRATION_SAMPLES = 262144

# Global variables for window settings
window_scale = DEFAULT_WINDOW_SCALE
x_min = DEFAULT_X_MIN * window_scale
x_max = DEFAULT_X_MAX * window_scale
y_min = DEFAULT_Y_MIN * window_scale
y_max = DEFAULT_Y_MAX * window_scale


# Helper functions
# ----------------
def to_ndc_x(val):
    """Convert a world space x-coordinate to NDC [-1, 1]."""

    # Get the distance from the left edge of the screen (minimum x)
    distance = (val - x_min)
    # Get the ratio of how far the value is across the x-axis
    pos = distance / (x_max - x_min)
    return 2 * pos - 1


def to_ndc_y(val):
    """Convert a world space y-coordinate to NDC [-1, 1]."""

    # Get the distance from the bottom edge of the screen (minimum y)
    distance = (val - y_min)
    # Get the ratio of how far the value is across the y-axis
    pos = distance / (y_max - y_min)
    return 2 * pos - 1
