"""
Synthetic Data Generator for Digital Twin Platform
Generates realistic HVAC telemetry data for training ML models
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random

class HVACDataGenerator:
    """Generate synthetic HVAC telemetry data"""
    
    def __init__(self, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        
        # HVAC system parameters
        self.normal_temp_range = (18, 25)  # Celsius
        self.normal_humidity_range = (40, 60)  # Percentage