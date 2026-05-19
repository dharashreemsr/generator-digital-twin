import numpy as np
import pandas as pd
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, List
from sklearn.ensemble import IsolationForest
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# DATA MODELS
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

    def __init__(self, specs: GeneratorSpecs):

        self.specs = specs

    def calculate_power(self,
                        voltage,
                        current):

        return (voltage * current) / 1000

    def calculate_efficiency(self,
                             power_kw,
                             current):

        copper_loss = (
            current ** 2
        ) * self.specs.winding_resistance

        input_power = power_kw + (copper_loss / 1000)

        if input_power <= 0:
            return 0

        efficiency = (
            power_kw / input_power
        ) * 100

        return min(100, max(0, efficiency))

    def process(self,
                reading: SensorReading):

        power_kw = self.calculate_power(
            reading.voltage,
            reading.current
        )

        efficiency = self.calculate_efficiency(
            power_kw,
            reading.current
        )

        load_percent = (
            reading.current /
            self.specs.rated_current
        ) * 100

        return {
            'voltage': reading.voltage,
            'current': reading.current,
            'power_kw': power_kw,
            'efficiency': efficiency,
            'rpm': reading.rpm,
            'load_percent': load_percent
        }


# ============================================================
# THERMAL MODEL
# ============================================================

class ThermalModel:

    def process(self,
                reading: SensorReading,
                load_percent):

        predicted_temp = (
            reading.winding_temperature +
            (load_percent * 0.05)
        )

        return {
            'winding_temperature':
            reading.winding_temperature,

            'predicted_temperature':
            predicted_temp,

            'ambient_temperature':
            reading.ambient_temperature
        }


# ============================================================
# DEGRADATION MODEL
# ============================================================

class DegradationModel:

    def health_index(self,
                     temp,
                     vibration,
                     age):

        temp_score = max(
            0,
            100 - ((temp - 50) * 1.5)
        )

        vibration_score = max(
            0,
            100 - (vibration * 20)
        )

        age_score = max(
            0,
            100 - (age * 2)
        )

        return (
            0.4 * temp_score +
            0.3 * vibration_score +
            0.3 * age_score
        )

    def remaining_life(self,
                       health_index):

        return (health_index / 100) * 15

    def process(self,
                specs,
                reading):

        health = self.health_index(
            reading.winding_temperature,
            reading.vibration,
            specs.age_years
        )

        remaining = self.remaining_life(
            health
        )

        if health >= 80:
            condition = 'EXCELLENT'
        elif health >= 60:
            condition = 'GOOD'
        elif health >= 40:
            condition = 'FAIR'
        else:
            condition = 'CRITICAL'

        return {
            'health_index': health,
            'remaining_life_years': remaining,
            'condition': condition
        }


# ============================================================
# ML ANOMALY DETECTOR
# ============================================================

class MLAnomalyDetector:

    def __init__(self):

        self.model = IsolationForest(
            contamination=0.05,
            random_state=42
        )

        self.train_model()

    def train_model(self):

        data = []

        for i in range(500):

            voltage = np.random.normal(230, 5)

            current = np.random.normal(6, 1)

            rpm = np.random.normal(1500, 50)

            temperature = np.random.normal(65, 5)

            data.append([
                voltage,
                current,
                rpm,
                temperature
            ])

        self.model.fit(data)

    def detect(self,
               voltage,
               current,
               rpm,
               temperature):

        sample = [[
            voltage,
            current,
            rpm,
            temperature
        ]]

        prediction = self.model.predict(sample)

        return prediction[0]

# ============================================================================
# DIGITAL TWIN ENGINE
# ============================================================================

class GeneratorTwinEngine:
    """Integrate all generator models"""

    def __init__(self, specs: GeneratorSpecs):

        self.specs = specs

        self.electrical_model = ElectricalModel(specs)

        self.thermal_model = ThermalModel()

        self.degradation_model = DegradationModel()

        self.ml_detector = MLAnomalyDetector()

        self.current_state = {
            'timestamp': None,
            'electrical': {},
            'thermal': {},
            'degradation': {},
            'faults': [],
            'health_status': 'UNKNOWN'
        }

    def update(self, reading: SensorReading) -> Dict:
        """Update generator twin"""

        # Electrical calculations
        electrical_results = self.electrical_model.process(
            reading
        )

        # Thermal calculations
        thermal_results = self.thermal_model.process(
            reading,
            electrical_results['load_percent']
        )

        # Degradation assessment
        degradation_results = self.degradation_model.process(
            self.specs,
            reading
        )

        # ML anomaly detection
        ml_result = self.ml_detector.detect(

            reading.voltage,

            reading.current,

            reading.rpm,

            reading.winding_temperature

        )

        # Fault detection
        faults = self._detect_faults(

            reading,

            electrical_results,

            degradation_results,

            ml_result

        )

        # Update current state
        self.current_state = {

            'timestamp': reading.timestamp,

            'electrical': electrical_results,

            'thermal': thermal_results,

            'degradation': degradation_results,

            'faults': faults,

            'health_status':
            degradation_results['condition']
        }

        return self.current_state

    def _detect_faults(self,
                       reading,
                       electrical,
                       degradation,
                       ml_result):

        faults = []

        # Overheating
        if reading.winding_temperature > 95:

            faults.append({

                'type': 'OVERHEATING',

                'severity': 'CRITICAL',

                'value': reading.winding_temperature,

                'threshold': 95,

                'recommendation':
                'Reduce generator load'

            })

        # High vibration
        if reading.vibration > 2:

            faults.append({

                'type': 'HIGH_VIBRATION',

                'severity': 'HIGH',

                'value': reading.vibration,

                'threshold': 2,

                'recommendation':
                'Inspect bearings and shaft alignment'

            })

        # Low efficiency
        if electrical['efficiency'] < 90:

            faults.append({

                'type': 'LOW_EFFICIENCY',

                'severity': 'WARNING',

                'value': electrical['efficiency'],

                'threshold': 90,

                'recommendation':
                'Inspect generator windings'

            })

        # End of life
        if degradation['remaining_life_years'] < 2:

            faults.append({

                'type': 'END_OF_LIFE',

                'severity': 'HIGH',

                'value':
                degradation['remaining_life_years'],

                'recommendation':
                'Plan generator replacement'

            })

        # ML anomaly detection
        if ml_result == -1:

            faults.append({

                'type': 'ML_ANOMALY_DETECTED',

                'severity': 'HIGH',

                'value': reading.winding_temperature,

                'recommendation':
                'Machine learning detected abnormal behavior'

            })

        return faults

    def get_status_report(self):

        return {

            'generator_id':
            self.specs.generator_id,

            'timestamp':
            self.current_state['timestamp'],

            'overall_health':
            self.current_state['health_status'],

            'summary': {

                'voltage':
                self.current_state['electrical'].get(
                    'voltage', 0
                ),

                'current':
                self.current_state['electrical'].get(
                    'current', 0
                ),

                'power':
                self.current_state['electrical'].get(
                    'power_kw', 0
                ),

                'efficiency':
                self.current_state['electrical'].get(
                    'efficiency', 0
                ),

                'rpm':
                self.current_state['electrical'].get(
                    'rpm', 0
                ),

                'temperature':
                self.current_state['thermal'].get(
                    'winding_temperature', 0
                ),

                'health_index':
                self.current_state['degradation'].get(
                    'health_index', 0
                ),

                'remaining_life_years':
                self.current_state['degradation'].get(
                    'remaining_life_years', 0
                )

            },

            'active_faults':
            self.current_state['faults'],

            'recommendations':
            self._generate_recommendations()
        }

    def _generate_recommendations(self):

        recommendations = []

        health = self.current_state[
            'degradation'
        ].get('health_index', 100)

        remaining_life = self.current_state[
            'degradation'
        ].get('remaining_life_years', 0)

        faults = self.current_state['faults']

        if health < 40:

            recommendations.append(
                "URGENT: Immediate generator inspection required"
            )

        elif health < 60:

            recommendations.append(
                "Schedule generator maintenance soon"
            )

        if remaining_life < 2:

            recommendations.append(
                f"Plan generator replacement in "
                f"{remaining_life:.1f} years"
            )

        critical_faults = [

            f for f in faults

            if f['severity'] == 'CRITICAL'

        ]

        for fault in critical_faults:

            recommendations.append(

                f"Critical: "
                f"{fault['recommendation']}"

            )

        return recommendations if recommendations else [
            "Generator operating normally"
        ]


# ============================================================================
# DEMONSTRATION
# ============================================================================

def demo():

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

    twin = GeneratorTwinEngine(specs)

    print("=" * 70)
    print("DIGITAL TWIN OF GENERATOR - DEMONSTRATION")
    print("=" * 70)

    for hour in range(3):

        reading = SensorReading(

            timestamp=datetime.utcnow().isoformat(),

            voltage=230 + np.random.randint(-15, 15),

            current=np.random.uniform(2, 12),

            rpm=np.random.randint(1200, 1800),

            winding_temperature=np.random.randint(50, 110),

            ambient_temperature=30,

            vibration=np.random.uniform(0.1, 2.5),

            cooling_active=True
        )

        # Update twin
        state = twin.update(reading)

        report = twin.get_status_report()

        print(f"\n[{report['timestamp']}]")

        print(
            f"  Generator ID: "
            f"{report['generator_id']}"
        )

        print(
            f"  Overall Health: "
            f"{report['overall_health']}"
        )

        print(f"\n  Electrical Metrics:")

        print(
            f"    Voltage: "
            f"{report['summary']['voltage']:.1f} V"
        )

        print(
            f"    Current: "
            f"{report['summary']['current']:.2f} A"
        )

        print(
            f"    Power: "
            f"{report['summary']['power']:.2f} kW"
        )

        print(
            f"    Efficiency: "
            f"{report['summary']['efficiency']:.2f}%"
        )

        print(
            f"    RPM: "
            f"{report['summary']['rpm']:.0f}"
        )

        print(
            f"    Temperature: "
            f"{report['summary']['temperature']:.1f}°C"
        )

        print(f"\n  Condition Metrics:")

        print(
            f"    Health Index: "
            f"{report['summary']['health_index']:.1f}/100"
        )

        print(
            f"    Remaining Life: "
            f"{report['summary']['remaining_life_years']:.1f} years"
        )

        if report['active_faults']:

            print(f"\n  ⚠️ Active Faults:")

            for fault in report['active_faults']:

                print(
                    f"    - {fault['type']} "
                    f"({fault['severity']})"
                )

                threshold = fault.get(
                    'threshold',
                    'N/A'
                )

                print(
                    f"      Value: "
                    f"{fault['value']:.2f} "
                    f"| Threshold: {threshold}"
                )

                print(
                    f"      Recommendation: "
                    f"{fault['recommendation']}"
                )

        print(f"\n  Recommendations:")

        for rec in report['recommendations']:

            print(f"    • {rec}")

        print("-" * 70)

"""
if __name__ == "__main__":

    demo()

    print(
        "\n✅ Generator Digital Twin demonstration completed!"
    )

    print("\nFeatures Enabled:")

    print("  1. Real-time generator monitoring")

    print("  2. RPM and vibration analysis")

    print("  3. ML anomaly detection")

    print("  4. Predictive maintenance")

    print("  5. Generator fault detection")
""" 