from typing import List, Any, Union

import config.interface
from config.component.grid_forming_unit import default_thermal_config_registry, \
    default_storage_config_registry
from config.component.grid_model import default_single_grid_network_registry, \
    default_grid_network_registry
from config.component.load_demand import default_load_config_registry
from config.component.renewable_unit import default_renewable_config_registry
from config.interface import UnknownComponentConfigType, ComponentConfigRegistryData, Reference, \
    ClassImportModuler, IUnitConfig, IGridNetworkConfig


class IComponentRegistry:
    def get_component_config_references(self):
        raise NotImplementedError

    @staticmethod
    def validate_component_registry_data(component_registry: List[ComponentConfigRegistryData]):
        reference_ = [c.reference for c in component_registry]
        config_class_module_ = [c.config_class_module for c in component_registry]
        for i, c in enumerate(config_class_module_):
            if c in config_class_module_[i + 1:]:
                return False
        if len(reference_) == len(list(set(reference_))):
            return True
        else:
            return False

    def get_component_config_reference(self, config: Union[IUnitConfig, IGridNetworkConfig]) \
            -> Reference:
        raise NotImplementedError

    def get_component_config(self, reference: Reference) -> ComponentConfigRegistryData:
        raise NotImplementedError

    def get_thermal_config_references(self) -> List[Reference]:
        raise NotImplementedError

    def get_storage_config_references(self) -> List[Reference]:
        raise NotImplementedError

    def get_renewable_config_references(self) -> List[Reference]:
        raise NotImplementedError

    def get_load_config_references(self) -> List[Reference]:
        raise NotImplementedError

    def get_grid_config_references(self) -> List[Reference]:
        raise NotImplementedError

class DefaultComponentRegistry(IComponentRegistry):
    component_registry = [
        default_thermal_config_registry, default_renewable_config_registry,
        default_storage_config_registry, default_load_config_registry,
        default_single_grid_network_registry, default_grid_network_registry
    ]
    def __init__(self):
        if not self.validate_component_registry_data(self.component_registry):
            raise ValueError('Config registry should has unique reference and config class modules')

    def get_component_config_references(self):
        return [c.reference for c in self.component_registry]

    def get_component_config(self, reference: str) -> ComponentConfigRegistryData:
        try:
            return [c for c in self.component_registry if c.reference == reference][0]
        except IndexError:
            raise UnknownComponentConfigType(f'{reference} is not part of the config registry')

    def get_component_config_reference(self, config: Union[IUnitConfig, IGridNetworkConfig]) -> Reference:
        class_importer = ClassImportModuler(config.__module__, config.__class__.__name__)

        try:
            return [c.reference for c in self.component_registry if c.config_class_module == class_importer][0]
        except IndexError:
            raise UnknownComponentConfigType(
                f'config class {config.__name__} is not part of the config registry'
            )

    def get_thermal_config_references(self) -> List[Reference]:
        return [c.reference for c in self.component_registry if c is default_thermal_config_registry]

    def get_storage_config_references(self) -> List[Reference]:
        return [c.reference for c in self.component_registry if c is default_storage_config_registry]

    def get_renewable_config_references(self) -> List[Reference]:
        return [c.reference for c in self.component_registry if c is default_renewable_config_registry]

    def get_load_config_references(self) -> List[Reference]:
        return [c.reference for c in self.component_registry if c is default_load_config_registry]

    def get_grid_config_references(self) -> List[Reference]:
        return [c.reference for c in self.component_registry if c is default_grid_network_registry or
                c is default_single_grid_network_registry]


def default_component_registry() -> DefaultComponentRegistry:
    return DefaultComponentRegistry()
