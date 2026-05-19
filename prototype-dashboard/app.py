from flask import Flask, render_template
from datetime import datetime
import random
import sys
import os

# Add project root
sys.path.append(
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')
    )
)

from models.integrated_generator_twin import (
    GeneratorSpecs,
    SensorReading,
    GeneratorTwinEngine
)

app = Flask(__name__)

@app.route('/')
def dashboard():

    # Generator specifications
    specs = GeneratorSpecs(
        generator_id="GEN-001",
        rated_voltage=230,
        rated_current=10,
        rated_power_kw=2.5,
        rated_rpm=1500,
        age_years=4,
        winding_resistance=0.8,
        cooling_type="AIR"
    )

    # Create generator twin
    twin = GeneratorTwinEngine(specs)

    # Simulated sensor readings
    reading = SensorReading(

        timestamp=datetime.utcnow().isoformat(),

        voltage=random.randint(210, 250),

        current=random.uniform(2, 12),

        rpm=random.randint(1200, 1800),

        winding_temperature=random.randint(45, 110),

        ambient_temperature=30,

        vibration=random.uniform(0.1, 2.5),

        cooling_active=True
    )

    # Update digital twin
    state = twin.update(reading)

    electrical = state['electrical']
    thermal = state['thermal']
    degradation = state['degradation']
    faults = state['faults']

    recommendations = twin.get_status_report()['recommendations']

    return render_template(
        'generator_dashboard.html',

        voltage=round(electrical['voltage'], 1),

        current=round(electrical['current'], 2),

        power=round(electrical['power_kw'], 2),

        efficiency=round(electrical['efficiency'], 2),

        rpm=round(electrical['rpm'], 1),

        winding_temp=round(thermal['winding_temperature'], 1),

        health_index=round(degradation['health_index'], 1),

        remaining_life=round(
            degradation['remaining_life_years'], 1
        ),

        condition=degradation['condition'],

        faults=faults,

        recommendations=recommendations
    )

if __name__ == '__main__':
    app.run(debug=True)