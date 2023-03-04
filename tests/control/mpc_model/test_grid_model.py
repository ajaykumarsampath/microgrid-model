from operator import itemgetter

import numpy as np
import pytest

from common.model.component import GridLine
from common.timeseries.domain import Timestamps, ConstantTimeseriesData, Bounds, BoundTimeseries
from control.mpc_model.component.grid_model import ControlGridNetwork
from control.mpc_model.control_data_model import ControlGridNetworkData
from control.optimisation_engine.domain import OptimisationExpression
from tests.control.mock_optimisation_engine import MockOptimisationEngine, MockIndexVariable

from common.model.grid_network_util import GridNetworkUtils


class TestControlGridModel:
    def _setup(self):
        timestamps = Timestamps([1])
        bounds = Bounds(-1, 1)
        bus_ids = [f'bus_{i}' for i in range(3)]
        grid_lines = [
            GridLine(bus_ids[0], bus_ids[1], 1, bounds),
            GridLine(bus_ids[1], bus_ids[2], 1.5, bounds),
            GridLine(bus_ids[2], bus_ids[0], 1, bounds)
        ]
        self.data = ControlGridNetworkData('grid', timestamps, grid_lines, bus_ids)
        self.grid_model = ControlGridNetwork(self.data)
        self.mock_engine = MockOptimisationEngine()
        self.grid_model.extend_optimisation_model(self.mock_engine)

    def test_extend_optimisation_model(self):
        self._setup()
        assert len(self.grid_model.line_power) == 3
        assert len(self.grid_model.bus_power) == 3

    def _create_variable(self, name: str, value: float, timestamps: Timestamps):
        initial_value = ConstantTimeseriesData(timestamps, 0)
        mock_opt_var_1 = self.mock_engine.add_timeindex_variable(
            name,
            BoundTimeseries.constant_bound_timeseries(
                timestamps, value, value),
            initial_value
        )

        return MockIndexVariable(name, timestamps, mock_opt_var_1.value)

    @pytest.mark.parametrize("bus_powers", [
        ([1, -1, 0]), (-1, 1, 0), (-1, 0.5, 0.5)]
    )
    def test_feasible_problem(self, bus_powers):
        self._setup()

        for i, p in enumerate(bus_powers):
            self.mock_engine.add_index_constraint(
                f'bus_{i}_constraint_power',
                [self.grid_model.bus_power[i].get_value_timestamp(t) == p
                 for t in self.grid_model.timestamps]
            )

        objective = [
            self.grid_model.line_power[0][i] + self.grid_model.line_power[1][i] +
            self.grid_model.line_power[2][i]
            for i, t in enumerate(self.data.timestamps)
        ]

        self.mock_engine.add_objective(
            'obj_1', OptimisationExpression(sum([o.value.value for o in objective]))
        )

        self.mock_engine.generate_model()
        self.mock_engine.solve()

        dc_power_flow_matrix = GridNetworkUtils.calculate_dc_power_flow_matrix(
            self.data.buses, self.data.lines
        )

        for i, t in enumerate(self.grid_model.timestamps):
            bus_power = [np.round(p[i].evaluate(), 3) for p in self.grid_model.bus_power]
            phase_angle = dc_power_flow_matrix @ np.array(bus_power)
            phase_angle[0] = 0
            p = [phase_angle[0] - phase_angle[1], phase_angle[1] - phase_angle[2],
                 phase_angle[2] - phase_angle[0]]

            print(np.diag([c.admittance for c in self.data.lines]) @ np.array(p))

            line_power = [np.round(p[i].evaluate(), 3) for p in self.grid_model.line_power]

            from_buses, to_buses = zip(*[(line.from_bus, line.to_bus) for line in self.data.lines])
            for bus, power in zip(self.data.buses, bus_powers):
                from_line_power = itemgetter(
                    *[i for i, b in enumerate(from_buses) if b == bus]
                )(line_power)
                to_line_power = itemgetter(
                    *[i for i, b in enumerate(to_buses) if b == bus]
                )(line_power)
                assert power == from_line_power - to_line_power

        assert self.mock_engine.model.status == 'optimal'
