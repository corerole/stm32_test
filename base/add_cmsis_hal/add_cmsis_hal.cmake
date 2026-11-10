# HAL

FetchContent_Declare(
    stm32_hal
    GIT_REPOSITORY https://github.com/STMicroelectronics/stm32f4xx_hal_driver.git
    GIT_TAG        master
)
FetchContent_MakeAvailable(stm32_hal)

set(STM32F4_HSE_VALUE 8000000U CACHE STRING "HSE crystal frequency on the board")

set(HAL_CONF_DIR "${CMAKE_BINARY_DIR}/include")
set(HAL_CONF_OUT "${HAL_CONF_DIR}/stm32f4xx_hal_conf.h")
set(HAL_CONF_TPL "${stm32_hal_SOURCE_DIR}/Inc/stm32f4xx_hal_conf_template.h")

if(NOT EXISTS "${HAL_CONF_TPL}")
    message(FATAL_ERROR "HAL config template not found: ${HAL_CONF_TPL}")
endif()

file(MAKE_DIRECTORY "${HAL_CONF_DIR}")
file(READ "${HAL_CONF_TPL}" _hal_conf_txt)

#string(REGEX REPLACE
#    "/\\*[ \t]*#define[ \t]+(HAL_[A-Za-z0-9_]+_MODULE_ENABLED)[ \t]*\\*/"
#    "#define \\1"
#    _hal_conf_txt "${_hal_conf_txt}"
#)

file(WRITE "${HAL_CONF_OUT}.tmp" "${_hal_conf_txt}")
file(COPY_FILE "${HAL_CONF_OUT}.tmp" "${HAL_CONF_OUT}" ONLY_IF_DIFFERENT)
file(REMOVE "${HAL_CONF_OUT}.tmp")

message(STATUS "HAL config: ${HAL_CONF_OUT}")

file(GLOB STM32_HAL_SOURCES CONFIGURE_DEPENDS
    "${stm32_hal_SOURCE_DIR}/Src/*.c"
)
list(FILTER STM32_HAL_SOURCES EXCLUDE REGEX "_template\\.c$")
list(FILTER STM32_HAL_SOURCES EXCLUDE REGEX "/stm32f4xx_ll_.*\\.c$")

add_library(stm_hal STATIC ${STM32_HAL_SOURCES})

target_include_directories(stm_hal PUBLIC
    "${stm32_hal_SOURCE_DIR}/Inc"
    "${HAL_CONF_DIR}"
)

target_compile_definitions(stm_hal PUBLIC
    USE_HAL_DRIVER
)

target_link_libraries(stm_hal PUBLIC stm_device)