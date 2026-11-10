import std;

#include "stm32f4xx_hal.h"

extern "C" void SysTick_Handler(void) { HAL_IncTick(); }

int main() {
	HAL_Init();
    volatile std::uint32_t t0 = HAL_GetTick();
    HAL_Delay(100);
    volatile std::uint32_t t1 = HAL_GetTick();

	constexpr std::string_view h = "Hello World!";
    std::vector<char> x;
	for(auto e : h) { x.push_back(e); }
	
	while (true) { }
}