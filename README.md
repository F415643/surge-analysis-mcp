# 股票暴涨分析 MCP 服务

一个基于 Model Context Protocol (MCP) 的专业股票暴涨分析工具，提供全面的技术分析和投资决策支持。

## 功能特性

- **单股深度分析**: 全面分析个股的技术指标、暴涨模式和投资价值
- **批量股票筛选**: 支持预设股票组合的批量分析和排名
- **股票对比分析**: 多只股票的横向对比和相对强弱分析  
- **暴涨事件检测**: 智能识别历史暴涨事件和触发条件
- **实时数据获取**: 基于 AKShare 的 A股实时数据支持
- **MCP 标准接口**: 完全兼容 Kiro IDE 和其他 MCP 客户端

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

```bash
# 安装依赖
pip install -r requirements.txt

# 测试服务
python test_mcp_server.py
```

## MCP 工具接口

### 1. analyze_single_stock
分析单只股票的完整技术面报告

**参数**:
- `symbol`: 股票代码，如 "000001"
- `name`: 股票名称（可选）
- `days`: 分析天数，默认 180 天

### 2. get_surge_summary
获取股票暴涨事件摘要信息

### 3. compare_stocks
对比分析多只股票的相对表现

### 4. batch_analyze_stocks
批量分析预设股票组合并生成排行榜

## 使用示例

在 Kiro IDE 中使用：
```
请分析大华股份最近半年的表现
工具: analyze_single_stock
参数: {"symbol": "002236", "days": 180}
```

## 技术支持

- 详细文档请参考 USER_MANUAL.md
- 问题反馈请提交 GitHub Issues
- 基于 Python 3.8+ 开发，支持 Windows/Linux/macOS

## 免责声明

本工具仅供学习和研究使用，不构成投资建议。股市有风险，投资需谨慎。