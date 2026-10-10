# simple_counter

A ROS 2 (Humble) Python package that covers two things:

1. A basic **publisher/subscriber** pair that sends and receives messages over a topic.
2. A **turtlesim controller** that draws shapes and drives the turtle to a target pose with no human input, using only ROS 2 topics.

## Nodes

| Executable   | What it does |
|--------------|--------------|
| `publisher`  | Publishes a counting `"Hello World: N"` string to the topic `topic` every 0.5 s. |
| `subscriber` | Subscribes to `topic` and prints each message it receives. |
| `draw_shape` | Controls the turtle in turtlesim. Subscribes to `/turtle1/pose` and publishes velocity commands to `/turtle1/cmd_vel`. |

## Requirements

- Ubuntu 22.04
- ROS 2 Humble (`ros-humble-desktop`)
- `colcon` build tools

## Setup

Clone this package into the `src` folder of a ROS 2 workspace and build it:

```bash
mkdir -p ~/rover_ws/src
cd ~/rover_ws/src
git clone git@github.com:YOURUSERNAME/simple_counter.git

cd ~/rover_ws
colcon build --packages-select simple_counter
source install/setup.bash
```

Run `source ~/rover_ws/install/setup.bash` in every new terminal (or add it to `~/.bashrc`), and rebuild after any code change.

## Usage

### Publisher and subscriber

In two separate terminals (workspace sourced in both):

```bash
ros2 run simple_counter publisher
```

```bash
ros2 run simple_counter subscriber
```

### Turtle drawing

Start turtlesim in one terminal:

```bash
ros2 run turtlesim turtlesim_node
```

In a second terminal, pick a shape with the `shape` parameter:

```bash
ros2 run simple_counter draw_shape --ros-args -p shape:=square
ros2 run simple_counter draw_shape --ros-args -p shape:=star
ros2 run simple_counter draw_shape --ros-args -p shape:=spiral
ros2 run simple_counter draw_shape --ros-args -p shape:=goto -p goal_x:=8.0 -p goal_y:=3.0 -p goal_theta:=1.57
```

Reset the canvas between runs:

```bash
ros2 service call /reset std_srvs/srv/Empty
```

## How the shapes work

- **Square:** drive forward a fixed distance, turn 90 degrees, repeat four times.
- **Five-pointed star:** drive forward, turn 144 degrees, repeat five times. The lines cross to form the star.
- **Golden spiral:** constant angular velocity with a linear velocity that grows exponentially, so the radius multiplies by the golden ratio (about 1.618) every quarter turn. It stops when the turtle nears the window edge.
- **Go to pose:** a proportional controller first steers toward `(goal_x, goal_y)`, then rotates in place until the heading matches `goal_theta`.

## Parameters (`draw_shape`)

| Parameter    | Default    | Description |
|--------------|------------|-------------|
| `shape`      | `square`   | One of `square`, `star`, `spiral`, `goto`. |
| `goal_x`     | `8.0`      | Target x position (used with `goto`). |
| `goal_y`     | `3.0`      | Target y position (used with `goto`). |
| `goal_theta` | `1.57`     | Target heading in radians (used with `goto`). |

## Package layout

```
simple_counter/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
├── simple_counter/
│   ├── __init__.py
│   ├── publisher_node.py
│   ├── subscriber_node.py
│   └── draw_shape.py
└── test/
```

## Troubleshooting

- **`Package 'simple_counter' not found`:** the terminal has not sourced the workspace. Run `source ~/rover_ws/install/setup.bash`.
- **`No executable found`:** the entry point is missing from `console_scripts` in `setup.py`, or the package needs a rebuild. Check with `ros2 pkg executables simple_counter`.
- **Turtle does not move:** make sure `turtlesim_node` is running in another terminal.
