# MISRA-C 关键规则速查（车载固件）

## 强制规则（节选）

| 规则 | 说明 |
|------|------|
| Rule 8.4 | 兼容类型显式声明 |
| Rule 10.1 | 隐式类型转换限制 |
| Rule 11.5 | void 指针转换限制 |
| Rule 17.7 | 禁止 printf 族函数 |
| Rule 21.3 | 禁止动态内存分配 |

## 常见违规与修复

### 动态内存

```c
// ❌ 违规
uint8_t *buf = malloc(64);

// ✅ 修复
static uint8_t s_buf[64];
```

### 魔数

```c
// ❌ 违规
if (len > 8) return ERROR;

// ✅ 修复
#define CAN_MAX_DLC 8
if (len > CAN_MAX_DLC) return STATUS_INVALID_PARAM;
```

### 空指针检查

所有指针参数必须在函数入口检查：

```c
Status_t Module_DoWork(const Config_t *cfg) {
    if (cfg == NULL) return STATUS_INVALID_PARAM;
    // ...
}
```

## 静态分析工具

- PC-lint Plus（推荐）
- cppcheck with MISRA addon
- Polyspace（量产级）
