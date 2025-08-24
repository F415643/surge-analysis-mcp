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
        total_return = basic['total_return']
        
        print(f"💡 技术面分析:")
        if surge_count > 10:
            print(f"  🔥 暴涨频率极高: {surge_count}个暴涨日")
        elif surge_count > 5:
            print(f"  📈 暴涨频率较高: {surge_count}个暴涨日")
        else:
            print(f"  📊 暴涨频率一般: {surge_count}个暴涨日")
        
        if volume_spike_count > 5:
            print(f"  🚀 资金关注度高: {volume_spike_count}个成交量异常日")
        elif volume_spike_count > 2:
            print(f"  💰 资金关注度中等: {volume_spike_count}个成交量异常日")
        
        if total_return > 50:
            print(f"  🎯 期间表现优异: 涨幅{total_return:.1f}%")
        elif total_return > 20:
            print(f"  📊 期间表现良好: 涨幅{total_return:.1f}%")
        elif total_return > 0:
            print(f"  📈 期间表现平稳: 涨幅{total_return:.1f}%")
        else:
            print(f"  📉 期间表现疲弱: 跌幅{abs(total_return):.1f}%")
        
        # 行业分析
        industry = company.get('行业', '')
        if industry:
            print(f"\n💼 行业特征:")
            print(f"  所属行业: {industry}")
            
            # 根据行业给出分析
            if any(keyword in industry for keyword in ['科技', '软件', '互联网', '电子', '通信']):
                print(f"  🔥 科技股特征: 政策敏感度高，成长性强")
            elif any(keyword in industry for keyword in ['医药', '生物', '医疗']):
                print(f"  💊 医药股特征: 创新驱动，政策影响大")
            elif any(keyword in industry for keyword in ['新能源', '电池', '光伏']):
                print(f"  🔋 新能源特征: 政策红利，成长空间大")
        
        print(f"\n⚠️ 风险提示:")
        if surge_count > 15:
            print(f"  • 暴涨频率过高，注意回调风险")
        if basic['volatility'] > 5:
            print(f"  • 波动率较高({basic['volatility']:.1f}%)，风险较大")
        if total_return > 100:
            print(f"  • 涨幅过大，注意获利回吐压力")
        
        print(f"  • 市场情绪变化风险")
        print(f"  • 政策环境变化影响")
        print(f"  • 基本面变化风险")


async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='通用股票暴涨分析器')
    parser.add_argument('symbol', help='股票代码 (如: 000158)')
    parser.add_argument('--name', help='股票名称', default=None)
    parser.add_argument('--days', type=int, help='分析天数', default=180)
    
    args = parser.parse_args()
    
    analyzer = UniversalSurgeAnalyzer()
    await analyzer.analyze_stock(args.symbol, args.name, args.days)


if __name__ == "__main__":
    asyncio.run(main())