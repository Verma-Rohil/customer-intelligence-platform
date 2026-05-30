import { useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api/client';
import PlotlyChart from '../components/Charts/PlotlyChart';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';

export default function CustomerLookup() {
  const [customerId, setCustomerId] = useState('');
  const [result, setResult] = useState(null);
  const [features, setFeatures] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const samples = [
    { id: '001928b561575b2821c92254a2327d06', name: 'Champions (Low Risk)', badgeColor: 'bg-emerald-500/10 text-emerald-600 hover:bg-emerald-500/20 border-emerald-500/20' },
    { id: '000ec5bff359e1c0ad76a81a45cb598f', name: 'New Customer (Active)', badgeColor: 'bg-blue-500/10 text-blue-500 hover:bg-blue-500/20 border-blue-500/20' },
    { id: '0004aac84e0df4da2b147fca70cf8255', name: 'At Risk (High Spend)', badgeColor: 'bg-amber-500/10 text-amber-500 hover:bg-amber-500/20 border-amber-500/20' },
    { id: '0000f46a3911fa3c0805444483337064', name: 'Lost / Hibernating', badgeColor: 'bg-rose-500/10 text-rose-500 hover:bg-rose-500/20 border-rose-500/20' },
  ];

  const handleSearch = async (idToSearch) => {
    const searchId = typeof idToSearch === 'string' ? idToSearch : customerId;
    if (!searchId || !searchId.trim()) {
      setError("Please enter a customer ID or click a sample profile below.");
      return;
    }
    
    setLoading(true);
    setError(null);
    setResult(null);
    setFeatures(null);
    
    try {
      // 1. Fetch real customer attributes
      const custFeatures = await api.getCustomer(searchId.trim());
      setFeatures(custFeatures);
      
      // 2. Perform live inference on the real attributes
      const data = await api.predictChurn(custFeatures);
      setResult({ ...data, customerId: searchId.trim() });
    } catch (e) {
      if (e.message.includes('404')) {
        setError(`Customer ID "${searchId}" not found in database.`);
      } else {
        setError(`Failed to retrieve profile: ${e.message}`);
      }
    } finally {
      setLoading(false);
    }
  };

  const prob = result ? result.churn_probability * 100 : 0;
  const gaugeColor = prob > 60 ? '#EF4444' : prob > 30 ? '#F59E0B' : '#10B981';

  return (
    <div>
      <motion.h1 className="page-title" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
        🔍 Customer Lookup Engine
      </motion.h1>
      <p className="page-subtitle">
        Analyze individual customer risk probability and view feature contributions using SHAP explainability matrices.
      </p>

      {/* Search Bar using shadcn components */}
      <Card className="flex gap-4 items-center p-4 mb-4 shadow-sm border border-border">
        <Input
          type="text"
          placeholder="Enter Customer ID (e.g., 001928b561575b2821c92254a2327d06)"
          value={customerId}
          onChange={(e) => setCustomerId(e.target.value)}
          className="flex-1 h-10 px-4 py-2 text-sm bg-transparent border-input rounded-lg focus-visible:ring-emerald-500/20 focus-visible:border-emerald-500"
          onKeyDown={(e) => { if (e.key === 'Enter') handleSearch(); }}
        />
        <Button 
          onClick={handleSearch} 
          disabled={loading}
          className="h-10 px-6 font-semibold text-sm bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white rounded-lg shadow-sm cursor-pointer border-none"
        >
          {loading ? 'Analyzing…' : '🔍 Search Profile'}
        </Button>
      </Card>

      {/* Quick Test Samples */}
      <div className="mb-6 p-4 rounded-lg bg-slate-900/40 border border-slate-800/80">
        <span className="text-xs font-semibold text-slate-400 block mb-2.5">💡 Quick Test: Click a real customer profile from the dataset</span>
        <div className="flex flex-wrap gap-2.5">
          {samples.map((s) => (
            <button
              key={s.id}
              onClick={() => {
                setCustomerId(s.id);
                handleSearch(s.id);
              }}
              className={`text-left text-xs px-3.5 py-2.5 rounded-lg border font-medium transition-all duration-200 cursor-pointer ${s.badgeColor}`}
            >
              <div className="font-semibold text-xs mb-0.5">{s.name}</div>
              <div className="opacity-70 text-[10px] font-mono">{s.id}</div>
            </button>
          ))}
        </div>
      </div>

      {error && <div className="error-banner">⚠️ {error}</div>}

      {result && features && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          {/* Info Banner */}
          <div className="mb-5 flex gap-2">
            <Badge 
              variant="default"
              className="px-3 py-1.5 flex items-center font-semibold text-xs border border-emerald-500/20"
              style={{
                backgroundColor: 'rgba(16, 185, 129, 0.12)',
                color: 'var(--accent-emerald)',
              }}
            >
              ✅ Profile Loaded — {result.customerId} | Tenure: {features.tenure_months} months | Total Orders: {features.frequency_total} | Spend: ₹{features.monetary_value_total.toLocaleString()}
            </Badge>
          </div>

          <div className="grid-2">
            {/* Gauge */}
            <div>
              <h3 className="section-title">Churn Probability Gauge</h3>
              <Card className="p-4 shadow-sm border border-border flex items-center justify-center" style={{ height: 320 }}>
                <PlotlyChart
                  data={[{
                    type: 'indicator',
                    mode: 'gauge+number',
                    value: prob,
                    title: { text: 'Churn Probability (%)' },
                    gauge: {
                      axis: { range: [0, 100] },
                      bar: { color: gaugeColor },
                      steps: [
                        { range: [0, 30], color: 'rgba(16, 185, 129, 0.1)' },
                        { range: [30, 60], color: 'rgba(245, 158, 11, 0.1)' },
                        { range: [60, 100], color: 'rgba(239, 68, 68, 0.1)' },
                      ],
                    },
                  }]}
                  layout={{ height: 280, width: 340, margin: { t: 40, b: 20, l: 30, r: 30 } }}
                />
              </Card>
            </div>

            {/* Action Plan */}
            <div>
              <h3 className="section-title">Recommended Action Plan</h3>
              <Card className="h-[calc(100%-36px)] p-6 shadow-sm border border-border flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-4">
                    <span style={{ fontSize: 28 }}>
                      {result.risk_level === 'HIGH' ? '🔴' : result.risk_level === 'MEDIUM' ? '🟡' : '🟢'}
                    </span>
                    <span style={{ fontSize: 22, fontWeight: 700 }}>
                      Risk Level: {result.risk_level}
                    </span>
                  </div>
                  <div style={{ color: 'var(--text-secondary)', marginBottom: 12, fontSize: 14 }}>
                    <strong>Recommended Marketing Action:</strong>
                  </div>
                </div>
                
                <div>
                  <Badge 
                    className="px-4 py-2.5 flex items-center font-bold text-sm w-fit border-none rounded-lg"
                    style={{
                      backgroundColor: 'rgba(16, 185, 129, 0.12)',
                      color: 'var(--accent-emerald)',
                    }}
                  >
                    ⚡ {result.recommended_action}
                  </Badge>
                </div>
              </Card>
            </div>
          </div>

          {/* SHAP Feature Bar */}
          <hr className="divider" />
          <h3 className="section-title">📊 SHAP Feature Contributions Matrix</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginBottom: 16 }}>
            Quantifies how each metric pushed the churn probability up (red) or down (green).
          </p>
          <Card className="p-4 shadow-sm border border-border">
            <div style={{ height: 300 }}>
              <PlotlyChart
                data={[{
                  type: 'bar',
                  x: result.top_risk_factors.map(f => f.shap_value),
                  y: result.top_risk_factors.map(f => f.feature.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())),
                  orientation: 'h',
                  marker: {
                    color: result.top_risk_factors.map(f =>
                      f.direction === 'increases_risk' ? '#EF4444' : '#10B981'
                    ),
                  },
                }]}
                layout={{
                  xaxis: { title: 'SHAP Contribution Score' },
                  yaxis: { automargin: true },
                  height: 280,
                }}
              />
            </div>
          </Card>
        </motion.div>
      )}
    </div>
  );
}
