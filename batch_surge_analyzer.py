#!/usr/bin/env python3
"""
批量股票暴涨分析器
Batch Stock Surge Analyzer
"""

import asyncio
import sys
import os
from datetime import datetime
import pandas as pd
import json

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from universal_surge_analyzer import UniversalSurgeAnalyzer


class BatchSurgeAnalyzer:
    """批量暴涨分析器"""
    
    def __init__(self):
        self.analyzer = UniversalSurgeAnalyzer()
        self.results = []
    
    async def analyze_stock_list(self, stock_list, days=180):
        """分析股票列表"""
        print(f"🚀 批量股票暴涨分析")
        print(f"📊 分析股票数量: {len(stock_list)}")
        print(f"📅 分析周期: {days}天")
        print("=" * 60)
        
        for i, (symbol, name) in enumerate(stock_list, 1):
            print(f"\n[{i}/{len(stock_list)}] 正在分析: {name}({symbol})")
            print("-" * 40)
            
            try:
                result = await self.analyzer.analyze_stock(symbol, name, days)
                if result:
                    # 添加汇总信息
                    summary = self._create_summary(symbol, name, result)
                    self.results.append(summary)
                    
                    print(f"✅ {name} 分析完成")
                else:
                    print(f"❌ {name} 分析失败")
                    
            except Exception as e:
                print(f"❌ {name} 分析出错: {e}")
            
            # 添加延迟避免请求过快
            if i < len(stock_list):
                await asyncio.sleep(1)
        
        # 生成汇总报告
        self._generate_summary_report()
        
        return self.results
    
    def _create_summary(self, symbol, name, result):
        """创建股票汇总信息"""
        basic = result['basic']
        surges = result['surges']
        volume = result['volume']
        company = result['company']
        
        return {
            'symbol': symbol,
            'name': name,
            'current_price': basic['current_price'],
            'total_return': basic['total_return'],
            'volatility': basic['volatility'],
            'surge_count': len(surges),
            'volume_spike_count': len(volume['spikes']),
            'max_surge': max([s['return'] for s in surges]) if surges else 0,
            'industry': company.get('行业', '未知'),
            'market_cap': company.get('总市值', '未知'),
            'analysis_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def _generate_summary_report(self):
        """生成汇总报告"""
        if not self.results:
            print("\n❌ 没有有效的分析结果")
            return
        
        print(f"\n" + "=" * 60)
        print(f"📊 批量分析汇总报告")
        print(f"📅 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # 按暴涨频率排序
        surge_ranking = sorted(self.results, key=lambda x: x['surge_count'], reverse=True)
        
        print(f"\n🚀 暴涨频率排行榜 (TOP 10):")
        print("-" * 50)
        for i, stock in enumerate(surge_ranking[:10], 1):
            print(f"{i:2d}. {stock['name']:8s} ({stock['symbol']}) - {stock['surge_count']:2d}次暴涨, 涨幅{stock['total_return']:+6.1f}%")
        
        # 按收益率排序
        return_ranking = sorted(self.results, key=lambda x: x['total_return'], reverse=True)
        
        print(f"\n📈 收益率排行榜 (TOP 10):")
        print("-" * 50)
        for i, stock in enumerate(return_ranking[:10], 1):
            print(f"{i:2d}. {stock['name']:8s} ({stock['symbol']}) - 涨幅{stock['total_return']:+6.1f}%, {stock['surge_count']:2d}次暴涨")
        
        # 按波动率排序
        volatility_ranking = sorted(self.results, key=lambda x: x['volatility'], reverse=True)
        
        print(f"\n📊 波动率排行榜 (TOP 10):")
        print("-" * 50)
        for i, stock in enumerate(volatility_ranking[:10], 1):
            print(f"{i:2d}. {stock['name']:8s} ({stock['symbol']}) - 波动率{stock['volatility']:5.1f}%, 涨幅{stock['total_return']:+6.1f}%")
        
        # 行业分析
        industry_stats = {}
        for stock in self.results:
            industry = stock['industry']
            if industry not in industry_stats:
                industry_stats[industry] = {
                    'count': 0,
                    'avg_return': 0,
                    'avg_surge_count': 0,
                    'stocks': []
                }
            
            industry_stats[industry]['count'] += 1
            industry_stats[industry]['avg_return'] += stock['total_return']
            industry_stats[industry]['avg_surge_count'] += stock['surge_count']
            industry_stats[industry]['stocks'].append(stock['name'])
        
        # 计算平均值
        for industry in industry_stats:
            count = industry_stats[industry]['count']
            industry_stats[industry]['avg_return'] /= count
            industry_stats[industry]['avg_surge_count'] /= count
        
        print(f"\n🏢 行业表现分析:")
        print("-" * 50)
        for industry, stats in sorted(industry_stats.items(), key=lambda x: x[1]['avg_return'], reverse=True):
            print(f"{industry:12s}: {stats['count']:2d}只股票, 平均涨幅{stats['avg_return']:+6.1f}%, 平均暴涨{stats['avg_surge_count']:4.1f}次")
        
        # 投资建议
        print(f"\n💡 投资建议:")
        print("-" * 50)
        
        # 寻找高潜力股票
        high_potential = [s for s in self.results if s['surge_count'] >= 5 and s['total_return'] > 10]
        if high_potential:
            print(f"🎯 高潜力股票 (暴涨≥5次且涨幅>10%):")
            for stock in sorted(high_potential, key=lambda x: x['surge_count'], reverse=True)[:5]:
                print(f"   • {stock['name']} ({stock['symbol']}): {stock['surge_count']}次暴涨, 涨幅{stock['total_return']:+.1f}%")
        
        # 寻找稳健股票
        stable_stocks = [s for s in self.results if s['volatility'] < 3 and s['total_return'] > 5]
        if stable_stocks:
            print(f"\n📊 稳健增长股票 (波动率<3%且涨幅>5%):")
            for stock in sorted(stable_stocks, key=lambda x: x['total_return'], reverse=True)[:5]:
                print(f"   • {stock['name']} ({stock['symbol']}): 波动率{stock['volatility']:.1f}%, 涨幅{stock['total_return']:+.1f}%")
        
        # 风险提示
        high_risk = [s for s in self.results if s['volatility'] > 8 or s['total_return'] < -20]
        if high_risk:
            print(f"\n⚠️ 高风险股票 (波动率>8%或跌幅>20%):")
            for stock in sorted(high_risk, key=lambda x: x['volatility'], reverse=True)[:5]:
                print(f"   • {stock['name']} ({stock['symbol']}): 波动率{stock['volatility']:.1f}%, 涨幅{stock['total_return']:+.1f}%")
    
    def save_results(self, filename=None):
        """保存结果到文件"""
        if not filename:
            filename = f"batch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 分析结果已保存到: {filename}")


# 预定义股票列表
POPULAR_STOCKS = [
    ("000001", "平安银行"),
    ("000002", "万科A"),
    ("000158", "常山北明"),
    ("000858", "五粮液"),
    ("002415", "海康威视"),
    ("300059", "东方财富"),
    ("600036", "招商银行"),
    ("600519", "贵州茅台"),
    ("600887", "伊利股份"),
    ("000725", "京东方A")
]

TECH_STOCKS = [
    ("000158", "常山北明"),
    ("002415", "海康威视"),
    ("300059", "东方财富"),
    ("300750", "宁德时代"),
    ("002594", "比亚迪"),
    ("603986", "兆易创新"),
    ("603160", "汇顶科技"),
    ("300760", "迈瑞医疗"),
    ("002371", "北方华创"),
    ("300124", "汇川技术")
]

BANK_STOCKS = [
    ("000001", "平安银行"),
    ("600036", "招商银行"),
    ("601398", "工商银行"),
    ("601288", "农业银行"),
    ("601988", "中国银行"),
    ("601939", "建设银行"),
    ("600000", "浦发银行"),
    ("600016", "民生银行"),
    ("601166", "兴业银行"),
    ("600030", "中信证券")
]

async def main():
    """主函数"""
    analyzer = BatchSurgeAnalyzer()
    
    # 示例：分析科技股组合
    results = await analyzer.analyze_stock_list(TECH_STOCKS, days=180)
    
    # 保存结果
    analyzer.save_results()
    
    print(f"\n✅ 批量分析完成！共分析了 {len(results)} 只股票")


if __name__ == "__main__":
    asyncio.run(main())