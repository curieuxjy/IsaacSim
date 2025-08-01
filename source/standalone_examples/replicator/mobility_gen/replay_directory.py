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
from isaacsim.replicator.mobility_gen.impl.build import load_scenario
from isaacsim.replicator.mobility_gen.impl.reader import MobilityGenReader
from isaacsim.replicator.mobility_gen.impl.utils.global_utils import get_world
from isaacsim.replicator.mobility_gen.impl.writer import MobilityGenWriter
from PIL import Image

if "MOBILITY_GEN_DATA" in os.environ:
    DATA_DIR = os.environ["MOBILITY_GEN_DATA"]
else:
    DATA_DIR = os.path.expanduser("~/MobilityGenData")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=str, default=None)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--rgb_enabled", type=bool, default=True)
    parser.add_argument("--segmentation_enabled", type=bool, default=True)
    parser.add_argument("--depth_enabled", type=bool, default=True)
    parser.add_argument("--instance_id_segmentation_enabled", type=bool, default=False)
    parser.add_argument("--normals_enabled", type=bool, default=False)
    parser.add_argument("--render_rt_subframes", type=int, default=1)
    parser.add_argument("--render_interval", type=int, default=1)
    args, unknown = parser.parse_known_args()

    if args.input is None:
        args.input = os.path.join(DATA_DIR, "recordings")

    if args.output is None:
        args.output = os.path.join(DATA_DIR, "replays")

    args.input = os.path.expanduser(args.input)
    args.output = os.path.expanduser(args.output)

    recording_paths = glob.glob(os.path.join(args.input, "*"))

    recording_count = 0
    for recording_path in recording_paths:
        recording_count += 1
        name = os.path.basename(recording_path)

        output_path = os.path.join(args.output, name)

        scenario = load_scenario(recording_path)

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

        reader = MobilityGenReader(recording_path)
        num_steps = len(reader)

        if os.path.exists(output_path):
            shutil.rmtree(output_path)

        writer = MobilityGenWriter(output_path)
        writer.copy_init(recording_path)

        carb.log_warn(f"============== Replaying {recording_count} / {len(recording_paths)}==============")
        carb.log_warn(f"\tInput path: {recording_path}")
        carb.log_warn(f"\tOutput path: {output_path}")
        carb.log_warn(f"\tRgb enabled: {args.rgb_enabled}")
        carb.log_warn(f"\tSegmentation enabled: {args.segmentation_enabled}")
        carb.log_warn(f"\tRendering RT subframes: {args.render_rt_subframes}")
        carb.log_warn(f"\tRender interval: {args.render_interval}")

        t0 = time.perf_counter()
        count = 0
        for step in range(0, num_steps, args.render_interval):

            carb.log_warn(f"{step} / {num_steps}")
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
