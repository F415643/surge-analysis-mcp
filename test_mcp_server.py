#!/usr/bin/env python3
"""
MCP服务器功能测试脚本
MCP Server Testing Suite
"""

import asyncio
import json
import os
import sys
from datetime import datetime
import subprocess
import time

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from surge_analysis_mcp_server import analyze_single_stock, get_surge_summary, compare_stocks, batch_analyze_stocks


class MCPServerTester:
    """MCP服务器测试器"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = None
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("🧪 MCP服务器功能测试套件")
        print("=" * 60)
        self.start_time = time.time()
        
        # 测试1: 单股分析
        await self.test_single_stock_analysis()
        
        # 测试2: 暴涨摘要
        await self.test_surge_summary()
        
        # 测试3: 股票对比
        await self.test_stock_comparison()
        
        # 测试4: 批量分析
        await self.test_batch_analysis()
        
        # 测试5: 配置文件生成
        self.test_config_generation()
        
        # 生成测试报告
        self.generate_test_report()
    
    async def test_single_stock_analysis(self):
        """测试单股分析功能"""
        print("\n📊 测试1: 单股分析功能")
        print("-" * 40)
        
        test_cases = [
            {"symbol": "000158", "name": "常山北明", "days": 180},
            {"symbol": "000858", "name": "五粮液", "days": 90},
            {"symbol": "300750", "name": "宁德时代", "days": 30}
        ]
        
        for case in test_cases:
            try:
                print(f"测试 {case['name']}({case['symbol']})...")
                
                result = await analyze_single_stock(
                    symbol=case['symbol'],
                    name=case['name'],
                    days=case['days']
                )
                
                if result:
                    self.test_results.append({
                        "test": "single_stock",
                        "symbol": case['symbol'],
                        "name": case['name'],
                        "status": "PASS",
                        "data_points": len(result.get('basic', {}).get('data', [])),
                        "surge_count": len(result.get('surges', [])),
                        "volume_spikes": len(result.get('volume', {}).get('spikes', [])),
                        "error": None
                    })
                    print(f"✅ {case['name']} 分析成功")
                    print(f"   数据点: {len(result.get('basic', {}).get('data', []))}")
                    print(f"   暴涨次数: {len(result.get('surges', []))}")
                    print(f"   成交量异常: {len(result.get('volume', {}).get('spikes', []))}")
                else:
                    self.test_results.append({
                        "test": "single_stock",
                        "symbol": case['symbol'],
                        "name": case['name'],
                        "status": "FAIL",
                        "error": "返回空数据"
                    })
                    print(f"❌ {case['name']} 分析失败: 返回空数据")
                    
            except Exception as e:
                self.test_results.append({
                    "test": "single_stock",
                    "symbol": case['symbol'],
                    "name": case['name'],
                    "status": "ERROR",
                    "error": str(e)
                })
                print(f"❌ {case['name']} 分析出错: {e}")
    
    async def test_surge_summary(self):
        """测试暴涨摘要功能"""
        print("\n📈 测试2: 暴涨摘要功能")
        print("-" * 40)
        
        test_symbols = [
            {"symbol": "000158", "name": "常山北明"},
            {"symbol": "300750", "name": "宁德时代"}
        ]
        
        try:
            result = await get_surge_summary(
                symbols=test_symbols,
                days=180
            )
            
            if result:
                self.test_results.append({
                    "test": "surge_summary",
                    "symbols": [s['symbol'] for s in test_symbols],
                    "status": "PASS",
                    "total_stocks": len(result.get('stocks', [])),
                    "total_surges": result.get('summary', {}).get('total_surges', 0),
                    "error": None
                })
                print(f"✅ 暴涨摘要生成成功")
                print(f"   分析股票数: {len(result.get('stocks', []))}")
                print(f"   总暴涨次数: {result.get('summary', {}).get('total_surges', 0)}")
                
                # 显示摘要信息
                if result.get('summary'):
                    summary = result['summary']
                    print(f"   平均涨幅: {summary.get('avg_return', 0):+.1f}%")
                    print(f"   最大涨幅: {summary.get('max_return', 0):+.1f}%")
                    print(f"   平均持续时间: {summary.get('avg_duration', 0):.1f}天")
            else:
                self.test_results.append({
                    "test": "surge_summary",
                    "symbols": [s['symbol'] for s in test_symbols],
                    "status": "FAIL",
                    "error": "返回空数据"
                })
                print(f"❌ 暴涨摘要生成失败")
                
        except Exception as e:
            self.test_results.append({
                "test": "surge_summary",
                "symbols": [s['symbol'] for s in test_symbols],
                "status": "ERROR",
                "error": str(e)
            })
            print(f"❌ 暴涨摘要出错: {e}")
    
    async def test_stock_comparison(self):
        """测试股票对比功能"""
        print("\n🔍 测试3: 股票对比功能")
        print("-" * 40)
        
        test_symbols = [
            {"symbol": "000158", "name": "常山北明"},
            {"symbol": "000858", "name": "五粮液"},
            {"symbol": "300750", "name": "宁德时代"}
        ]
        
        try:
            result = await compare_stocks(
                symbols=test_symbols,
                days=180
            )
            
            if result:
                self.test_results.append({
                    "test": "stock_comparison",
                    "symbols": [s['symbol'] for s in test_symbols],
                    "status": "PASS",
                    "comparison_count": len(result.get('comparisons', [])),
                    "rankings": len(result.get('rankings', [])),
                    "error": None
                })
                print(f"✅ 股票对比成功")
                print(f"   对比组合数: {len(result.get('comparisons', []))}")
                print(f"   排名项目: {len(result.get('rankings', []))}")
                
                # 显示排名信息
                if result.get('rankings'):
                    rankings = result['rankings']
                    for ranking in rankings:
                        print(f"   {ranking['metric']}: {ranking['leader']['name']} ({ranking['leader']['value']:.1f})")
            else:
                self.test_results.append({
                    "test": "stock_comparison",
                    "symbols": [s['symbol'] for s in test_symbols],
                    "status": "FAIL",
                    "error": "返回空数据"
                })
                print(f"❌ 股票对比失败")
                
        except Exception as e:
            self.test_results.append({
                "test": "stock_comparison",
                "symbols": [s['symbol'] for s in test_symbols],
                "status": "ERROR",
                "error": str(e)
            })
            print(f"❌ 股票对比出错: {e}")
    
    async def test_batch_analysis(self):
        """测试批量分析功能"""
        print("\n📊 测试4: 批量分析功能")
        print("-" * 40)
        
        test_symbols = [
            {"symbol": "000158", "name": "常山北明"},
            {"symbol": "000858", "name": "五粮液"},
            {"symbol": "300750", "name": "宁德时代"},
            {"symbol": "600519", "name": "贵州茅台"},
            {"symbol": "000725", "name": "京东方A"}
        ]
        
        try:
            result = await batch_analyze_stocks(
                symbols=test_symbols,
                days=90
            )
            
            if result:
                self.test_results.append({
                    "test": "batch_analysis",
                    "symbols": [s['symbol'] for s in test_symbols],
                    "status": "PASS",
                    "total_stocks": len(result.get('stocks', [])),
                    "summary_data": len(result.get('summary', {})),
                    "error": None
                })
                print(f"✅ 批量分析成功")
                print(f"   分析股票数: {len(result.get('stocks', []))}")
                print(f"   汇总信息: {len(result.get('summary', {}))}项")
                
                # 显示汇总信息
                summary = result.get('summary', {})
                if summary:
                    print(f"   平均收益率: {summary.get('avg_return', 0):+.1f}%")
                    print(f"   平均波动率: {summary.get('avg_volatility', 0):.1f}%")
                    print(f"   总暴涨次数: {summary.get('total_surges', 0)}")
            else:
                self.test_results.append({
                    "test": "batch_analysis",
                    "symbols": [s['symbol'] for s in test_symbols],
                    "status": "FAIL",
                    "error": "返回空数据"
                })
                print(f"❌ 批量分析失败")
                
        except Exception as e:
            self.test_results.append({
                "test": "batch_analysis",
                "symbols": [s['symbol'] for s in test_symbols],
                "status": "ERROR",
                "error": str(e)
            })
            print(f"❌ 批量分析出错: {e}")
    
    def test_config_generation(self):
        """测试配置文件生成"""
        print("\n⚙️ 测试5: 配置文件生成")
        print("-" * 40)
        
        try:
            # 生成MCP配置文件
            config = {
                "mcpServers": {
                    "surge-analysis": {
                        "command": "python",
                        "args": ["-m", "surge_analysis_mcp_server"],
                        "env": {
                            "PYTHONPATH": ".",
                            "MCP_LOG_LEVEL": "INFO"
                        }
                    }
                }
            }
            
            with open('mcp_config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.test_results.append({
                "test": "config_generation",
                "status": "PASS",
                "filename": "mcp_config.json",
                "error": None
            })
            print(f"✅ MCP配置文件已生成: mcp_config.json")
            
        except Exception as e:
            self.test_results.append({
                "test": "config_generation",
                "status": "ERROR",
                "error": str(e)
            })
            print(f"❌ 配置文件生成失败: {e}")
    
    def generate_test_report(self):
        """生成测试报告"""
        print(f"\n" + "=" * 60)
        print("📋 测试报告")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r['status'] == 'PASS')
        failed_tests = sum(1 for r in self.test_results if r['status'] == 'FAIL')
        error_tests = sum(1 for r in self.test_results if r['status'] == 'ERROR')
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {passed_tests}")
        print(f"失败: {failed_tests}")
        print(f"错误: {error_tests}")
        
        if passed_tests == total_tests:
            print("🎉 所有测试通过!")
        else:
            print("\n❌ 失败/错误详情:")
            for result in self.test_results:
                if result['status'] in ['FAIL', 'ERROR']:
                    print(f"   {result['test']}: {result['status']} - {result.get('error', '未知错误')}")
        
        # 测试用时
        if self.start_time:
            elapsed_time = time.time() - self.start_time
            print(f"\n⏱️ 测试用时: {elapsed_time:.2f}秒")
        
        # 保存测试报告
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "results": self.test_results,
            "elapsed_time": elapsed_time if self.start_time else None
        }
        
        with open('test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 测试报告已保存: test_report.json")


def check_dependencies():
    """检查依赖"""
    print("🔍 检查依赖环境...")
    
    required_packages = [
        'mcp', 'fastmcp', 'akshare', 'pandas', 'numpy',
        'matplotlib', 'seaborn', 'requests', 'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package}")
    
    if missing_packages:
        print(f"\n⚠️ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: pip install -r requirements.txt")
        return False
    
    print("🎉 所有依赖已安装")
    return True


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP服务器测试套件')
    parser.add_argument('--check-deps', action='store_true', help='仅检查依赖')
    parser.add_argument('--test', choices=['single', 'summary', 'compare', 'batch', 'config'], help='运行特定测试')
    
    args = parser.parse_args()
    
    if args.check_deps:
        check_dependencies()
        return
    
    # 检查依赖
    if not check_dependencies():
        return
    
    tester = MCPServerTester()
    
    if args.test:
        # 运行特定测试
        if args.test == 'single':
            await tester.test_single_stock_analysis()
        elif args.test == 'summary':
            await tester.test_surge_summary()
        elif args.test == 'compare':
            await tester.test_stock_comparison()
        elif args.test == 'batch':
            await tester.test_batch_analysis()
        elif args.test == 'config':
            tester.test_config_generation()
    else:
        # 运行所有测试
        await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())