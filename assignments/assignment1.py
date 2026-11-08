
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



def create_door_openings(
    height=6.0,
    radius=2.0,
    step_height=0.17,
    steps_per_turn=24,
    step_thickness=0.12,
    door_width=0.9,
    door_height=2.0,
    door_interval=24,
    clearance=0.10
):
    """
    Create door openings aligned with the spiral staircase.

    height         : float -- cylinder height
    radius         : float -- cylinder radius
    step_height    : float -- target stair riser height
    steps_per_turn : int -- steps per full revolution
    step_thickness : float -- thickness of each stair
    door_width     : float -- width of each door
    door_height    : float -- requested door height
    door_interval  : int -- number of steps between doors
    clearance      : float -- clearance below the stairs above

    Returns a list of Rhino.Geometry.Brep cutting volumes.
    """

    # 1. Validate parameters
    if min(height, radius, step_height,
           step_thickness, door_width, door_height) <= 0:
        raise ValueError("Dimensions must be positive.")

    steps_per_turn = int(steps_per_turn)
    door_interval = int(door_interval)

    if steps_per_turn < 3 or door_interval < 1:
        raise ValueError("Invalid step or door interval.")

    if clearance < 0:
        raise ValueError("Clearance cannot be negative.")

    # 2. Calculate stair geometry
    number_steps = int(math.ceil(height / step_height))
    actual_rise = height / number_steps

    angle_step = 2.0 * math.pi / steps_per_turn

    # 3. Calculate available door height
    # One complete revolution above the current stair
    turn_height = actual_rise * steps_per_turn

    # Subtract upper stair thickness and clearance
    max_door_height = (
        turn_height
        - step_thickness
        - clearance
    )

    if max_door_height <= 0:
        raise ValueError(
            "Insufficient vertical clearance for doors."
        )

    # Automatically restrict the door height
    actual_door_height = min(
        door_height,
        max_door_height
    )

    cutters = []

    # 4. Generate doors at selected stair positions
    for i in range(0, number_steps, door_interval):

        # Match the angular centre of the stair
        angle = (i + 0.5) * angle_step

        # Align door threshold with stair top
        z = (i + 1) * actual_rise

        # Do not extend doors above cylinder
        if z + actual_door_height > height:
            continue

        # Radial direction
        radial = rg.Vector3d(
            math.cos(angle),
            math.sin(angle),
            0
        )

        # Tangential direction
        tangent = rg.Vector3d(
            
            -math.sin(angle),
            math.cos(angle),
            0
        )

        # Door origin at cylinder surface
        origin = rg.Point3d(
            radius * math.cos(angle),
            radius * math.sin(angle),
            z
        )

        # Local coordinate system for the door
        plane = rg.Plane(
            origin,
            radial,
            tangent
        )

        # 5. Create cutting geometry
        cut_depth = min(radius * 0.8, 1.5)

        door_box = rg.Box(
            plane,
            rg.Interval(-cut_depth, 0.5),
            rg.Interval(-door_width / 2.0, door_width / 2.0),
            rg.Interval(0, actual_door_height)
        )

        cutters.append(door_box.ToBrep())

    return cutters


def subtract_door_openings(cylinder, cutters, tolerance=0.001):
    """
    Subtract door openings from the cylinder
    using Boolean Difference.

    cylinder  : Rhino.Geometry.Brep
    cutters   : list of Rhino.Geometry.Brep
    tolerance : float

    Returns a list of Rhino.Geometry.Brep objects.
    """

    if cylinder is None:
        raise ValueError("Cylinder is missing.")

    if not cylinder.IsValid:
        raise ValueError("Cylinder is not valid.")

    if not cutters:
        return [cylinder]

    result = rg.Brep.CreateBooleanDifference(
        [cylinder],
        cutters,
        tolerance
    )

    if result is None or len(result) == 0:
        raise RuntimeError("Boolean Difference failed.")

    return list(result)


def separate_door_surfaces(cylinder_breps, tolerance=0.001):
    """
    Separate exterior cylinder surfaces from
    the planar interior surfaces of door openings.

    cylinder_breps : list of Rhino.Geometry.Brep
                     after Boolean Difference
    tolerance     : float -- geometric tolerance

    Returns:
        exterior_surfaces : list of Breps
        door_surfaces     : list of Breps
    """

    exterior_surfaces = []
    door_surfaces = []

    for brep in cylinder_breps:

        bbox = brep.GetBoundingBox(True)
        bottom_z = bbox.Min.Z
        top_z = bbox.Max.Z

        for face in brep.Faces:

            surface = face.DuplicateFace(False)
            face_box = surface.GetBoundingBox(True)

            # Check if surface is planar
            is_planar = face.IsPlanar(tolerance)

            # Exclude the horizontal top and bottom
            is_end_cap = (
                abs(face_box.Min.Z - bottom_z) < tolerance
                and abs(face_box.Max.Z - bottom_z) < tolerance
            ) or (
                abs(face_box.Min.Z - top_z) < tolerance
                and abs(face_box.Max.Z - top_z) < tolerance
            )

            if is_planar and not is_end_cap:
                door_surfaces.append(surface)
            else:
                exterior_surfaces.append(surface)

    return exterior_surfaces, door_surfaces
