/**
 * CRS填报助手 - 移动加权平均法计算引擎
 * 
 * 税务规则：
 * - 利息、股息：20%税率（已实现）
 * - 财产转让所得：20%税率（已实现，即卖出时的实际盈亏）
 * - 浮盈浮亏不征税
 * - 盈亏互抵：同一年度、同一地区内可互抵
 * - 跨年/跨地区盈亏不能互抵
 * - 汇率：每年12月31日人民银行中间价
 * - 滞纳金：日万分之五（2023年税款从2024/7/1起算）
 */

export const FX_RATES = {
  // 2023-12-31 人民银行美元中间价（示例，实际从API获取）
  '2023-12-31': { USD: 7.0827, HKD: 0.9070 },
  // 2024-12-31 人民银行美元中间价（示例）
  '2024-12-31': { USD: 7.3278, HKD: 0.9426 },
};

// 地区分类
export const REGION_MAP = {
  'HK': '香港',
  'US': '美国',
  'SG': '新加坡',
  'JP': '日本',
  'OTHER': '其他',
};

// 纳税主体（实际应用中从用户信息获取）
export function getRegionForAccount(accountId) {
  // 根据账户识别地区
  // 例如：H开头账号 = 香港，8位数UID = 美国IBKR
  if (accountId.startsWith('H') || accountId.includes('HK')) return 'HK';
  if (accountId.match(/^\d{8}$/)) return 'US'; // IBKR
  if (accountId.includes('SG')) return 'SG';
  return 'OTHER';
}

/**
 * 移动加权平均法计算成本均价
 * 每次买入后重新计算：成本均价 = (原总成本 + 新买入总成本) / 总股数
 */
export function calcMovingWeightedAverage(buys, currentPosition) {
  // buys: [{date, shares, price, amount}] 按时间顺序
  // currentPosition: {totalShares, avgCost, totalCost}
  if (buys.length === 0) return currentPosition;
  
  let totalShares = currentPosition ? currentPosition.totalShares : 0;
  let totalCost = currentPosition ? currentPosition.totalCost : 0;
  
  for (const buy of buys) {
    totalCost += buy.amount;
    totalShares += buy.shares;
  }
  
  return {
    totalShares,
    avgCost: totalShares > 0 ? totalCost / totalShares : 0,
    totalCost,
  };
}

/**
 * 计算单笔卖出的盈亏（使用移动加权平均成本）
 */
export function calcSellGainLoss(sell, avgCost, fxRate) {
  // sell: {date, shares, price, amount(本币)}
  const proceeds = sell.shares * sell.price;  // 本币收入
  const cost = sell.shares * avgCost;        // 移动加权平均成本
  const gainLossLocal = proceeds - cost;     // 本币盈亏
  const gainLossRMB = gainLossLocal * fxRate; // 人民币盈亏
  
  return {
    proceeds: proceeds.toFixed(2),
    cost: cost.toFixed(2),
    gainLossLocal: gainLossLocal.toFixed(2),
    gainLossRMB: gainLossRMB.toFixed(2),
    fxRate,
    taxable: gainLossLocal > 0 ? gainLossRMB.toFixed(2) : '0.00',
  };
}

/**
 * 按年度和地区汇总计算
 */
export function aggregateByYearAndRegion(transactions) {
  const result = {}; // {year: {region: {dividends, interest, realizedGL, losses}}}
  
  for (const tx of transactions) {
    const year = tx.date.substring(0, 4);
    const region = tx.region || 'OTHER';
    
    if (!result[year]) result[year] = {};
    if (!result[year][region]) {
      result[year][region] = {
        dividends: 0,
        interest: 0,
        realizedGains: 0,
        realizedLosses: 0,
        netGainLoss: 0,
        taxableAmount: 0,
        taxRate: 0.2,
      };
    }
    
    const r = result[year][region];
    if (tx.type === 'DIVIDEND') {
      r.dividends += tx.amountLocal;
    } else if (tx === 'INTEREST') {
      r.interest += tx.amountLocal;
    } else if (tx.type === 'SELL') {
      const gl = parseFloat(tx.gainLossRMB || 0);
      if (gl > 0) {
        r.realizedGains += gl;
      } else {
        r.realizedLosses += Math.abs(gl);
      }
    }
  }
  
  // 计算净收益和税额（同一地区同年度内盈亏互抵）
  for (const year of Object.keys(result)) {
    for (const region of Object.keys(result[year])) {
      const r = result[year][region];
      r.netGainLoss = r.realizedGains - r.realizedLosses + r.dividends + r.interest;
      r.taxableAmount = Math.max(0, r.realizedGains + r.dividends + r.interest);
      r.taxDue = r.taxableAmount * 0.2;
    }
  }
  
  return result;
}

/**
 * 计算滞纳金
 * 2023年税款：2024/7/1起按日万分之五
 * 2024年税款：2025/6/30前申报
 */
export function calcLatePenalty(year, taxAmount, asOfDate = '2025-06-30') {
  if (year === '2023') {
    // 从2024-07-01到asOfDate的滞纳金
    const startDate = new Date('2024-07-01');
    const endDate = new Date(asOfDate);
    const days = Math.max(0, Math.floor((endDate - startDate) / (1000 * 60 * 60 * 24)));
    const penalty = taxAmount * 0.0005 * days;
    return { year, penalty: penalty.toFixed(2), days, dailyRate: 0.0005 };
  } else if (year === '2024') {
    // 必须在2025-06-30前申报
    const deadline = new Date('2025-06-30');
    const today = new Date(asOfDate);
    if (today > deadline) {
      const days = Math.floor((today - deadline) / (1000 * 60 * 60 * 24));
      const penalty = taxAmount * 0.0005 * days;
      return { year, penalty: penalty.toFixed(2), days, dailyRate: 0.0005 };
    }
  }
  return { year, penalty: '0.00', days: 0, dailyRate: 0.0005 };
}

/**
 * 生成完整报告数据
 */
export function generateReport(parsedData, fxRates = FX_RATES) {
  const summary = {};
  
  for (const year of ['2023', '2024']) {
    const yearData = parsedData[year] || {};
    let totalTaxable = 0;
    let totalTaxDue = 0;
    let totalPenalty = 0;
    const regionDetails = {};
    
    for (const [region, amounts] of Object.entries(yearData)) {
      totalTaxable += amounts.taxableAmount;
      totalTaxDue += amounts.taxDue;
      const penalty = calcLatePenalty(year, amounts.taxDue);
      totalPenalty += parseFloat(penalty.penalty);
      regionDetails[region] = { ...amounts, penalty };
    }
    
    summary[year] = {
      totalTaxable: totalTaxable.toFixed(2),
      totalTaxDue: totalTaxDue.toFixed(2),
      totalPenalty: totalPenalty.toFixed(2),
      grandTotal: (totalTaxDue + totalPenalty).toFixed(2),
      regions: regionDetails,
    };
  }
  
  return summary;
}

// ===== 模拟数据测试 =====
export function runMockCalculation() {
  const mockTransactions = [
    // 2023 香港账户
    { date: '2023-03-15', type: 'BUY', symbol: '0700.HK', shares: 100, price: 350.0, amount: 35000, region: 'HK', account: 'H10810499' },
    { date: '2023-06-20', type: 'DIVIDEND', symbol: '0700.HK', amountLocal: 1200, region: 'HK', account: 'H10810499' },
    { date: '2023-09-10', type: 'SELL', symbol: '0700.HK', shares: 50, price: 380.0, amount: 19000, gainLossRMB: 1500, region: 'HK', account: 'H10810499' },
    { date: '2023-12-31', type: 'INTEREST', amountLocal: 350.50, region: 'HK', account: 'H10810499' },
    // 2023 美国账户
    { date: '2023-05-10', type: 'BUY', symbol: 'AAPL', shares: 10, price: 170.0, amount: 1700, region: 'US', account: 'U12345678' },
    { date: '2023-11-20', type: 'SELL', symbol: 'AAPL', shares: 5, price: 190.0, amount: 950, gainLossRMB: 730, region: 'US', account: 'U12345678' },
    { date: '2023-12-31', type: 'DIVIDEND', symbol: 'AAPL', amountLocal: 96.0, region: 'US', account: 'U12345678' },
    // 2024 香港账户
    { date: '2024-02-01', type: 'BUY', symbol: '0700.HK', shares: 50, price: 330.0, amount: 16500, region: 'HK', account: 'H10810499' },
    { date: '2024-07-15', type: 'SELL', symbol: '0700.HK', shares: 50, price: 360.0, amount: 18000, gainLossRMB: 500, region: 'HK', account: 'H10810499' },
    { date: '2024-12-31', type: 'DIVIDEND', symbol: '0700.HK', amountLocal: 1500, region: 'HK', account: 'H10810499' },
  ];
  
  const aggregated = aggregateByYearAndRegion(mockTransactions);
  const report = generateReport(aggregated);
  
  return { transactions: mockTransactions, aggregated, report };
}
