from typing import List

from shared.component import ComponentSimulationData


class IComponentDataStorage:
    def add_simulation_data(self, current_timestamp: int, data: ComponentSimulationData):
        raise NotImplementedError

    def get_historical_data(self, unit_id: str, since: int, until: int = None) \
            -> List[ComponentSimulationData]:
        raise NotImplementedError
