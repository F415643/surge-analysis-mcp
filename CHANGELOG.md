# 更新日志 / Changelog

All notable changes to this project will be documented in this file.

## [v1.1.0] - 2025-08-24

### 新增 / Added
- 完整的 MCP 服务器实现，支持 4 个核心分析工具
- 自动安装脚本 `install.py`，简化部署流程
- 快速启动工具 `quick_start.py`，提供交互式分析界面
- 完善的错误处理和异常管理机制
- 支持批量股票分析和排行榜生成
- 股票对比分析功能
- 暴涨事件检测和统计分析

### 改进 / Improved
- 修复 Windows 系统编码问题，提高跨平台兼容性
- 移除 emoji 字符，避免终端显示问题
- 优化数据缓存机制，提升分析性能
- 改进 MCP 工具接口设计，增强易用性
- 完善文档结构，添加详细的使用指南

### 修复 / Fixed
- 解决 AKShare 数据获取时的编码错误
- 修复批量分析时的内存泄漏问题
- 改进异常处理，避免程序崩溃
- 修复 MCP 服务器连接稳定性问题

### 技术改进 / Technical Improvements
- 重构代码结构，提高可维护性
- 添加完整的类型注解
- 优化算法性能，减少计算时间
- 改进日志系统，便于问题诊断

## [v1.0.0] - 2025-08-23

### 初始版本 / Initial Release
- 基础的股票暴涨分析功能
- MCP 服务器框架搭建
- AKShare 数据源集成
- 基本的技术指标计算
- 简单的分析报告生成

---

## 版本规范 / Version Convention

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范：

- **主版本号**：不兼容的 API 修改
- **次版本号**：向下兼容的功能性新增
- **修订号**：向下兼容的问题修正

## 贡献指南 / Contributing

欢迎提交 Issue 和 Pull Request 来改进项目：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 反馈和支持 / Feedback and Support

- 提交 Issue：报告 Bug 或请求新功能
- 查看文档：`USER_MANUAL.md` 和 `MCP_SHARING_GUIDE.md`
- 参考示例：项目中的示例分析文件