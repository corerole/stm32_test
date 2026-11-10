# stm32_test

A minimal **C++23 project for STM32F4** built with **Clang 24 + LLVM libc / libc++ / libunwind**
Using CMake with C++23 modules support. 
CMSIS and STM32 HAL are fetched from ST’s GitHub.

## Prerequisites

| Component |
|---|
| **CMake** |
| **Ninja** |
| **Clang** |
| **LLVM libc / libc++ / libc++abi / libunwind** |
| **Python** |
| **Git** |

## Building LLVM host tools

```bash
git clone https://github.com/llvm/llvm-project.git
cd llvm-project
mkdir build_host && mkdir build_host_result
cd build_host

cmake ../llvm -GNinja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=../build_host_result \
  -DLLVM_ENABLE_PROJECTS="clang;clang-tools-extra;lld" \
  -DLLVM_ENABLE_RUNTIMES="libc;libcxx;compiler-rt"

cmake --build . --config=Release
cmake --install .
```

## Building SYSROOT
```PS
cd ..
mkdir build_sysroot 
cmake ../runtimes -G Ninja \
  -DCMAKE_DEPENDS_USE_COMPILER=OFF \
  -DCMAKE_SYSTEM_NAME=Generic \
  -DCMAKE_SYSTEM_PROCESSOR=arm \
  -DCMAKE_INSTALL_PREFIX="<sysroot_install_dir>" \
  -DCMAKE_ASM_COMPILER="<llvm_host_install_dir>/bin/clang.exe" \
  -DCMAKE_C_COMPILER="<llvm_host_install_dir>/bin/clang.exe" \
  -DCMAKE_CXX_COMPILER="<llvm_host_install_dir>/bin/clang++.exe" \
  -DCMAKE_LINKER="<ld.lld_path>" \
  -DCMAKE_C_COMPILER_TARGET=arm-none-eabi \
  -DCMAKE_CXX_COMPILER_TARGET=arm-none-eabi \
  -DCMAKE_ASM_COMPILER_TARGET=arm-none-eabi \
  -DCMAKE_TRY_COMPILE_TARGET_TYPE=STATIC_LIBRARY \
  -DCOMPILER_RT_BAREMETAL_BUILD=ON \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
  -DLLVM_ENABLE_RUNTIMES="libc;libcxx;libunwind;libcxxabi;compiler-rt" \
  -DLLVM_FORCE_BUILD_RUNTIME=ON \
  -DLLVM_RUNTIME_TARGETS=arm-none-eabi \
  -DLIBCXX_ENABLE_SHARED=OFF \
  -DLIBCXX_ENABLE_STATIC=ON \
  -DLLVM_LIBC_FULL_BUILD=ON \
  -DLIBC_TARGET_TRIPLE=arm-none-eabi \
  -DLIBCXX_TARGET_TRIPLE=arm-none-eabi \
  -DCXX_LINKER_SUPPORTS_STDLIB=TRUE \
  -DLIBCXXABI_BAREMETAL=ON \
  -DLIBCXX_BAREMETAL=ON \
  -DLIBCXX_ENABLE_THREADS=OFF \
  -DLIBCXX_ENABLE_MONOTONIC_CLOCK=OFF \
  -DCMAKE_C_FLAGS="-mcpu=cortex-m4 -mthumb -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=hard -fuse-ld=<ld.lld_path> -Wno-atomic-alignment" \
  -DCMAKE_CXX_FLAGS="-mcpu=cortex-m4 -mthumb -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=hard -Wno-atomic-alignment" \
  -DCMAKE_ASM_FLAGS="-mcpu=cortex-m4 -mthumb -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=hard" \
  -DCOMPILER_RT_BAREMETAL_BUILD=ON \
  -DLIBCXX_LIBC=llvm-libc \
  -DLIBC_ENABLE_UNITTESTS=OFF \
  -DLIBC_ENABLE_HERMETIC_TESTS=OFF \
  -DLLVM_INCLUDE_TESTS=OFF \
  -DLIBCXX_USE_LLVM_LIBC=ON \
  -DLIBCXX_LIBC="llvm-libc" \
  -DRUNTIMES_USE_LIBC="llvm-libc" \
  -DLIBCXX_ENABLE_WIDE_CHARACTERS=OFF \
  -DLIBCXX_ENABLE_FILESYSTEM=OFF \
  -DLIBCXX_ENABLE_LOCALIZATION=OFF \
  -DLIBCXX_ENABLE_RANDOM_DEVICE=OFF \
  -DLIBUNWIND_HAS_DL_LIB=OFF \
  -DLIBUNWIND_ENABLE_THREADS=OFF \
  -DLIBUNWIND_IS_BAREMETAL=ON \
  -DLIBCXXABI_ENABLE_THREADS=OFF \
  -DLIBUNWIND_ENABLE_ASSERTIONS=OFF \
  -DCOMPILER_RT_BAREMETAL_BUILD=ON \
  -DLLVM_DEFAULT_TARGET_TRIPLE=arm-none-eabi \
  -DLLVM_HOST_TRIPLE=x86_64-pc-windows-msvc \
  -DCOMPILER_RT_DEFAULT_TARGET_ONLY=ON
```

## toolchain.cmake
```CMake
set(LLVM_HOST_TOOLCHAIN_PATH "<llvm_host_install_dir>")
set(SYSROOT "<sysroot_install_dir>")

set(CMAKE_SYSTEM_NAME      Generic)
set(CMAKE_SYSTEM_PROCESSOR arm)
set(CMAKE_LINKER           "${LLVM_HOST_TOOLCHAIN_PATH}/bin/ld.lld.exe")
set(CMAKE_C_COMPILER       "${LLVM_HOST_TOOLCHAIN_PATH}/bin/clang.exe")
set(CMAKE_CXX_COMPILER     "${LLVM_HOST_TOOLCHAIN_PATH}/bin/clang++.exe")
set(CMAKE_ASM_COMPILER     "${LLVM_HOST_TOOLCHAIN_PATH}/bin/clang.exe")
set(CMAKE_AR               "${LLVM_HOST_TOOLCHAIN_PATH}/bin/llvm-ar.exe")
set(CMAKE_RANLIB           "${LLVM_HOST_TOOLCHAIN_PATH}/bin/llvm-ranlib.exe")
set(CMAKE_STRIP            "${LLVM_HOST_TOOLCHAIN_PATH}/bin/llvm-strip.exe")

set(CMAKE_C_COMPILER_TARGET   arm-none-eabi)
set(CMAKE_CXX_COMPILER_TARGET arm-none-eabi)
set(CMAKE_ASM_COMPILER_TARGET arm-none-eabi)

set(ARCH_FLAGS " -mcpu=cortex-m4 -mthumb -march=armv7e-m -mfpu=fpv4-sp-d16 -mfloat-abi=hard")
string(APPEND CMAKE_C_FLAGS_INIT   " ${ARCH_FLAGS}")
string(APPEND CMAKE_CXX_FLAGS_INIT " ${ARCH_FLAGS}")
string(APPEND CMAKE_ASM_FLAGS_INIT " ${ARCH_FLAGS}")

string(APPEND CMAKE_CXX_FLAGS_INIT " -nostdinc++ -nostdlibinc")
string(APPEND CMAKE_C_FLAGS_INIT   " -nostdlibinc")

string(APPEND CMAKE_CXX_FLAGS_INIT
    " -isystem ${SYSROOT}/include/c++/v1"
    " -isystem ${SYSROOT}/include/"
)

string(APPEND CMAKE_C_FLAGS_INIT
    " -isystem ${SYSROOT}/include/"
)

set(CMAKE_EXE_LINKER_FLAGS_INIT "")
string(APPEND CMAKE_EXE_LINKER_FLAGS_INIT
    " -nostartfiles"
    " -nostdlib"
    " -fuse-ld=${LLVM_HOST_TOOLCHAIN_PATH}/bin/ld.lld.exe"
    " -L${SYSROOT}/lib/arm-none-eabi"
    " -L${SYSROOT}/lib/"
    " -L${SYSROOT}/lib/generic"
    " -lclang_rt.builtins-arm"
)
set(LIBCXX_MODULES_JSON "${SYSROOT}/lib/libc++.modules.json")
set(CMAKE_CXX_STDLIB_MODULES_JSON "${LIBCXX_MODULES_JSON}")
set(CMAKE_TRY_COMPILE_TARGET_TYPE STATIC_LIBRARY)
```

## Build it
```bash
cd stm32_test 
mkdir build
cd build
cmake .. -GNinja -DCMAKE_BUILD_TYPE=Release -DCMAKE_DEPENDS_USE_COMPILER=FALSE -DCMAKE_TOOLCHAIN_FILE=<toolchain.cmake> -DSTM32F4_DEVICE=STM32F4... -DSTM32F4_HSE_VALUE=8000000
cmake --build . --config=Release --clear-first
ls
stm32_test - your firmware
```

