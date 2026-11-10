set(CMSIS_CORE_DIR "${CMAKE_CURRENT_LIST_DIR}")

FetchContent_Declare(
    cmsis-core
    GIT_REPOSITORY https://github.com/STMicroelectronics/cmsis-core.git
    GIT_TAG        master
)

FetchContent_MakeAvailable(cmsis-core)

message("-- CMSIS-core directory: ${cmsis-core_SOURCE_DIR}")

set(CMSIS_CORE_INCLUDE_DIR "${cmsis-core_SOURCE_DIR}/CMSIS/Core/Include")

if(NOT EXISTS "${CMSIS_CORE_INCLUDE_DIR}")
	message(FATAL_ERROR "CMSIS-core unavailable")
endif()

add_library(cmsis_core INTERFACE)

target_include_directories(
	cmsis_core 
		INTERFACE
			${CMSIS_CORE_INCLUDE_DIR}
)
