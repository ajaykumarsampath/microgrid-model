from control.mpc_model.control_data_model import ControlLoadDemandData
from control.mpc_model.domain import IControlComponent
from control.optimisation_engine.interface import IOptimisationEngine
from control.optimisation_engine.variable import TimeIndexParameter


class LoadDemand(IControlComponent):
    def __init__(self, data: ControlLoadDemandData):
        self._data = data

        self._generate_variables()

    @property
    def power(self) -> TimeIndexParameter:
        return self._power

    @property
    def name(self) -> str:
        return self._data.name

    @property
    def timestamps(self):
        return self._data.timestamps

    def _generate_variables(self):
        self._power = TimeIndexParameter(f"{self.name}_power", parameter_value=self._data.power_forecast)

    def extend_optimisation_model(self, optimisation_engine: IOptimisationEngine):
        self._power.optimisation_value = optimisation_engine.add_timeindex_parameter(
            self._power.name, self.power.parameter_value
        )
