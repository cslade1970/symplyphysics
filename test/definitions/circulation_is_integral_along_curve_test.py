from collections import namedtuple
from pytest import approx, fixture

from math import pi
from sympy import sin, cos, sqrt
from sympy.vector import CoordSys3D
from symplyphysics import (
    units, convert_to, SI, expr_to_quantity
)
from symplyphysics.definitions import circulation_is_integral_along_curve as circulation_def

@fixture
def test_args():
    C = CoordSys3D('C')
    force_unit = units.Quantity('force_unit')
    SI.set_quantity_dimension(force_unit, units.force)
    SI.set_quantity_scale_factor(force_unit, 1 * units.newton)
    radius_unit = units.Quantity('radius_unit')
    SI.set_quantity_dimension(radius_unit, units.length)
    SI.set_quantity_scale_factor(radius_unit, 1 * units.meter)
    # field is a field of gravitational forces, force is directed down by the Y coordinate
    # field is (0, -1 * G * m * M / y**2)
    # G * m * M = k * force * length**2 / mass**2
    # let k = 1
    field = 0 * C.i + -1 * force_unit * radius_unit**2 / C.y**2 * C.j

    Args = namedtuple('Args', ['C', 'force_unit', 'radius_unit', 'field'])
    return Args(C=C, force_unit=force_unit, radius_unit=radius_unit, field=field)


def test_basic_circulation(test_args):
    field = test_args.C.y * test_args.C.i + (test_args.C.z + test_args.C.x) * test_args.C.k
    curve = cos(circulation_def.parameter) * test_args.C.i + sin(circulation_def.parameter) * test_args.C.j
    result_expr = circulation_def.calculate_circulation(field, curve, 0, pi / 2)
    assert result_expr.evalf(4) == approx(-pi / 4, 0.001)

def test_two_parameters_circulation(test_args):
    field = test_args.C.y * test_args.C.i + -1 * test_args.C.x * test_args.C.j
    # circle function is: x**2 + y**2 = 9
    # parametrize by circulation_def.parameter
    circle = 3 * cos(circulation_def.parameter) * test_args.C.i + 3 * sin(circulation_def.parameter) * test_args.C.j
    result_expr = circulation_def.calculate_circulation(field, circle, 0, 2 * pi)
    assert result_expr.evalf(4) == approx(-18 * pi, 0.001)
    # now try to define trajectory without parametrization
    # parametrized solution uses angle [0, 2*pi] that corresponds to the counter-clockwise direction
    # so we should integrate in the same direction: [r, -r] for upper part of the circle and [-r, r] for lower
    # y = sqrt(9 - x**2) for upper part of the circle
    # y = -sqrt(9 - x**2) for lower part of the circle
    circle_implicit_up = circulation_def.parameter * test_args.C.i + sqrt(9 - circulation_def.parameter**2) * test_args.C.j
    result_expr_up = circulation_def.calculate_circulation(field, circle_implicit_up, 3, -3)
    circle_implicit_down = circulation_def.parameter * test_args.C.i - sqrt(9 - circulation_def.parameter**2) * test_args.C.j
    result_expr_down = circulation_def.calculate_circulation(field, circle_implicit_down, -3, 3)
    assert (result_expr_up + result_expr_down).evalf(4) == approx(-18 * pi, 0.001)

def test_orthogonal_movement_circulation(test_args):
    field = test_args.C.y * test_args.C.i + -1 * test_args.C.x * test_args.C.j + test_args.C.k
    # trajectory is upwards helix
    helix = cos(circulation_def.parameter) * test_args.C.i + sin(circulation_def.parameter) * test_args.C.j + circulation_def.parameter * test_args.C.k
    result_expr = circulation_def.calculate_circulation(field, helix, 0, 2 * pi)
    assert result_expr == 0
    # trajectory is upwards straight line
    trajectory_vertical = 1 * test_args.C.i + circulation_def.parameter * test_args.C.k
    result_expr = circulation_def.calculate_circulation(field, trajectory_vertical, 0, 2 * pi)
    assert result_expr.evalf(4) == approx(2 * pi, 0.001)

def test_force_circulation(test_args):
    # trajectory is linear: y = x
    #HACK: gravitational force is undefined at 0 distance, use any non-zero value
    trajectory = circulation_def.parameter * test_args.C.i + circulation_def.parameter * test_args.C.j
    result_expr = circulation_def.calculate_circulation(test_args.field, trajectory, 1 * test_args.radius_unit, 2 * test_args.radius_unit)
    result = expr_to_quantity(result_expr, 'force_work')
    assert SI.get_dimension_system().equivalent_dims(result.dimension, units.energy)
    result_work = convert_to(result, units.joule).subs({units.joule: 1}).evalf(2)
    assert result_work == approx(-0.5, 0.01)

def test_force_circulation_horizontal(test_args):
    # trajectory is horizontal line: y = 5
    trajectory_horizontal = circulation_def.parameter * test_args.C.i + 5 * test_args.radius_unit * test_args.C.j
    result_expr = circulation_def.calculate_circulation(test_args.field, trajectory_horizontal, 1 * test_args.radius_unit, 2 * test_args.radius_unit)
    assert result_expr == 0

def test_force_circulation_horizontal_up(test_args):
    # trajectory is vertical line: x = 5
    trajectory_vertical = 5 * test_args.radius_unit * test_args.C.i + circulation_def.parameter * test_args.C.j
    result_expr = circulation_def.calculate_circulation(test_args.field, trajectory_vertical, 1 * test_args.radius_unit, 2 * test_args.radius_unit)
    result = expr_to_quantity(result_expr, 'force_work_vertical_up')
    result_work = convert_to(result, units.joule).subs({units.joule: 1}).evalf(2)
    assert result_work == approx(-0.5, 0.01)

def test_force_circulation_horizontal_down(test_args):
    # trajectory is vertical line, but with down direction: x = 6
    trajectory_vertical = 6 * test_args.radius_unit * test_args.C.i + circulation_def.parameter * test_args.C.j
    result_expr = circulation_def.calculate_circulation(test_args.field, trajectory_vertical, 2 * test_args.radius_unit, 1 * test_args.radius_unit)
    result = expr_to_quantity(result_expr, 'force_work_vertical_down')
    result_work = convert_to(result, units.joule).subs({units.joule: 1}).evalf(2)
    assert result_work == approx(0.5, 0.01)

