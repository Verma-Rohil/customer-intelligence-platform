import { useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api/client';
import { MetricCard } from '../components/Cards/MetricCard';
import PlotlyChart from '../components/Charts/PlotlyChart';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from '../components/ui/select';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';

export default function CampaignSimulator() {
  const [segmentName, setSegmentName] = useState('At Risk');
  const [campaignId, setCampaignId] = useState('C1');
  const [costOverride, setCostOverride] = useState('');
  
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSimulate = async () => {
    setLoading(true);
    setError(null);
    try {
      const payload = {
        segment_name: segmentName,
        campaign_id: campaignId,
        custom_cost_override: costOverride ? parseFloat(costOverride) : null
      };
      const data = await api.simulateCampaign(payload);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <motion.h1 className="page-title" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
        ⚡ Business Action & Campaign Simulator
      </motion.h1>
      <p className="page-subtitle">
        Interactive sandbox to project Return on Investment (ROI) and customer save rates for targeted retention campaigns.
      </p>

      {/* Control Panel using shadcn */}
      <Card className="mb-6 shadow-sm border border-border">
        <CardHeader>
          <CardTitle className="section-title text-base font-bold">Configure Campaign Parameters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid-3">
            <div>
              <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 6, fontWeight: 500 }}>Target Segment</label>
              <Select value={segmentName} onValueChange={setSegmentName}>
                <SelectTrigger className="w-full h-10 border-input bg-transparent text-sm rounded-lg focus-visible:ring-emerald-500/20 focus-visible:border-emerald-500">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="At Risk">At Risk</SelectItem>
                  <SelectItem value="Loyal Customers">Loyal Customers</SelectItem>
                  <SelectItem value="Recent Buyers">Recent Buyers</SelectItem>
                  <SelectItem value="Lost">Lost / Hibernating</SelectItem>
                  <SelectItem value="Champions">Champions</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 6, fontWeight: 500 }}>Campaign Template</label>
              <Select value={campaignId} onValueChange={setCampaignId}>
                <SelectTrigger className="w-full h-10 border-input bg-transparent text-sm rounded-lg focus-visible:ring-emerald-500/20 focus-visible:border-emerald-500">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="bg-white">
                  <SelectItem value="C1">C1: Flat 20% Discount</SelectItem>
                  <SelectItem value="C2">C2: 2x Loyalty Points</SelectItem>
                  <SelectItem value="C3">C3: Personal Outreach Call</SelectItem>
                  <SelectItem value="C4">C4: Onboarding Email Series</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <label style={{ fontSize: 12, color: 'var(--text-secondary)', display: 'block', marginBottom: 6, fontWeight: 500 }}>Cost Per User Override (₹) [Optional]</label>
              <Input 
                type="number" 
                placeholder="e.g., 500" 
                value={costOverride} 
                onChange={e => setCostOverride(e.target.value)} 
                className="h-10 px-3 py-2 text-sm bg-transparent border-input rounded-lg focus-visible:ring-emerald-500/20 focus-visible:border-emerald-500"
              />
            </div>
          </div>
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            <Button 
              onClick={handleSimulate} 
              disabled={loading}
              className="h-10 px-6 font-semibold text-sm bg-gradient-to-r from-emerald-600 to-blue-600 hover:from-emerald-700 hover:to-blue-700 text-white rounded-lg shadow-sm cursor-pointer border-none"
            >
              {loading ? 'Running Simulation…' : '▶ Run ROI Simulation'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {error && <div className="error-banner">⚠️ {error}</div>}

      {/* Results */}
      {result && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="grid-4" style={{ marginBottom: 24 }}>
            <MetricCard title="Segment Size" value={result.segment_size.toLocaleString()} delta="Target Audience" deltaType="neutral" />
            <MetricCard title="Customers Saved" value={result.customers_saved.toLocaleString()} delta={`${(result.assumed_churn_reduction * 100).toFixed(0)}% Conversion`} deltaType="up" />
            <MetricCard title="Campaign Cost" value={`₹${result.total_campaign_cost.toLocaleString()}`} delta={`₹${result.cost_per_user} per user`} deltaType="down" />
            <MetricCard title="Revenue Saved" value={`₹${result.revenue_saved.toLocaleString()}`} delta={`Avg CLV: ₹${result.avg_clv}`} deltaType="up" />
          </div>

          <div className="grid-2">
            <div>
              <h3 className="section-title"> 📈 Financial Impact Analysis</h3>
              <Card className="p-4 shadow-sm border border-border">
                <div style={{ height: 350 }}>
                  <PlotlyChart
                    data={[
                      {
                        type: 'bar',
                        x: ['Campaign Cost', 'Revenue Saved'],
                        y: [result.total_campaign_cost, result.revenue_saved],
                        marker: { color: ['#EF4444', '#10B981'] }
                      }
                    ]}
                    layout={{
                      yaxis: { title: 'Amount (₹)' },
                      height: 330,
                      margin: { t: 20, r: 20, b: 40, l: 60 }
                    }}
                  />
                </div>
              </Card>
            </div>

            <div>
              <h3 className="section-title">🎯 Final ROI Recommendation</h3>
              <Card className="h-[calc(100%-36px)] p-6 shadow-sm border border-border flex flex-col justify-center items-center text-center">
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 8, fontWeight: 600 }}>
                  Projected Net ROI
                </div>
                <div style={{ fontSize: 60, fontWeight: 800, color: result.roi_percent >= 0 ? 'var(--accent-emerald)' : 'var(--accent-red)', marginBottom: 20 }}>
                  {result.roi_percent > 0 ? '+' : ''}{result.roi_percent}%
                </div>
                
                <div style={{ fontSize: 13, color: 'var(--text-secondary)', marginBottom: 12, fontWeight: 500 }}>
                  System Recommendation:
                </div>
                
                <Badge 
                  className="px-6 py-2.5 flex items-center font-bold text-sm w-fit border-none rounded-lg"
                  style={{
                    backgroundColor: result.roi_percent >= 0 ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
                    color: result.roi_percent >= 0 ? 'var(--accent-emerald)' : 'var(--accent-red)',
                  }}
                >
                  {result.recommendation === 'PROCEED' ? '✅ PROCEED WITH CAMPAIGN' : '⛔ DO NOT PROCEED'}
                </Badge>
              </Card>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
