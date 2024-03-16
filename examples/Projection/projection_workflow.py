"""
Example 1:  Simple optimization of a 3D layout
Author:     Chad Peterson
"""

import openmdao.api as om
from SPI2py.API.system import System
from SPI2py.API.utilities import Multiplexer, MaxAggregator
from SPI2py.API.projection import Projection, Projections
from SPI2py.models.utilities.visualization import plot_problem
from SPI2py.models.utilities.inputs import read_input_file


# Read the input file
input_file = read_input_file('input.toml')

# Initialize the problem
prob = om.Problem()
model = prob.model

# Initialize the groups
model.add_subsystem('system', System(input_dict=input_file))
model.add_subsystem('projections', Projections(n_comp_projections=1,n_int_projections=0,min_xyz=-3, max_xyz=10, n_el_xyz=25))
model.connect('system.components.comp_0.transformed_sphere_positions', 'projections.projection_comp_0.points')

# Set the initial state
prob.setup()


# Configure the system
# prob.set_val('system.components.comp_0.translation', [2, 7, 0])

prob.set_val('system.components.comp_0.translation', [5, 5, 0])
prob.set_val('system.components.comp_0.rotation', [0, 0, 0])





prob.run_model()


# Check the initial state
plot_problem(prob)

densities = prob.get_val('projections.projection_comp_0.element_pseudo_densities')

total_density = densities.sum()
