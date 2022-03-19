from data_loader.grid_forming_unit import StoragePowerPlantDataLoader, ThermalGeneratorDataLoader
from data_loader.grid_model import IGridNetworkDataLoader
from data_loader.load_demand import ILoadDemandDataLoader
from data_loader.renewable_unit import IRenewableUnitDataLoader
from model.domain import BUS_ID, ComponentType
from model.grid_forming_unit import StoragePowerPlant, ThermalGenerator
from model.grid_model import GridNetwork
from model.component_interface import IUnitConfig, IGridNetworkConfig
from model.generator_interface import IGeneratorComponentConfig
from model.load_demand import LoadDemand
from model.renewable_unit import RenewablePowerUnit


class RenewableUnitConfig(IGeneratorComponentConfig):

    def __init__(self, name: str, data_loader: IRenewableUnitDataLoader, bus_id: BUS_ID):
        super().__init__(name, data_loader, bus_id)
        self.data_loader = data_loader
        self._component_type = ComponentType.Renewable

    def create_unit(self):
        return RenewablePowerUnit(self.name, self.data_loader)


class StoragePowerPlantConfig(IGeneratorComponentConfig):

    def __init__(self, name: str, data_loader: StoragePowerPlantDataLoader, bus_id: BUS_ID):
        super().__init__(name, data_loader, bus_id)
        self.data_loader = data_loader
        self._component_type = ComponentType.Storage

    def create_unit(self):
        return StoragePowerPlant(self.name, self.data_loader)


class ThermalGeneratorConfig(IGeneratorComponentConfig):
    def __init__(self, name: str, data_loader: ThermalGeneratorDataLoader, bus_id: BUS_ID):
        super().__init__(name, data_loader, bus_id)
        self.data_loader = data_loader
        self._component_type = ComponentType.Thermal

    def create_unit(self):
        return ThermalGenerator(self.name, self.data_loader)


class LoadDemandConfig(IUnitConfig):
    def __init__(self, name: str, data_loader: ILoadDemandDataLoader, bus_id: BUS_ID):
        super().__init__(name, data_loader,  bus_id)
        self.data_loader = data_loader
        self._component_type = ComponentType.Load

    def create_unit(self):
        return LoadDemand(self.name, self.data_loader)

class GridNetworkConfig(IGridNetworkConfig):
    def __init__(self, name: str, data_loader: IGridNetworkDataLoader):
        super().__init__(name, data_loader)
        self.data_loader = data_loader
        self._component_type = ComponentType.Grid

    def create_unit(self):
        return GridNetwork(self.name, self.data_loader)