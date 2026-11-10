using size_t = unsigned long long int;
extern "C" {
	void *__llvm_libc_stderr_cookie = nullptr;
	void __llvm_libc_stdio_write(void *cookie, const char *buf, size_t size) { }
} // extern "C"