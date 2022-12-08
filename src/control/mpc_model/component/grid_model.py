from typing import List

from common.model.grid_network_util import GridNetworkUtils
from common.timeseries.domain import Bounds, ConstantTimeseriesData, \
    BoundTimeseries
from control.mpc_model.control_data_model import ControlGridNetworkData
from control.mpc_model.domain import IControlComponent
from control.optimisation_engine.interface import IOptimisationEngine
from control.optimisation_engine.operation import VariableArray, matmul
from control.optimisation_engine.variable import TimeIndexVariable, TimeIndexConstraint


class GridNetwork(IControlComponent):
    def __init__(self, data: ControlGridNetworkData):
        self._data = data
        self._admittance_matrix = GridNetworkUtils.calculate_admittance_matrix(
            self._data.buses, self._data.lines
        )
        self._dc_power_flow_matrix = GridNetworkUtils.calculate_dc_power_flow_matrix(
            self._data.buses, self._data.lines
        )
        self._default_bus_limits = Bounds(-100, 100)
        self._generate_variables()
        self._generate_pf_constraint()

    @property
    def line_power(self) -> List[TimeIndexVariable]:
        return self._line_power

    @property
    def bus_power(self):
        return self._bus_power

    @property
    def name(self) -> str:
        return self._data.name

    @property
    def timestamps(self):
        return self._data.timestamps

    def _generate_variables(self):
        line_power = []
        for line in self._data.lines:
            power = TimeIndexVariable(
                f'{self.name}_line_power_{line.to_bus}{line.from_bus}',
                bounds= BoundTimeseries(
                    min=ConstantTimeseriesData(self.timestamps, line.bounds.min),
                    max=ConstantTimeseriesData(self.timestamps, line.bounds.max)
                ), initial_value=ConstantTimeseriesData(self.timestamps, 0)
            )
            line_power.append(power)

        self._line_power = line_power

        bus_power = []
        for bus in self._data.buses:
            power = TimeIndexVariable(
                f'{self.name}_bus_{bus}', bounds=BoundTimeseries(
                    min=ConstantTimeseriesData(self.timestamps, self._default_bus_limits.min),
                    max=ConstantTimeseriesData(self.timestamps, self._default_bus_limits.max)
                ), initial_value=ConstantTimeseriesData(self.timestamps, 0)
            )
            bus_power.append(power)

        self._bus_power = bus_power


    def _calculate_line_power(self, bus_power_var_ts: VariableArray,
                              line_power_var_ts: VariableArray):
        phase_angle = matmul(self._dc_power_flow_matrix, bus_power_var_ts)
        phase_angle[0] = 0

        constraint = []
        for count, line in enumerate(self._data.lines):
            to_bus_index = self._data.buses.index(line.to_bus)
            from_bus_index = self._data.buses.index(line.from_bus)
            c_constraint = line_power_var_ts[count] == \
                line.admittance * (phase_angle[from_bus_index] - phase_angle[to_bus_index])
            constraint.append(c_constraint)

        return constraint

    def _pf_constraint(self, bus_power_var_ts: VariableArray,
                              line_power_var_ts: VariableArray):
        phase_angle = matmul(self._dc_power_flow_matrix, bus_power_var_ts)
        phase_angle[0] = 0

        constraint = []
        for count, line in enumerate(self._data.lines):
            to_bus_index = self._data.buses.index(line.to_bus)
            from_bus_index = self._data.buses.index(line.from_bus)
            c_constraint = line_power_var_ts[count] == \
                line.admittance * (phase_angle[from_bus_index] - phase_angle[to_bus_index])
            constraint.append(c_constraint)

        return constraint

    def _generate_pf_constraint(self):
        pf_constraint = []
        for t in self.timestamps:
            line_var_ts = VariableArray([l.get_value_timestamp(t) for l in self._line_power])
            bus_var_ts = VariableArray([b.get_value_timestamp(t) for b in self._bus_power])

            pf_constraint_ts = self._pf_constraint(bus_var_ts, line_var_ts)
            pf_constraint.extend(pf_constraint_ts)

        number_lines = len(self._data.lines)
        self._pf_constraint = []

        for i in range(0, number_lines):
            pf_constraint_line = TimeIndexConstraint(
                f'{self.name}_line_{i}', self.timestamps,
                [pf_constraint[j * number_lines + i] for j, _ in enumerate(self.timestamps)]
            )
            self._pf_constraint.append(pf_constraint_line)

    def extend_optimisation_model(self, optimisation_engine: IOptimisationEngine):
        for line in self._line_power:
            line.optimisation_value = optimisation_engine.add_timeindex_variable(
                line.name, line.bounds, line.initial_value
            )

        for line in self._pf_constraint:
            line.optimisation_value = optimisation_engine.add_timeindex_constraint(
                line.name, [v.constraint_expression.value for v in line.value]
            )
