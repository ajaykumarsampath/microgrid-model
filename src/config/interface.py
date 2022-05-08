from dataclasses import dataclass
from typing import Any

import pydantic
from dacite import from_dict

from data_loader.interface import IGeneratorDataLoader
from model.component_interface import IComponent, IGridNetwork
from model.generator_interface import IGeneratorComponent
from shared.component import ComponentType
from shared.data_loader import IUnitConfigData, IGeneratorConfigData, IGridNetworkConfigData


class IUnitConfig:
    def __init__(self, config_data: IUnitConfigData):
        self.config_data = config_data

    @property
    def name(self):
        return self.config_data.name

    @property
    def bus_id(self):
        return self.config_data.bus_id

    @property
    def data_loader_data(self):
        return self.config_data.data_loader_data

    @property
    def component_type(self) -> ComponentType:
        return self.config_data.component_type

    def create_unit(self) -> IComponent:
        raise NotImplementedError

    def create_data_loader(self):
        raise NotImplementedError


class IGridNetworkConfig:
    def __init__(self, config_data: IGridNetworkConfigData):
        self.config_data = config_data

    @property
    def component_type(self) -> ComponentType:
        return self.config_data.component_type

    def create_grid_network(self) -> IGridNetwork:
       raise NotImplementedError

    def create_data_loader(self):
        raise NotImplementedError

class IGeneratorComponentConfig(IUnitConfig):
    def __init__(self, config_data: IGeneratorConfigData):
        super().__init__(config_data)
        self.config_data = config_data

    @property
    def data_loader_data(self):
        return self.config_data.data_loader_data

    def create_unit(self) -> IGeneratorComponent:
        raise NotImplementedError

    def create_data_loader(self) -> IGeneratorDataLoader:
        raise NotImplementedError

Reference = str

"""
from importlib import import_module


    def import_class(path):
        package, klass = path.rsplit('.', 1)
        module = import_module(package)
        return getattr(module, klass)
    
    
    def import_instance(path):
        package, class_name = path.rsplit('.', 1)
        module = import_module(package)
        klass = getattr(module, class_name)
    return klass()
"""

class ClassImportModuler:
    def __init__(self, module: str, value: str):
        self.module = module
        self.value = value

    def create_class(self) -> Any:
        try:
           import importlib
           module = importlib.import_module(self.module)
           class_ = getattr(module, self.value)
           return class_
        except ImportError as e:
            raise WrongComponentConfigImporter(f'config error {e}')

    def __eq__(self, other):
        try:
            return self.value == other.value and self.module == other.module
        except Exception:
            return False

    def create_class_instance(self, *args, **kwargs):
        pass

    def __call__(self, *args, **kwargs):
        return self.create_class()


@dataclass
class ComponentConfigRegistryData:
    reference: Reference
    config_class_module: ClassImportModuler
    config_data_module: ClassImportModuler

    def create_config_class(self, dict_: dict) -> Any: #IUnitConfig:
        try:
            config_data_type = self.config_data_module.create_class()
            config_class_type = self.config_class_module.create_class()
            data = from_dict(config_data_type, dict_)
            return config_class_type(data)
        except WrongComponentConfigImporter as e:
            raise WrongComponentConfigData(f'Wrong config data at reference {self.reference} as {e}')

    def get_config_schema(self) -> dict:
        config_data_type = self.config_data_module.create_class()
        pydantic_cls = pydantic.dataclasses.dataclass(config_data_type)
        schema = pydantic_cls.__pydantic_model__.schema()
        return schema


class UnknownComponentConfigType(Exception):
    pass

class WrongComponentConfigData(Exception):
    pass

class WrongComponentConfigImporter(Exception):
    pass
