# Copyright 2026 Elad Fish
# Based on turtlebot3_gazebo/launch/empty_world.launch.py,
# Copyright 2019 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    bringup_dir = get_package_share_directory('tag_dock_bringup')
    tb3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    tb3_launch_dir = os.path.join(tb3_gazebo_dir, 'launch')
    gz_sim_launch = os.path.join(
        get_package_share_directory('ros_gz_sim'), 'launch', 'gz_sim.launch.py')
    world = os.path.join(bringup_dir, 'worlds', 'warehouse.sdf')

    x_pose = LaunchConfiguration('x_pose')
    y_pose = LaunchConfiguration('y_pose')
    gui = LaunchConfiguration('gui')

    return LaunchDescription([
        DeclareLaunchArgument('x_pose', default_value='0.0', description='Start x [m]'),
        DeclareLaunchArgument('y_pose', default_value='0.0', description='Start y [m]'),
        DeclareLaunchArgument('gui', default_value='true', description='Open the Gazebo window'),

        # First, so Gazebo starts with these folders on its model search path.
        AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH', os.path.join(tb3_gazebo_dir, 'models')),
        AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH', os.path.join(bringup_dir, 'models')),

        # Simulation server: runs physics and sensors (-r: start unpaused, -s: no window).
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_sim_launch),
            launch_arguments={
                'gz_args': ['-r -s -v2 ', world],
                'on_exit_shutdown': 'true',
            }.items()),

        # Gazebo window (-g). Skipped with gui:=false.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(gz_sim_launch),
            launch_arguments={'gz_args': '-g -v2 '}.items(),
            condition=IfCondition(gui)),

        # Publishes the robot's fixed TF frames (base, wheels, camera...) from its URDF.
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(tb3_launch_dir, 'robot_state_publisher.launch.py')),
            launch_arguments={'use_sim_time': 'true'}.items()),

        # Spawns the waffle_pi and starts the ROS <-> Gazebo bridges
        # (clock, tf, odom, cmd_vel, scan, imu, camera).
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(tb3_launch_dir, 'spawn_turtlebot3.launch.py')),
            launch_arguments={'x_pose': x_pose, 'y_pose': y_pose}.items()),
    ])