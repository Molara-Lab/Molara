from .const import TOL
from .transform import (
    Identity,
    Inversion,
    Rotation,
    Reflection,
    Rotoreflection,
)


def ops2group(transforms):
    def add(op, mat):
        if op not in group:
            group[op] = mat
        else:
            if op.endswith(("+", "-")):
                op = op[:-1] + "'" + op[-1:]
            else:
                op += "'"
            add(op, mat)

    transforms = list(transforms)
    group = {"E": Identity().mat}
    for transform in transforms:
        transform_type = type(transform)
        if transform_type == Inversion:
            group["i"] = transform.mat
        elif transform_type == Rotation:
            vec = transform.vec
            order = transform.order
            symb = f"C{order}"
            if order > 2:
                add(f"{symb}+", transform.mat)
                add(f"{symb}-", Rotation(-vec, order).mat)
                for factor in range(2, order):
                    if order % factor == 0:
                        transforms.append(Rotation(vec, factor))
            elif order == 2:
                add(symb, transform.mat)
        elif transform_type == Reflection:
            add("s", transform.mat)
        elif transform_type == Rotoreflection:
            vec = transform.vec
            order = transform.order
            symb = f"S{order}"
            if order > 2:
                add(f"{symb}+", transform.mat)
                add(f"{symb}-", Rotoreflection(-vec, order).mat)
                for factor in range(3, order):
                    if order % factor == 0:
                        transforms.append(Rotoreflection(vec, factor))
            elif order == 2:
                transforms.append(Inversion())
            elif order == 1:
                transforms.append(Reflection(vec))
    return group


def opmul(group, op1, op2, tol=TOL):
    mat = group[op1] @ group[op2]
    for op, mat_ in group.items():
        if abs(mat - mat_).max() <= tol:
            return op


def multable(group, tol=TOL):
    def fill(string):
        return string + (cell - len(string)) * " "

    cell = max(len(op) for op in group)
    table = [
        [fill(""), "|"] + [fill(op) for op in group],
        [((cell + 1) * (len(group) + 1) + 1) * "-"],
    ]
    for op1 in group:
        row = [fill(op1), "|"]
        for op2 in group:
            row.append(fill(opmul(group, op1, op2, tol)))
        table.append(row)
    for row in table:
        print(" ".join(row))
