# CMakeLists.txt
cmake_minimum_required(VERSION 4.2.0)

set(PROJECT_DIR "${CMAKE_CURRENT_LIST_DIR}")

set(CMAKE_CXX_STANDARD 23)
set(CMAKE_CXX_STANDARD_REQUIRED TRUE)
set(CMAKE_CXX_EXTENSIONS NO)
set(CMAKE_EXPERIMENTAL_CXX_IMPORT_STD "f35a9ac6-8463-4d38-8eec-5d6008153e7d")
set(CMAKE_CXX_SCAN_FOR_MODULES ON)
set(CMAKE_CXX_MODULE_STD ON)

project("stm32_test" LANGUAGES ASM C CXX)

# include("${PROJECT_DIR}/toolchain_test/toolchain_test.cmake")

if(NOT STM32F4_DEVICE) 
	message(FATAL_ERROR "use -DSTM32F4_DEVICE=/ your device name like STM32F479AI /")
endif()

message("Configuring for device: ${STM32F4_DEVICE}")

add_executable(${PROJECT_NAME})

# -------- remove_it --------
include("${PROJECT_DIR}/retarget/retarget.cmake")
# ---------------------------

include("${PROJECT_DIR}/base/stm.cmake")
include("${PROJECT_DIR}/src/src.cmake")

target_sources(${PROJECT_NAME} PUBLIC "${PROJECT_DIR}/main.cpp")

target_link_libraries(
	${PROJECT_NAME}
		PRIVATE
			c++
			c++abi
			unwind
			c
			m
# -------- remove_it --------
			stm_hal
			stm_system
			stm_device
			stm_linker
			stm_startup
			retarget
# ---------------------------
)
