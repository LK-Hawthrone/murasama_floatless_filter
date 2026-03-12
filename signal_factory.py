## SIGNAL FACTORY | PROSTHETIC DSP CORE
# Author: L.K Hawthrone

import numpy as np
import xml.etree.ElementTree as ET
import os

# Internal state and global parameters
state = {"tick": 0, "x_z1": 0, "x_z2": 0, "y_z1": 0, "y_z2": 0}
params = {}

def load_xml_config(path="config_parameter.xml"):
    """Loads coefficients and env settings from XML."""
    global params
    # Defaults in case of file absence
    params = {
        'b0': 31, 'b1': 62, 'b2': 31, 'a1': -62625, 'a2': 30000, 'shift': 15,
        'adc': 1000, 'noise': 1.2, 'hum': 0.5
    }
    
    if os.path.exists(path):
        try:
            tree = ET.parse(path)
            root = tree.getroot()
            
            # Filter mapping
            f = root.find('filter')
            for k in ['b0', 'b1', 'b2', 'a1', 'a2', 'shift']:
                params[k] = int(f.find(k).text)
            
            # Env mapping
            e = root.find('environment')
            params['adc'] = int(e.find('adc_multiplier').text)
            params['noise'] = float(e.find('noise_gain').text)
            params['hum'] = float(e.find('hum_60hz_gain').text)
        except Exception as err:
            print(f"[*] XML Parse Error: {err}. Using defaults.")

# Initialize parameters on import
load_xml_config()

def get_next_sample():
    """Generates one dirty sample based on XML environment parameters."""
    state["tick"] += 1
    t = state["tick"] / 1000.0
    
    intent = np.sin(2 * np.pi * 5 * t) * (t % 1.0 > 0.2) * (t % 1.0 < 0.8)
    
    # Using XML params for noise levels
    noise = params['noise'] * np.random.normal()
    hum = params['hum'] * np.sin(2 * np.pi * 60 * t)
    dirty = intent + noise + hum
    
    return t, intent, dirty

def apply_murasama_step(x_n):
    """Processes sample using XML coefficients."""
    # ADC Simulation using XML multiplier
    x_n_int = int(x_n * params['adc'])
    
    # Difference Equation with Q15
    term_b = (params['b0'] * x_n_int) + (params['b1'] * state["x_z1"]) + (params['b2'] * state["x_z2"])
    term_a = (params['a1'] * state["y_z1"]) + (params['a2'] * state["y_z2"])
    
    y_n = (term_b - term_a) >> params['shift']
    
    # State update
    state["x_z2"], state["x_z1"] = state["x_z1"], x_n_int
    state["y_z2"], state["y_z1"] = state["y_z1"], y_n
    
    return y_n / params['adc']