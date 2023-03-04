import numpy as np
import pytest

from common.timeseries.domain import Timestamps, ConstantTimeseriesData, Bounds, BoundTimeseries
from control.mpc_model.component.renewable_unit import RenewablePowerUnit
from control.mpc_model.control_data_model import ControlRenewableUnitData
from control.optimisation_engine.domain import OptimisationExpression
from tests.control.mock_optimisation_engine import MockOptimisationEngine, MockIndexVariable

import pytest as py


class TestControlRenewableUnit:
    def test_extend_optimisation_model(self):
        timestamps = Timestamps([1, 2, 3, 4, 5])
        power_forecast = ConstantTimeseriesData(timestamps, 5)
        bounds = Bounds(0, 10)
        data = ControlRenewableUnitData('renew_unit_1', timestamps, power_forecast, bounds)
        renew_unit = RenewablePowerUnit(data)
        mock_engine = MockOptimisationEngine()
        renew_unit.extend_optimisation_model(mock_engine)

        assert all([v == 0 for v in renew_unit.power.bounds.min.values])
        assert all([v == 10 for v in renew_unit.power.bounds.max.values])
        assert all([v == 5 for v in renew_unit.power_forecast.values])
        assert renew_unit.power.optimisation_value == mock_engine.variable[0]

    def test_solve_feasible_problem(self):
        timestamps = Timestamps([1, 2, 3])
        power_forecast = ConstantTimeseriesData(timestamps, 5)
        bounds = Bounds(0, 10)
        data = ControlRenewableUnitData('renew_unit_1', timestamps, power_forecast, bounds)
        renew_unit = RenewablePowerUnit(data)
        mock_engine = MockOptimisationEngine()
        renew_unit.extend_optimisation_model(mock_engine)

        initial_value = ConstantTimeseriesData(timestamps, 2)
        mock_opt_var_1 = mock_engine.add_timeindex_variable(
            'power_1',
            BoundTimeseries.constant_bound_timeseries(timestamps, bounds.min, bounds.max),
            initial_value
        )

        var_1 = MockIndexVariable('var_1', timestamps, mock_opt_var_1.value)

        mock_engine.add_index_constraint(
            'constraint_1', [var_1[i] + renew_unit.power[i] == 8 for i, t in enumerate(timestamps)]
        )

        objective = [var_1[i] + 0.1 * renew_unit.power[i] for i, t in enumerate(timestamps)]

        mock_engine.add_objective(
            'obj_1', OptimisationExpression(sum([o.value.value for o in objective]))
        )

        mock_engine.generate_model()
        mock_engine.solve()
        assert all([pytest.approx(p.evaluate(), 1e-4) == 5 for p in renew_unit.power])
        assert mock_engine.model.status == 'optimal'
        assert py.approx(mock_engine.model.value, 1e-3) == 3 * (0.1 * 5 + 3)

    def test_solve_zero_renew_power(self):
        timestamps = Timestamps([1, 2, 3])
        power_forecast = ConstantTimeseriesData(timestamps, 0)
        bounds = Bounds(0, 10)
        data = ControlRenewableUnitData('renew_unit_1', timestamps, power_forecast, bounds)
        renew_unit = RenewablePowerUnit(data)
        mock_engine = MockOptimisationEngine()
        renew_unit.extend_optimisation_model(mock_engine)

        initial_value = ConstantTimeseriesData(timestamps, 2)
        mock_opt_var_1 = mock_engine.add_timeindex_variable(
            'power_1',
            BoundTimeseries.constant_bound_timeseries(timestamps, bounds.min, bounds.max),
            initial_value
        )

        var_1 = MockIndexVariable('var_1', timestamps, mock_opt_var_1.value)

        mock_engine.add_index_constraint(
            'constraint_1', [var_1[i] + renew_unit.power[i] == 3 for i, t in enumerate(timestamps)]
        )

        objective = [var_1[i] + 0.1 * renew_unit.power[i] for i, t in enumerate(timestamps)]

        mock_engine.add_objective(
            'obj_1', OptimisationExpression(sum([o.value.value for o in objective]))
        )

        mock_engine.generate_model()
        mock_engine.solve()

        assert all([np.round(p.evaluate(), 3) == 0 for p in renew_unit.power])
        assert mock_engine.model.status == 'optimal'
        assert py.approx(mock_engine.model.value, 1e-3) == 9
