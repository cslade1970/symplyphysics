#!/usr/bin/env python3
from sympy import solve, pretty, symbols
from sympy.plotting import plot
from sympy import pretty
from sympy.plotting import plot
from sympy.plotting.plot import MatplotlibBackend
from symplyphysics.laws.dynamics import free_fall_acceleration_from_height as acceleration

print("Formula is:\n{}".format(acceleration.print()))
height = symbols('height')
solved = solve(acceleration.law, acceleration.acceleration_free_fall, dict=True)[0][acceleration.acceleration_free_fall]
result_accel = solved.subs({
             acceleration.height: acceleration.height,
             acceleration.constant_gravitation: 6.672e-11,
             acceleration.earth_mass: 5.976e+24,
             acceleration.earth_radius: 6.371e+6})

print("\nFree fall accelleration on Earth surface function is:\n{}".format(
    pretty(result_accel, use_unicode=False)))

p1 = plot(
    result_accel,
    (acceleration.height, 0, 10000),
    ylim=(9.74,9.85),
    axis_center=(0.0,9.75),
    line_color='green',
    title='Free fall acceleration(height)',
    label='Acceleration(height)',
    legend=True,
    backend=MatplotlibBackend,
    show=False)
p1.show()
