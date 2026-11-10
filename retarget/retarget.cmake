set(RETARGET_DIR "${CMAKE_CURRENT_LIST_DIR}")

add_library(
	retarget
		STATIC
			"${RETARGET_DIR}/retarget_io.cpp"
			"${RETARGET_DIR}/retarget_errno.cpp"
)

file(WRITE "${CMAKE_BINARY_DIR}/retarget_heap_limit.ld" 
    "__llvm_libc_heap_limit = _estack - _Min_Stack_Size;\n"
)

target_include_directories(
	retarget
		INTERFACE 
			"${RETARGET_DIR}"
)
target_link_options(
	retarget 
		INTERFACE 
			-T${CMAKE_BINARY_DIR}/retarget_heap_limit.ld
)