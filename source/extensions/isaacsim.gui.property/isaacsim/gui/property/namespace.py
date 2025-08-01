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

import asyncio
from typing import List

import carb
import omni
import omni.ui as ui
from omni.kit.property.usd.prim_selection_payload import PrimSelectionPayload
from omni.kit.property.usd.usd_attribute_model import UsdAttributeModel
from omni.kit.property.usd.usd_property_widget import UsdPropertiesWidget, UsdPropertyUiEntry
from omni.kit.property.usd.usd_property_widget_builder import UsdPropertiesWidgetBuilder
from omni.kit.property.usd.widgets import ICON_PATH
from omni.kit.window.property.templates import (
    HORIZONTAL_SPACING,
    LABEL_HEIGHT,
    LABEL_WIDTH,
    SimplePropertyWidget,
    build_frame_header,
)
from pxr import Gf, Sdf, Tf, Usd
from usd.schema.isaac import robot_schema


def Singleton(class_):
    """A singleton decorator"""
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@Singleton
class NamespaceWidget(UsdPropertiesWidget):
    def __init__(self, title: str, collapsed: bool = False):
        super().__init__(title, collapsed)
        from omni.kit.property.usd import PrimPathWidget

        self._add_button_menus = []
        self._add_button_menus.append(
            PrimPathWidget.add_button_menu_entry(
                "Isaac/Namespace", show_fn=self._button_show, onclick_fn=self._button_onclick
            )
        )
        self._old_payload = None

    def destroy(self):
        from omni.kit.property.usd import PrimPathWidget

        for menu in self._add_button_menus:
            PrimPathWidget.remove_button_menu_entry(menu)
        self._add_button_menus = []

    def _button_show(self, objects: dict):
        if "prim_list" not in objects or "stage" not in objects:
            return False
        stage = objects["stage"]
        if not stage:
            return False
        prim_list = objects["prim_list"]
        if len(prim_list) < 1:
            return False
        for item in prim_list:
            if isinstance(item, Sdf.Path):
                prim = stage.GetPrimAtPath(item)
            elif isinstance(item, Usd.Prim):
                prim = item
            if not prim.HasAttribute(robot_schema.Attributes.NAMESPACE.name):
                return True
            else:
                return False
        return True

    def _button_onclick(self, payload: PrimSelectionPayload):
        stage = self._payload.get_stage()
        for path in payload:
            if path:
                prim = stage.GetPrimAtPath(path)
                if not prim.HasAttribute(robot_schema.Attributes.NAMESPACE.name):
                    prim.CreateAttribute(robot_schema.Attributes.NAMESPACE.name, Sdf.ValueTypeNames.String, True).Set(
                        prim.GetName()
                    )
        self._request_refresh()

    def _request_refresh(self):
        """Refreshes the entire property window"""
        selection = omni.usd.get_context().get_selection()
        selected_paths = selection.get_selected_prim_paths()
        window = omni.kit.window.property.get_window()._window  # noqa: PLW0212

        selection.clear_selected_prim_paths()
        window.frame.rebuild()
        selection.set_selected_prim_paths(selected_paths, True)
        window.frame.rebuild()

    def _on_usd_changed(self, notice, stage):
        targets = notice.GetChangedInfoOnlyPaths()
        if self._old_payload != self.on_new_payload(
            self._payload
        ):  # if selection didn't change, check if attribute still exists, and force rebuild if so
            self._request_refresh()
        else:
            super()._on_usd_changed(notice, stage)

    def _get_prim(self, prim_path):
        if prim_path:
            stage = self._payload.get_stage()
            if stage:
                prim = stage.GetPrimAtPath(prim_path)
                if prim and prim.HasAttribute(robot_schema.Attributes.NAMESPACE.name):
                    return prim
        return None

    def on_new_payload(self, payload):
        """
        See PropertyWidget.on_new_payload
        """

        if not super().on_new_payload(payload):
            return False

        if len(self._payload) != 1:  # avoids allowing changing multiple prims at the same time.
            return False
        prim_path = self._payload.get_paths()[0]
        self._prim = self._get_prim(prim_path)
        self._old_payload = self._prim
        if not self._prim:
            return False

        return self._prim

    def on_remove_attr(self):
        stage = self._payload.get_stage()
        if stage:
            prim = self._get_prim(self._payload.get_paths()[0])
            if prim and prim.HasAttribute(robot_schema.Attributes.NAMESPACE.name):
                prim.RemoveProperty(robot_schema.Attributes.NAMESPACE.name)

    def _filter_props_to_build(self, props):
        props = [
            prop
            for prop in props
            if isinstance(prop, Usd.Attribute) and (prop.GetName() == robot_schema.Attributes.NAMESPACE.name)
        ]
        if props:
            props[0].SetDisplayName("Namespace")
            props[0].SetDocumentation("Namespace of the prim in Isaac Sim")
        return props

    def build_items(self):
        if self._collapsable_frame and not self._collapsable_frame.collapsed and self._prim:
            super().build_items()

    def _build_frame_header(self, collapsed, text: str, id: str = None):
        """Custom header for CollapsableFrame"""
        if id is None:
            id = text

        if collapsed:
            alignment = ui.Alignment.RIGHT_CENTER
            width = 5
            height = 7
        else:
            alignment = ui.Alignment.CENTER_BOTTOM
            width = 7
            height = 5

        header_stack = ui.HStack(spacing=8)
        with header_stack:
            with ui.VStack(width=0):
                ui.Spacer()
                ui.Triangle(
                    style_type_name_override="CollapsableFrame.Header", width=width, height=height, alignment=alignment
                )
                ui.Spacer()
            ui.Label(text, style_type_name_override="CollapsableFrame.Header", width=ui.Fraction(1))

            button_style = {"Button.Image": {"color": 0xFFFFFFFF, "alignment": ui.Alignment.CENTER}}

            ui.Spacer(width=ui.Fraction(6))
            button_style["Button.Image"]["image_url"] = "${icons}/Cancel_64.png"

            with ui.ZStack(content_clipping=True, width=16, height=16):
                ui.Button(
                    "",
                    style=button_style,
                    clicked_fn=self.on_remove_attr,
                    identifier="remove_namespace",
                    tooltip="Remove Namespace",
                )
