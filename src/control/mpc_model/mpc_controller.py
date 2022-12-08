from typing import List

from control.mpc_model.domain import Horizon, IControlComponent
from control.optimisation_engine.interface import IOptimisationEngine


class MPCModelController:
    def __init__(self, optimisation_engine: IOptimisationEngine, horizon: Horizon):
        self._optimisation_engine = optimisation_engine
        self._horizon = horizon

        self._timestamps = self._optimisation_engine.add_timeindex_parameter(
            'timestamps', horizon.timestamps)

    def solve(self, component_model: List[IControlComponent]):
        for model in component_model:
            model.extend_optimisation_model(self._optimisation_engine)

        self._optimisation_engine.solve()

        results = []
        for model in component_model:
            results.append(model.get_results())

        return results
