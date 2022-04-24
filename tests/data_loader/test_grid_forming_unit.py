import pytest

from data_loader.domain import UnitDataLoaderError
from data_loader.component.grid_forming_unit import StoragePowerPlantDataLoader, ThermalGeneratorDataLoader
from shared.component import Bounds


class TestStoragePowerPlantDataLoader:
    modelling_error_data_scenario = [(-3, 1, 1), (2, 2, 1), (2, -2, 1),
                                     (2, 1, 2), (2, 1, -2)]

    def test_storage_power(self):
        initial_timestamp = 1646462896
        power_bounds = Bounds(min=-100, max=100)
        droop_gain = 1
        energy_bounds = Bounds(min=0, max=6)
        initial_energy = 3
        storage_data_loader = StoragePowerPlantDataLoader(
            initial_timestamp=initial_timestamp, power_bounds=power_bounds, droop_gain=droop_gain,
            energy_bounds=energy_bounds, initial_energy=initial_energy
        )

        assert storage_data_loader.initial_energy == initial_energy
        assert storage_data_loader.power_bounds == power_bounds
        assert storage_data_loader.droop_gain == droop_gain
        assert storage_data_loader.grid_forming_unit_flag == True

    @pytest.mark.parametrize('initial_energy, charge_efficiency, discharge_efficiency',
                             modelling_error_data_scenario)
    def test_modelling_error(self, initial_energy, charge_efficiency, discharge_efficiency):
        initial_timestamp = 1646462896
        power_bounds = Bounds(min=-100, max=100)
        droop_gain = 1
        energy_bounds = Bounds(min=0, max=6)
        initial_energy = -3

        with pytest.raises(UnitDataLoaderError):
            StoragePowerPlantDataLoader(
                initial_timestamp=initial_timestamp, power_bounds=power_bounds, droop_gain=droop_gain,
                energy_bounds=energy_bounds, initial_energy=initial_energy,
                charge_efficiency=charge_efficiency, discharge_efficiency=discharge_efficiency
            )


class TestThermalGeneratorDataLoader:

    def test_thermal_generator(self):
        initial_timestamp = 1646462896
        power_bounds = Bounds(min=-100, max=100)
        droop_gain = 1
        thermal_data_loader = ThermalGeneratorDataLoader(
            initial_timestamp=initial_timestamp, power_bounds=power_bounds, droop_gain=droop_gain,
            switch_state=True
        )

        assert thermal_data_loader.power_bounds == power_bounds
        assert thermal_data_loader.droop_gain == droop_gain
        assert thermal_data_loader.grid_forming_unit_flag == True
        assert thermal_data_loader.switch_state == True