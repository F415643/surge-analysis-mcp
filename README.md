# 股票暴涨分析 MCP 服务

一个基于 Model Context Protocol (MCP) 的专业股票暴涨分析工具，提供全面的技术分析和投资决策支持。

## 功能特性

- **单股深度分析**: 全面分析个股的技术指标、暴涨模式和投资价值
- **批量股票筛选**: 支持预设股票组合的批量分析和排名
- **股票对比分析**: 多只股票的横向对比和相对强弱分析  
- **暴涨事件检测**: 智能识别历史暴涨事件和触发条件
- **实时数据获取**: 基于 AKShare 的 A股实时数据支持
- **MCP 标准接口**: 完全兼容 Kiro IDE 和其他 MCP 客户端

## 系统架构

```
surge_analysis_mcp_complete/
├── 核心服务
│   ├── surge_analysis_mcp_server.py    # MCP 服务器主程序
│   ├── universal_surge_analyzer.py     # 通用分析引擎
│   └── batch_surge_analyzer.py         # 批量分析引擎
├── 数据层
│   ├── akshare_data_source.py         # AKShare 数据接口
│   ├── data_manager.py                # 数据管理器
│   └── models.py                      # 数据模型定义
├── 配置管理
│   ├── config.py                      # 配置管理
│   ├── exceptions.py                  # 异常处理
│   └── mcp.json                       # MCP 服务配置
├── 工具脚本
│   ├── install.py                     # 自动安装脚本
│   ├── quick_start.py                 # 快速启动工具
│   └── test_mcp_server.py            # 服务测试工具
└── 文档
    ├── README.md                      # 本文档
    ├── USER_MANUAL.md                 # 用户手册
    └── MCP_SHARING_GUIDE.md          # MCP 共享指南
```

## 快速部署

### 方法一：自动安装（推荐）

```bash
# 1. 进入项目目录
cd surge_analysis_mcp_complete

# 2. 运行自动安装脚本
python install.py

# 3. 按提示完成配置
```

### 方法二：手动安装

#### 1. 环境准备

```bash
# 确保 Python 3.8+ 环境
python --version

# 安装核心依赖
pip install akshare pandas numpy mcp fastmcp
```

#### 2. 依赖安装

```bash
# 安装完整依赖包
pip install -r requirements.txt

# 或使用 pip 安装核心包
pip install akshare>=1.9.0 pandas>=1.3.0 numpy>=1.21.0 mcp>=1.0.0
```

#### 3. MCP 服务配置

创建或编辑 `.kiro/settings/mcp.json` 文件：

```json
{
  "mcpServers": {
    "surge-analysis": {
      "command": "python",
      "args": [
        "/path/to/surge_analysis_mcp_complete/surge_analysis_mcp_server.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8"
      },
      "disabled": false,
      "autoApprove": [
        "analyze_single_stock",
        "get_surge_summary", 
        "compare_stocks",
        "batch_analyze_stocks"
      ]
    }
  }
}
```

#### 4. 服务启动测试

```bash
# 测试 MCP 服务器
python test_mcp_server.py

# 测试单股分析
python quick_start.py
```

## MCP 工具接口

### 1. analyze_single_stock
**功能**: 分析单只股票的完整技术面报告

**参数**:
- `symbol` (必需): 股票代码，如 "000001", "600036"
- `name` (可选): 股票名称，如 "平安银行"
- `days` (可选): 分析天数，默认 180 天

**返回**: 包含技术指标、暴涨分析、风险评估的详细报告

**示例**:
```json
{
  "symbol": "000001",
  "name": "平安银行", 
  "days": 180
}
```

### 2. get_surge_summary
**功能**: 获取股票暴涨事件摘要信息

**参数**:
- `symbol` (必需): 股票代码
- `name` (可选): 股票名称
- `surge_threshold` (可选): 暴涨阈值（百分比），默认 5.0

**返回**: 暴涨频率统计和关键指标摘要

**示例**:
```json
{
  "symbol": "002236",
  "surge_threshold": 8.0
}
```

### 3. compare_stocks  
**功能**: 对比分析多只股票的相对表现

**参数**:
- `stocks` (必需): 股票列表，格式 [["代码", "名称"], ...]
- `days` (可选): 分析天数，默认 180 天

**返回**: 对比分析表格和投资建议

**示例**:
```json
{
  "stocks": [
    ["002236", "大华股份"],
    ["002415", "海康威视"]
  ],
  "days": 180
}
```

### 4. batch_analyze_stocks
**功能**: 批量分析预设股票组合并生成排行榜

**参数**:
- `preset` (必需): 预设组合类型
  - `"popular"`: 热门股票组合
  - `"tech"`: 科技股组合  
  - `"custom"`: 自定义组合
- `custom_stocks` (preset="custom" 时必需): 自定义股票列表
- `days` (可选): 分析天数，默认 180 天

**返回**: 股票排行榜和投资建议

**示例**:
```json
{
  "preset": "popular",
  "days": 90
}
```

## 使用场景

### 在 Kiro IDE 中使用

1. **单股分析**
```
请分析大华股份最近半年的表现
工具: analyze_single_stock
```

2. **股票对比**
```
对比分析大华股份和海康威视
工具: compare_stocks
```

3. **批量分析**
```
分析科技股组合最近3个月的表现
工具: batch_analyze_stocks
```

### 程序化调用

```python
from surge_analysis_mcp_server import analyze_single_stock

# 分析德新科技
result = analyze_single_stock("603032", "德新科技", 360)
print(result)
```

## 技术支持

- **数据支持**: 基于 AKShare 的 A 股实时数据
- **分析周期**: 支持 30-360 天的历史数据分析
- **技术指标**: 包含 MACD、RSI、KDJ、布林带等主流指标
- **风险评估**: 基于历史波动率的量化风险评估模型

## 开发团队

- **项目**: surge-analysis-mcp
- **版本**: 1.0.0
- **维护**: F415643
- **许可证**: MIT