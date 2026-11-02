
import math
import Rhino.Geometry as rg

def create_cylinder(height=6.0, radius=2.0):
    """
    Create a closed cylindrical Brep.
    """
    base_plane = rg.Plane.WorldXY
    circle = rg.Circle(base_plane, float(radius))

    cylinder = rg.Cylinder(circle, float(height))

    brep = cylinder.ToBrep(True, True)

    return brep
    
def create_spiral_staircase(
    height=6.0,
    radius=2.0,
    stair_width=1.0,
    step_height=0.17,
    steps_per_turn=24,
    step_thickness=0.12
):
    """
    Create individual spiral stair treads around a cylinder.

    height         : float -- total staircase height
    radius         : float -- inner staircase radius
    stair_width    : float -- radial width of each tread
    step_height    : float -- target riser height
    steps_per_turn : int   -- steps in one full revolution
    step_thickness : float -- vertical tread thickness

    Returns a list of Rhino.Geometry.Brep objects.
    """
    if min(height, radius, stair_width,
           step_height, step_thickness) <= 0:
        raise ValueError("Dimensions must be positive.")

    steps_per_turn = int(steps_per_turn)
    if steps_per_turn < 3:
        raise ValueError("Use at least 3 steps per turn.")

    number_steps = int(math.ceil(height / step_height))
    actual_rise = height / number_steps
    angle_step = 2.0 * math.pi / steps_per_turn

    stairs = []

    for i in range(number_steps):

        angle_start = i * angle_step
        angle_end = (i + 1) * angle_step

        # Top surface of the current step
        z = (i + 1) * actual_rise

        inner_radius = radius
        outer_radius = radius + stair_width

        # Approximate curved edges with short segments
        segments = 8
        points = []

        # Outer curved edge
        for j in range(segments + 1):
            t = j / float(segments)
            angle = angle_start + t * (angle_end - angle_start)

            x = outer_radius * math.cos(angle)
            y = outer_radius * math.sin(angle)
            points.append(rg.Point3d(x, y, z))

        # Inner curved edge, in reverse
        for j in range(segments, -1, -1):
            t = j / float(segments)
            angle = angle_start + t * (angle_end - angle_start)

            x = inner_radius * math.cos(angle)
            y = inner_radius * math.sin(angle)
            points.append(rg.Point3d(x, y, z))

        # Close the profile
        points.append(points[0])

        profile = rg.PolylineCurve(points)

        # Extrude downward to give the step thickness
        extrusion = rg.Extrusion.Create(
            profile, -step_thickness, True
        )

        if extrusion is not None:
            stairs.append(extrusion.ToBrep())

    return stairs




