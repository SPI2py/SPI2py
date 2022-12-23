"""Optimizer

Implements the nonlinear programming solver.

Additionally, defines the objective and constraint functions.

Instead of specifying one constraint function for interference, we split it up into
    1. component-component
    2. component-interconnect
    3. interconnect-interconnect
    4. structure-all
This provides more flexibility. For instance, depending on the level of fidelity, it can be hard to prevent two
interconnects that connect to the same component, from overlapping at the starting point. If you enforce a
zero-tolerance interference, then the solver will never be able to avoid collision and will get all confused. So
we slightly relax the interconnect-interconnect constraint. On the other hand, strictly enforcing interference
constraints for component-component doesn't seem to cause any problems.

In the future, if JAX supports adds native Windows support, or Numba adds support to Autograd,
we will also define the objective and constraint gradient functions here. Since the objective
and constraint functions call Numba-JIT-compiled functions, we can't apply algorithmic differentiation.
JAX allows this, but is only natively supported on Mac and Linux... many industry collaborators use Windows
and are not allowed to build from the source (or it just adds another level of difficulty).

"""

import numpy as np

from scipy.optimize import minimize, NonlinearConstraint

from src.SPI2Py.analysis.objective_functions import aggregate_pairwise_distance

from src.SPI2Py.analysis.constraint_functions import interference_component_component, interference_component_interconnect, \
    interference_interconnect_interconnect, interference_structure_all

import logging
# TODO Set filename...
logging.basicConfig(filename='examples/demo_1/design_vector.log', filemode='w', encoding='utf-8', level=logging.INFO, format='')
handler = logging.StreamHandler()
handler.terminator = ""

def log_design_vector(xk, *argv):
    """
    Logs the design vector...

    argv is since difference solvers pass diff arguments but we only want to capture xk
    Note: callback function args for trust-const method
    :return:
    """

    # Convert the NumPy array to a string for the logger
    xk_str = np.array2string(xk)

    # Log the design vector
    logging.info(xk_str)

    design_vector_log.append(xk)


def gradient_based_optimization(layout):
    """
    Constrained optimization...

    There are plans to use the JAX-wrapped implementation of scipy.optimize.minimize;
    however, it currently only supports the BFGS method for unconstrained optimization.

    Bounds are not implemented.

    For now objective function and constraints are hard-coded into this solver. Future versions
    may seek more flexibility.
    :param layout:
    :param x0: Initial design vector
    :return:
    """

    # Declare design vector log as global to read/write it
    global design_vector_log

    fun = aggregate_pairwise_distance

    x0 = layout.design_vector



    # NonlinearConstraint object for trust-constr method does not take kwargs
    # Use lambda functions to format constraint functions as needed with kwargs
    nlc_component_component = NonlinearConstraint(lambda x: interference_component_component(x, layout), -np.inf, -1.5)
    nlc_component_interconnect = NonlinearConstraint(lambda x: interference_component_interconnect(x, layout), -np.inf, 0)
    nlc_interconnect_interconnect = NonlinearConstraint(lambda x: interference_interconnect_interconnect(x, layout), -np.inf, 0)
    nlc_structure_all = NonlinearConstraint(lambda x: interference_structure_all(x, layout), -np.inf, 0)

    nlcs = [nlc_component_component]
    # nlcs = [nlc_component_component, nlc_component_interconnect]
    # nlcs = [nlc_component_component, nlc_component_interconnect, nlc_interconnect_interconnect, nlc_structure_all]

    options = {}

    # Add initial value
    design_vector_log.append(x0)

    # TODO Evaluate different solver methods and parametric tunings

    res = minimize(fun, x0, args=layout, method='trust-constr', constraints=nlcs, tol=1e-2,
                   options=options, callback=log_design_vector)

    # Add final value
    design_vector_log.append(res.x)

    # For troubleshooting
    print('Constraint is', interference_component_component(res.x, layout))

    return res, design_vector_log


# Define the log outside the functions so functions can declare it as a global variable and read/write to it
# without the callback function needing to take an argument
design_vector_log = []