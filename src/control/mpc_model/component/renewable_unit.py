from common.timeseries.domain import BoundTimeseries, ConstantTimeseriesData
from control.mpc_model.control_data_model import ControlRenewableUnitData
from control.mpc_model.domain import IControlComponent
from control.optimisation_engine.interface import IOptimisationEngine
from control.optimisation_engine.variable import TimeIndexVariable, TimeIndexConstraint


class RenewablePowerUnit(IControlComponent):
    def __init__(self, data: ControlRenewableUnitData):
        self._data = data
        self._generate_variables()
        self._generate_constraint()

    @property
    def name(self):
        return self._data.name

    @property
    def power(self):
        return self._power

    @property
    def power_forecast(self):
        return self._data.power_forecast

    @property
    def timestamps(self):
        return self._data.timestamps

    def _generate_variables(self):
        power_bounds = BoundTimeseries.constant_bound_timeseries(
            self.timestamps,
            min_value=self._data.power_bounds.min,
            max_value=self._data.power_bounds.max,
        )
        self._power = TimeIndexVariable(
            f"{self.name}_power",
            bounds=power_bounds,
            initial_value=ConstantTimeseriesData(self.timestamps, 0),
        )

    def _generate_constraint(self):
        constraint = [
            self._power.get_value_index(i) <= self.power_forecast.get_value(t) for i, t in enumerate(self.timestamps)
        ]
        self._power_constraint = TimeIndexConstraint(f"{self.name}_available_power_limit", self.timestamps, constraint)

    def extend_optimisation_model(self, optimisation_engine: IOptimisationEngine):
        self._power.optimisation_value = optimisation_engine.add_timeindex_variable(
            self._power.name, self._power.bounds, self._power.initial_value
        )

        self._power_constraint.optimisation_value = optimisation_engine.add_index_constraint(
            self._power_constraint.name,
            [v.constraint_expression for v in self._power_constraint.value],
        )
