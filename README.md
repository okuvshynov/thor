# thor


**T**mux **HOR**izon - minimalistic [horizon charts](https://en.wikipedia.org/wiki/Horizon_chart) for tmux status bar.


See bottom-right corner for demo:

https://github.com/user-attachments/assets/09660e54-9716-4d67-ae98-5cd3ae38c069

thor was originally created as a toy project to check if/how AI coding assistant can help me write something I'm not very familiar with (tmux addon).

Supports:
* Linux - CPU Load, NVidia GPU load, RSS, Swap
* MacOS (Apple Silicon, M1/M2/M3) - CPU Load per core cluster, GPU load, RSS, Wired memory
* Custom metrics - see [demo](demo/any.sh) 
* Graphite metrics - see [demo](demo/graphite.sh)

Motivation:
* visualize metrics history, not immediate measurements only;
* not be distracting;
* support for Apple Silicon GPU;
* support for remote metrics, e.g. via [Graphite](https://grafana.com/docs/grafana-cloud/send-data/metrics/metrics-graphite/http-api/);

## Setup

Current limitations:
* Requires Python, but no external python packages, so most default distributions of Linux/MacOS would have it. It might be possible to rewrite everything in shell, but that was becoming a little ugly.
* For local metrics starts a [background job](scripts/local.py) in separate tmux session (thor_bg). Local job will run metric providers (e.g. `powermetrics` on MacOS or `nvidia-smi` on Linux with NVidia GPU).
* IPC between [local metrics job](scripts/local.py) and the [local metric script](scripts/local.sh) is done over text files, which needs to be improved.

### MacOS

Example `.tmux.conf` for MacOS:

```
# Green colors
set -g @thor_color_start '#52bf37'
set -g @thor_color_end '#003300'
set -g @thor_color_bands 8
set -g @thor_width 12

set -g @thor_force_redraw 1
set -g @thor_interval_ms 1000

set -g status-right 'GPU:#{thor_gpu}|WiredMem:#{thor_wired}|RSS:#{thor_rss}|ECPU:#{thor_ecpu}|PCPU:#{thor_pcpu}'
set -g status-right-length 120

run-shell ~/projects/thor/thor.tmux
```

The source of this information for MacOS is `powermetrics` which needs to run as sudo. 
I don't know a way to get GPU load without sudo access. To avoid having to enter your password in background job, we can add powermetrics to `/etc/sudoers`:

```
your_user_name ALL=(ALL) NOPASSWD: /usr/bin/powermetrics
```

This way powermetrics can run with sudo and not require password.


### Linux

Example `.tmux.conf` for Linux:
```
set -g @thor_color_start '#52bf37'
set -g @thor_color_end '#003300'
set -g @thor_color_bands 8
set -g @thor_width 8

set -g status-left-length 160
set -g status-right-length 160

set -g status-left 'R:#(thor_graphite ~/thor/demo/graphite.sh)|A:#(thor_any ~/thor/demo/any.sh)|'
set -g status-right 'C:#{thor_cpu}|M:#{thor_rss}|S:#{thor_swap}'

run-shell ~/thor/thor.tmux
```

### TODO

- [ ] more metrics: io (network, disk), swap
- [ ] better IPC, no files
- [x] local runs without http?
- [x] command in tmux conf itself, not only set externally
- [x] we define command which runs status bar, but if it ran once and long-poll is set up, it does nothing
- [x] remote version
- [x] graphite API?
- [x] two parts - local with placeholders + a set of scripts to parse other data sources.
