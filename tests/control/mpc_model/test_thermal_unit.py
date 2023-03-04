from common.timeseries.domain import Timestamps, ConstantTimeseriesData, Bounds, BoundTimeseries
from control.mpc_model.component.thermal_unit import ControlThermalGenerator
from control.mpc_model.control_data_model import ControlThermalGeneratorData
from control.optimisation_engine.domain import OptimisationExpression
from tests.control.mock_optimisation_engine import MockOptimisationEngine, MockIndexVariable

import pytest as py


class TestControlThermalUnit:
    def set_up(self):
        timestamps = Timestamps([1, 2, 3, 4])
        bounds = Bounds(2, 10)
        self.data = ControlThermalGeneratorData('unit', timestamps, bounds, current_switch_state=False)
        self.thermal_unit = ControlThermalGenerator(data=self.data)
        self.mock_engine = MockOptimisationEngine()
        self.thermal_unit.extend_optimisation_model(self.mock_engine)

    def _create_variable(self):
        initial_value = ConstantTimeseriesData(self.data.timestamps, 2)
        mock_opt_var_1 = self.mock_engine.add_timeindex_variable(
            'power_1',
            BoundTimeseries.constant_bound_timeseries(
                self.data.timestamps, self.data.power_bounds.min, self.data.power_bounds.max),
            initial_value
        )

        return MockIndexVariable('var_1', self.data.timestamps, mock_opt_var_1.value)

    def test_extend_optimisation_model(self):
        self.set_up()
        assert all(
            [self.thermal_unit.power.bounds.get_value_as_bound(t) ==
             Bounds(0, 10) for t in self.data.timestamps]
        )
        assert self.thermal_unit.power.optimisation_value.value.shape == \
               (len(self.data.timestamps), )

        assert all(
            [self.thermal_unit.switch_state.bounds.get_value_as_bound(t) ==
             Bounds(0, 1) for t in self.data.timestamps]
        )
        assert self.thermal_unit.switch_state.optimisation_value.value.shape == \
               (len(self.data.timestamps),)

    def test_feasible_switch_on_problem(self):
        self.set_up()
        var_1 = self._create_variable()

        self.mock_engine.add_index_constraint(
            'constraint_1', [var_1[i] + self.thermal_unit.power[i] == 4
                             for i, t in enumerate(self.data.timestamps)]
        )

        objective = [var_1[i] + 0.1 * self.thermal_unit.power[i]
                     for i, t in enumerate(self.data.timestamps)]

        self.mock_engine.add_objective(
            'obj_1', OptimisationExpression(sum([o.value.value for o in objective]))
        )

        self.mock_engine.generate_model()
        self.mock_engine.solve()

        assert all([py.approx(p.evaluate()) == 2 for p in self.thermal_unit.power])
        assert all([p.evaluate() for p in self.thermal_unit.switch_state])
        assert self.mock_engine.model.status == 'optimal'

    def test_feasible_switch_off_problem(self):
        self.set_up()
        var_1 = self._create_variable()

        self.mock_engine.add_index_constraint(
            'constraint_1', [var_1[i] + self.thermal_unit.power[i] == 3
                             for i, t in enumerate(self.data.timestamps)]
        )

        objective = [var_1[i] + 0.1 * self.thermal_unit.power[i]
                     for i, t in enumerate(self.data.timestamps)]

        self.mock_engine.add_objective(
            'obj_1', OptimisationExpression(sum([o.value.value for o in objective]))
        )

        self.mock_engine.generate_model()
        self.mock_engine.solve()

        assert all([py.approx(p.evaluate()) == 0 for p in self.thermal_unit.power])
        assert all([not p.evaluate() for p in self.thermal_unit.switch_state])
        assert self.mock_engine.model.status == 'optimal'

    def test_infeasible_problem(self):
        self.set_up()
        var_1 = self._create_variable()

        self.mock_engine.add_index_constraint(
            'constraint_1', [var_1[i] + self.thermal_unit.power[i] == 1
                             for i, t in enumerate(self.data.timestamps)]
        )

        objective = [var_1[i] + 0.1 * self.thermal_unit.power[i]
                     for i, t in enumerate(self.data.timestamps)]

        self.mock_engine.add_objective(
            'obj_1', OptimisationExpression(sum([o.value.value for o in objective]))
        )

        self.mock_engine.generate_model()
        self.mock_engine.solve()

        assert self.mock_engine.model.status == 'infeasible'
