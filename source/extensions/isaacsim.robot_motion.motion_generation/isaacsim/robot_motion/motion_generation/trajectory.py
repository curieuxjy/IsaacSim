# SPDX-FileCopyrightText: Copyright (c) 2021-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import List, Tuple

import numpy as np


class Trajectory:
    """Interface class for defining a continuous-time trajectory for a robot in Isaac Sim.
    A Trajectory may be passed to an ArticulationTrajectory to have its continuous-time output discretized and converted
    to a ArticulationActions.
    """

    def __init__(self):
        pass

    @property
    def start_time(self) -> float:
        """Return the start time of the trajectory.

        Returns:
            float: Start time of the trajectory.
        """
        pass

    @property
    def end_time(self) -> float:
        """Return the end time of the trajectory

        Returns:
            float: End time of the trajectory
        """
        pass

    def get_active_joints(self) -> List[str]:
        """Active joints are directly controlled by this Trajectory

        A Trajectory may be specified for only a subset of the joints in a robot Articulation.  For example, it may include the DOFs in a robot
        arm, but not in the gripper.

        Returns:
            List[str]: Names of active joints.  The order of joints in this list determines the order in which a
                Trajectory will return joint targets for the robot.
        """
        return []

    def get_joint_targets(self, time: float) -> Tuple[np.array, np.array]:
        """Return joint targets for the robot at the given time.  The Trajectory interface assumes trajectories to
        be represented continuously between a start time and end time.  In instance of this class that internally generates discrete time
        trajectories will need to implement some form of interpolation for times that have not been computed.

        Args:
            time (float): Time in trajectory at which to return joint targets.

        Returns:
            Tuple[np.array,np.array]:
            joint position targets for the active robot joints\n
            joint velocity targets for the active robot joints
        """
        pass
