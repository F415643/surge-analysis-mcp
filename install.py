#!/usr/bin/env python3
"""
股票暴涨分析MCP系统安装脚本
Installation script for Surge Analysis MCP System
"""

import os
import sys
import json
import shutil
from pathlib import Path


def install_dependencies():
    """安装依赖包"""
    print("📦 安装Python依赖包...")
    
    dependencies = [
        "akshare",
        "pandas", 
        "numpy",
        "mcp"
    ]
    
    for dep in dependencies:
        try:
            os.system(f"pip install {dep}")
            print(f"✅ {dep} 安装成功")
        except Exception as e:
            print(f"❌ {dep} 安装失败: {e}")


def setup_mcp_config():
    """设置MCP配置"""
    print("\n🔧 配置MCP服务...")
    
    # 获取当前脚本路径
    current_dir = Path(__file__).parent.absolute()
    server_path = current_dir / "surge_analysis_mcp_server.py"
    
    # MCP配置
    config = {
        "mcpServers": {
            "surge-analysis": {
                "command": "python",
                "args": [str(server_path)],
                "env": {},
                "disabled": False,
                "autoApprove": [
                    "analyze_single_stock",
                    "get_surge_summary", 
                    "compare_stocks",
                    "batch_analyze_stocks"
                ]
            }
        }
    }
    
    # 确定配置文件路径
    kiro_config_dir = Path.home() / ".kiro" / "settings"
    workspace_config_dir = Path(".kiro") / "settings"
    
    # 优先使用工作区配置
    if workspace_config_dir.exists():
        config_path = workspace_config_dir / "mcp.json"
    else:
        # 创建工作区配置目录
        workspace_config_dir.mkdir(parents=True, exist_ok=True)
        config_path = workspace_config_dir / "mcp.json"
    
    # 读取现有配置（如果存在）
    existing_config = {}
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
        except Exception as e:
            print(f"⚠️ 读取现有配置失败: {e}")
    
    # 合并配置
    if "mcpServers" not in existing_config:
        existing_config["mcpServers"] = {}
    
    existing_config["mcpServers"]["surge-analysis"] = config["mcpServers"]["surge-analysis"]
    
    # 保存配置
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(existing_config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ MCP配置已保存到: {config_path}")
        return True
        
    except Exception as e:
        print(f"❌ MCP配置保存失败: {e}")
        return False


def test_installation():
    """测试安装"""
    print("\n🧪 测试安装...")
    
    try:
        # 测试导入
        import akshare as ak
        import pandas as pd
        import numpy as np
        print("✅ 依赖包导入成功")
        
        # 测试数据获取
        print("📡 测试数据获取...")
        test_data = ak.stock_zh_a_hist(
            symbol="000001",
            period="daily",
            start_date="20250801",
            end_date="20250823",
            adjust="qfq"
        )
        
        if not test_data.empty:
            print(f"✅ 数据获取成功，获得 {len(test_data)} 条记录")
        else:
            print("⚠️ 数据获取为空，请检查网络连接")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False
    
    return True


def main():
    """主安装流程"""
    print("🚀 股票暴涨分析MCP系统安装程序")
    print("=" * 50)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return
    
    print(f"✅ Python版本: {sys.version}")
    
    # 安装依赖
    install_dependencies()
    
    # 配置MCP
    if setup_mcp_config():
        print("✅ MCP配置完成")
    else:
        print("❌ MCP配置失败")
        return
    
    # 测试安装
    if test_installation():
        print("\n🎉 安装完成！")
        print("\n📋 下一步操作:")
        print("1. 重启Kiro IDE")
        print("2. 在Kiro中使用MCP工具进行股票分析")
        print("3. 或者直接运行Python脚本:")
        print("   python universal_surge_analyzer.py 000158 --name '常山北明'")
        
    else:
        print("\n❌ 安装测试失败，请检查错误信息")


if __name__ == "__main__":
    main()