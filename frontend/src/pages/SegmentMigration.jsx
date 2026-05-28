import { useState } from 'react';
import { motion } from 'framer-motion';
import PlotlyChart from '../components/Charts/PlotlyChart';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';

export default function SegmentMigration() {
  const [flowOpacity, setFlowOpacity] = useState(0.4);

  // 15 Nodes: Q1 (0-4), Q2 (5-9), Q3 (10-14)
  const labels = [
    'Q1: Champions', 'Q1: Loyal', 'Q1: New Customers', 'Q1: At Risk', 'Q1: Lost',
    'Q2: Champions', 'Q2: Loyal', 'Q2: New Customers', 'Q2: At Risk', 'Q2: Lost',
    'Q3: Champions', 'Q3: Loyal', 'Q3: New Customers', 'Q3: At Risk', 'Q3: Lost',
  ];

  const colors = [
    '#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444',
    '#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444',
    '#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444',
  ];

  // Q1 → Q2
  const src1 = [0,0,0, 1,1,1, 2,2,2, 3,3,3, 4];
  const tgt1 = [5,6,8, 6,5,8, 7,6,8, 8,6,9, 9];
  const val1 = [2000,500,500, 1800,300,900, 500,1000,1000, 700,300,1000, 1000];

  // Q2 → Q3
  const src2 = [5,5,5, 6,6,6, 7,7,7, 8,8,8, 9,9];
  const tgt2 = [10,11,13, 11,10,13, 12,11,13, 13,11,14, 14,11];
  const val2 = [1900,300,100, 2000,200,900, 200,200,100, 1400,400,800, 1700,200];

  const allTargets = [...tgt1, ...tgt2];
  const linkColors = allTargets.map(t => {
    if ([5,10,6,11].includes(t)) return `rgba(16, 185, 129, ${flowOpacity})`;
    if ([9,14].includes(t)) return `rgba(239, 68, 68, ${flowOpacity})`;
    return `rgba(245, 158, 11, ${flowOpacity})`;
  });

  return (
    <div>
      <motion.h1 className="page-title" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
        📈 Cohort Segment Migration Over Time
      </motion.h1>
      <p className="page-subtitle">
        Track and visualize how customer cohorts migrate between RFM lifecycle stages across sequential quarters using multi-stage flows.
      </p>

      {/* Opacity Control Card */}
      <Card className="flex gap-4 items-center p-4 mb-6 shadow-sm border border-border">
        <span style={{ fontSize: 13, color: 'var(--text-secondary)', fontWeight: 500 }}>Flow Opacity:</span>
        <input
          type="range" min="0.1" max="0.9" step="0.1"
          value={flowOpacity}
          onChange={(e) => setFlowOpacity(parseFloat(e.target.value))}
          style={{ flex: 1, accentColor: 'var(--accent-emerald)' }}
        />
        <span style={{ fontSize: 13, color: 'var(--text-primary)', width: 40, fontWeight: 600 }}>{flowOpacity}</span>
      </Card>

      <Card className="p-4 shadow-sm border border-border mb-6">
        <div style={{ height: 600 }}>
          <PlotlyChart
            data={[{
              type: 'sankey',
              node: {
                pad: 18, thickness: 25,
                line: { color: 'rgba(0,0,0,0)', width: 0 },
                label: labels, color: colors,
              },
              link: {
                source: [...src1, ...src2],
                target: [...tgt1, ...tgt2],
                value: [...val1, ...val2],
                color: linkColors,
              },
            }]}
            layout={{ height: 580, font: { size: 12 } }}
          />
        </div>
      </Card>

      <hr className="divider" />

      <div className="grid-2">
        <Card className="shadow-sm border border-border">
          <CardHeader>
            <CardTitle className="section-title text-base font-bold">🔍 Critical Retention Takeaways</CardTitle>
          </CardHeader>
          <CardContent>
            <ul style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 2, paddingLeft: 16 }}>
              <li>🔴 <strong>High Slippage:</strong> ~30% of Loyal Customers slipped to <em>At Risk</em> during Q1→Q2.</li>
              <li>🟢 <strong>Win-Back Success:</strong> 300 <em>At Risk</em> customers migrated back to <em>Loyal</em> in Q2.</li>
              <li>🎯 <strong>Late Recovery:</strong> 200 previously <em>Lost</em> customers were reactivated in Q3.</li>
            </ul>
          </CardContent>
        </Card>
        
        <Card className="shadow-sm border border-border">
          <CardHeader>
            <CardTitle className="section-title text-base font-bold">📈 Cohort Statistics</CardTitle>
          </CardHeader>
          <CardContent>
            <ul style={{ color: 'var(--text-secondary)', fontSize: 14, lineHeight: 2, paddingLeft: 16 }}>
              <li><strong>Initial Cohort Size:</strong> 10,000 active customers</li>
              <li><strong>Q1 Active Ratio:</strong> 90.0% (9,000 active, 1,000 lost)</li>
              <li><strong>Q2 Active Ratio:</strong> 81.0% (8,100 active, 1,900 lost)</li>
              <li><strong>Q3 Active Ratio:</strong> 73.0% (7,300 active, 2,700 lost)</li>
              <li><strong>Overall Retention:</strong> 73.0% across three quarters</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
