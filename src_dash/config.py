"""
Configurations for the app
"""
import os

# DASH OPTIONS
error_bars_for = ['IntraDay']
# Add or remove from  Options:  ['Day Ahead Ensemble', 'Satellite', 'IntraDay', 'Logs']


# HOST
HOST = '127.0.0.1'
# HOST = '10.10.2.34'
PORT = '7500'

# PATH CONFIG
# real_path = '/home/nrldc/Solar_Forecast/real'
# intra_day_path = '/home/nrldc/Solar_Forecast/IntraDay'
# day_ahead_ensemble_path = '/home/nrldc/Solar_Forecast/Predicted'
# satellite_forecast_path = '/home/nrldc/Solar_Forecast/Sattellite_Tensor/Predicted'
# logs_path = '/home/nrldc/Solar_Forecast/log'

# DEV PATHS (USED FOR ADDING UPDATES)
real_path = '/Users/vasu/TensorDynamics/SolarDash/real'
intra_day_path = '/Users/vasu/TensorDynamics/SolarDash/IntraDay'
day_ahead_ensemble_path = '/Users/vasu/TensorDynamics/SolarDash/da_ensemble'
satellite_forecast_path = '/Users/vasu/TensorDynamics/SolarDash/satellite_pred'
logs_path = '/Users/vasu/TensorDynamics/SolarDash/log'

src_path = os.path.join(os.getcwd())

# DASH UI SETTINGS
G1_HEIGHT = 600
G2_HEIGHT = 150
AXIS_TICK_SIZE = 11
GEN_FONT_GRAPHS = 12
HOVER_SIZE = 16
GRAPH_BG = '#242526'  # '#242526' DEV RENDER -> Prod - '#28231D'
GRID_COL = '#404040'  # '#404040' DEV RENDER -> Prod - '#212121'
REFRESH_RATE = 2  # MINS
