extern "C" {

	int *__llvm_libc_errno(void) {
		static int storage = 0;
		return &storage;
	}

} // extern "C"