-- SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
-- SPDX-License-Identifier: Apache-2.0
--
-- Licensed under the Apache License, Version 2.0 (the "License");
-- you may not use this file except in compliance with the License.
-- You may obtain a copy of the License at
--
-- http://www.apache.org/licenses/LICENSE-2.0
--
-- Unless required by applicable law or agreed to in writing, software
-- distributed under the License is distributed on an "AS IS" BASIS,
-- WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
-- See the License for the specific language governing permissions and
-- limitations under the License.

-- Use folder name to build extension name and tag.
local ext = get_current_extension_info()

-- Generic dummy project for extension, adds all python/toml/lua/rst files to VS. Automatically links "config" and "scripts" folders.
project_ext(ext)
-- Link more folder to target folder.
repo_build.prebuild_link { "docs", ext.target_dir .. "/docs" }
repo_build.prebuild_link { "data", ext.target_dir .. "/data" }
repo_build.prebuild_link { "isaacsim", ext.target_dir .. "/isaacsim" }
