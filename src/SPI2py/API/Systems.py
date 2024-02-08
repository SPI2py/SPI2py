import numpy as np
import torch
from torch.autograd.functional import jacobian
from openmdao.api import ExplicitComponent

from ..models.geometry.bounding_box_volume import bounding_box_bounds, bounding_box_volume, smooth_bounding_box_bounds
# from ..models.kinematics.distance_calculations import distances_points_points


class VerticalStackComp(ExplicitComponent):
    """
    An ExplicitComponent that vertically stacks a series of inputs with sizes (n, 3) or (n, 1).
    """

    def initialize(self):
        # Initialize with a list of sizes for each input
        self.options.declare('input_sizes', types=list, desc='List of sizes (n) for each input array')
        self.options.declare('column_size', types=int, desc='Column size, either 1 or 3')

    def setup(self):
        input_sizes = self.options['input_sizes']
        column_size = self.options['column_size']
        total_rows = sum(input_sizes)

        # Define inputs and output
        for i, size in enumerate(input_sizes):
            self.add_input(f'input_{i}', shape=(size, column_size))

        self.add_output('stacked_output', shape=(total_rows, column_size))

        # Declare partials for each input-output pair
        # start_idx = 0
        # for i, size in enumerate(input_sizes):
        #     # rows: Each input contributes size*column_size elements in the output
        #     rows = np.arange(start_idx, start_idx + size * column_size)
        #
        #     # cols: Need to ensure cols aligns with how OpenMDAO flattens the inputs for each partial
        #     # For a single input, OpenMDAO flattens it as [row1_col1, row1_col2, ..., row2_col1, row2_col2, ...]
        #     # Therefore, we need to create a pattern that matches this flattening
        #     if column_size == 1:
        #         # For (n, 1) inputs, it's a direct mapping
        #         cols = np.arange(size)
        #     elif column_size == 3:
        #         # For (n, 3) inputs, repeat each index 3 times to account for each column
        #         cols = np.repeat(np.arange(size), column_size)
        #
        #     self.declare_partials('stacked_output', f'input_{i}', rows=rows, cols=cols, val=1.0)
        #     start_idx += size * column_size

    def setup_partials(self):
        self.declare_partials('*', '*')
        # self.declare_partials('*', '*', method='fd')

    def compute(self, inputs, outputs):
        # Unpack the settings
        input_sizes = self.options['input_sizes']
        column_size = self.options['column_size']

        input_arrays = ()
        for i in range(len(input_sizes)):
            input_arrays = input_arrays + (inputs[f'input_{i}'],)

        # Convert the inputs to torch tensors
        input_tensors = ()
        for input_array in input_arrays:
            input_tensors = input_tensors + (torch.tensor(input_array, dtype=torch.float64),)

        # Stack inputs vertically
        stacked_output = self._vstack(*input_tensors)
        outputs['stacked_output'] = stacked_output

    def compute_partials(self, inputs, partials):
        # The partial derivatives have been declared in setup as constant 1.0, so no further action is needed.
        # pass

        # Unpack the settings
        input_sizes = self.options['input_sizes']
        column_size = self.options['column_size']

        input_arrays = ()
        for i in range(len(input_sizes)):
            input_arrays = input_arrays + (inputs[f'input_{i}'],)

        # Convert the inputs to torch tensors
        input_tensors = ()
        for input_array in input_arrays:
            input_tensors = input_tensors + (torch.tensor(input_array, dtype=torch.float64, requires_grad=True),)

        # stacked_output = self._vstack(*input_tensors)
        # outputs['stacked_output'] = stacked_output

        # Calculate the partial derivatives
        jac_stacked_output = jacobian(self._vstack, input_tensors)

        # Convert the partial derivatives to numpy arrays
        jac_stacked_output_np = []
        for jac in jac_stacked_output:
            jac_stacked_output_np.append(jac.detach().numpy())

        # Set the partial derivatives
        for i in range(len(input_sizes)):
            partials['stacked_output', f'input_{i}'] = jac_stacked_output_np[i]


    @staticmethod
    def _vstack(*args):

        return torch.vstack(args)

# class VerticalStackComp(ExplicitComponent):
#     """
#     An ExplicitComponent that vertically stacks a series of inputs with sizes (n, 3) or (n, 1).
#     """
#
#     def initialize(self):
#         # Initialize with a list of sizes for each input
#     #     self.options.declare('input_sizes', types=list, desc='List of sizes (n) for each input array')
#         self.options.declare('column_size', types=int, desc='Column size, either 1 or 3')
#
#     def setup(self):
#         # input_sizes = self.options['input_sizes']
#         column_size = self.options['column_size']
#         # total_rows = sum(input_sizes)
#
#         # # Define inputs and output
#         # for i, size in enumerate(input_sizes):
#         #     self.add_input(f'input_{i}', shape=(size, column_size))
#         self.add_input('input_0', shape=(100, column_size))
#         self.add_input('input_1', shape=(100, column_size))
#
#         # self.add_output('stacked_output', shape=(total_rows, column_size))
#         self.add_output('stacked_output', shape=(200, column_size))
#
#     def setup_partials(self):
#         self.declare_partials('*', '*', method='fd')
#
#     def compute(self, inputs, outputs):
#         # Stack inputs vertically
#         # outputs['stacked_output'] = np.vstack([inputs[f'input_{i}'] for i in range(len(self.options['input_sizes']))])
#         input_0 = inputs['input_0']
#         input_1 = inputs['input_1']
#         stacked_output = np.vstack((input_0, input_1))
#         outputs['stacked_output'] = stacked_output
#
#     def compute_partials(self, inputs, partials):
#         # The partial derivatives have been declared in setup as constant 1.0, so no further action is needed.
#         pass

class System(ExplicitComponent):

    def initialize(self):
        self.options.declare('num_components', types=int)


    def setup(self):


        self.add_input('transformed_sphere_positions', shape_by_conn=True)
        self.add_input('transformed_sphere_radii', shape_by_conn=True)
        # self.add_input('comp_0_transformed_sphere_positions', shape_by_conn=True)
        # self.add_input('comp_0_transformed_sphere_radii', shape_by_conn=True)
        # self.add_input('comp_1_transformed_sphere_positions', shape_by_conn=True)
        # self.add_input('comp_1_transformed_sphere_radii', shape_by_conn=True)

        # self.add_output('distance')
        self.add_output('bounding_box_volume', val=1)
        self.add_output('bounding_box_bounds', shape=(6,))
        # self.add_output('constraints', val=torch.zeros(1))

    def setup_partials(self):
        self.declare_partials('*', '*', method='fd')
        # self.declare_partials('bounding_box_volume', 'transformed_sphere_positions')
        # self.declare_partials('bounding_box_volume', 'transformed_sphere_radii')

        # for i in range(self.options['num_components']):
        #     self.declare_partials('bounding_box_volume', f'comp_{i}_sphere_positions')
        # self.declare_partials('*', '*')

    def compute(self, inputs, outputs):

        # Get the input variables
        sphere_positions = inputs['transformed_sphere_positions']
        sphere_radii = inputs['transformed_sphere_radii']
        # comp_0_transformed_sphere_positions = inputs['comp_0_transformed_sphere_positions']
        # comp_0_transformed_sphere_radii = inputs['comp_0_transformed_sphere_radii']
        # comp_1_transformed_sphere_positions = inputs['comp_1_transformed_sphere_positions']
        # comp_1_transformed_sphere_radii = inputs['comp_1_transformed_sphere_radii']

        # Convert the inputs to torch tensors
        sphere_positions = torch.tensor(sphere_positions, dtype=torch.float64)
        sphere_radii = torch.tensor(sphere_radii, dtype=torch.float64)
        # comp_0_transformed_sphere_positions = torch.tensor(comp_0_transformed_sphere_positions, dtype=torch.float64)
        # comp_1_transformed_sphere_positions = torch.tensor(comp_1_transformed_sphere_positions, dtype=torch.float64)
        # comp_0_transformed_sphere_radii = torch.tensor(comp_0_transformed_sphere_radii, dtype=torch.float64)
        # comp_1_transformed_sphere_radii = torch.tensor(comp_1_transformed_sphere_radii, dtype=torch.float64)

        # Calculate the bounding box volume
        bb_bounds = bounding_box_bounds(sphere_positions, sphere_radii)
        bb_volume = self.compute_bounding_box_volume(sphere_positions, sphere_radii)
        # objective = self.sum_of_pairwise_distances(comp_0_transformed_sphere_positions, comp_1_transformed_sphere_positions)
        # bb_volume, bb_bounds = self.compute_bounding_box_volume(comp_0_transformed_sphere_positions,
        #                                              comp_0_transformed_sphere_radii,
        #                                              comp_1_transformed_sphere_positions,
        #                                              comp_1_transformed_sphere_radii)

        # Convert the outputs to numpy arrays
        bb_bounds = bb_bounds.detach().numpy()
        bb_volume = bb_volume.detach().numpy()
        # objective = objective.detach().numpy()

        # Set the outputs
        outputs['bounding_box_bounds'] = bb_bounds
        outputs['bounding_box_volume'] = bb_volume
        # outputs['constraints'] = constraints
        # outputs['distance'] = objective

    def compute_partials(self, inputs, partials):
        pass
        # # Get the input variables
        # sphere_positions = inputs['transformed_sphere_positions']
        # sphere_radii = inputs['transformed_sphere_radii']
        #
        # # Convert the inputs to torch tensors
        # sphere_positions = torch.tensor(sphere_positions, dtype=torch.float64, requires_grad=True)
        # sphere_radii = torch.tensor(sphere_radii, dtype=torch.float64, requires_grad=True)  # TODO Remove True
        #
        # # Calculate the bounding box volume
        # jac_bb_volume = jacobian(self.compute_bounding_box_volume, (sphere_positions, sphere_radii))
        #
        # # Convert the outputs to numpy arrays
        # # jac_bb_volume = jac_bb_volume.detach().numpy()
        # jac_bbv_positions = jac_bb_volume[0].detach().numpy()
        # jac_bbv_radii = jac_bb_volume[1].detach().numpy()
        #
        # # Set the outputs
        # partials['bounding_box_volume', 'transformed_sphere_positions'] = jac_bbv_positions
        # partials['bounding_box_volume', 'transformed_sphere_radii'] = jac_bbv_radii

    # @staticmethod
    # def sum_of_pairwise_distances(A, B):
    #     # A is (n, 3), B is (m, 3)
    #     # Expand A and B to make their shapes compatible for broadcasting
    #     A_expanded = A.unsqueeze(1)  # Shape becomes (n, 1, 3)
    #     B_expanded = B.unsqueeze(0)  # Shape becomes (1, m, 3)
    #
    #     # Compute the squared differences using broadcasting, resulting in a (n, m, 3) tensor
    #     squared_diffs = (A_expanded - B_expanded) ** 2
    #
    #     # Sum the squared differences along the last dimension to get squared Euclidean distances, resulting in a (n, m) tensor
    #     squared_dists = torch.sum(squared_diffs, dim=2)
    #
    #     # Take the square root to get Euclidean distances and sum all the distances
    #     sum_dists = torch.sum(torch.sqrt(squared_dists))
    #
    #     return sum_dists


    # @staticmethod
    # def compute_distance(sphere_positions_0, sphere_positions_1):
    #     return torch.norm(sphere_positions_0 - sphere_positions_1, dim=1).max()

    @staticmethod
    def compute_bounding_box_volume(sphere_positions, sphere_radii, include_bounds=False):

        # bb_bounds = smooth_bounding_box_bounds(sphere_positions, sphere_radii)
        bb_bounds = bounding_box_bounds(sphere_positions, sphere_radii)
        bb_volume = bounding_box_volume(bb_bounds)

        if include_bounds:
            return bb_volume, bb_bounds
        else:
            return bb_volume

    # @staticmethod
    # def compute_bounding_box_volume(sphere_positions_0, sphere_radii_0, sphere_positions_1, sphere_radii_1):
    #
    #     # bb_bounds = smooth_bounding_box_bounds(sphere_positions, sphere_radii)
    #     bb_bounds = bounding_box_bounds(sphere_positions_0, sphere_radii_0, sphere_positions_1, sphere_radii_1)
    #     bb_volume = bounding_box_volume(bb_bounds)
    #
    #
    #     return bb_volume, bb_bounds



# class _System:
#     def __init__(self, components, interconnects):
#
#
#         self.components = components
#         self.interconnects = interconnects
#         self.objects = self.components + self.interconnects
#
#
#         self.component_pairs = self.get_component_pairs()
#         self.interconnect_pairs = self.get_interconnect_pairs()
#         self.component_interconnect_pairs = self.get_component_interconnect_pairs()
#
#
#         objective = self.input['problem']['objective']
#         self.set_objective(objective)
#
#         self.translations_shape = (self.num_components, 3)
#         self.rotations_shape = (self.num_components, 3)
#         self.routings_shape = (self.num_interconnects, self.num_nodes, 3)
#
#     # def set_objective(self, objective: str):
#     #
#     #     """
#     #     Add an objective to the design study.
#     #
#     #     :param objective: The objective function to be added.
#     #     :param options: The options for the objective function.
#     #     """
#     #
#     #     # SELECT THE OBJECTIVE FUNCTION HANDLE
#     #
#     #     if objective == 'bounding box volume':
#     #         _objective_function = bounding_box_volume
#     #     else:
#     #         raise NotImplementedError
#     #
#     #     def objective_function(positions):
#     #         return _objective_function(positions)
#     #
#     #     self.objective = objective_function
#     #
#     # def calculate_positions(self, translations, rotations, routings):
#     #
#     #     objects_dict = {}
#     #
#     #     for component, translation, rotation in zip(self.components, translations, rotations):
#     #         object_dict = component.calculate_positions(translation, rotation)
#     #         objects_dict = {**objects_dict, **object_dict}
#     #
#     #     for interconnect, routing in zip(self.interconnects, routings):
#     #         object_dict = interconnect.calculate_positions(routing)
#     #         objects_dict = {**objects_dict, **object_dict}
#     #
#     #     return objects_dict
#
#     def get_component_pairs(self):
#         component_component_pairs = list(combinations(self.components, 2))
#         return component_component_pairs
#
#     def get_interconnect_pairs(self):
#         interconnect_interconnect_pairs = list(combinations(self.interconnects, 2))
#         return interconnect_interconnect_pairs
#
#     def get_component_interconnect_pairs(self):
#         component_interconnect_pairs = list(product(self.components, self.interconnects))
#         return component_interconnect_pairs
#
#     def collision_component_pairs(self, positions_dict):
#         signed_distance_vals = aggregate_signed_distance(positions_dict, self.component_pairs)
#         max_signed_distance = kreisselmeier_steinhauser(signed_distance_vals)
#         return max_signed_distance
#
#     def collision_interconnect_pairs(self, positions_dict):
#         signed_distance_vals = aggregate_signed_distance(positions_dict, self.interconnect_pairs)
#         max_signed_distance = kreisselmeier_steinhauser(signed_distance_vals)
#         return max_signed_distance
#
#     def collision_component_interconnect_pairs(self, positions_dict):
#         # TODO Remove tolerance
#         signed_distance_vals = aggregate_signed_distance(positions_dict, self.component_interconnect_pairs)
#         max_signed_distance = kreisselmeier_steinhauser(signed_distance_vals) - 0.2
#         return max_signed_distance
#
#
#
#     def calculate_constraints(self, translations, rotations, routings):
#
#         positions_dict = self.calculate_positions(translations, rotations, routings)
#
#         # g_component_pairs = self.collision_component_pairs(positions_dict)
#         # g_interconnect_pairs = self.collision_interconnect_pairs(positions_dict)
#         # g_component_interconnect_pairs = self.collision_component_interconnect_pairs(positions_dict)
#         # g = torch.tensor((g_component_pairs, g_interconnect_pairs, g_component_interconnect_pairs))
#
#         # TODO Add other constraints back in
#         g = self.collision_component_pairs(positions_dict)
#
#         return g
#
#