# ADC 采样模块设计规范

## 功能要求

ADC 模块负责多通道模拟信号采集，应用于电池电压监测、温度传感器读取等场景。

## 接口设计

```c
Status_t AdcSampler_Init(void);
Status_t AdcSampler_ReadChannel(uint8_t ch, uint16_t *value);
Status_t AdcSampler_ReadAll(uint16_t *buf, size_t cap);
```

## 采样参数

- 分辨率：12-bit
- 参考电压：3.3V
- 采样频率：最高 1MHz（单通道）
- 通道数：最多 16 路

## DMA 模式

推荐使用 DMA 循环模式采集，减少 CPU 占用：

1. 配置 ADC + DMA 通道
2. 双缓冲（Ping-Pong）避免数据覆盖
3. 完成中断中通知上层模块

## 校准

- 上电后执行一次偏移校准
- 每 24 小时执行增益漂移检查
- 校准失败上报 `STATUS_HW_ERROR`

## 数据有效性

- 读取值需在 `[0, 4095]` 范围内
- 连续 3 次读取相同值需触发传感器故障检测
- 温度通道需应用查表法转换为物理量
