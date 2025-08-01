# SPDX-FileCopyrightText: Copyright (c) 2020-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import sys

from isaacsim import SimulationApp

simulation_app = SimulationApp({"headless": True})

# This sample loads an articulation and prints its information
import carb
import omni
from isaacsim.storage.native import get_assets_root_path
from omni.isaac.dynamic_control import _dynamic_control

stage = simulation_app.context.get_stage()

assets_root_path = get_assets_root_path()
if assets_root_path is None:
    carb.log_error("Could not find Isaac Sim assets folder")
    simulation_app.close()
    sys.exit()
asset_path = assets_root_path + "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd"
omni.usd.get_context().open_stage(asset_path)
# start simulation
omni.timeline.get_timeline_interface().play()

# perform timestep
simulation_app.update()

dc = _dynamic_control.acquire_dynamic_control_interface()
# Get handle to articulation
art = dc.get_articulation("/panda")
if art == _dynamic_control.INVALID_HANDLE:
    print("*** '%s' is not an articulation" % "/panda")
else:
    # Print information about articulation
    root = dc.get_articulation_root_body(art)
    print(str("Got articulation handle %d \n" % art) + str("--- Hierarchy\n"))

    body_states = dc.get_articulation_body_states(art, _dynamic_control.STATE_ALL)
    print(str("--- Body states:\n") + str(body_states) + "\n")

    dof_states = dc.get_articulation_dof_states(art, _dynamic_control.STATE_ALL)
    print(str("--- DOF states:\n") + str(dof_states) + "\n")

    dof_props = dc.get_articulation_dof_properties(art)
    print(str("--- DOF properties:\n") + str(dof_props) + "\n")

# Simulate robot coming to a rest configuration
for i in range(100):
    simulation_app.update()

# Simulate robot for a fixed number of frames and specify a joint position target
for i in range(100):
    dof_ptr = dc.find_articulation_dof(art, "panda_joint2")
    # This should be called each frame of simulation if state on the articulation is being changed.
    dc.wake_up_articulation(art)
    # Set joint position target
    dc.set_dof_position_target(dof_ptr, -1.5)
    simulation_app.update()

simulation_app.close()
