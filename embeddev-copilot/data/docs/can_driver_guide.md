# CAN 总线驱动开发指南

## 概述

车载 CAN 通信遵循 ISO 11898 标准。小鹏 ECU 节点通常使用 CAN 2.0B 扩展帧或标准帧。

## 初始化流程

1. 使能 CAN 外设时钟
2. 配置波特率（常见：500Kbps / 250Kbps）
3. 配置硬件滤波器，仅接收目标 ID 范围
4. 使能接收中断或 DMA
5. 设置状态为 `CAN_STATE_READY`

## 波特率配置参考

| 场景 | 波特率 | 采样点 |
|------|--------|--------|
| 动力 CAN | 500K | 75% |
| 舒适 CAN | 250K | 75% |
| 诊断 CAN | 500K | 80% |

## 报文发送规范

- 数据长度 DLC 范围 0-8 字节
- 发送前检查总线状态（Bus-Off 恢复）
- 关键报文需实现发送确认回调
- 发送失败重试不超过 3 次

## 滤波器配置示例

```c
Can_Filter_t filter = {
    .id = 0x100,
    .mask = 0x7FF,
    .mode = CAN_FILTER_MODE_STANDARD
};
```

## 错误处理

- Bus-Off 状态：自动恢复 + 上报 DTC
- 发送超时：记录错误计数，超阈值进入降级模式
- 接收溢出：丢弃最旧帧并告警

## AUTOSAR 接口映射

| AUTOSAR API | 本项目接口 |
|-------------|-----------|
| Can_Init | Can_Init |
| Can_Write | Can_Transmit |
| Can_MainFunction_Read | Can_PollReceive |
