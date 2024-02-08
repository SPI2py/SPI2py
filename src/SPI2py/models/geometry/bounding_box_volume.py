import torch
from ..utilities.aggregation import kreisselmeier_steinhauser


# def bounding_box_bounds(positions, radii):
#     """
#     Calculate the bounding box that contains all spheres.
#
#     Parameters:
#     spheres (Tensor): A tensor of shape (n, 4) where each row is [x, y, z, radius]
#
#     Returns:
#     Tensor: A tensor of shape (2, 3) representing the two opposite vertices (min and max) of the bounding box.
#     """
#
#     # Calculate min and max coordinates for each sphere
#     # min_coords = spheres[:, :3] - spheres[:, 3].view(-1, 1)
#     # max_coords = spheres[:, :3] + spheres[:, 3].view(-1, 1)
#     min_coords = positions - radii.view(-1, 1)
#     max_coords = positions + radii.view(-1, 1)
#
#     # Find overall min and max coordinates
#     x_min, y_min, z_min = torch.min(min_coords, dim=0)[0].reshape(3, 1)
#     x_max, y_max, z_max = torch.max(max_coords, dim=0)[0].reshape(3, 1)
#
#     # Combine into a single tensor representing the bounding box
#     bounds = torch.concatenate((x_min, x_max, y_min, y_max, z_min, z_max))
#
#     return bounds

def bounding_box_bounds(positions1, radii1, positions2, radii2):
    """
    Calculate the bounding box that contains all spheres.

    Parameters:
    spheres (Tensor): A tensor of shape (n, 4) where each row is [x, y, z, radius]

    Returns:
    Tensor: A tensor of shape (2, 3) representing the two opposite vertices (min and max) of the bounding box.
    """

    positions = torch.cat((positions1, positions2), dim=0)
    radii = torch.cat((radii1, radii2), dim=0)

    # Calculate min and max coordinates for each sphere
    # min_coords = spheres[:, :3] - spheres[:, 3].view(-1, 1)
    # max_coords = spheres[:, :3] + spheres[:, 3].view(-1, 1)
    min_coords = positions - radii.view(-1, 1)
    max_coords = positions + radii.view(-1, 1)

    # Find overall min and max coordinates
    x_min, y_min, z_min = torch.min(min_coords, dim=0)[0].reshape(3, 1)
    x_max, y_max, z_max = torch.max(max_coords, dim=0)[0].reshape(3, 1)

    # Combine into a single tensor representing the bounding box
    bounds = torch.concatenate((x_min, x_max, y_min, y_max, z_min, z_max))

    return bounds

def smooth_bounding_box_bounds(positions, radii):

    # Calculate min and max coordinates for each sphere
    min_coords = positions - radii.view(-1, 1)
    max_coords = positions + radii.view(-1, 1)

    # Find overall min and max coordinates
    x_min = kreisselmeier_steinhauser(min_coords[0, :], type='min')
    y_min = kreisselmeier_steinhauser(min_coords[1, :], type='min')
    z_min = kreisselmeier_steinhauser(min_coords[2, :], type='min')

    x_max = kreisselmeier_steinhauser(max_coords[0, :], type='max')
    y_max = kreisselmeier_steinhauser(max_coords[1, :], type='max')
    z_max = kreisselmeier_steinhauser(max_coords[2, :], type='max')

    # Combine into a single tensor representing the bounding box
    # bounds = torch.concatenate((x_min, x_max, y_min, y_max, z_min, z_max))
    bounds = torch.tensor([x_min, x_max, y_min, y_max, z_min, z_max])

    return bounds


def bounding_box_volume(bounds):

    x_min, x_max, y_min, y_max, z_min, z_max = bounds

    volume = (x_max - x_min) * (y_max - y_min) * (z_max - z_min)

    return volume


