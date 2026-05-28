import { motion } from 'framer-motion';
import { LandingCard } from '../components/Cards/LandingCard';

const cards = [
  {
    to: '/executive-overview',
    icon: '📊',
    title: 'Executive Overview',
    description: 'Audit your entire customer base at a glance. Real-time KPI summaries, spend metrics, and rule-based cohort segment distributions powered by your Olist database.',
  },
  {
    to: '/customer-lookup',
    icon: '🔍',
    title: 'Customer Lookup Engine',
    description: 'Drill down into individual profiles. Uses SHAP explainability matrices to detail positive/negative feature contributions driving real-time churn predictions.',
  },
  {
    to: '/segment-deep-dive',
    icon: '🎯',
    title: 'Segment Deep Dive',
    description: 'Examine demographic attribute profiles. Uses principal component analysis (PCA) to project your high-dimensional segments into an interactive, rotatable 3D cluster space.',
  },
  {
    to: '/segment-migration',
    icon: '📈',
    title: 'Segment Migration',
    description: 'Visualize attrition rates. A multi-stage Sankey flow diagram plotting cohort migration, campaign recovery, and customer slippages across quarters.',
  },
  {
    to: '/campaign-simulator',
    icon: '⚡',
    title: 'Campaign Simulator',
    description: 'An interactive simulation sandbox allowing business teams to test coupon cost models, predict customer saves, and audit projected ROI impacts.',
  },
  {
    to: '/model-performance',
    icon: '🏆',
    title: 'Model Performance',
    description: 'Verify classification metrics. Live reads of ROC-AUC and Precision curves accompanied by interactive SHAP feature importance visualizations.',
  },
];

export default function Home() {
  return (
    <div>
      <motion.h1
        className="page-title"
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.5 }}
      >
        🔮 Customer Intelligence & Retention Platform
      </motion.h1>
      <motion.p
        className="page-subtitle"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        An enterprise-grade MLOps platform transforming raw transactional logs into deep
        predictive retention and segmentation analytics.
      </motion.p>

      <h3 className="section-title" style={{ marginBottom: 20 }}>
        🛠️ Core Analytical Pillars
      </h3>

      <div className="grid-3">
        {cards.map((card, i) => (
          <LandingCard key={card.to} {...card} delay={0.1 + i * 0.08} />
        ))}
      </div>

      <hr className="divider" />

      <motion.p
        style={{ fontSize: 14, color: 'var(--text-secondary)', lineHeight: 1.7 }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.8 }}
      >
        💡 <strong>MLOps Platform Architecture:</strong> This application communicates with a
        high-performance <strong>FastAPI</strong> REST backend serving serialized{' '}
        <strong>Scikit-Learn</strong> preprocessing scalers, <strong>K-Means</strong> clustering
        models, <strong>XGBoost</strong> churn predictors, and <strong>PyTorch</strong>{' '}
        representation learning encoders.
      </motion.p>
    </div>
  );
}
