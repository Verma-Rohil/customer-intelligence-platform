import { useEffect, useState, useMemo } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api/client';
import { MetricCard } from '../components/Cards/MetricCard';
import PlotlyChart from '../components/Charts/PlotlyChart';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../components/ui/select';

const COLORS = ['#10B981', '#3B82F6', '#F59E0B', '#EF4444', '#EC4899'];

export default function SegmentDeepDive() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [segType, setSegType] = useState('rfm'); // 'rfm' or 'cluster'
  const [selectedSeg, setSelectedSeg] = useState('');
  const [selectedMetric, setSelectedMetric] = useState('monetary_value_total');

  useEffect(() => {
    api.segmentData()
      .then((d) => {
        setData(d);
        if (d.available_segments?.length > 0) setSelectedSeg(d.available_segments[0]);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const filtered = useMemo(() => {
    if (!data) return [];
    if (segType === 'rfm') {
      return data.customers.filter((c) => c.rfm_segment === selectedSeg);
    }
    return data.customers.filter((c) => String(c.cluster_id) === String(selectedSeg));
  }, [data, segType, selectedSeg]);

  const segOptions = useMemo(() => {
    if (!data) return [];
    return segType === 'rfm' ? data.available_segments : data.available_clusters.map(String);
  }, [data, segType]);

  const allCustomers = useMemo(() => {
    return data?.customers || [];
  }, [data]);

  const safeAvg = (arr, key) => {
    const vals = arr.map(c => c[key]).filter(v => v != null);
    return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
  };

  // Radar chart data
  const { ratios, attrNames } = useMemo(() => {
    if (!data || filtered.length === 0) return { ratios: [], attrNames: [] };
    const attrs = ['monetary_value_total', 'recency_days', 'frequency_total', 'avg_order_value', 'tenure_months'];
    const names = ['Monetary Spend', 'Recency', 'Frequency', 'Avg Order Value', 'Tenure'];
    const segVals = attrs.map(a => safeAvg(filtered, a));
    const globalVals = attrs.map(a => safeAvg(allCustomers, a));
    const calculatedRatios = segVals.map((s, i) => ((s / Math.max(0.01, globalVals[i])) * 100));
    return { ratios: calculatedRatios, attrNames: names };
  }, [data, filtered, allCustomers]);

  if (loading) return <div className="loading-container"><div className="loading-spinner" /><span className="loading-text">Loading segment data…</span></div>;
  if (error) return <div className="error-banner">⚠️ {error}</div>;

  return (
    <div>
      <motion.h1 className="page-title" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
        🎯 Segment Deep Dive & Profiling
      </motion.h1>
      <p className="page-subtitle">
        Profile specific customer clusters and visualize spatial representations in high-dimensional learning spaces.
      </p>

      {/* Controls using shadcn Card & Select */}
      <Card className="flex gap-4 p-4 mb-6 shadow-sm border border-border">
        <div style={{ flex: 1 }}>
          <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 6, fontWeight: 500 }}>Segment Type</label>
          <Select value={segType} onValueChange={(val) => { setSegType(val); setSelectedSeg(''); }}>
            <SelectTrigger className="w-full h-10 border-input bg-transparent text-sm rounded-lg focus-visible:ring-emerald-500/20 focus-visible:border-emerald-500">
              <SelectValue />
            </SelectTrigger>
            <SelectContent className="bg-white">
              <SelectItem value="rfm">RFM Segment</SelectItem>
              <SelectItem value="cluster">K-Means Cluster</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div style={{ flex: 1 }}>
          <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 6, fontWeight: 500 }}>
            {segType === 'rfm' ? 'RFM Cohort' : 'Cluster ID'}
          </label>
          <Select value={selectedSeg} onValueChange={setSelectedSeg}>
            <SelectTrigger className="w-full h-10 border-input bg-transparent text-sm rounded-lg focus-visible:ring-emerald-500/20 focus-visible:border-emerald-500">
              <SelectValue placeholder="Select segment..." />
            </SelectTrigger>
            <SelectContent className="bg-white">
              {segOptions.map(s => (
                <SelectItem key={s} value={s}>
                  {segType === 'rfm' ? s : `Cluster ${s}`}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </Card>

      {/* Metrics */}
      <div className="grid-4">
        <MetricCard title="Customer Count" value={filtered.length.toLocaleString()} delta={`${((filtered.length / Math.max(1, allCustomers.length)) * 100).toFixed(1)}% of cohort`} deltaType="neutral" />
        <MetricCard title="Avg Spend (₹)" value={`₹${safeAvg(filtered, 'monetary_value_total').toFixed(2)}`} delta={`Overall: ₹${safeAvg(allCustomers, 'monetary_value_total').toFixed(2)}`} deltaType="neutral" />
        <MetricCard title="Avg Recency" value={`${safeAvg(filtered, 'recency_days').toFixed(1)} D`} delta={`Overall: ${safeAvg(allCustomers, 'recency_days').toFixed(1)} days`} deltaType="neutral" />
        <MetricCard title="Avg Frequency" value={`${safeAvg(filtered, 'frequency_total').toFixed(2)} O`} delta={`Overall: ${safeAvg(allCustomers, 'frequency_total').toFixed(2)} orders`} deltaType="neutral" />
      </div>

      <hr className="divider" />

      <div className="grid-2">
        {/* Radar */}
        <div>
          <h3 className="section-title">📊 Attribute Profiles: {selectedSeg || 'All'}</h3>
          <Card className="p-4 shadow-sm border border-border">
            <div style={{ height: 400 }}>
              {ratios.length > 0 && (
                <PlotlyChart
                  data={[{
                    type: 'scatterpolar',
                    r: [...ratios, ratios[0]],
                    theta: [...attrNames, attrNames[0]],
                    fill: 'toself',
                    fillcolor: 'rgba(16, 185, 129, 0.15)',
                    line: { color: '#10B981', width: 2 },
                    name: selectedSeg || 'All',
                  }]}
                  layout={{
                    polar: {
                      radialaxis: { visible: true, range: [0, Math.max(250, ...ratios) + 20], color: 'rgba(0,0,0,0.1)' },
                      angularaxis: { color: '#475569' },
                    },
                    showlegend: false,
                    height: 380,
                  }}
                />
              )}
            </div>
          </Card>
        </div>

        {/* Distribution Histogram */}
        <div>
          <h3 className="section-title">💡 Behavioral Distribution</h3>
          <div style={{ marginBottom: 12 }}>
            <Select value={selectedMetric} onValueChange={setSelectedMetric}>
              <SelectTrigger className="w-full h-10 border-input bg-transparent text-sm rounded-lg focus-visible:ring-emerald-500/20 focus-visible:border-emerald-500">
                <SelectValue />
              </SelectTrigger>
              <SelectContent className="bg-white">
                {['monetary_value_total', 'recency_days', 'frequency_total', 'tenure_months'].map(m => (
                  <SelectItem key={m} value={m}>
                    {m.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <Card className="p-4 shadow-sm border border-border">
            <div style={{ height: 350 }}>
              <PlotlyChart
                data={[
                  {
                    type: 'histogram',
                    x: allCustomers.map(c => c[selectedMetric]).filter(v => v != null),
                    name: 'Cohort Overall',
                    marker: { color: 'rgba(156, 163, 175, 0.35)' },
                    nbinsx: 40,
                    histnorm: 'probability density',
                  },
                  {
                    type: 'histogram',
                    x: filtered.map(c => c[selectedMetric]).filter(v => v != null),
                    name: selectedSeg || 'Selected',
                    marker: { color: 'rgba(16, 185, 129, 0.7)' },
                    nbinsx: 40,
                    histnorm: 'probability density',
                  },
                ]}
                layout={{
                  barmode: 'overlay',
                  xaxis: { title: selectedMetric.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) },
                  yaxis: { title: 'Probability Density' },
                  legend: { y: 0.99, x: 0.99, xanchor: 'right' },
                  height: 330,
                }}
              />
            </div>
          </Card>
        </div>
      </div>

      {/* 3D PCA */}
      <hr className="divider" />
      <h3 className="section-title">🔮 Rotatable 3D PCA Cluster Representation Space</h3>
      <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 16 }}>
        Projects core customer metrics into a fully interactive 3D scatter space. Grab, rotate, and zoom into cluster boundaries!
      </p>
      <Card className="p-4 shadow-sm border border-border">
        <div style={{ height: 600 }}>
          <PlotlyChart
            data={data.available_clusters.map((cid, idx) => {
              const pts = allCustomers.filter(c => c.cluster_id === cid);
              return {
                type: 'scatter3d',
                mode: 'markers',
                name: `Cluster ${cid}`,
                x: pts.map(p => p.recency_days || 0),
                y: pts.map(p => p.frequency_total || 0),
                z: pts.map(p => p.monetary_value_total || 0),
                marker: { size: 3, color: COLORS[idx % COLORS.length], opacity: 0.7 },
                text: pts.map(p => p.customer_id),
                hovertemplate: 'ID: %{text}<br>Recency: %{x}<br>Freq: %{y}<br>Spend: %{z}<extra></extra>',
              };
            })}
            layout={{
              scene: {
                xaxis: { title: 'Recency (days)', showgrid: true, gridcolor: 'rgba(0,0,0,0.05)' },
                yaxis: { title: 'Frequency', showgrid: true, gridcolor: 'rgba(0,0,0,0.05)' },
                zaxis: { title: 'Monetary (₹)', showgrid: true, gridcolor: 'rgba(0,0,0,0.05)' },
                bgcolor: 'rgba(0,0,0,0)',
              },
              height: 580,
              legend: { y: 0.9, x: 0.01 },
            }}
          />
        </div>
      </Card>
    </div>
  );
}
