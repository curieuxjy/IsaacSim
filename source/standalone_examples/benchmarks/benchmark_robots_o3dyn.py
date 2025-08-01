# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--num-robots", type=int, default=1, help="Number of robots")
parser.add_argument("--num-frames", type=int, default=600, help="Number of frames to run benchmark for")
parser.add_argument("--num-gpus", type=int, default=None, help="Number of GPUs on machine.")
parser.add_argument("--max-in-line", type=int, default=10, help="Max number of robots in line")
parser.add_argument(
    "--physics",
    type=str,
    default="torch",
    choices=["warp", "torch", "numpy"],
    help="Choose physics backend - numpy for CPU",
)
parser.add_argument("--gpu-frametime", action="store_true", help="Enable GPU frametime measurement")
parser.add_argument("--non-headless", action="store_false", help="Run with GUI - nonheadless mode")
parser.add_argument("--viewport-updates", action="store_false", help="Enable viewport updates when headless")
parser.add_argument(
    "--backend-type",
    default="OmniPerfKPIFile",
    choices=["LocalLogMetrics", "JSONFileMetrics", "OsmoKPIFile", "OmniPerfKPIFile"],
    help="Benchmarking backend, defaults",
)

args, unknown = parser.parse_known_args()

n_robots = args.num_robots
n_frames = args.num_frames
n_gpus = args.num_gpus
max_line = args.max_in_line
physics_backend = args.physics
gpu_frametime = args.gpu_frametime
headless = args.non_headless
viewport_updates = args.viewport_updates

from isaacsim import SimulationApp

simulation_app = SimulationApp(
    {"headless": headless, "max_gpu_count": n_gpus, "disable_viewport_updates": viewport_updates}
)

import carb
import isaacsim.core.utils.stage as stage_utils
import numpy as np
import omni.kit.test
from isaacsim.core.experimental.prims import Articulation
from isaacsim.core.simulation_manager import SimulationManager
from isaacsim.core.utils.extensions import enable_extension
from isaacsim.core.utils.viewports import set_camera_view
from omni.kit.viewport.utility import get_active_viewport

enable_extension("isaacsim.benchmark.services")
from isaacsim.benchmark.services import BaseIsaacBenchmark

# Create benchmark
benchmark = BaseIsaacBenchmark(
    benchmark_name="benchmark_o3dyn_robot",
    workflow_metadata={
        "metadata": [
            {"name": "num_robots", "data": n_robots},
            {"name": "num_gpus", "data": carb.settings.get_settings().get("/renderer/multiGpu/currentGpuCount")},
            {"name": "physics_backend", "data": physics_backend},
        ]
    },
    backend_type=args.backend_type,
    gpu_frametime=gpu_frametime,
)
benchmark.set_phase("loading", start_recording_frametime=False, start_recording_runtime=True)

robot_path = benchmark.assets_root_path + "/Isaac/Robots/Fraunhofer/O3dyn/o3dyn.usd"
scene_path = benchmark.assets_root_path + "/Isaac/Environments/Simple_Warehouse/full_warehouse.usd"
benchmark.fully_load_stage(scene_path)

SimulationManager.set_backend(physics_backend)
if physics_backend == "numpy":
    SimulationManager.set_physics_sim_device("cpu")
else:
    SimulationManager.set_physics_sim_device("cuda")

set_camera_view(eye=[-6, -15.5, 6.5], target=[-6, 10.5, -1], camera_prim_path="/OmniverseKit_Persp")

# Configure robots
robot_positions = []
for i in range(n_robots):
    prim_path = f"/Robots/Robot_{i}"
    stage_utils.add_reference_to_stage(robot_path, prim_path=prim_path)
    # Position robots in a grid pattern:
    robot_positions.append([-3 * (i % max_line) + 3, -3 * (i // max_line), 0.1])

# Collect all robot prims into Articulation wrapper
robot_prim_paths = "/Robots/Robot_*"
robots = Articulation(robot_prim_paths, positions=robot_positions)

viewport = get_active_viewport()
viewport.set_texture_resolution([1280, 720])
omni.kit.app.get_app().update()
omni.kit.app.get_app().update()


timeline = omni.timeline.get_timeline_interface()
timeline.play()
omni.kit.app.get_app().update()

# Start robot movement - rotation in place
joint_velocities = np.tile((5 * np.array([1.0, -1.0, 1.0, -1.0], dtype=np.float32)), (n_robots, 1))
joint_names = ["wheel_fr_joint", "wheel_fl_joint", "wheel_rr_joint", "wheel_rl_joint"]

robots.set_dof_velocity_targets(velocities=joint_velocities, dof_indices=robots.get_dof_indices(joint_names))

omni.kit.app.get_app().update()

benchmark.store_measurements()
benchmark.set_phase("benchmark")
for _ in range(0, n_frames):
    omni.kit.app.get_app().update()

benchmark.store_measurements()
benchmark.stop()

timeline.stop()

simulation_app.close()
