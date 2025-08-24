#!/usr/bin/env python3
"""
股票暴涨分析MCP系统快速启动脚本
Quick Start script for Surge Analysis MCP System
"""

import os
import sys
import asyncio
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))


def show_menu():
    """显示菜单"""
    print("🚀 股票暴涨分析MCP系统 - 快速启动")
    print("=" * 50)
    print("1. 🔧 安装和配置系统")
    print("2. 📊 分析单只股票")
    print("3. 🚀 批量分析热门股票")
    print("4. 🆚 对比两只股票")
    print("5. 🧪 测试MCP服务器")
    print("6. 📋 查看使用说明")
    print("0. 退出")
    print("-" * 50)


async def analyze_single_stock():
    """分析单只股票"""
    from universal_surge_analyzer import UniversalSurgeAnalyzer
    
    print("\n📊 单只股票分析")
    print("-" * 30)
    
    symbol = input("请输入股票代码 (如: 002236): ").strip()
    name = input("请输入股票名称 (可选): ").strip()
    
    if not symbol:
        print("❌ 股票代码不能为空")
        return
    
    try:
        analyzer = UniversalSurgeAnalyzer()
        print(f"\n🔍 正在分析 {name or symbol}...")
        result = await analyzer.analyze_stock(symbol, name or None, 180)
        
        if result:
            print("✅ 分析完成！")
        else:
            print("❌ 分析失败，请检查股票代码")
            
    except Exception as e:
        print(f"❌ 分析出错: {e}")


async def batch_analyze():
    """批量分析"""
    from batch_surge_analyzer import BatchSurgeAnalyzer, POPULAR_STOCKS, TECH_STOCKS
    
    print("\n🚀 批量股票分析")
    print("-" * 30)
    print("1. 热门股票组合")
    print("2. 科技股票组合")
    
    choice = input("请选择分析组合 (1/2): ").strip()
    
    if choice == "1":
        stock_list = POPULAR_STOCKS[:5]  # 前5只
        preset_name = "热门股票"
    elif choice == "2":
        stock_list = TECH_STOCKS[:5]  # 前5只
        preset_name = "科技股票"
    else:
        print("❌ 无效选择")
        return
    
    try:
        analyzer = BatchSurgeAnalyzer()
        print(f"\n📊 正在分析 {preset_name} 组合...")
        results = await analyzer.analyze_stock_list(stock_list, 180)
        
        if results:
            print("✅ 批量分析完成！")
        else:
            print("❌ 批量分析失败")
            
    except Exception as e:
        print(f"❌ 分析出错: {e}")


async def compare_stocks():
    """对比股票"""
    from universal_surge_analyzer import UniversalSurgeAnalyzer
    
    print("\n🆚 股票对比分析")
    print("-" * 30)
    
    stock1_symbol = input("请输入第一只股票代码: ").strip()
    stock1_name = input("请输入第一只股票名称: ").strip()
    stock2_symbol = input("请输入第二只股票代码: ").strip()
    stock2_name = input("请输入第二只股票名称: ").strip()
    
    if not stock1_symbol or not stock2_symbol:
        print("❌ 股票代码不能为空")
        return
    
    try:
        analyzer = UniversalSurgeAnalyzer()
        
        print(f"\n🔍 正在分析 {stock1_name}({stock1_symbol})...")
        result1 = await analyzer.analyze_stock(stock1_symbol, stock1_name, 180)
        
        print(f"🔍 正在分析 {stock2_name}({stock2_symbol})...")
        result2 = await analyzer.analyze_stock(stock2_symbol, stock2_name, 180)
        
        if result1 and result2:
            # 简单对比
            print(f"\n📊 对比结果:")
            print(f"{'股票':10s} {'涨幅':8s} {'暴涨次数':8s} {'波动率':8s}")
            print("-" * 40)
            
            r1_return = result1['basic']['total_return']
            r1_surges = len(result1['surges'])
            r1_vol = result1['basic']['volatility']
            
            r2_return = result2['basic']['total_return']
            r2_surges = len(result2['surges'])
            r2_vol = result2['basic']['volatility']
            
            print(f"{stock1_name[:8]:10s} {r1_return:+6.1f}% {r1_surges:6d}次 {r1_vol:6.1f}%")
            print(f"{stock2_name[:8]:10s} {r2_return:+6.1f}% {r2_surges:6d}次 {r2_vol:6.1f}%")
            
            print("✅ 对比分析完成！")
        else:
            print("❌ 对比分析失败")
            
    except Exception as e:
        print(f"❌ 分析出错: {e}")


def test_mcp_server():
    """测试MCP服务器"""
    print("\n🧪 测试MCP服务器")
    print("-" * 30)
    
    try:
        os.system("python test_mcp_server.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")


def show_help():
    """显示帮助"""
    print("\n📋 使用说明")
    print("=" * 50)
    print("📁 文件说明:")
    print("  - README.md: 主要使用说明")
    print("  - SURGE_ANALYSIS_SYSTEM_GUIDE.md: 完整系统指南")
    print("  - FILE_LIST.md: 文件清单")
    print("")
    print("🔧 安装说明:")
    print("  1. 运行 install.py 自动安装")
    print("  2. 或手动安装: pip install -r requirements.txt")
    print("")
    print("🚀 MCP使用:")
    print("  1. 配置MCP服务 (选择菜单选项1)")
    print("  2. 重启Kiro IDE")
    print("  3. 在Kiro中使用MCP工具")
    print("")
    print("📊 直接使用:")
    print("  - 单股分析: python universal_surge_analyzer.py 股票代码")
    print("  - 批量分析: python batch_surge_analyzer.py --preset popular")


async def main():
    """主程序"""
    while True:
        show_menu()
        choice = input("请选择操作 (0-6): ").strip()
        
        if choice == "0":
            print("👋 再见！")
            break
        elif choice == "1":
            print("\n🔧 开始安装和配置...")
            os.system("python install.py")
        elif choice == "2":
            await analyze_single_stock()
        elif choice == "3":
            await batch_analyze()
        elif choice == "4":
            await compare_stocks()
        elif choice == "5":
            test_mcp_server()
        elif choice == "6":
            show_help()
        else:
            print("❌ 无效选择，请重新输入")
        
        if choice != "0":
            input("\n按回车键继续...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 程序已退出")
    except Exception as e:
        print(f"❌ 程序出错: {e}")