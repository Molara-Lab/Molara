import numpy as np
from molara.eval.mos import calculate_mo_cartesian
from molara.eval.generate_voxel_grid import generate_voxel_grid

aos_values = np.zeros((15), dtype=np.float64)


def octree(origin,
           voxel_size,
                  direction,
                  size,
                  iso,
                  aos,
                  mo_coefficients,
                  widget,
                  ):
    max_length = 0
    for ao in aos:
        if len(ao.exponents) > max_length:
            max_length = len(ao.exponents)
    orbital_exponents = np.zeros((len(aos), max_length), dtype=np.float64)
    orbital_coefficients = np.zeros((len(aos), max_length), dtype=np.float64)
    orbital_norms = np.zeros((len(aos), max_length), dtype=np.float64)
    orbital_positions = np.zeros((len(aos), 3), dtype=np.float64)
    orbital_ijks = np.zeros((len(aos), 3), dtype=np.int64)
    for ao_index, ao in enumerate(aos):
        for i in range(len(ao.exponents)):
            orbital_exponents[ao_index, i] = ao.exponents[i]
            orbital_coefficients[ao_index, i] = ao.coefficients[i]
            orbital_norms[ao_index, i] = ao.norms[i]
        orbital_positions[ao_index, :] = ao.position
        orbital_ijks[ao_index, :] = ao.ijk

    voxel_number = np.array(
        [
            int(size[0] / voxel_size[0]) + 1,
            int(size[1] / voxel_size[1]) + 1,
            int(size[2] / voxel_size[2]) + 1,
        ],
        dtype=np.int32,
    )

    grid = generate_voxel_grid(
        np.array(origin, dtype=np.float64),
        direction,
        voxel_size,
        voxel_number,
        aos,
        mo_coefficients,
    )

    for i in range(voxel_number[0] - 1):
        for j in range(voxel_number[1] - 1):
            for k in range(voxel_number[2] - 1):
                voxel_indices = np.array(
                    [
                        [i, j, k],
                        [i + 1, j, k],
                        [i, j + 1, k],
                        [i, j, k + 1],
                        [i, j + 1, k + 1],
                        [i + 1, j + 1, k],
                        [i + 1, j, k + 1],
                        [i + 1, j + 1, k + 1],
                    ],
                    dtype=np.uint32,
                )
                voxel_values = np.zeros(8)
                positions = np.zeros((8, 3), dtype=np.float64)
                for corner_index in range(8):
                    voxel_values[corner_index] = grid[
                        voxel_indices[corner_index, 0],
                        voxel_indices[corner_index, 1],
                        voxel_indices[corner_index, 2],
                    ]
                    positions[corner_index] = origin + voxel_size * voxel_indices[corner_index, :]
                depth = 3
                new_cube(depth,
                         0,
                         iso,
                         positions,
                         voxel_values,
                         widget,
                         orbital_positions,
                         orbital_coefficients,
                         orbital_exponents,
                         orbital_norms,
                         orbital_ijks,
                         mo_coefficients)


    # positions = np.zeros((8,3), dtype=np.float64)
    # values = np.zeros(8, dtype=np.float64)
    # positions[0] = origin
    # positions[1] = origin + size * direction @ np.array([1, 0, 0])
    # positions[2] = origin + size * direction @ np.array([0, 1, 0])
    # positions[3] = origin + size * direction @ np.array([0, 0, 1])
    # positions[4] = origin + size * direction @ np.array([0, 1, 1])
    # positions[5] = origin + size * direction @ np.array([1, 1, 0])
    # positions[6] = origin + size * direction @ np.array([1, 0, 1])
    # positions[7] = origin + size * direction @ np.array([1, 1, 1])
    # for i, position in enumerate(positions):
    #     values[i] = calculate_mo_cartesian(
    #         position * 1.889726124565062,
    #         orbital_positions * 1.889726124565062,
    #         orbital_coefficients,
    #         orbital_exponents,
    #         orbital_norms,
    #         orbital_ijks,
    #         mo_coefficients,
    #         aos_values
    #     )
    #
    # depth = 5
    # new_cube(depth,
    #          0,
    #          iso,
    #          positions,
    #          values,
    #          widget,
    #          orbital_positions,
    #          orbital_coefficients,
    #          orbital_exponents,
    #          orbital_norms,
    #          orbital_ijks,
    #          mo_coefficients)



def new_cube(depth,
             depth_counter,
             iso,
             positions,
             values,
             widget,
             orbital_positions_au,
             orbital_coefficients,
             orbital_exponents,
             orbital_norms,
             orbital_ijks,
             mo_coefficients):

    new_grid = np.zeros((3,3,3), dtype=np.float64)
    new_pos_grid = np.zeros((3,3,3,3), dtype=np.float64)
    if depth <= 0:
        edges = np.array(
            [
                [positions[0], positions[2]],
                [positions[0], positions[3]],
                [positions[2], positions[4]],
                [positions[3], positions[4]],
                [positions[1], positions[5]],
                [positions[1], positions[6]],
                [positions[7], positions[5]],
                [positions[7], positions[6]],
                [positions[7], positions[4]],
                [positions[2], positions[5]],
                [positions[3], positions[6]],
                [positions[0], positions[1]],
            ],
            dtype=np.float32,
        )
        colors = np.array([1, 0, 0] * 12, dtype=np.float32)
        radii = np.array([0.01] * 12, dtype=np.float32)
        # widget.renderer.draw_cylinders_from_to(
        #     edges,
        #     radii,
        #     colors,
        #     10,
        # )
        pos = []
        radii = []
        colors = []
        check = False
        print(values, iso)
        for i, value in enumerate(values):
            if value > iso:
                pos.append(positions[i])
                radii.append([0.01])
                colors.append([0, 1, 0])
                check = True
        if check:
            widget.renderer.draw_spheres(
                np.array(pos, dtype=np.float32),
                np.array(radii, dtype=np.float32),
                np.array(colors, dtype=np.float32),
                10,
            )
        return

    inside_indices = np.zeros(8, dtype=np.int32)
    inside_number = 0
    for i, value in enumerate(values):
        if value < iso:
            inside_indices[i] = 1
            inside_number += 1
    if inside_number == 0 or inside_number == 8 and depth_counter > -1:
        edges = np.array(
            [
                [positions[0], positions[2]],
                [positions[0], positions[3]],
                [positions[2], positions[4]],
                [positions[3], positions[4]],
                [positions[1], positions[5]],
                [positions[1], positions[6]],
                [positions[7], positions[5]],
                [positions[7], positions[6]],
                [positions[7], positions[4]],
                [positions[2], positions[5]],
                [positions[3], positions[6]],
                [positions[0], positions[1]],
            ],
            dtype=np.float32,
        )
        colors = np.array([depth_counter / 5, 0, 0] * 12, dtype=np.float32)
        radii = np.array([0.001 * 1/depth] * 12, dtype=np.float32)
        widget.renderer.draw_cylinders_from_to(
            edges,
            radii,
            colors,
            10,
        )
        return
    center_position = (positions[0] + positions[7]) * 0.5
    center_value = calculate_mo_cartesian(
        center_position * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values
    )
    # calculate 8 new cube (octree) without calculating the same vertex twice
    #
    #            6             7
    #            +-------------+
    #          / |           / |
    #        /   |         /   |
    #    1 +-----+-------+  5  |
    #      |   3 +-------+-----+ 4
    #      |   /         |   /
    #      | /           | /
    #    0 +-------------+ 2
    #
    new_pos_grid[0, 0, 0] = positions[0]
    new_grid[0, 0, 0] = values[0]
    new_pos_grid[0, 1, 0] = (positions[0] + positions[2]) * 0.5
    new_grid[0, 1, 0] = calculate_mo_cartesian(
        new_pos_grid[0, 1, 0] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[0, 2, 0] = positions[2]
    new_grid[0, 2, 0] = values[2]
    new_pos_grid[0, 0, 1] = (positions[0] + positions[3]) * 0.5
    new_grid[0, 0, 1] = calculate_mo_cartesian(
        new_pos_grid[0, 0, 1] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[0, 1, 1] = (positions[0] + positions[4]) * 0.5
    new_grid[0, 1, 1] = calculate_mo_cartesian(
        new_pos_grid[0, 1, 1] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[0, 2, 1] = (positions[2] + positions[4]) * 0.5
    new_grid[0, 2, 1] = calculate_mo_cartesian(
        new_pos_grid[0, 2, 1] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[0, 0, 2] = positions[3]
    new_grid[0, 0, 2] = values[3]
    new_pos_grid[0, 1, 2] = (positions[3] + positions[4]) * 0.5
    new_grid[0, 1, 2] = calculate_mo_cartesian(
        new_pos_grid[0, 1, 2] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[0, 2, 2] = positions[4]
    new_grid[0, 2, 2] = values[4]
    new_pos_grid[1, 0, 0] = (positions[1] + positions[0]) * 0.5
    new_grid[1, 0, 0] = calculate_mo_cartesian(
        new_pos_grid[1, 0, 0] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[1, 1, 0] = (positions[1] + positions[2]) * 0.5
    new_grid[1, 1, 0] = calculate_mo_cartesian(
        new_pos_grid[1, 1, 0] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[1, 2, 0] = (positions[2] + positions[5]) * 0.5
    new_grid[1, 2, 0] = calculate_mo_cartesian(
        new_pos_grid[1, 2, 0] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[1, 0, 1] = (positions[1] + positions[3]) * 0.5
    new_grid[1, 0, 1] = calculate_mo_cartesian(
        new_pos_grid[1, 0, 1] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[1, 1, 1] = center_position
    new_grid[1, 1, 1] = center_value
    new_pos_grid[1, 2, 1] = (positions[2] + positions[7]) * 0.5
    new_grid[1, 2, 1] = calculate_mo_cartesian(
        new_pos_grid[1, 2, 1] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[1, 0, 2] = (positions[3] + positions[6]) * 0.5
    new_grid[1, 0, 2] = calculate_mo_cartesian(
        new_pos_grid[1, 0, 2] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[1, 1, 2] = (positions[7] + positions[3]) * 0.5
    new_grid[1, 1, 2] = calculate_mo_cartesian(
        new_pos_grid[1, 1, 2] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[1, 2, 2] = (positions[4] + positions[7]) * 0.5
    new_grid[1, 2, 2] = calculate_mo_cartesian(
        new_pos_grid[1, 2, 2] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[2, 0, 0] = positions[1]
    new_grid[2, 0, 0] = values[1]
    new_pos_grid[2, 1, 0] = (positions[1] + positions[5]) * 0.5
    new_grid[2, 1, 0] = calculate_mo_cartesian(
        new_pos_grid[2, 1, 0] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[2, 2, 0] = positions[5]
    new_grid[2, 2, 0] = values[5]
    new_pos_grid[2, 0, 1] = (positions[1] + positions[6]) * 0.5
    new_grid[2, 0, 1] = calculate_mo_cartesian(
        new_pos_grid[2, 0, 1] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[2, 1, 1] = (positions[1] + positions[7]) * 0.5
    new_grid[2, 1, 1] = calculate_mo_cartesian(
        new_pos_grid[2, 1, 1] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[2, 2, 1] = (positions[5] + positions[7]) * 0.5
    new_grid[2, 2, 1] = calculate_mo_cartesian(
        new_pos_grid[2, 2, 1] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[2, 0, 2] = positions[6]
    new_grid[2, 0, 2] = values[6]
    new_pos_grid[2, 1, 2] = (positions[6] + positions[7]) * 0.5
    new_grid[2, 1, 2] = calculate_mo_cartesian(
        new_pos_grid[2, 1, 2] * 1.889726124565062,
        orbital_positions_au,
        orbital_coefficients,
        orbital_exponents,
        orbital_norms,
        orbital_ijks,
        mo_coefficients,
        aos_values)
    new_pos_grid[2, 2, 2] = positions[7]
    new_grid[2, 2, 2] = values[7]

    new_depth = depth - 1
    new_depth_counter = depth_counter + 1

    new_positions = np.zeros((8, 3), dtype=np.float64)
    new_values = np.zeros(8, dtype=np.float64)
    new_positions[0] = new_pos_grid[0, 0, 0]
    new_values[0] = new_grid[0, 0, 0]
    new_positions[1] = new_pos_grid[1, 0, 0]
    new_values[1] = new_grid[1, 0, 0]
    new_positions[2] = new_pos_grid[0, 1, 0]
    new_values[2] = new_grid[0, 1, 0]
    new_positions[3] = new_pos_grid[0, 0, 1]
    new_values[3] = new_grid[0, 0, 1]
    new_positions[4] = new_pos_grid[0, 1, 1]
    new_values[4] = new_grid[0, 1, 1]
    new_positions[5] = new_pos_grid[1, 1, 0]
    new_values[5] = new_grid[1, 1, 0]
    new_positions[6] = new_pos_grid[1, 0, 1]
    new_values[6] = new_grid[1, 0, 1]
    new_positions[7] = new_pos_grid[1, 1, 1]
    new_values[7] = new_grid[1, 1, 1]
    new_cube(new_depth,
             new_depth_counter,
             iso,
             new_positions,
             new_values,
             widget,
             orbital_positions_au,
             orbital_coefficients,
             orbital_exponents,
             orbital_norms,
             orbital_ijks,
             mo_coefficients)

    new_positions[0] = new_pos_grid[1, 0, 0]
    new_values[0] = new_grid[1, 0, 0]
    new_positions[1] = new_pos_grid[2, 0, 0]
    new_values[1] = new_grid[2, 0, 0]
    new_positions[2] = new_pos_grid[1, 1, 0]
    new_values[2] = new_grid[1, 1, 0]
    new_positions[3] = new_pos_grid[1, 0, 1]
    new_values[3] = new_grid[1, 0, 1]
    new_positions[4] = new_pos_grid[1, 1, 1]
    new_values[4] = new_grid[1, 1, 1]
    new_positions[5] = new_pos_grid[2, 1, 0]
    new_values[5] = new_grid[2, 1, 0]
    new_positions[6] = new_pos_grid[2, 0, 1]
    new_values[6] = new_grid[2, 0, 1]
    new_positions[7] = new_pos_grid[2, 1, 1]
    new_values[7] = new_grid[2, 1, 1]
    new_cube(new_depth,
             new_depth_counter,
                iso,
                new_positions,
                new_values,
             widget,
                orbital_positions_au,
                orbital_coefficients,
                orbital_exponents,
                orbital_norms,
                orbital_ijks,
                mo_coefficients)

    new_positions[0] = new_pos_grid[0, 1, 0]
    new_values[0] = new_grid[0, 1, 0]
    new_positions[1] = new_pos_grid[1, 1, 0]
    new_values[1] = new_grid[1, 1, 0]
    new_positions[2] = new_pos_grid[0, 2, 0]
    new_values[2] = new_grid[0, 2, 0]
    new_positions[3] = new_pos_grid[0, 1, 1]
    new_values[3] = new_grid[0, 1, 1]
    new_positions[4] = new_pos_grid[0, 2, 1]
    new_values[4] = new_grid[0, 2, 1]
    new_positions[5] = new_pos_grid[1, 2, 0]
    new_values[5] = new_grid[1, 2, 0]
    new_positions[6] = new_pos_grid[1, 1, 1]
    new_values[6] = new_grid[1, 1, 1]
    new_positions[7] = new_pos_grid[1, 2, 1]
    new_values[7] = new_grid[1, 2, 1]
    new_cube(new_depth,
             new_depth_counter,
                iso,
                new_positions,
                new_values,
             widget,
                orbital_positions_au,
                orbital_coefficients,
                orbital_exponents,
                orbital_norms,
                orbital_ijks,
                mo_coefficients)

    new_positions[0] = new_pos_grid[0, 0, 1]
    new_values[0] = new_grid[0, 0, 1]
    new_positions[1] = new_pos_grid[1, 0, 1]
    new_values[1] = new_grid[1, 0, 1]
    new_positions[2] = new_pos_grid[0, 1, 1]
    new_values[2] = new_grid[0, 1, 1]
    new_positions[3] = new_pos_grid[0, 0, 2]
    new_values[3] = new_grid[0, 0, 2]
    new_positions[4] = new_pos_grid[0, 1, 2]
    new_values[4] = new_grid[0, 1, 2]
    new_positions[5] = new_pos_grid[1, 1, 1]
    new_values[5] = new_grid[1, 1, 1]
    new_positions[6] = new_pos_grid[1, 0, 2]
    new_values[6] = new_grid[1, 0, 2]
    new_positions[7] = new_pos_grid[1, 1, 2]
    new_values[7] = new_grid[1, 1, 2]
    new_cube(new_depth,
             new_depth_counter,
                iso,
                new_positions,
                new_values,
             widget,
                orbital_positions_au,
                orbital_coefficients,
                orbital_exponents,
                orbital_norms,
                orbital_ijks,
                mo_coefficients)

    new_positions[0] = new_pos_grid[1, 1, 0]
    new_values[0] = new_grid[1, 1, 0]
    new_positions[1] = new_pos_grid[2, 1, 0]
    new_values[1] = new_grid[2, 1, 0]
    new_positions[2] = new_pos_grid[1, 2, 0]
    new_values[2] = new_grid[1, 2, 0]
    new_positions[3] = new_pos_grid[1, 1, 1]
    new_values[3] = new_grid[1, 1, 1]
    new_positions[4] = new_pos_grid[1, 2, 1]
    new_values[4] = new_grid[1, 2, 1]
    new_positions[5] = new_pos_grid[2, 2, 0]
    new_values[5] = new_grid[2, 2, 0]
    new_positions[6] = new_pos_grid[2, 1, 1]
    new_values[6] = new_grid[2, 1, 1]
    new_positions[7] = new_pos_grid[2, 2, 1]
    new_values[7] = new_grid[2, 2, 1]
    new_cube(new_depth,
             new_depth_counter,
                iso,
                new_positions,
                new_values,
             widget,
                orbital_positions_au,
                orbital_coefficients,
                orbital_exponents,
                orbital_norms,
                orbital_ijks,
                mo_coefficients)

    new_positions[0] = new_pos_grid[0, 1, 1]
    new_values[0] = new_grid[0, 1, 1]
    new_positions[1] = new_pos_grid[1, 1, 1]
    new_values[1] = new_grid[1, 1, 1]
    new_positions[2] = new_pos_grid[0, 2, 1]
    new_values[2] = new_grid[0, 2, 1]
    new_positions[3] = new_pos_grid[0, 1, 2]
    new_values[3] = new_grid[0, 1, 2]
    new_positions[4] = new_pos_grid[0, 2, 2]
    new_values[4] = new_grid[0, 2, 2]
    new_positions[5] = new_pos_grid[1, 2, 1]
    new_values[5] = new_grid[1, 2, 1]
    new_positions[6] = new_pos_grid[1, 1, 2]
    new_values[6] = new_grid[1, 1, 2]
    new_positions[7] = new_pos_grid[1, 2, 2]
    new_values[7] = new_grid[1, 2, 2]
    new_cube(new_depth,
             new_depth_counter,
                iso,
                new_positions,
                new_values,
             widget,
                orbital_positions_au,
                orbital_coefficients,
                orbital_exponents,
                orbital_norms,
                orbital_ijks,
                mo_coefficients)

    new_positions[0] = new_pos_grid[1, 0, 1]
    new_values[0] = new_grid[1, 0, 1]
    new_positions[1] = new_pos_grid[2, 0, 1]
    new_values[1] = new_grid[2, 0, 1]
    new_positions[2] = new_pos_grid[1, 1, 1]
    new_values[2] = new_grid[1, 1, 1]
    new_positions[3] = new_pos_grid[1, 0, 2]
    new_values[3] = new_grid[1, 0, 2]
    new_positions[4] = new_pos_grid[1, 1, 2]
    new_values[4] = new_grid[1, 1, 2]
    new_positions[5] = new_pos_grid[2, 1, 1]
    new_values[5] = new_grid[2, 1, 1]
    new_positions[6] = new_pos_grid[2, 0, 2]
    new_values[6] = new_grid[2, 0, 2]
    new_positions[7] = new_pos_grid[2, 1, 2]
    new_values[7] = new_grid[2, 1, 2]
    new_cube(new_depth,
             new_depth_counter,
                iso,
                new_positions,
                new_values,
             widget,
                orbital_positions_au,
                orbital_coefficients,
                orbital_exponents,
                orbital_norms,
                orbital_ijks,
                mo_coefficients)

    new_positions[0] = new_pos_grid[1, 1, 1]
    new_values[0] = new_grid[1, 1, 1]
    new_positions[1] = new_pos_grid[2, 1, 1]
    new_values[1] = new_grid[2, 1, 1]
    new_positions[2] = new_pos_grid[1, 2, 1]
    new_values[2] = new_grid[1, 2, 1]
    new_positions[3] = new_pos_grid[1, 1, 2]
    new_values[3] = new_grid[1, 1, 2]
    new_positions[4] = new_pos_grid[1, 2, 2]
    new_values[4] = new_grid[1, 2, 2]
    new_positions[5] = new_pos_grid[2, 2, 1]
    new_values[5] = new_grid[2, 2, 1]
    new_positions[6] = new_pos_grid[2, 1, 2]
    new_values[6] = new_grid[2, 1, 2]
    new_positions[7] = new_pos_grid[2, 2, 2]
    new_values[7] = new_grid[2, 2, 2]
    new_cube(new_depth,
             new_depth_counter,
                iso,
                new_positions,
                new_values,
             widget,
                orbital_positions_au,
                orbital_coefficients,
                orbital_exponents,
                orbital_norms,
                orbital_ijks,
                mo_coefficients)



















