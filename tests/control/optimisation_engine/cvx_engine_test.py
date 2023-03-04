from common.timeseries.domain import Bounds, BoundTimeseries, Timestamps, ConstantTimeseriesData
from control.optimisation_engine.cvx_engine.cvx_engine import CvxEngine, DuplicateOptimisationEngineValue, \
    OptimisationEngineStatus
from control.optimisation_engine.domain import OptimisationExpression
import cvxpy as cp

import pytest

from tests.control.mock_optimisation_engine import MockBaseVariable, \
    MockOptimisationVariable, MockIndexVariable


class TestCvxEngineInterface:
    def test_create_cvx_variable(self):
        cvx_engine = CvxEngine()
        variable = cvx_engine.add_variable('test', bounds=Bounds(0, 10), initial_value=1.5)

        expected_bound_constraint_name = ['test <= 10', '0 <= test']

        assert variable.bounds == Bounds(0, 10)
        assert len(cvx_engine.variable) == 1
        assert variable.value.name() == 'test'
        assert variable.value.name() == cvx_engine.variable[0].value.name()
        assert [v.name() in expected_bound_constraint_name for v in variable.bound_constraints]
        assert variable.evaluate() == 1.5

    def test_create_cvx_binary_variable(self):
        cvx_engine = CvxEngine()
        variable = cvx_engine.add_binary_variable('test', initial_value=1)

        assert variable.bounds == Bounds(0, 1)
        assert variable.value.name() == 'test'

    def test_create_cvx_constraint(self):
        cvx_engine = CvxEngine()
        var_1 = MockBaseVariable('var_1', MockOptimisationVariable(cp.Variable(1, name='var_1')))
        expr = var_1 <= 2
        cvx_constraint = cvx_engine.add_constraint('const_1', expr)
        assert cvx_constraint.value.name() == expr.value.value.name()

    def test_create_cvx_objective(self):
        cvx_engine = CvxEngine()
        var_1 = MockBaseVariable(
            'var_1', MockOptimisationVariable(cp.Variable(1, name='var_1'))
        )

        cvx_engine.add_objective('obj_1', OptimisationExpression(2 * var_1.value.value))
        expected_objective_name = '2.0 @ var_1'
        assert cvx_engine.objective.evaluate().args[0].name() == expected_objective_name

    def test_update_cvx_objective(self):
        cvx_engine = CvxEngine()
        var_1 = MockBaseVariable(
            'var_1', MockOptimisationVariable(cp.Variable(1, name='var_1'))
        )
        var_2 = MockBaseVariable(
            'var_2', MockOptimisationVariable(cp.Variable(1, name='var_2'))
        )

        cvx_engine.add_objective('obj_1', OptimisationExpression(2 * var_1.value.value))
        cvx_engine.update_objective(var_2.value, lambda x: x)
        expected_objective_name = '2.0 @ var_1 + var_2'

        assert cvx_engine.objective.value.name() == expected_objective_name

    def test_create_index_cvx_variable(self):
        cvx_engine = CvxEngine()
        timestamps = Timestamps([1, 2, 3, 4])
        bounds = BoundTimeseries(
            min=ConstantTimeseriesData(timestamps, 0),
            max=ConstantTimeseriesData(timestamps, 1)
        )
        initial_value = ConstantTimeseriesData(timestamps, 0.5)

        cvx_index_variable = cvx_engine.add_timeindex_variable(
            'var_1', bounds, initial_value
        )

        assert len(cvx_engine.variable) == 1
        assert cvx_index_variable.value.name() == 'var_1'
        assert [cvx_engine.variable[0].value[i].name() == f'var_1[{i}]'
                for i, t in enumerate(timestamps)]
        assert all([v == 0.5 for v in cvx_index_variable.value.value])

    def test_create_index_cvx_constraint(self):
        cvx_engine = CvxEngine()
        timestamps = Timestamps([1, 2, 3])
        var_list = [
            MockBaseVariable(
                f'var_{i}', MockOptimisationVariable(cp.Variable(1, name=f'var_{i}', value=[i])))
            for i, t in enumerate(timestamps)]
        constraint_expr = [v <= 1 for v in var_list]
        cvx_constraint = cvx_engine.add_index_constraint('test', constraint_expr)

        expected_name = ['var_0 <= 1.0', 'var_1 <= 1.0', 'var_2 <= 1.0']

        assert all([v.name() in expected_name for v in cvx_constraint.value])
        assert len(cvx_engine.constraint) == 1

    def test_duplicate_optimisation_value(self):
        cvx_engine = CvxEngine()
        cvx_engine.add_variable('test', bounds=Bounds(0, 10), initial_value=1.5)

        with pytest.raises(DuplicateOptimisationEngineValue):
            cvx_engine.add_variable('test', bounds=Bounds(0, 10), initial_value=1.5)

    def test_solving_cvx_solver(self):
        cvx_engine = CvxEngine()
        cvx_var_1 = cvx_engine.add_variable('var_1', Bounds(0, 10), 0)

        cvx_var_2 = cvx_engine.add_variable('var_2', Bounds(0, 10), 0)

        var_1 = MockBaseVariable('var_1', cvx_var_1.value)

        var_2 = MockBaseVariable('var_2', cvx_var_2.value)

        cvx_engine.add_constraint('constraint', var_1 <= var_2)
        cvx_engine.add_constraint('constraint_1', var_1 + var_2 == 2.5)

        obj_expr = var_1 + var_2
        cvx_engine.add_objective('objective', OptimisationExpression(obj_expr.value.value))

        cvx_engine.generate_optimisation_model()
        cvx_engine.solve()

        assert cvx_engine.variable[0].value.value == var_1.value.value
        assert cvx_engine.variable[1].value.value == var_2.value.value
        assert pytest.approx(cvx_engine.value, 1e-3) == 2.5
        assert cvx_engine.status == OptimisationEngineStatus.Optimal

    def test_cvx_solver_binary_problem(self):
        cvx_engine = CvxEngine()
        cvx_var_1 = cvx_engine.add_variable('var_1', Bounds(0, 10), 0)

        cvx_var_2 = cvx_engine.add_variable('var_2', Bounds(2, 10), 0)

        cvx_binary_var = cvx_engine.add_binary_variable('binary_var', 1)

        var_1 = MockBaseVariable('var_1', cvx_var_1.value)
        var_2 = MockBaseVariable('var_2', cvx_var_2.value)
        binary_var = MockBaseVariable('binary_var', cvx_binary_var.value)

        cvx_engine.add_constraint('constraint', var_1 <= var_2)
        cvx_engine.add_constraint('constraint_1', var_1 + var_2 == 2.5)
        cvx_engine.add_constraint('constraint_2', var_1 <= 5 * binary_var)
        cvx_engine.add_constraint('constraint_3', var_2 >= 5 * binary_var)

        obj_expr = var_1 + var_2
        cvx_engine.add_objective('objective', OptimisationExpression(obj_expr.value.value))

        cvx_engine.generate_optimisation_model()
        cvx_engine.solve()

        assert cvx_engine.variable[0].value.value == var_1.value.value
        assert cvx_engine.variable[1].value.value == var_2.value.value
        assert pytest.approx(cvx_engine.value, 1e-3) == 2.5
        assert cvx_engine.status == OptimisationEngineStatus.Optimal

    def test_cvx_solve_timeindex_problem(self):
        cvx_engine = CvxEngine()
        timestamps = Timestamps([1, 2, 3, 4])

        cvx_var_1 = cvx_engine.add_timeindex_variable(
            'var_1', BoundTimeseries.constant_bound_timeseries(timestamps, 0, 1),
            ConstantTimeseriesData(timestamps, 1)
        )

        cvx_var_2 = cvx_engine.add_timeindex_variable(
            'var_2', BoundTimeseries.constant_bound_timeseries(timestamps, 0, 1),
            ConstantTimeseriesData(timestamps, 1)
        )

        var_1 = MockIndexVariable('var_1', timestamps, cvx_var_1.value)
        var_2 = MockIndexVariable('var_2', timestamps, cvx_var_2.value)

        constraint_expr = [v_1 + v_2 == 1.5 for v_1, v_2 in zip(var_1.variable, var_2.variable)]

        cvx_engine.add_index_constraint('test', constraint_expr)

        objective_expr = sum([v_1 + 0.3 * v_2 for v_1, v_2 in zip(var_1.variable, var_2.variable)])
        cvx_engine.add_objective(
            'obj', OptimisationExpression(objective_expr.value.value)
        )

        cvx_engine.generate_optimisation_model()
        cvx_engine.solve()

        expected_objective = sum(
            [v_1 + 0.3 * v_2 for v_1, v_2 in zip(var_1.value, var_2.value)]
        )

        assert cvx_engine.status == OptimisationEngineStatus.Optimal
        assert all([pytest.approx(v, 0.5, 1e-3) == 0.5 for v in var_1.value])
        assert all([pytest.approx(v, 1, 1e-3) == 1 for v in var_2.value])
        assert pytest.approx(
            expected_objective, cvx_engine.objective.value.value, 1e-3) == expected_objective
        assert len(cvx_engine.constraint) == 1
