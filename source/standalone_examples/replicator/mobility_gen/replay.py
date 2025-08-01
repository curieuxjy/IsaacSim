# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

"""

This script launches a simulation app for replaying and rendering
a recording.

"""

from isaacsim import SimulationApp

simulation_app = SimulationApp(launch_config={"headless": True})

import argparse
import glob
import os
import shutil
import time

import carb
import numpy as np
import omni.replicator.core as rep
import tqdm
from isaacsim.replicator.mobility_gen.impl.build import load_scenario
from isaacsim.replicator.mobility_gen.impl.reader import MobilityGenReader
from isaacsim.replicator.mobility_gen.impl.utils.global_utils import get_world
from isaacsim.replicator.mobility_gen.impl.writer import MobilityGenWriter
from PIL import Image

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", type=str)
    parser.add_argument("--output_path", type=str)
    parser.add_argument("--rgb_enabled", type=bool, default=True)
    parser.add_argument("--segmentation_enabled", type=bool, default=True)
    parser.add_argument("--depth_enabled", type=bool, default=True)
    parser.add_argument("--instance_id_segmentation_enabled", type=bool, default=False)
    parser.add_argument("--normals_enabled", type=bool, default=False)
    parser.add_argument("--render_rt_subframes", type=int, default=1)
    parser.add_argument("--render_interval", type=int, default=1)

    args, unknown = parser.parse_known_args()

    scenario = load_scenario(os.path.join(args.input_path))

    world = get_world()
    world.reset()

    if args.rgb_enabled:
        scenario.enable_rgb_rendering()

    if args.segmentation_enabled:
        scenario.enable_segmentation_rendering()

    if args.depth_enabled:
        scenario.enable_depth_rendering()

    if args.instance_id_segmentation_enabled:
        scenario.enable_instance_id_segmentation_rendering()

    if args.normals_enabled:
        scenario.enable_normals_rendering()

    simulation_app.update()
    rep.orchestrator.step(rt_subframes=args.render_rt_subframes, delta_time=0.0, pause_timeline=False)

    reader = MobilityGenReader(args.input_path)
    num_steps = len(reader)

    if os.path.exists(args.output_path):
        shutil.rmtree(args.output_path)

    writer = MobilityGenWriter(args.output_path)
    writer.copy_init(args.input_path)

    carb.log_warn(f"============== Replaying ==============")
    carb.log_warn(f"\tInput path: {args.input_path}")
    carb.log_warn(f"\tOutput path: {args.output_path}")
    carb.log_warn(f"\tRgb enabled: {args.rgb_enabled}")
    carb.log_warn(f"\tSegmentation enabled: {args.segmentation_enabled}")
    carb.log_warn(f"\tRendering RT subframes: {args.render_rt_subframes}")
    carb.log_warn(f"\tRender interval: {args.render_interval}")

    t0 = time.perf_counter()
    count = 0
    for step in tqdm.tqdm(range(0, num_steps, args.render_interval)):

        state_dict_original = reader.read_state_dict(index=step)

        scenario.load_state_dict(state_dict_original)
        scenario.write_replay_data()

        simulation_app.update()

        rep.orchestrator.step(rt_subframes=args.render_rt_subframes, delta_time=0.00, pause_timeline=False)

        scenario.update_state()

        state_dict = scenario.state_dict_common()

        for k, v in state_dict_original.items():
            # overwrite with original state, to ensure physics based values are correct
            if v is not None:
                state_dict[k] = v  # don't overwrite "None" values

        state_rgb = scenario.state_dict_rgb()
        state_segmentation = scenario.state_dict_segmentation()
        state_depth = scenario.state_dict_depth()
        state_normals = scenario.state_dict_normals()

        writer.write_state_dict_common(state_dict, step)
        writer.write_state_dict_rgb(state_rgb, step)
        writer.write_state_dict_segmentation(state_segmentation, step)
        writer.write_state_dict_depth(state_depth, step)
        writer.write_state_dict_normals(state_normals, step)

        count += 1
    t1 = time.perf_counter()

    carb.log_warn(f"Process time per frame: {count / (t1 - t0)}")

    simulation_app.close()
