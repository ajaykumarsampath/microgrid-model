from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

BUS_ID = str


@dataclass
class Bounds:
    min: float
    max: float

    def __post_init__(self):
        if self.min > self.max:
            raise ValueError('Bounds are not correct: min should be less than max')


@dataclass
class GridLine:
    from_bus: BUS_ID
    to_bus: BUS_ID
    admittance: Optional[float] = field(default=None)
    bounds: Optional[Bounds] = field(default=None)

    def __eq__(self, other):
        try:
            if other.to_bus in [self.to_bus, self.from_bus] and \
                    other.from_bus in [self.to_bus, self.from_bus] and \
                    self.admittance == other.admittance:
                return True
            else:
                return False
        except AttributeError:
            return False

    def __post_init__(self):
        if self.to_bus == self.from_bus:
            raise ValueError('to_bus and from_bus of the line are same')


@dataclass
class ComponentSimulationData:
    name: str
    values: dict


class ComponentType(Enum):
    Load = 'Load'
    Renewable = 'Renewable'
    Storage = 'Storage'
    Thermal = 'Thermal'
    Grid = 'Grid'
    Unknown = 'None'
