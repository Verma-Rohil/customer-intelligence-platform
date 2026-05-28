import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Layout/Sidebar';
import Home from './pages/Home';
import ExecutiveOverview from './pages/ExecutiveOverview';
import CustomerLookup from './pages/CustomerLookup';
import SegmentDeepDive from './pages/SegmentDeepDive';
import SegmentMigration from './pages/SegmentMigration';
import CampaignSimulator from './pages/CampaignSimulator';
import ModelPerformance from './pages/ModelPerformance';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/executive-overview" element={<ExecutiveOverview />} />
            <Route path="/customer-lookup" element={<CustomerLookup />} />
            <Route path="/segment-deep-dive" element={<SegmentDeepDive />} />
            <Route path="/segment-migration" element={<SegmentMigration />} />
            <Route path="/campaign-simulator" element={<CampaignSimulator />} />
            <Route path="/model-performance" element={<ModelPerformance />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
