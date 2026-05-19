import numpy as np
from dataclasses import dataclass
from datetime import datetime
from sklearn.ensemble import IsolationForest
import serial
import json
import time

# ============================================================
# GENERATOR SPECIFICATIONS
# ============================================================

@dataclass
class GeneratorSpecs:

    generator_id: str

    rated_voltage: float

    rated_current: float

    rated_power_kw: float

    rated_rpm: float

    age_years: int

    winding_resistance: float

    cooling_type: str


# ============================================================
# SENSOR READING
# ============================================================

@dataclass
class SensorReading:

    timestamp: str

    voltage: float

    current: float

    rpm: float

    winding_temperature: float

    ambient_temperature: float

    vibration: float

    cooling_active: bool


# ============================================================
# ELECTRICAL MODEL
# ============================================================

class ElectricalModel:

    def __init__(self, specs):

        self.specs = specs

    def process(self, reading):

        power_kw = (
            reading.voltage *
            reading.current
        ) / 1000

        copper_loss = (
            reading.current ** 2
        ) * self.specs.winding_resistance

        efficiency = (
            power_kw /
            (
                power_kw +
                copper_loss / 1000
            )
        ) * 100

        return {

            "voltage": reading.voltage,

            "current": reading.current,

            "power_kw": power_kw,

            "efficiency": efficiency,

            "rpm": reading.rpm,

            "copper_loss": copper_loss
        }


# ============================================================
# THERMAL MODEL
# ============================================================

class ThermalModel:

    def process(self, reading):

        temp_rise = (
            reading.winding_temperature -
            reading.ambient_temperature
        )

        hotspot = (
            reading.winding_temperature +
            (temp_rise * 0.25)
        )

        return {

            "winding_temperature":
            reading.winding_temperature,

            "ambient_temperature":
            reading.ambient_temperature,

            "temperature_rise":
            temp_rise,

            "hotspot_temperature":
            hotspot
        }


# ============================================================
# DEGRADATION MODEL
# ============================================================

class DegradationModel:

    def health_index(
        self,
        age,
        temperature,
        vibration
    ):

        age_score = max(
            0,
            100 - age * 2
        )

        temp_score = max(
            0,
            100 - (temperature - 60) * 1.5
        )

        vibration_score = max(
            0,
            100 - vibration * 20
        )

        health = (
            age_score * 0.4 +
            temp_score * 0.4 +
            vibration_score * 0.2
        )

        return health

    def remaining_life(
        self,
        health_index
    ):

        return (
            health_index / 100
        ) * 20


# ============================================================
# MACHINE LEARNING MODEL
# ============================================================

class MLAnomalyDetector:

    def __init__(self):

        self.model = IsolationForest(
            contamination=0.05,
            random_state=42
        )

        training_data = np.array([

            [230, 6, 1500, 55, 0.2],
            [228, 5.5, 1490, 58, 0.3],
            [232, 6.2, 1510, 56, 0.2],
            [231, 6.1, 1505, 57, 0.25]

        ])

        self.model.fit(training_data)

    def detect(
        self,
        voltage,
        current,
        rpm,
        temperature,
        vibration
    ):

        sample = np.array([[
            voltage,
            current,
            rpm,
            temperature,
            vibration
        ]])

        result = self.model.predict(sample)

        return result[0]


# ============================================================
# DIGITAL TWIN ENGINE
# ============================================================

class GeneratorTwinEngine:

    def __init__(self, specs):

        self.specs = specs

        self.electrical_model = ElectricalModel(
            specs
        )

        self.thermal_model = ThermalModel()

        self.degradation_model = (
            DegradationModel()
        )

        self.ml_model = (
            MLAnomalyDetector()
        )

    def update(self, reading):

        electrical = (
            self.electrical_model.process(
                reading
            )
        )

        thermal = (
            self.thermal_model.process(
                reading
            )
        )

        health = (
            self.degradation_model.health_index(

                self.specs.age_years,

                thermal[
                    "hotspot_temperature"
                ],

                reading.vibration
            )
        )

        remaining_life = (
            self.degradation_model.remaining_life(
                health
            )
        )

        ml_result = self.ml_model.detect(

            reading.voltage,

            reading.current,

            reading.rpm,

            reading.winding_temperature,

            reading.vibration
        )

        faults = []

        if thermal[
            "hotspot_temperature"
        ] > 95:

            faults.append({

                "type":
                "OVERHEATING",

                "severity":
                "CRITICAL",

                "recommendation":
                "Reduce generator load"
            })

        if reading.vibration > 2:

            faults.append({

                "type":
                "HIGH VIBRATION",

                "severity":
                "WARNING",

                "recommendation":
                "Inspect bearings and shaft alignment"
            })

        if electrical[
            "efficiency"
        ] < 90:

            faults.append({

                "type":
                "LOW EFFICIENCY",

                "severity":
                "WARNING",

                "recommendation":
                "Inspect generator windings"
            })

        if ml_result == -1:

            faults.append({

                "type":
                "ML ANOMALY DETECTED",

                "severity":
                "HIGH",

                "recommendation":
                "Abnormal operating condition detected"
            })

        return {

            "electrical":
            electrical,

            "thermal":
            thermal,

            "degradation": {

                "health_index":
                health,

                "remaining_life_years":
                remaining_life,

                "condition":
                (
                    "GOOD"
                    if health > 70
                    else "FAIR"
                )
            },

            "faults":
            faults
        }


# ============================================================
# REAL-TIME SENSOR READING
# ============================================================

def read_sensor_data():

    try:

        ser = serial.Serial(
            'COM3',
            115200,
            timeout=1
        )

        line = (
            ser.readline()
            .decode()
            .strip()
        )

        data = json.loads(line)

        reading = SensorReading(

            timestamp=datetime.utcnow().isoformat(),

            voltage=float(
                data["voltage"]
            ),

            current=float(
                data["current"]
            ),

            rpm=float(
                data["rpm"]
            ),

            winding_temperature=float(
                data["temperature"]
            ),

            ambient_temperature=float(
                data["ambient_temperature"]
            ),

            vibration=float(
                data["vibration"]
            ),

            cooling_active=bool(
                data["cooling_active"]
            )
        )

        return reading

    except Exception as e:

        print(
            "Sensor Error:",
            e
        )

        return None


# ============================================================
# MAIN EXECUTION
# ============================================================

if __name__ == "__main__":

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

    twin = GeneratorTwinEngine(
        specs
    )

    print("=" * 60)

    print(
        "REAL-TIME GENERATOR DIGITAL TWIN"
    )

    print("=" * 60)

    while True:

        reading = read_sensor_data()

        if reading is None:
            continue

        state = twin.update(
            reading
        )

        print("\n")

        print("=" * 60)

        print(
            f"Timestamp: "
            f"{reading.timestamp}"
        )

        print(
            f"Voltage: "
            f"{state['electrical']['voltage']:.2f} V"
        )

        print(
            f"Current: "
            f"{state['electrical']['current']:.2f} A"
        )

        print(
            f"Power Output: "
            f"{state['electrical']['power_kw']:.2f} kW"
        )

        print(
            f"RPM: "
            f"{state['electrical']['rpm']:.0f}"
        )

        print(
            f"Efficiency: "
            f"{state['electrical']['efficiency']:.2f}%"
        )

        print(
            f"Temperature: "
            f"{state['thermal']['winding_temperature']:.1f} °C"
        )

        print(
            f"Health Index: "
            f"{state['degradation']['health_index']:.1f}"
        )

        print(
            f"Remaining Life: "
            f"{state['degradation']['remaining_life_years']:.1f} years"
        )

        if state["faults"]:

            print("\nFAULTS:")

            for fault in state["faults"]:

                print(
                    f"- {fault['type']}"
                )

                print(
                    f"  Severity: "
                    f"{fault['severity']}"
                )

                print(
                    f"  Recommendation: "
                    f"{fault['recommendation']}"
                )

        else:

            print(
                "\nNo faults detected"
            )

        time.sleep(2)