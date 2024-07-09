# Copyright (c) 2023 PAL Robotics S.L. All rights reserved.
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
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument,
    OpaqueFunction,
)
from launch.conditions import IfCondition, UnlessCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource


def navigation_bringup(context, *args, **kwargs):
    actions = []
    is_public_sim = LaunchConfiguration("is_public_sim").perform(context)
    world_name = LaunchConfiguration("world_name").perform(context)
    base_type = LaunchConfiguration("base_type").perform(context)

    if base_type != "omni_base":
        base_type = "diff_base"

    tiago_2dnav = get_package_share_directory("tiago_2dnav")
    pal_maps = get_package_share_directory("pal_maps")
    nav2_bringup = get_package_share_directory("nav2_bringup")

    if is_public_sim == "True" or is_public_sim == "true":
        public_param_file = os.path.join(
            tiago_2dnav, "params", "tiago_"+base_type+"_nav_public_sim.yaml")

        nav2_bringup_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_bringup, "launch", "navigation_launch.py")
            ),
            launch_arguments={
                "params_file": public_param_file,
                "use_sim_time": "True",
            }.items(),
        )

        slam_bringup_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_bringup, "launch", "slam_launch.py")
            ),
            launch_arguments={
                "params_file": public_param_file,
                "use_sim_time": "True",
            }.items(),
            condition=IfCondition(LaunchConfiguration("slam")),
        )

        loc_bringup_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_bringup, "launch", "localization_launch.py")
            ),
            launch_arguments={
                "params_file": public_param_file,
                "map": os.path.join(
                    pal_maps,
                    "maps",
                    world_name,
                    "map.yaml",
                ),
                "use_sim_time": "True",
            }.items(),
            condition=UnlessCondition(LaunchConfiguration("slam")),
        )

        rviz_bringup_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_bringup, "launch", "rviz_launch.py")
            ),
            launch_arguments={
                "rviz_config": os.path.join(
                    tiago_2dnav, "config", "rviz", "navigation.rviz"
                ),
            }.items(),
            condition=IfCondition(is_public_sim),
        )

        actions.append(nav2_bringup_launch)
        actions.append(loc_bringup_launch)
        actions.append(slam_bringup_launch)
        actions.append(rviz_bringup_launch)
    else:
        remappings_file = os.path.join(
            tiago_2dnav, "params", "tiago_"+base_type+"_remappings_sim.yaml")

        pal_nav2_bringup = get_package_share_directory("pal_nav2_bringup")
        laser_bringup_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    pal_nav2_bringup,
                    "launch",
                    "nav_bringup.launch.py",
                )
            ),
            launch_arguments={
                "params_pkg": "tiago_laser_sensors",
                "params_file": base_type + "_laser_pipeline_sim.yaml",
                "robot_name": "tiago",
                "remappings_file": remappings_file,
            }.items(),
        )

        nav_bringup_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    pal_nav2_bringup,
                    "launch",
                    "nav_bringup.launch.py",
                )
            ),
            launch_arguments={
                "params_pkg": "tiago_2dnav",
                "params_file": "tiago_" + base_type + "_nav.yaml",
                "robot_name": "tiago",
                "remappings_file": remappings_file,
            }.items(),
        )

        slam_bringup_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    pal_nav2_bringup,
                    "launch",
                    "nav_bringup.launch.py",
                )
            ),
            launch_arguments={
                "params_pkg": "tiago_2dnav",
                "params_file": "tiago_slam.yaml",
                "robot_name": "tiago",
                "remappings_file": remappings_file,
            }.items(),
            condition=IfCondition(LaunchConfiguration("slam")),
        )

        loc_bringup_launch = IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    pal_nav2_bringup,
                    "launch",
                    "nav_bringup.launch.py",
                )
            ),
            launch_arguments={
                "params_pkg": "tiago_2dnav",
                "params_file": "tiago_" + base_type + "_loc.yaml",
                "robot_name": "tiago",
                "remappings_file": remappings_file,
            }.items(),
            condition=UnlessCondition(LaunchConfiguration("slam")),
        )

        rviz_node = Node(
            package="rviz2",
            executable="rviz2",
            arguments=["-d", os.path.join(
                tiago_2dnav,
                "config",
                "rviz",
                "navigation.rviz",
            )],
            output="screen",
        )

        actions.append(laser_bringup_launch)
        actions.append(nav_bringup_launch)
        actions.append(slam_bringup_launch)
        actions.append(loc_bringup_launch)
        actions.append(rviz_node)

    return actions


def generate_launch_description():
    """Launch Navigation common application Robot + Simulation."""
    declare_is_public_sim_arg = DeclareLaunchArgument(
        "is_public_sim",
        default_value="False",
        description="Whether or not you are using a public simulation",
    )

    declare_slam_arg = DeclareLaunchArgument(
        "slam",
        default_value="False",
        description="Whether or not you are using SLAM",
    )

    declare_world_name_arg = DeclareLaunchArgument(
        "world_name", default_value="",
        description="Specify world name, we'll convert to full path"
    )

    declare_base_type_arg = DeclareLaunchArgument(
        "base_type",
        default_value="diff_base",
        description="Type of base for the robot",
    )

    navigation_bringup_launch = OpaqueFunction(function=navigation_bringup)

    # Create the launch description and populate
    ld = LaunchDescription()
    ld.add_action(declare_is_public_sim_arg)
    ld.add_action(declare_slam_arg)
    ld.add_action(declare_world_name_arg)
    ld.add_action(declare_base_type_arg)
    ld.add_action(navigation_bringup_launch)

    return ld
