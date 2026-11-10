set(STM_DIR "${CMAKE_CURRENT_LIST_DIR}")
include(FetchContent)

include("${STM_DIR}/add_cmsis_core/add_cmsis_core.cmake")
include("${STM_DIR}/add_cmsis_device/add_cmsis_device.cmake")
include("${STM_DIR}/add_cmsis_hal/add_cmsis_hal.cmake")