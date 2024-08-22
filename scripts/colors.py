def interpolator(start, end):
    """
    Returns a linear interpolation function that maps 
    [0.0; 1.0] -> [start, end] where start and end are RGB color strings
    in the format '#RRGGBB'.

    The return value of the built function is in the same '#RRGGBB' format.
    """

    # Convert start and end colors from hex strings to RGB tuples
    start_rgb = tuple(int(start[i:i+2], 16) for i in (1, 3, 5))
    end_rgb = tuple(int(end[i:i+2], 16) for i in (1, 3, 5))

    # Define the interpolation function
    def interpolate(t):
        # Clamp t to [0.0, 1.0] range
        t = min(max(t, 0.0), 1.0)

        # Calculate interpolated RGB values
        r = int(start_rgb[0] + t * (end_rgb[0] - start_rgb[0]))
        g = int(start_rgb[1] + t * (end_rgb[1] - start_rgb[1]))
        b = int(start_rgb[2] + t * (end_rgb[2] - start_rgb[2]))

        # Convert interpolated RGB values back to hex string
        return '#{:02x}{:02x}{:02x}'.format(r, g, b)

    return interpolate


def to_scheme(start, end, n):
    color = interpolator(start, end)
    step = 1.0 / (n - 1.0)
    return [color(i * step) for i in range(n)]
