import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardContent } from '../ui/card';
import './Cards.css';

export function MetricCard({ title, value, delta, deltaType = 'up' }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
    >
      <Card className="metric-card hover:border-emerald-500/40 transition-all duration-300">
        <CardHeader className="pb-1">
          <CardTitle className="metric-card-title text-sm font-medium text-muted-foreground">{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="metric-card-value text-3xl font-bold text-foreground tracking-tight">{value}</div>
          {delta && (
            <div className={`metric-card-delta delta-${deltaType} text-xs mt-1.5 flex items-center gap-1 font-semibold`}>
              {deltaType === 'up' ? '▲' : deltaType === 'down' ? '▼' : '●'} {delta}
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
}
