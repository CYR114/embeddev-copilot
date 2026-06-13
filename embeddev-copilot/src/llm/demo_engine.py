"""Demo 模式规则引擎：无 API Key 时提供可运行的演示输出"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class DemoResponse:
    content: str
    role: str = "assistant"


class DemoEngine:
    """基于模板与关键词的轻量模拟，用于面试 Demo 与本地调试"""

    def analyze_requirement(self, requirement: str, context: str = "") -> str:
        keywords = self._extract_keywords(requirement)
        return (
            f"## 需求分析\n\n"
            f"**原始需求**: {requirement}\n\n"
            f"**识别模块**: {', '.join(keywords) or '通用嵌入式模块'}\n\n"
            f"**功能拆解**:\n"
            f"1. 初始化外设与时钟配置\n"
            f"2. 实现核心业务逻辑与状态机\n"
            f"3. 添加错误处理与看门狗喂狗\n"
            f"4. 编写单元测试覆盖边界条件\n\n"
            f"**参考文档片段**:\n{context[:500] if context else '（无检索上下文）'}"
        )

    def generate_code(self, requirement: str, analysis: str, context: str = "") -> str:
        if "can" in requirement.lower() or "CAN" in requirement:
            return self._can_driver_template()
        if "adc" in requirement.lower() or "采样" in requirement:
            return self._adc_template()
        return self._gpio_template()

    def generate_tests(self, code: str) -> str:
        funcs = re.findall(r"(?:void|int|uint\d+_t)\s+(\w+)\s*\(", code)
        tests = []
        for fn in funcs[:5]:
            tests.append(
                f"TEST({fn}_null_pointer) {{\n"
                f"    EXPECT_EQ(ERROR_INVALID_PARAM, {fn}(NULL));\n"
                f"}}\n"
            )
        header = (
            "#include \"unity.h\"\n"
            "#include \"target_module.h\"\n\n"
            "void setUp(void) {}\n"
            "void tearDown(void) {}\n\n"
        )
        return header + "\n".join(tests) + "\nint main(void) {\n    UNITY_BEGIN();\n    return UNITY_END();\n}\n"

    def review_code(self, code: str) -> str:
        issues = []
        if "malloc" in code and "free" not in code:
            issues.append("- [严重] 使用 malloc 但未配对 free，嵌入式场景建议静态分配")
        if "printf" in code and "RTOS" not in code:
            issues.append("- [建议] 裸机环境慎用 printf，考虑 UART 日志宏")
        if not issues:
            issues.append("- 未发现明显问题，建议补充 MISRA-C 静态分析")
        return "## 代码审查报告\n\n" + "\n".join(issues)

    def complete_code(self, prefix: str, context: str = "") -> str:
        if "init" in prefix.lower():
            return prefix + "\n    /* TODO: 配置时钟与外设 */\n    return STATUS_OK;\n}"
        return prefix + "\n    /* AI 补全建议 */\n    return 0;\n}"

    def _extract_keywords(self, text: str) -> list[str]:
        mapping = {
            "can": "CAN 通信",
            "adc": "ADC 采样",
            "gpio": "GPIO 控制",
            "pwm": "PWM 驱动",
            "uart": "串口通信",
            "看门狗": "看门狗",
            "中断": "中断处理",
            "ecu": "ECU 固件",
        }
        found = []
        lower = text.lower()
        for k, v in mapping.items():
            if k in lower or k in text:
                found.append(v)
        return found

    def _can_driver_template(self) -> str:
        return '''/**
 * @file can_driver.c
 * @brief CAN 总线驱动 - 基于 AUTOSAR 风格接口
 */
#include "can_driver.h"
#include "can_hw.h"

static Can_State_t s_can_state = CAN_STATE_UNINIT;

Status_t Can_Init(const Can_Config_t *cfg) {
    if (cfg == NULL) return STATUS_INVALID_PARAM;
    if (s_can_state != CAN_STATE_UNINIT) return STATUS_ALREADY_INIT;

    Can_Hw_Init(cfg->baudrate, cfg->filter);
    s_can_state = CAN_STATE_READY;
    return STATUS_OK;
}

Status_t Can_Transmit(uint32_t id, const uint8_t *data, uint8_t len) {
    if (s_can_state != CAN_STATE_READY) return STATUS_NOT_READY;
    if (data == NULL || len > 8) return STATUS_INVALID_PARAM;

    return Can_Hw_Send(id, data, len);
}
'''

    def _adc_template(self) -> str:
        return '''/**
 * @file adc_sampler.c
 * @brief ADC 多通道采样模块
 */
#include "adc_sampler.h"

#define ADC_CHANNEL_COUNT 4

static uint16_t s_adc_buffer[ADC_CHANNEL_COUNT];

Status_t AdcSampler_Init(void) {
    Adc_Hw_ConfigChannels(ADC_CHANNEL_COUNT);
    return STATUS_OK;
}

Status_t AdcSampler_ReadAll(uint16_t *out, size_t cap) {
    if (out == NULL || cap < ADC_CHANNEL_COUNT) return STATUS_INVALID_PARAM;
    for (int i = 0; i < ADC_CHANNEL_COUNT; i++) {
        s_adc_buffer[i] = Adc_Hw_ReadChannel(i);
        out[i] = s_adc_buffer[i];
    }
    return STATUS_OK;
}
'''

    def _gpio_template(self) -> str:
        return '''/**
 * @file gpio_ctrl.c
 * @brief GPIO 控制模块
 */
#include "gpio_ctrl.h"

Status_t Gpio_SetPin(uint8_t port, uint8_t pin, bool level) {
    if (port >= GPIO_PORT_MAX) return STATUS_INVALID_PARAM;
    Gpio_Hw_Write(port, pin, level);
    return STATUS_OK;
}
'''
