![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)

# CaBot

CaBot (Carry on Robot) is an AI suitcase to help people with visually impairments travel independently. Can you imagine to walk around at airports without vision? It’s huge open space and there are lots of things and people, so that it is really dangerous for them to walk around at airports. [see project detail](https://www.cs.cmu.edu/~NavCog/cabot.html)

## CaBot v2

CaBot v2 uses ROS1, ROS2, and ros1_bridge to use [navigation2](https://github.com/ros-planning/navigation2) package for ROS2 and existing packges for ROS1. Also, it uses Docker container to maintain development/production systems.

### Hardware
- Robot frame + handle
  - [CaBot2-E2 model](https://github.com/CMU-cabot/cabot_design/tree/master/cabot2-e2)
  - [CaBot2-GT model](https://github.com/CMU-cabot/cabot_design/tree/master/cabot2-gt)
- LiDAR
  - Velodyne VLP-16
- Stereo Camera(s)
  - 1 RealSense camera (D435)
  - 3 RealSense cameras (**under development**)
- Motor Controller
  - ODrive Motor Controller v3.6 (Firmware v0.5.1)
- Micro Controller (Handle and sensors)
  - [cabot-arduino](https://github.com/CMU-cabot/cabot-arduino) for controlling handle, IMU, and other sensors
- Processor
  - PC with NVIDIA GPU (ZOTAC Magnus EN72070V)
  - NUC (Ruby R8) + Jetson Xavier NX (**under development**)

### Localization
- [mf_localization](https://github.com/CMU-cabot/cabot/tree/dev/mf_localization) (cartogrpher+iBeacons/WiFi)

### Tested Environment
- PC
  - Host Ubuntu 20.04
  - Docker v20
  - docker-compose v1.28~
  - Docker compose services
    - `ros1`: Ubuntu20.04, ROS1 noetic
    - `ros2`: Ubuntu20.04, ROS2 galactic
    - `bridge`: Ubuntu20.04, ROS1 noetic, ROS2 galactic
    - `localization`: Ubuntu20.04, ROS1 noetic
    - `people`: Ubuntu20.04, ROS1 noetic
- Jetson (**under development**)
  - Host Ubuntu 18.04
  - Docker compose services
  - `people-jetson`: Ubuntu18.04, ROS1 melodic (source build with python3), Jetson

## Setup
- import thirdparty repos by using vcstool
  ```
  pip3 install vcstool # if you don't have vcs
  tools/setup-thirdparty-repos.sh
  ```
- run all script in tools based on your requirements
  ```
  cd tools
  ./install-docker.sh                # if you need docker
  ./install-arm-emulator.sh          # if you use Jetson
  ./install-host-ros.sh              # if you watch system performance
  ./install-realsense-udev-rules.sh  # if you use realsense camera
  ./setup-display.sh                 # for display connections from docker containers
  ./setup-usb.sh                     # if you run physical robot
  ./setup-model.sh                   # if you need to recognize people
  ```

## Build Docker Images
- build docker containers (at top direcotry)
  ```
  ./build-docker.sh -P                              # for build all images for PC with nVIDIA gpu
  ./build-docker.sh -g mesa -P                      # for build all images for PC with mesa/OpenGL compatible gpu
  ./prebuild-docker.sh l4t && ./build-docker.sh l4t # for build image for Jetson (only people)
  ```

## Launch
- prepare .env file
  ```
  ROS_IP               # host machine IP address or 127.0.0.1 for single PC setting
  MASTER_IP            # ROS1 master IP address or 127.0.0.1 for single PC setting
  CABOT_SITE           # package name for cabot site (default=cabot_site_cmu_3d)
  ROBOT                # robot name (default=cabot2-gt1)
  CABOT_INITX          # initial robot position x for gazebo
  CABOT_INITY          # initial robot position y for gazebo
  CABOT_INITZ          # initial robot position z for gazebo
  CABOT_INITA          # initial robot angle (degree) for gazebo
  CABOT_TOUCH_PARAMS   # touch sensor parameter for cabot-arduino handle default=[128,48,24]
  GAMEPAD              # gamepad type for remote controll (ex. PS4 controller) / pro (Nintendo Switch Pro controller)
  ```
- run containers. This will show up Rviz.
  ```
  ./launch.sh -s       # for simulator
  ./launch.sh          # for robot
  ./launch.sh -r       # for robot with recording rgb camera
  ```

### Navigate CaBot

- **`Nav2 Goal` tool does not work properly**: the robot will move with the nav2 default BT xml (only for debugging purpose)
- right click on a blue dot in `demo_2d_floors.rviz` (-Y option for ros1 service to show) and select "Navigate to Here" menu
- or directory publish a `/cabot/event` topic on ROS1. see [here](doc/destinations.md) more detail about destinations.
  ```
  # example destination in cabot_site_cmu_3d environment
  $ rostopic pub -1 /cabot/event std_msgs/String "data: 'navigation;destination;EDITOR_node_1496171299873'"
  ```

### CaBot app for iOS

TBD

## Customization

See [customization](doc/customization.md) for more details.

## Getting Involved

### Issues and Questions

Please use Issues for both issue tracking and your questions about CaBot repository.

### Developer Certificate of Origin (DCO)

The developer need to add a Signed-off-by statement and thereby agrees to the DCO, which you can find below. You can add either -s or --signoff to your usual git commit commands. If Signed-off-by is attached to the commit message, it is regarded as agreed to the Developer's Certificate of Origin 1.1.


https://developercertificate.org/
```
Developer's Certificate of Origin 1.1

By making a contribution to this project, I certify that:

(a) The contribution was created in whole or in part by me and I
    have the right to submit it under the open source license
    indicated in the file; or

(b) The contribution is based upon previous work that, to the
    best of my knowledge, is covered under an appropriate open
    source license and I have the right under that license to
    submit that work with modifications, whether created in whole
    or in part by me, under the same open source license (unless
    I am permitted to submit under a different license), as
    Indicated in the file; or

(c) The contribution was provided directly to me by some other
    person who certified (a), (b) or (c) and I have not modified
    it.

(d) I understand and agree that this project and the contribution
    are public and that a record of the contribution (including
    all personal information I submit with it, including my
    sign-off) is maintained indefinitely and may be redistributed
    consistent with this project or the open source license(s)
    involved.
```

# License

[MIT License](LICENSE)


---
The following files/folder are under Apache-2.0 License

- cabot_description/urdf/sensors/_d435.gazebo.xacro
- cabot_description/urdf/sensors/_d435.urdf.xacro
- cabot_navigation/launch/cartographer_mapping.launch
- nav2_action_bridge/cmake/find_ros1_package.cmake
- docker/bridge/ros1/nav2_msgs/
