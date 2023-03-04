import numpy as np

from common.timeseries.domain import Timestamps, ConstantTimeseriesData, Bounds, BoundTimeseries
from control.mpc_model.component.storage_unit import ControlStoragePowerPlant
from control.mpc_model.control_data_model import ControlStoragePowerPlantData
from control.optimisation_engine.domain import OptimisationExpression
from tests.control.mock_optimisation_engine import MockOptimisationEngine, MockIndexVariable

import pytest as py


class TestControlStorageUnit:
    def _set_up(self, current_energy: float):
        timestamps = Timestamps([360, 2 * 360, 3 * 360, 4 * 360])
        bounds = Bounds(-10, 10)
        energy_bounds = Bounds(0, 5)
        self.data = ControlStoragePowerPlantData(
            'unit', timestamps, bounds, energy_bounds, current_energy=current_energy
        )
        self.storage_unit = ControlStoragePowerPlant(data=self.data)
        self.mock_engine = MockOptimisationEngine()
        self.storage_unit.extend_optimisation_model(self.mock_engine)

    def _create_variable(self, value: float):
        initial_value = ConstantTimeseriesData(self.data.timestamps, 0)
        mock_opt_var_1 = self.mock_engine.add_timeindex_variable(
            'power_1',
            BoundTimeseries.constant_bound_timeseries(
                self.data.timestamps, 0, value),
            initial_value
        )

        return MockIndexVariable('var_1', self.data.timestamps, mock_opt_var_1.value)

    def test_extend_optimisation_model(self):
        self._set_up(current_energy=2)
        assert all([self.storage_unit.power.bounds.get_value_as_bound(t) == Bounds(-10, 10)
                    for t in self.data.timestamps])
        assert all([self.storage_unit.energy.bounds.get_value_as_bound(t) == Bounds(0, 5)
                    for t in self.data.timestamps])
        assert self.storage_unit.power.optimisation_value.value.shape == \
               (len(self.data.timestamps), )
        assert self.storage_unit.energy.optimisation_value.value.shape == \
               (len(self.data.timestamps),)

    def test_feasible_charging_problem(self):
        self._set_up(current_energy=2)
        var_1 = self._create_variable(value=5)

        self.mock_engine.add_index_constraint(
            'constraint_1', [var_1[i] + self.storage_unit.power[i] == 6
                             for i, t in enumerate(self.data.timestamps)]
        )

        objective = [var_1[i] + 0.1 * self.storage_unit.power[i]
                     for i, t in enumerate(self.data.timestamps)]

        self.mock_engine.add_objective(
            'obj_1', OptimisationExpression(sum([o.value.value for o in objective]))
        )

        self.mock_engine.generate_model()
        self.mock_engine.solve()

        energy = [np.around(e.evaluate(), 3) for e in self.storage_unit.energy]

        assert all([py.approx(p.evaluate()) == 6 for p in self.storage_unit.power])
        assert all([np.around(e, 2) <= 2 for e in energy])
        assert all(np.around(np.diff(energy), 3) == [-0.6] * 3)
        assert self.mock_engine.model.status == 'optimal'

    def test_feasible_discharge_problem(self):
        self._set_up(current_energy=2)
        var_1 = self._create_variable(value=8)

        self.mock_engine.add_index_constraint(
            'constraint_1', [var_1[i] + self.storage_unit.power[i] == 6
                             for i, t in enumerate(self.data.timestamps)]
        )

        objective = [0.1 * var_1[i] + self.storage_unit.power[i]
                     for i, t in enumerate(self.data.timestamps)]

        self.mock_engine.add_objective(
            'obj_1', OptimisationExpression(sum([o.value.value for o in objective]))
        )

        self.mock_engine.generate_model()
        self.mock_engine.solve()

        assert all([py.approx(p.evaluate()) == -2 for p in self.storage_unit.power])
        assert all([np.around(e.evaluate()) >= 2 for e in self.storage_unit.energy])
        assert self.mock_engine.model.status == 'optimal'

    def test_energy_constraint_infeasible_problem(self):
        self._set_up(current_energy=0.1)
        var_1 = self._create_variable(value=8)

        self.mock_engine.add_index_constraint(
            'constraint_1', [var_1[i] + self.storage_unit.power[i] == 10
                             for i, t in enumerate(self.data.timestamps)]
        )

        objective = [-0.1 * var_1[i] + self.storage_unit.power[i]
                     for i, t in enumerate(self.data.timestamps)]

        self.mock_engine.add_objective(
            'obj_1', OptimisationExpression(sum([o.value.value for o in objective]))
        )

        self.mock_engine.generate_model()
        self.mock_engine.solve()

        assert self.mock_engine.model.status == 'infeasible'
