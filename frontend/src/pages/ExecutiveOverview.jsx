import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api/client';
import { MetricCard } from '../components/Cards/MetricCard';
import PlotlyChart from '../components/Charts/PlotlyChart';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';

const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

export default function ExecutiveOverview() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.executiveSummary()
      .then(setData)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-container"><div className="loading-spinner" /><span className="loading-text">Loading executive metrics…</span></div>;
  if (error) return <div className="error-banner">⚠️ {error}</div>;
  if (!data || data.error) return <div className="error-banner">⚠️ {data?.error || 'No data available'}</div>;

  const { kpis, segment_distribution, segment_spend, treemap_data } = data;

  return (
    <div>
      <motion.h1 className="page-title" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
        📊 Executive Platform Overview
      </motion.h1>
      <p className="page-subtitle">
        High-level key performance indicators and customer segment distributions generated from your live database.
      </p>

      {/* KPI Cards */}
      <div className="grid-4">
        <MetricCard title="Active Customers" value={kpis.active_customers.toLocaleString()} delta="100% Ingested" deltaType="up" />
        <MetricCard title="Overall Churn Rate" value={`${kpis.churn_rate}%`} delta="60-Day Threshold" deltaType="down" />
        <MetricCard title="High-Risk Customers" value={kpis.high_risk_count.toLocaleString()} delta="🔴 Critical Alert" deltaType="down" />
        <MetricCard title="Avg Customer Tenure" value={`${kpis.avg_tenure_months} M`} delta="Active Lifespan" deltaType="up" />
      </div>

      <hr className="divider" />

      {/* Charts Row inside shadcn Cards */}
      <div className="grid-2">
        <div>
          <h3 className="section-title">🎯 Customer Segment Distribution</h3>
          <Card className="p-4 shadow-sm border border-border">
            <div style={{ height: 380 }}>
              <PlotlyChart
                data={[{
                  type: 'pie',
                  labels: segment_distribution.map(s => s.segment),
                  values: segment_distribution.map(s => s.count),
                  hole: 0.45,
                  marker: { colors: COLORS },
                  textinfo: 'label+percent',
                  textfont: { size: 12 },
                }]}
                layout={{
                  showlegend: true,
                  legend: { orientation: 'h', y: -0.05, x: 0.5, xanchor: 'center', font: { size: 11 } },
                }}
              />
            </div>
          </Card>
        </div>
        
        <div>
          <h3 className="section-title">💰 Revenue Contribution by Segment</h3>
          <Card className="p-4 shadow-sm border border-border">
            <div style={{ height: 380 }}>
              <PlotlyChart
                data={[{
                  type: 'bar',
                  x: segment_spend.map(s => s.total_spend),
                  y: segment_spend.map(s => s.segment),
                  orientation: 'h',
                  marker: {
                    color: segment_spend.map((_, i) => COLORS[i % COLORS.length]),
                    line: { width: 0 },
                  },
                }]}
                layout={{
                  xaxis: { title: 'Total Spend (₹)' },
                  yaxis: { title: '' },
                  showlegend: false,
                }}
              />
            </div>
          </Card>
        </div>
      </div>

      {/* Treemap inside shadcn Card */}
      {treemap_data.length > 0 && (
        <>
          <hr className="divider" />
          <h3 className="section-title">🗺️ E-Commerce Segments & Spending Treemap</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 16 }}>
            Hierarchical treemap displaying customer cohort sizes and average recency (color gradient).
          </p>
          <Card className="p-4 shadow-sm border border-border">
            <div style={{ height: 450 }}>
              <PlotlyChart
                data={[{
                  type: 'treemap',
                  labels: [
                    ...[...new Set(treemap_data.map(d => d.rfm_segment))],
                    ...treemap_data.map(d => `${d.rfm_segment} — ${d.city_tier}`)
                  ],
                  parents: [
                    ...[...new Set(treemap_data.map(d => d.rfm_segment))].map(() => ""),
                    ...treemap_data.map(d => d.rfm_segment)
                  ],
                  values: [
                    ...[...new Set(treemap_data.map(d => d.rfm_segment))].map(seg => 
                      treemap_data.filter(d => d.rfm_segment === seg).reduce((sum, d) => sum + d.customer_count, 0)
                    ),
                    ...treemap_data.map(d => d.customer_count)
                  ],
                  marker: {
                    colors: [
                      ...[...new Set(treemap_data.map(d => d.rfm_segment))].map(seg => {
                          const segData = treemap_data.filter(d => d.rfm_segment === seg);
                          const total = segData.reduce((sum, d) => sum + d.customer_count, 0);
                          return segData.reduce((sum, d) => sum + (d.avg_recency * d.customer_count), 0) / (total || 1);
                      }),
                      ...treemap_data.map(d => d.avg_recency)
                    ],
                    colorscale: 'RdYlGn_r',
                    showscale: true,
                    colorbar: { title: 'Avg Recency (Days)' },
                  },
                  textinfo: 'label+value',
                  branchvalues: 'total'
                }]}
                layout={{ height: 430 }}
              />
            </div>
          </Card>
        </>
      )}
    </div>
  );
}
