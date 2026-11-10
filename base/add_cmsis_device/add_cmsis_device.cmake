set(CMSIS_DEVICE_DIR "${CMAKE_CURRENT_LIST_DIR}")

FetchContent_Declare(
	cmsis-device-f4
	GIT_REPOSITORY	https://github.com/STMicroelectronics/cmsis-device-f4.git
	GIT_TAG 	master
)
FetchContent_MakeAvailable(cmsis-device-f4)

message("-- CMSIS-device-f4 DIR: ${cmsis-device-f4_SOURCE_DIR}")

# message(FATAL_ERROR "${STM32F4_DEVICE}")
if(NOT STM32F4_DEVICE)
	message(FATAL_ERROR "-DSTM32F4_DEVICE required")
endif()

include("${CMAKE_CURRENT_LIST_DIR}/parse_function.cmake")

stm32f4_resolve_part(${STM32F4_DEVICE})
message("part: ${STM32F4_PART}")
message("family: ${STM32F4_FAMILY}")
string(TOLOWER ${STM32F4_FAMILY} family)


set(ICF_FILE "${cmsis-device-f4_SOURCE_DIR}/Source/Templates/iar/linker/${family}_flash.icf")
set(LINKER_SCRIPT "${CMAKE_BINARY_DIR}/${family}_flash.ld")

if(NOT EXISTS "${ICF_FILE}")
    message(FATAL_ERROR "ICF file not found: ${ICF_FILE}")
endif()

find_package(Python3 COMPONENTS Interpreter REQUIRED)

execute_process(
    COMMAND ${Python3_EXECUTABLE} 
            "${CMSIS_DEVICE_DIR}/icf_to_ld.py"
            "${ICF_FILE}"
            "${LINKER_SCRIPT}"
    RESULT_VARIABLE ICF_CONVERT_RESULT
    ERROR_VARIABLE ICF_CONVERT_ERROR
)

if(NOT ICF_CONVERT_RESULT EQUAL 0)
    message(FATAL_ERROR "icf_to_ld.py failed: ${ICF_CONVERT_ERROR}")
endif()

if(NOT EXISTS "${LINKER_SCRIPT}")
    message(FATAL_ERROR "not created: ${LINKER_SCRIPT}")
endif()

# stm32f4_device
add_library(stm_device INTERFACE)
target_include_directories(stm_device INTERFACE
    "${cmsis-device-f4_SOURCE_DIR}/Include"
)
target_compile_definitions(stm_device INTERFACE
    ${STM32F4_FAMILY}
)
target_link_libraries(stm_device INTERFACE cmsis_core)

add_library(stm_linker INTERFACE)
target_link_options(stm_linker INTERFACE
    -T${LINKER_SCRIPT}
)

add_library(stm_system STATIC
    "${cmsis-device-f4_SOURCE_DIR}/Source/Templates/system_stm32f4xx.c"
)
target_link_libraries(stm_system PUBLIC stm_device stm_linker)

add_library(stm_startup STATIC
    "${cmsis-device-f4_SOURCE_DIR}/Source/Templates/gcc/startup_${family}.s"
)
target_link_libraries(stm_startup PUBLIC stm_device stm_system)
