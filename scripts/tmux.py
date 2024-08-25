import subprocess

from colors import to_scheme


def get_tmux_opt(name, default):
    name = f'@thor_{name}'
    command = ["tmux", "show-option", "-gv", name]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    else:
        return default


def get_colorscheme():
    start = get_tmux_opt('color_start', '#52bf37')
    end = get_tmux_opt('color_end', '#003300')
    bands = int(get_tmux_opt('color_bands', 4))
    return to_scheme(start, end, bands)
