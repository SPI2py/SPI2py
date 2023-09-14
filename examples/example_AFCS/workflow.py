"""
Example 1:  Simple optimization of a 3D layout
Author:     Chad Peterson
"""

# %% Import packages

import torch
import openmdao.api as om
from SPI2py import KinematicsInterface, Kinematics, Component, Interconnect  # , System

# %% Define the kinematics model

c1a = Component(name='radiator_and_ion_exchanger_1a',
                color='purple',
                degrees_of_freedom=('x', 'y', 'z', 'rx', 'ry', 'rz'),
                filepath='part_models/radiator_and_ion_exchanger.xyzr',
                ports=[{'name': 'supply', 'origin': [0.2850/2+0.05, 0, 0], 'radius': 0.05},
                       {'name': 'return', 'origin': [-(0.2850/2+0.05), 0, 0], 'radius': 0.05}])

c1b = Component(name='radiator_and_ion_exchanger_1b',
                color='purple',
                degrees_of_freedom=('x', 'y', 'z', 'rx', 'ry', 'rz'),
                filepath='part_models/radiator_and_ion_exchanger.xyzr',
                ports=[{'name': 'supply', 'origin': [0.2850/2+0.05, 0, 0], 'radius': 0.05},
                       {'name': 'return', 'origin': [-(0.2850/2+0.05), 0, 0], 'radius': 0.05}])

c2a = Component(name='pump_2a',
                color='blue',
                degrees_of_freedom=('x', 'y', 'z', 'rx', 'ry', 'rz'),
                filepath='part_models/pump.xyzr',
                ports=[{'name': 'supply', 'origin': [0, 0, 0], 'radius': 0.05},
                       {'name': 'return', 'origin': [0, 0, 0], 'radius': 0.05}])

c2b = Component(name='pump_2b',
                color='blue',
                degrees_of_freedom=('x', 'y', 'z', 'rx', 'ry', 'rz'),
                filepath='part_models/pump.xyzr',
                ports=[{'name': 'supply', 'origin': [0, 0, 0], 'radius': 0.05},
                       {'name': 'return', 'origin': [0, 0, 0], 'radius': 0.05}])

c3a = Component(name='particle_filter_3a',
                color='yellow',
                degrees_of_freedom=('x', 'y', 'z', 'rx', 'ry', 'rz'),
                filepath='part_models/particle_filter.xyzr')

c3b = Component(name='particle_filter_3b',
                color='yellow',
                degrees_of_freedom=('x', 'y', 'z', 'rx', 'ry', 'rz'),
                filepath='part_models/particle_filter.xyzr')

c4a = Component(name='fuel_cell_stack_4a',
                color='green',
                degrees_of_freedom=('x', 'y', 'z', 'rx', 'ry', 'rz'),
                filepath='part_models/fuel_cell_stack.xyzr')

c4b = Component(name='fuel_cell_stack_4b',
                color='green',
                degrees_of_freedom=('x', 'y', 'z', 'rx', 'ry', 'rz'),
                filepath='part_models/fuel_cell_stack.xyzr')

c5 = Component(name='WEG_heater_and_pump_5',
               color='gray',
               degrees_of_freedom=(),
               filepath='part_models/WEG_heater_and_pump.xyzr')

c6 = Component(name='heater_core_6',
               color='red',
               degrees_of_freedom=(),
               filepath='part_models/heater_core.xyzr')

ic0 = Interconnect(name='hp_cv_actuator',
                   color='black',
                   component_1_name='radiator_and_ion_exchanger_1a',
                   component_1_port_index=c1a.port_indices['supply'],
                   component_2_name='radiator_and_ion_exchanger_1b',
                   component_2_port_index=c1b.port_indices['supply'],
                   radius=0.05,
                   number_of_waypoints=0,
                   degrees_of_freedom=())

ic1 = Interconnect(name='lp_cv_actuator',
                   color='blue',
                   component_1_name='radiator_and_ion_exchanger_1b',
                   component_1_port_index=c1b.port_indices['return'],
                   component_2_name='pump_2b',
                   component_2_port_index=c2b.port_indices['return'],
                   radius=0.05,
                   number_of_waypoints=0,
                   degrees_of_freedom=())

kinematics = Kinematics(components=[c1a, c1b, c2a, c2b, c3a, c3b, c4a, c4b, c5, c6],
                        interconnects=[ic0, ic1],
                        objective='bounding box volume')

# %% Define the system

prob = om.Problem()
model = prob.model

kinematics_component = KinematicsInterface()
kinematics_component.options.declare('kinematics', default=kinematics)

model.add_subsystem('kinematics', kinematics_component, promotes=['*'])

prob.model.add_design_var('x')
prob.model.add_objective('f')
prob.model.add_constraint('g', upper=0)

prob.setup()

# %% Define the initial spatial configuration

default_positions_dict = {'radiator_and_ion_exchanger_1a':
                              {'translation': [0.5, 5, 0],
                               'rotation': [0., 0., 0.]},
                          'radiator_and_ion_exchanger_1b':
                              {'translation': [2.5, 5, 0],
                               'rotation': [0., 0., 0.]},
                          'pump_2a':
                              {'translation': [0, 4, 0],
                               'rotation': [0., 0., 0.]},
                          'pump_2b':
                              {'translation': [3., 4., 0],
                               'rotation': [0., 0., 0.]},
                          'particle_filter_3a':
                              {'translation': [0., 3., 0],
                               'rotation': [0., 0., 0.]},
                          'particle_filter_3b':
                              {'translation': [3., 3., 0],
                               'rotation': [0., 0., 0.]},
                          'fuel_cell_stack_4a':
                              {'translation': [0, 2, 0],
                               'rotation': [0., 0., 0.]},
                          'fuel_cell_stack_4b':
                              {'translation': [3, 2, 0],
                               'rotation': [0., 0., 0.]},
                          'WEG_heater_and_pump_5':
                              {'translation': [2., 1., 0],
                               'rotation': [0., 0., 0.]},
                          'heater_core_6':
                              {'translation': [1.5, 0., 0],
                               'rotation': [0., 0., 0.]},
                          'hp_cv_actuator': {'waypoints': []},
                          'lp_cv_actuator': {'waypoints': []}}

# 'hp_cv_actuator': {'waypoints': [[-3., -2., 2.], [-1., 0., 2.]]},
# 'lp_cv_actuator': {'waypoints': [[4., 0., 1.]]}}

kinematics_component.kinematics.set_default_positions(default_positions_dict)

# %% Run the optimization


x0 = kinematics_component.kinematics.design_vector
model.set_val('x', kinematics_component.kinematics.design_vector)

prob.driver = om.ScipyOptimizeDriver()
prob.driver.options['maxiter'] = 300

prob.run_model()

# Plot initial spatial configuration
# kinematics_component.kinematics_interface.plot()

# Perform gradient-based optimization

# print('Initial design vector: ', prob['x'])
# print('Initial objective: ', prob['f'])
# print('Initial constraint values: ', prob['g'])

# x0 = torch.tensor(prob['x'], dtype=torch.float64)
# objects_dict = kinematics_component.kinematics_interface.calculate_positions(x0)
# kinematics_component.kinematics_interface.set_positions(objects_dict)
# kinematics_component.kinematics_interface.plot()

# prob.run_driver()


print('Optimized design vector: ', prob['x'])
print('Optimized objective: ', prob['f'])
print('Optimized constraint values: ', prob['g'])

# Plot optimized spatial
xf = torch.tensor(prob['x'], dtype=torch.float64)
objects_dict = kinematics_component.kinematics.calculate_positions(xf)
kinematics_component.kinematics.set_positions(objects_dict)
kinematics_component.kinematics.plot()