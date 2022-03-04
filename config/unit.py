from data_loader.grid_forming_unit import StoragePowerPlantDataLoader, ThermalGeneratorDataLoader
from data_loader.grid_model import GridNetworkDataLoader
from data_loader.load_demand import LoadDemandDataLoader
from data_loader.renewable_unit import RenewableUnitDataLoader
from model.domain import BUS_ID
from model.grid_forming_unit import StoragePowerPlant, ThermalGenerator
from model.grid_model import GridNetwork
from model.interface import IPowerUnitConfig, IUnitConfig, IGridNetworkConfig
from model.load_demand import LoadDemand
from model.renewable_unit import RenewablePowerUnit
from model.storage import IUnitDataStorage


class RenewableUnitConfig(IPowerUnitConfig):

    def __init__(self, name: str, data_loader: RenewableUnitDataLoader, data_storage: IUnitDataStorage,
                 bus_id: BUS_ID):
        super().__init__(name, data_loader, data_storage, bus_id)
        self.data_loader = data_loader

    def create_unit(self):
        return RenewablePowerUnit(self.name, self.data_storage, self.data_loader)


class StoragePowerPlantConfig(IPowerUnitConfig):

    def __init__(self, name: str, data_loader: StoragePowerPlantDataLoader, data_storage: IUnitDataStorage,
                 bus_id: BUS_ID):
        super().__init__(name, data_loader, data_storage, bus_id)
        self.data_loader = data_loader

    def create_unit(self):
        return StoragePowerPlant(self.name, self.data_storage, self.data_loader)


class ThermalGeneratorConfig(IPowerUnitConfig):
    def __init__(self, name: str, data_loader: ThermalGeneratorDataLoader, data_storage: IUnitDataStorage,
                 bus_id: BUS_ID):
        super().__init__(name, data_loader, data_storage, bus_id)
        self.data_loader = data_loader

    def create_unit(self):
        return ThermalGenerator(self.name, self.data_storage, self.data_loader)


class LoadDemandConfig(IUnitConfig):

    def __init__(self, name: str, data_loader: LoadDemandDataLoader, data_storage: IUnitDataStorage,
                 bus_id: BUS_ID):
        super().__init__(name, data_loader, data_storage, bus_id)
        self.data_loader = data_loader

    def create_unit(self):
        return LoadDemand(self.name, self.data_storage, self.data_loader)


class GridNetworkConfig(IGridNetworkConfig):
    def __init__(self, name: str, data_loader: GridNetworkDataLoader, data_storage: IUnitDataStorage):
        super().__init__(name, data_loader, data_storage)
        self.data_loader = data_loader

    def create_unit(self):
        return GridNetwork(self.name, self.data_storage, self.data_loader)