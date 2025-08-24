#!/usr/bin/env python3
"""
通用股票暴涨分析器
Universal Stock Surge Analyzer
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import akshare as ak
import argparse

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class UniversalSurgeAnalyzer:
    """通用暴涨分析器"""
    
    def __init__(self):
        self.surge_threshold = 5.0  # 暴涨阈值
        self.volume_threshold = 2.0  # 成交量异常阈值
        
    async def analyze_stock(self, symbol: str, name: str = None, days: int = 180):
        """分析指定股票"""
        print(f"🔍 {name or symbol}暴涨逻辑分析")
        print("=" * 50)
        
        try:
            # 获取数据
            print("📡 获取股票数据...")
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            hist_df = ak.stock_zh_a_hist(
                symbol=symbol,
                period="daily", 
                start_date=start_date.strftime("%Y%m%d"),
                end_date=end_date.strftime("%Y%m%d"),
                adjust="qfq"
            )
            
            if hist_df.empty:
                print("❌ 数据获取失败")
                return None
            
            print(f"✅ 获取 {len(hist_df)} 个数据点")
            
            # 基本分析
            analysis_result = self._perform_basic_analysis(hist_df)
            
            # 暴涨分析
            surge_analysis = self._analyze_surges(hist_df)
            
            # 成交量分析
            volume_analysis = self._analyze_volume(hist_df)
            
            # 获取公司信息
            company_info = self._get_company_info(symbol)
            
            # 生成报告
            self._generate_report(analysis_result, surge_analysis, volume_analysis, company_info, name or symbol)
            
            return {
                'basic': analysis_result,
                'surges': surge_analysis,
                'volume': volume_analysis,
                'company': company_info
            }
            
        except Exception as e:
            print(f"❌ 分析过程出错: {e}")
            return None
    
    def _perform_basic_analysis(self, df):
        """基本分析"""
        closes = df['收盘'].tolist()
        
        current_price = closes[-1]
        start_price = closes[0]
        total_return = (current_price - start_price) / start_price * 100
        
        result = {
            'current_price': current_price,
            'start_price': start_price,
            'total_return': total_return,
            'max_price': max(closes),
            'min_price': min(closes),
            'volatility': pd.Series(closes).pct_change().std() * 100
        }
        
        print(f"📊 基本表现:")
        print(f"  当前价格: ¥{current_price:.2f}")
        print(f"  期间涨幅: {total_return:+.2f}%")
        print(f"  最高价: ¥{result['max_price']:.2f}")
        print(f"  最低价: ¥{result['min_price']:.2f}")
        print(f"  波动率: {result['volatility']:.2f}%")
        
        return result
    
    def _analyze_surges(self, df):
        """暴涨分析"""
        closes = df['收盘'].tolist()
        dates = df['日期'].tolist()
        volumes = df['成交量'].tolist()
        
        surge_days = []
        for i in range(1, len(closes)):
            daily_return = (closes[i] - closes[i-1]) / closes[i-1] * 100
            if daily_return > self.surge_threshold:
                surge_days.append({
                    'date': dates[i],
                    'return': daily_return,
                    'price': closes[i],
                    'volume': volumes[i]
                })
        
        print(f"\n🚀 暴涨事件:")
        print(f"  单日涨幅>{self.surge_threshold}%: {len(surge_days)}天")
        
        if surge_days:
            surge_days.sort(key=lambda x: x['return'], reverse=True)
            print(f"  前5个暴涨日:")
            for i, day in enumerate(surge_days[:5], 1):
                print(f"    {i}. {day['date']}: +{day['return']:.2f}% (¥{day['price']:.2f})")
        
        return surge_days
    
    def _analyze_volume(self, df):
        """成交量分析"""
        volumes = df['成交量'].tolist()
        dates = df['日期'].tolist()
        closes = df['收盘'].tolist()
        
        avg_volume = sum(volumes) / len(volumes)
        current_volume = volumes[-1]
        max_volume = max(volumes)
        
        print(f"\n📊 成交量分析:")
        print(f"  平均成交量: {avg_volume:,.0f}")
        print(f"  当前成交量: {current_volume:,.0f} ({current_volume/avg_volume:.1f}倍)")
        print(f"  最大成交量: {max_volume:,.0f} ({max_volume/avg_volume:.1f}倍)")
        
        # 寻找成交量异常日
        volume_spikes = []
        for i in range(10, len(volumes)):
            avg_vol = sum(volumes[i-10:i]) / 10
            if volumes[i] > avg_vol * self.volume_threshold:
                daily_return = (closes[i] - closes[i-1]) / closes[i-1] * 100 if i > 0 else 0
                volume_spikes.append({
                    'date': dates[i],
                    'volume_ratio': volumes[i] / avg_vol,
                    'return': daily_return
                })
        
        if volume_spikes:
            print(f"\n  成交量异常事件 (前5个):")
            volume_spikes.sort(key=lambda x: x['volume_ratio'], reverse=True)
            for i, spike in enumerate(volume_spikes[:5], 1):
                print(f"    {i}. {spike['date']}: 量比{spike['volume_ratio']:.1f}倍, 涨幅{spike['return']:+.2f}%")
        
        return {
            'avg_volume': avg_volume,
            'current_volume': current_volume,
            'max_volume': max_volume,
            'spikes': volume_spikes
        }
    
    def _get_company_info(self, symbol):
        """获取公司信息"""
        print(f"\n🏢 公司基本信息:")
        try:
            info = ak.stock_individual_info_em(symbol=symbol)
            if not info.empty:
                key_info = {}
                for _, row in info.iterrows():
                    item = row.get('item', '')
                    value = row.get('value', '')
                    if item in ['总市值', '流通市值', '行业', '总股本']:
                        key_info[item] = value
                
                for key, value in key_info.items():
                    print(f"  {key}: {value}")
                
                return key_info
        except:
            print("  信息获取受限")
        
        return {}
    
    def _generate_report(self, basic, surges, volume, company, stock_name):
        """生成分析报告"""
        print(f"\n🎯 {stock_name}暴涨逻辑分析")
        print("=" * 50)
        
        # 基于数据生成逻辑分析
        surge_count = len(surges)
        volume_spike_count = len(volume['spikes'])
        
        # 暴涨特征分析
        if surge_count > 5:
            print("📈 暴涨特征: 频繁暴涨型")
            print("  说明: 该股票在过去半年内出现多次单日暴涨")
            print("  投资建议: 适合短线交易，关注成交量配合")
        elif surge_count > 0:
            print("📊 暴涨特征: 间歇暴涨型")
            print("  说明: 偶尔出现暴涨，可能受消息面影响")
            print("  投资建议: 关注消息面变化，谨慎追高")
        else:
            print("📉 暴涨特征: 稳健型")
            print("  说明: 价格波动相对平稳，较少出现暴涨")
            print("  投资建议: 适合长期持有，关注基本面变化")
        
        # 成交量配合分析
        if volume_spike_count > surge_count:
            print("🔥 成交量配合: 量价齐升型")
            print("  特征: 成交量放大往往伴随价格上涨")
            print("  策略: 关注放量突破机会")
        else:
            print("📊 成交量配合: 温和放量型")
            print("  特征: 成交量变化相对温和")
            print("  策略: 适合稳健操作")
        
        # 风险提示
        print("\n⚠️ 风险提示:")
        print("  1. 历史表现不代表未来收益")
        print("  2. 暴涨股票波动较大，注意风险控制")
        print("  3. 建议结合基本面和技术面综合判断")
        print("  4. 设置合理的止损和止盈点位")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='通用股票暴涨分析器')
    parser.add_argument('symbol', help='股票代码')
    parser.add_argument('--name', help='股票名称', default=None)
    parser.add_argument('--days', type=int, default=180, help='分析天数')
    
    args = parser.parse_args()
    
    analyzer = UniversalSurgeAnalyzer()
    await analyzer.analyze_stock(args.symbol, args.name, args.days)


if __name__ == "__main__":
    asyncio.run(main())