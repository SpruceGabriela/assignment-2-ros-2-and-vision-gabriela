# CST8504 Assignment 2: ROS 2 and Vision

ROS 2 Humble packages that control the turtlesim simulator (or a Create3 robot) with hand gestures detected by the camera. Description based on Assignment 2 docx.

## Packages

| Package | Type | Description |
|---|---|---|
| `aisd_msgs` | ament_cmake | Starter interfaces: the `Hand` message (`xpinky`, `xindex`) |
| `aisd_vision` | ament_python | `image_publisher` (camera frames on `video_frames`) and `hands` (MediaPipe hand detection, publishes `Hand` on `cmd_hand`) |
| `aisd_motion` | ament_python | `move` (converts `Hand` messages into `Twist` commands on `cmd_vel`) |

Data flow:

```
camera → image_publisher → video_frames → hands → cmd_hand → move → cmd_vel → turtlesim / Create3
```

## Setup on a new machine

### 1. Clone into a ROS 2 workspace

Requires an SSH key added to GitHub (or copy `~/.ssh` from a machine that already has it).

```bash
mkdir -p ~/ros2_ws/src && cd ~/ros2_ws/src
git clone git@github.com:SpruceGabriela/assignment-2-ros-2-and-vision-gabriela.git
```

### 2. Install dependencies

```bash
sudo apt install python3-pip
cd ~/ros2_ws
rosdep install -i --from-path src --rosdistro humble -y
```

Expected result: `#All required rosdeps installed successfully`

### 3. Pin compatible Python package versions

`rosdep` installs the latest `mediapipe`, which pulls in numpy 2.x and OpenCV 5. Those versions are incompatible with ROS 2 Humble's `cv_bridge` and with the MediaPipe `solutions` API used by `hands.py`. I fixed it replacing them with these versions:

```bash
sudo pip install "numpy==1.25.2" "opencv-contrib-python==4.10.0.84" "mediapipe==0.10.14"
```

### 4. Build

```bash
cd ~/ros2_ws
colcon build
```

Expected result: `Summary: N packages finished` with no errors.

## Running

Use a new terminal (not the one used for `colcon build`). The camera is only available when the user is logged in to the console.

```bash
source ~/ros2_ws/install/local_setup.bash

# Simulator only (skip when using the Create3)
ros2 run turtlesim turtlesim_node --ros-args --remap /turtle1/cmd_vel:=cmd_vel &

ros2 run aisd_vision image_publisher &
ros2 run aisd_motion move &
ros2 run aisd_vision hands
```

Gestures (right hand):

- Index finger on the right side of the image: turn right. Left side: turn left. Middle: no rotation.
- Back of the hand facing the camera: move forward. Palm facing the camera: stay still.

To stop: `Ctrl+C` stops `hands`, then `jobs` lists the background nodes and `kill %N` stops each one.
