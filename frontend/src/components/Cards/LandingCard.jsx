import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/card';
import './Cards.css';

export function LandingCard({ to, icon, title, description, delay = 0 }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
    >
      <Link to={to} className="landing-card-link block">
        <Card className="landing-card cursor-pointer hover:border-emerald-500/40 hover:shadow-lg transition-all duration-300">
          <CardHeader className="pb-2">
            <div className="landing-card-icon text-3xl mb-1">{icon}</div>
            <CardTitle className="landing-card-title text-lg font-bold">{title}</CardTitle>
          </CardHeader>
          <CardContent className="pb-4">
            <CardDescription className="landing-card-desc text-sm text-muted-foreground">{description}</CardDescription>
            <div className="landing-card-arrow text-emerald-600 font-semibold text-xs mt-4 flex items-center gap-1">
              → Explore
            </div>
          </CardContent>
        </Card>
      </Link>
    </motion.div>
  );
}
