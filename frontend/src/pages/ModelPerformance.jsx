import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { api } from '../api/client';
import { MetricCard } from '../components/Cards/MetricCard';
import PlotlyChart from '../components/Charts/PlotlyChart';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/card';
import { Badge } from '../components/ui/badge';

export default function ModelPerformance() {
  const [info, setInfo] = useState(null);
  const [importance, setImportance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      api.modelInfo(),
      api.featureImportance().catch(() => null) // Fallback if no model exists
    ])
      .then(([infoData, impData]) => {
        setInfo(infoData);
        if (impData && !impData.error) setImportance(impData);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="loading-container"><div className="loading-spinner" /><span className="loading-text">Loading model metrics…</span></div>;
  if (error) return <div className="error-banner">⚠️ {error}</div>;

  return (
    <div>
      <motion.h1 className="page-title" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}>
        🏆 Model Performance & Interpretability
      </motion.h1>
      <p className="page-subtitle">
        Review current production model classification metrics and global feature importance rankings.
      </p>

      {/* Info Badge using shadcn */}
      {info && (
        <div className="mb-6 flex gap-2">
          <Badge 
            variant="default"
            className="px-3 py-1.5 flex items-center font-semibold text-xs border border-emerald-500/20"
            style={{
              backgroundColor: 'rgba(16, 185, 129, 0.12)',
              color: 'var(--accent-emerald)',
            }}
          >
            🟢 Live Production Model: {info.model_type} (v{info.version})
          </Badge>
        </div>
      )}

      {/* Metric Cards */}
      {info && info.metrics && (
        <div className="grid-4" style={{ marginBottom: 32 }}>
          <MetricCard title="ROC-AUC Score" value={info.metrics.roc_auc.toFixed(3)} delta="Primary Metric" deltaType="up" />
          <MetricCard title="F1-Score" value={info.metrics.f1_score.toFixed(3)} delta="Harmonic Mean" deltaType="up" />
          <MetricCard title="Precision" value={info.metrics.precision.toFixed(3)} delta="False Positive Control" deltaType="neutral" />
          <MetricCard title="Recall" value={info.metrics.recall.toFixed(3)} delta="False Negative Control" deltaType="down" />
        </div>
      )}

      {/* Feature Importance using shadcn Card */}
      {importance && importance.top_features ? (
        <Card className="shadow-sm border border-border">
          <CardHeader>
            <CardTitle className="section-title text-base font-bold">📊 Global Feature Importance (Top 15)</CardTitle>
            <p style={{ color: 'var(--text-secondary)', fontSize: 13, marginTop: 4 }}>
              Derived from the XGBoost native <code>feature_importances_</code> attribute. Higher values indicate greater weight in predicting customer churn.
            </p>
          </CardHeader>
          <CardContent>
            <div style={{ height: 450 }}>
              <PlotlyChart
                data={[
                  {
                    type: 'bar',
                    x: importance.top_features.map(f => f.importance).reverse(),
                    y: importance.top_features.map(f => f.feature.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())).reverse(),
                    orientation: 'h',
                    marker: {
                      color: '#10B981', // Solid emerald color for consistency
                      opacity: 0.8
                    },
                    text: importance.top_features.map(f => f.importance.toFixed(3)).reverse(),
                    textposition: 'auto',
                  }
                ]}
                layout={{
                  xaxis: { title: 'Relative Importance Score' },
                  yaxis: { automargin: true },
                  height: 430,
                  margin: { l: 150, r: 20, t: 20, b: 40 }
                }}
              />
            </div>
          </CardContent>
        </Card>
      ) : (
        <div className="error-banner">Feature importance data is unavailable. Please ensure the model is trained and loaded.</div>
      )}
    </div>
  );
}
