from unittest import TestCase

from data_loader.component.grid_forming_unit import StoragePowerPlantDataLoader, ThermalGeneratorDataLoader
from model.component.grid_forming_unit import StoragePowerPlant, ThermalGenerator
from shared.component import Bounds


class TestStoragePowerPlant(TestCase):
    def test_storage_initialisation(self):
        initial_timestamp = 1639396720
        initial_energy = 2
        power_setpoint = 2
        data_loader = StoragePowerPlantDataLoader(
            initial_timestamp, power_bounds=Bounds(0, 5), droop_gain=1, energy_bounds=Bounds(0, 5),
            initial_energy=initial_energy
        )
        storage_plant = StoragePowerPlant(name = 'storage', data_loader=data_loader)

        storage_plant.power_setpoint = power_setpoint

        assert storage_plant.current_energy == initial_energy
        assert storage_plant.current_power == 0
        assert storage_plant.power_setpoint == power_setpoint

    def test_step_simulation_timestamp(self):
        initial_timestamp = 1639396720
        data_loader = StoragePowerPlantDataLoader(
            initial_timestamp, power_bounds=Bounds(-5, 5), droop_gain=1, energy_bounds=Bounds(0, 5),
            initial_energy=2
        )
        storage_plant = StoragePowerPlant(name='storage', data_loader=data_loader)
        storage_plant.power_setpoint = 2
        storage_plant.step(initial_timestamp + 900)

        assert storage_plant.current_energy == 1.5
        assert storage_plant.current_power == 2

        storage_plant.power_setpoint = -2
        storage_plant.step(initial_timestamp + 1800)

        assert storage_plant.current_energy == 2
        assert storage_plant.current_power == -2

    def test_storage_power_sharing(self):
        initial_timestamp = 1639396720
        data_loader = StoragePowerPlantDataLoader(
            initial_timestamp, power_bounds=Bounds(-5, 5), droop_gain=0.5, energy_bounds=Bounds(0, 5),
            initial_energy=0
        )
        storage_plant = StoragePowerPlant(name='storage', data_loader=data_loader)

        storage_plant.power_setpoint = 0
        storage_plant.participate_power_sharing(delta_frequency=0.5)

        storage_plant.step(initial_timestamp + 900)

        assert storage_plant.current_energy == 0.25
        assert storage_plant.current_power == -1
        assert storage_plant.power_setpoint == 0

    def test_storage_logging_energy_bounds(self):
        initial_timestamp = 1639396720
        data_loader = StoragePowerPlantDataLoader(
            initial_timestamp, power_bounds=Bounds(-5, 5), droop_gain=0.5, energy_bounds=Bounds(0, 5),
            initial_energy=0
        )
        storage_plant = StoragePowerPlant(name='storage', data_loader=data_loader)

        storage_plant.power_setpoint = 1

        with self.assertLogs('model.component.grid_forming_unit') as cm:
            storage_plant.step(initial_timestamp + 900)
            storage_plant.step(initial_timestamp + 1800)
            assert len(cm.records) == 2

    def test_current_simulation_data(self):
        initial_timestamp = 1639396720
        data_loader = StoragePowerPlantDataLoader(
            initial_timestamp, power_bounds=Bounds(-5, 5), droop_gain=1, energy_bounds=Bounds(0, 5),
            initial_energy=2
        )
        storage_plant = StoragePowerPlant(name='storage', data_loader=data_loader)
        storage_plant.power_setpoint = 0
        storage_plant.step(initial_timestamp + 900)

        data = storage_plant.current_simulation_data()

        assert data.values['current_energy'] == 2
        assert data.values['power_setpoint'] == 0
        assert data.values['current_power'] == 0

class TestThermalGenerator(TestCase):
    def test_thermal_generator_initialisation(self):
        initial_timestamp = 1639396720
        power_setpoint = 2
        data_loader = ThermalGeneratorDataLoader(
            initial_timestamp, power_bounds=Bounds(0, 5), droop_gain=1, switch_state = False
        )
        thermal_plant = ThermalGenerator(name='thermal', data_loader=data_loader)

        thermal_plant.power_setpoint = power_setpoint

        assert thermal_plant.power_setpoint == power_setpoint
        assert thermal_plant.switch_state == True

    def test_step_simulation_timestamp(self):
        initial_timestamp = 1639396720
        power_setpoint = 0
        data_loader = ThermalGeneratorDataLoader(
            initial_timestamp, power_bounds=Bounds(1, 5), droop_gain=1, switch_state=False
        )
        thermal_plant = ThermalGenerator(name='thermal', data_loader=data_loader)

        thermal_plant.power_setpoint = power_setpoint
        thermal_plant.participate_power_sharing(delta_frequency=0.1)

        thermal_plant.step(initial_timestamp + 900)

        assert thermal_plant.power_setpoint == power_setpoint
        assert thermal_plant.current_power == power_setpoint
        assert thermal_plant.switch_state == False
        assert thermal_plant.power_sharing == 0

    def test_current_simulation_data(self):
        initial_timestamp = 1639396720
        power_setpoint = 2
        data_loader = ThermalGeneratorDataLoader(
            initial_timestamp, power_bounds=Bounds(1, 5), droop_gain=1, switch_state=False
        )
        thermal_plant = ThermalGenerator(name='thermal', data_loader=data_loader)

        thermal_plant.power_setpoint = power_setpoint

        thermal_plant.step(initial_timestamp + 900)

        data = thermal_plant.current_simulation_data()

        assert data.values['switch_state'] == True
        assert data.values['power_setpoint'] == power_setpoint
        assert data.values['current_power'] == power_setpoint
