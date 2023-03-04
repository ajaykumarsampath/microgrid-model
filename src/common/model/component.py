from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Dict, List

from common.timeseries.domain import Timestamp, Bounds


BUS_ID = str


class ComponentType(Enum):
    Load = "Load"
    Renewable = "Renewable"
    PV = "PVPlant"
    WIND = "WindPlant"
    Storage = "Storage"
    Thermal = "Thermal"
    Grid = "Grid"
    Unknown = "None"


@dataclass
class GridLine:
    from_bus: BUS_ID
    to_bus: BUS_ID
    admittance: Optional[float] = field(default=None)
    bounds: Optional[Bounds] = field(default=None)

    def __eq__(self, other):
        try:
            if (
                other.to_bus in [self.to_bus, self.from_bus] and
                other.from_bus in [self.to_bus, self.from_bus] and
                self.admittance == other.admittance
            ):
                return True
            else:
                return False
        except AttributeError:
            return False

    def __post_init__(self):
        if self.to_bus == self.from_bus:
            raise ValueError("to_bus and from_bus of the line are same")

    def is_connected_to_bus(self, bus_id: BUS_ID):
        return bus_id == self.to_bus or bus_id == self.from_bus


@dataclass
class ControlComponentParameters:
    grid_forming_flag: bool = False
    droop_gain: float = 0
    charging_efficiency: float = 1
    discharging_efficiency: float = 1


@dataclass
class ControlComponentData:
    name: str
    component_type: ComponentType
    timestamp: Timestamp
    power_bound: Optional[Bounds] = None
    measurements: Optional[Dict] = None
    parameters: Optional[ControlComponentParameters] = ControlComponentParameters()
    energy_bound: Optional[Bounds] = None

    def __post_init__(self):
        if self.component_type == ComponentType.Storage and self.energy_bound is None:
            raise ValueError("")


@dataclass
class GridControlComponentData:
    name: str
    component_type: ComponentType
    grid_lines: List[GridLine]
