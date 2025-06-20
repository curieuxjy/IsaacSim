# Changelog
## [2.0.7] - 2025-05-19
### Changed
- Update copyright and license to apache v2.0

## [2.0.6] - 2025-04-04
### Changed
- Version bump to fix extension publishing issues

## [2.0.5] - 2025-03-26
### Changed
- Cleanup and standardize extension.toml, update code formatting for all code

## [2.0.4] - 2025-03-25
### Changed
- Add import tests for deprecated extensions

## [2.0.3] - 2025-01-21
### Changed
- Update extension description and add extension specific test settings

## [2.0.2] - 2024-10-24
### Changed
- Updated dependencies and imports after renaming

## [2.0.1] - 2024-10-14
### Deprecated
- Restores previously-missing deprecated packages.

## [2.0.0] - 2024-09-20
### Deprecated
- Extension deprecated since Isaac Sim 4.5.0. Replaced by isaacsim.benchmark.services.

## [1.10.2] - 2024-09-09
### Fixed
- Physics time not captured unless app update was called

## [1.10.1] - 2024-09-05
### Fixed
- convert sim_elapsed_time to ms for calculating real-time factor

## [1.10.0] - 2024-08-05
### Changed
- use omni.physdx.get_physx_benchmarks_interface() to get physics simulation profiling data

## [1.9.0] - 2024-07-17
### Changed
- omni.hydra is not a required dependency, but is needed to collect memory stats
- omni.kit.test is a required dependency, not just for running tests

### Removed
- removed unused omni.kit.profiler.window dependency

## [1.8.3] - 2024-07-15
### Added
- Ability to store custom measurements in a specified phase

## [1.8.2] - 2024-07-02
### Changed
- Use psutil to count CPU cores.

## [1.8.1] - 2024-06-25
### Removed
- Stray print statement in IsaacFrameTimeRecorder

## [1.8.0] - 2024-06-07
### Changed
- Always capture physics metrics even if stepping without rendering

## [1.7.0] - 2024-05-01
### Changed
- Removes dependency on omni.isaac.core_nodes

## [1.6.0] - 2024-05-01
### Added
- ability to enable/disable frametime and runtime separately when starting a phase

## [1.5.0] - 2024-04-29
### Changed
- cleaned up imports
- updated docstrings
- removed unused functions

## [1.4.2] - 2024-04-15
### Fixed
- Error when zero frames were collected
- Test failure

## [1.4.1] - 2024-03-25
### Fixed
- Frametime collector skips frametime collection if start time is `None` (i.e if `set_phase(start_recording_time=False)` is called

## [1.4.0] - 2024-02-02
### Added
- User can now specify per-benchmark metadata when using BaseIsaacBenchmark, which will persist across phases

### Changed
- Refactors "middleware" in extension
- OsmoKPIFile backend now prints one KPI file per phase, rather than one KPI file per workflow
- Deprecates individual runtime/frametime APIs in BaseIsaacBenchmark, moves functionality to start_phase() and stop_collecting_measurements()
- metrics.measurements.TestRun renamed to metrics.measurements.TestPhase

## [1.3.2] - 2024-02-02
### Changed
- OSMOKPIFile writer logs exact KPI keys, rather than abbreviation.

## [1.3.1] - 2024-02-02
### Changed
- Updated path to the nucleus extension

## [1.3.0] - 2024-01-30
### Added
- IsaacStartupTimeRecorder measures startup time, collected only during "startup" phase

## [1.2.0] - 2024-01-25
### Added
- OsmoKPIFile writer logs KPIs to console.

## [1.1.0] - 2024-01-19
### Added
- Adds new BaseIsaacBenchmark for non-async benchmarking
- Adds new standalone examples for non-async benchmarking
- Adds OsmoKPIFile writer to publish KPIs compatible with OSMO's Kratos backend

### Fixed
- Async benchmark stability on new stage open
- ROS2 bridge camera helper

### Changed
- Move BaseIsaacBenchmark -> BaseIsaacBenchmarkAsync, for (eg) async unit tests

## [1.0.0] - 2024-01-04
### Changed
- Remove depdencies and added classes needed to make benchmarks work independently
- Helpers specific to certain benchmarks were moved to benchmarks extension

## [0.2.0] - 2023-12-14
### Added
- Added ROS2 camera graph helper

## [0.1.1] - 2023-11-30
### Changed
- Use get_assets_root_path_async()

## [0.1.0] - 2023-11-14
### Changed
- Moved utils from omni.isaac.benchmark into omni.isaac.benchmark.services

### Added
- Quasi-initial version
