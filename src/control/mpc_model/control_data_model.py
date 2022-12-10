from dataclasses import dataclass
from typing import List

from common.model.component import GridLine, BUS_ID
from common.model.grid_network_util import GridNetworkUtils

from common.timeseries.domain import Timestamps, TimeseriesModel, Bounds, Timestamp


@dataclass
class ControlLoadDemandData:
    name: str
    timestamps: Timestamps
    power_forecast: TimeseriesModel
    bounds: Bounds


@dataclass
class ControlRenewableUnitData:
    name: str
    timestamps: Timestamps
    power_forecast: TimeseriesModel
    power_bounds: Bounds


@dataclass
class ControlGridNetworkData:
    name: str
    timestamps: Timestamps
    lines: List[GridLine]
    buses: List[BUS_ID]

    def __post_init__(self):
        if not GridNetworkUtils.check_bus_grid_lines(self.buses, self.lines):
            print('Something is wrong in grid model')


@dataclass
class ControlStoragePowerPlantData:
    name: str
    timestamps: Timestamps
    power_bounds: Bounds  # TODO convert bounds to bounded timeseries
    energy_bounds: Bounds
    current_energy: float


@dataclass
class ControlThermalGeneratorData:
    name: str
    timestamps: Timestamps
    power_bounds: Bounds  # TODO convert bounds to bounded timeseries
    current_switch_state: bool


@dataclass
class MeasurementStoragePowerPlantData:
    name: str
    timestamp: Timestamp
    energy: float
