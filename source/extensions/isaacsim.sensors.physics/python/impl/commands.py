# SPDX-FileCopyrightText: Copyright (c) 2018-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

import carb
import omni.isaac.IsaacSensorSchema as IsaacSensorSchema
import omni.kit.commands
import omni.kit.utils
import omni.usd
from isaacsim.core.utils.prims import delete_prim
from isaacsim.core.utils.stage import get_next_free_path
from isaacsim.core.utils.xforms import reset_and_set_xform_ops
from pxr import Gf, PhysxSchema


class IsaacSensorCreatePrim(omni.kit.commands.Command):
    def __init__(
        self,
        path: str = "",
        parent: str = "",
        translation: Gf.Vec3d = Gf.Vec3d(0, 0, 0),
        orientation: Gf.Quatd = Gf.Quatd(1, 0, 0, 0),
        schema_type=IsaacSensorSchema.IsaacBaseSensor,
    ):
        # condensed way to copy all input arguments into self with an underscore prefix
        for name, value in vars().items():
            if name != "self":
                setattr(self, f"_{name}", value)
        self._prim_path = None

    def do(self):
        self._stage = omni.usd.get_context().get_stage()

        self._prim_path = get_next_free_path(self._path, self._parent)
        self._prim = self._schema_type.Define(self._stage, self._prim_path)
        IsaacSensorSchema.IsaacBaseSensor(self._prim).CreateEnabledAttr(True)
        reset_and_set_xform_ops(self._prim.GetPrim(), self._translation, self._orientation)

        return self._prim

    def undo(self):
        if self._prim_path is not None:
            return delete_prim(self._prim_path)


class IsaacSensorCreateContactSensor(omni.kit.commands.Command):
    def __init__(
        self,
        path: str = "/Contact_Sensor",
        parent: str = None,
        min_threshold: float = 0,
        max_threshold: float = 100000,
        color: Gf.Vec4f = Gf.Vec4f(1, 1, 1, 1),
        radius: float = -1,
        sensor_period: float = -1,
        translation: Gf.Vec3d = Gf.Vec3d(0, 0, 0),
    ):
        # condensed way to copy all input arguments into self with an underscore prefix
        for name, value in vars().items():
            if name != "self":
                setattr(self, f"_{name}", value)
        self._prim = None
        pass

    def do(self):

        if self._parent is None:
            carb.log_error("Valid parent prim must be selected before creating contact sensor prim.")
            return None

        success, self._prim = omni.kit.commands.execute(
            "IsaacSensorCreatePrim",
            path=self._path,
            parent=self._parent,
            schema_type=IsaacSensorSchema.IsaacContactSensor,
            translation=self._translation,
        )
        if success and self._prim:
            self._prim.CreateThresholdAttr().Set((self._min_threshold, self._max_threshold))
            self._prim.CreateColorAttr().Set(self._color)
            self._prim.CreateSensorPeriodAttr().Set(self._sensor_period)
            self._prim.CreateRadiusAttr().Set(self._radius)

            # Ensure parent has contact report API in it.
            stage = omni.usd.get_context().get_stage()
            parent_prim = stage.GetPrimAtPath(self._parent)
            contact_report = PhysxSchema.PhysxContactReportAPI.Apply(parent_prim)
            contact_report.CreateThresholdAttr(self._min_threshold)

            return self._prim

        else:
            carb.log_error("Could not create contact sensor prim")
            return None

    def undo(self):
        # undo must be defined even if empty
        pass


class IsaacSensorCreateImuSensor(omni.kit.commands.Command):
    def __init__(
        self,
        path: str = "/Imu_Sensor",
        parent: str = None,
        sensor_period: float = -1,
        translation: Gf.Vec3d = Gf.Vec3d(0, 0, 0),
        orientation: Gf.Quatd = Gf.Quatd(1, 0, 0, 0),
        linear_acceleration_filter_size: int = 1,
        angular_velocity_filter_size: int = 1,
        orientation_filter_size: int = 1,
    ):
        # condensed way to copy all input arguments into self with an underscore prefix
        for name, value in vars().items():
            if name != "self":
                setattr(self, f"_{name}", value)
        self._prim = None
        pass

    def do(self):
        success, self._prim = omni.kit.commands.execute(
            "IsaacSensorCreatePrim",
            path=self._path,
            parent=self._parent,
            schema_type=IsaacSensorSchema.IsaacImuSensor,
            translation=self._translation,
            orientation=self._orientation,
        )

        if success and self._prim:
            self._prim.CreateSensorPeriodAttr().Set(self._sensor_period)
            self._prim.CreateLinearAccelerationFilterWidthAttr().Set(self._linear_acceleration_filter_size)
            self._prim.CreateAngularVelocityFilterWidthAttr().Set(self._angular_velocity_filter_size)
            self._prim.CreateOrientationFilterWidthAttr().Set(self._orientation_filter_size)

            return self._prim
        else:
            carb.log_error("Could not create Imu sensor prim")
            return None

    def undo(self):
        # undo must be defined even if empty
        pass


omni.kit.commands.register_all_commands_in_module(__name__)
