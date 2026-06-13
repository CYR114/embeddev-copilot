# 小鹏车载 ECU 嵌入式编码规范（节选）

## 1. 命名规范

- 函数名：模块前缀 + 动词，如 `Can_Init`、`Adc_ReadChannel`
- 类型定义：大驼峰 + `_t` 后缀，如 `Status_t`、`Can_Config_t`
- 宏定义：全大写 + 下划线，如 `CAN_MAX_DATA_LEN`
- 静态变量：`s_` 前缀，如 `s_can_state`

## 2. 返回值约定

所有对外接口返回 `Status_t` 枚举：

```c
typedef enum {
    STATUS_OK = 0,
    STATUS_INVALID_PARAM,
    STATUS_NOT_READY,
    STATUS_ALREADY_INIT,
    STATUS_HW_ERROR
} Status_t;
```

## 3. 内存管理

- **禁止**在 ECU 固件中使用 `malloc`/`free`
- 使用静态缓冲区或池化内存管理
- 栈使用不超过 2KB（除 ISR 外）

## 4. 日志规范

- 使用 `LOG_ERROR` / `LOG_WARN` / `LOG_INFO` 宏，禁止直接 `printf`
- 日志级别通过编译开关 `LOG_LEVEL` 控制

## 5. 看门狗

- 主循环必须定期调用 `Wdg_Feed()`
- 初始化超时：500ms
- 任务周期超时由各模块自行监控
