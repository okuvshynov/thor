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
    """
    Generate a color scheme by interpolating between two colors.

    Args:
        start (str): The starting color in hexadecimal format (#RRGGBB).
        end (str): The ending color in hexadecimal format (#RRGGBB).
        n (int): The number of colors to generate in the scheme (must be >= 2).

    Returns:
        list: A list of n colors in hexadecimal format (#RRGGBB),
              interpolated between the start and end colors.

    Raises:
        ValueError: If n is less than 2.
        ValueError: If start or end is not a valid hexadecimal color.
    """
    if not isinstance(n, int) or n < 2:
        raise ValueError("n must be an integer greater than or equal to 2")

    if not is_valid_hex_color(start) or not is_valid_hex_color(end):
        raise ValueError("start and end must be valid hexadecimal colors")

    color = interpolator(start, end)
    step = 1.0 / (n - 1.0)
    return [color(i * step) for i in range(n)]


def is_valid_hex_color(color):
    """
    Check if a string is a valid hexadecimal color.

    Args:
        color (str): The color to check.

    Returns:
        bool: True if the color is a valid hexadecimal color, False otherwise.
    """
    if len(color) != 7 or color[0] != '#':
        return False
    try:
        int(color[1:], 16)
        return True
    except ValueError:
        return False
