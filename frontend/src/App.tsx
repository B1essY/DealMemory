import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { NegotiationPage } from './pages/NegotiationPage';
import { OutcomePage } from './pages/OutcomePage';
import { MemoryPage } from './pages/MemoryPage';
import { DemoPage } from './pages/DemoPage';
import { fetchHealthDetailed } from './services/api';
import type { SystemHealth, Negotiation, Outcome } from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [selectedDeal, setSelectedDeal] = useState<Negotiation | null>(null);

  useEffect(() => {
    fetchHealthDetailed()
      .then((h) => setHealth(h))
      .catch((err) => console.error('Health fetch failed:', err));

    const interval = setInterval(() => {
      fetchHealthDetailed()
        .then((h) => setHealth(h))
        .catch(() => {});
    }, 20000);

    return () => clearInterval(interval);
  }, []);

  const handleSelectDealForAnalysis = (deal: Negotiation) => {
    setSelectedDeal(deal);
    setActiveTab('negotiation');
  };

  const handleNavigateToOutcome = (deal: Negotiation) => {
    setSelectedDeal(deal);
    setActiveTab('outcome');
  };

  const handleOutcomeSaved = (_outcome: Outcome) => {
    fetchHealthDetailed().then((h) => setHealth(h));
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation */}
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} health={health} />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === 'dashboard' && (
          <DashboardPage
            setActiveTab={setActiveTab}
            onSelectDealForAnalysis={handleSelectDealForAnalysis}
          />
        )}

        {activeTab === 'negotiation' && (
          <NegotiationPage
            selectedDeal={selectedDeal}
            onDealAnalyzed={(d) => setSelectedDeal(d)}
            onNavigateToOutcome={handleNavigateToOutcome}
          />
        )}

        {activeTab === 'outcome' && (
          <OutcomePage
            deal={selectedDeal}
            onOutcomeSaved={handleOutcomeSaved}
            setActiveTab={setActiveTab}
          />
        )}

        {activeTab === 'memory' && <MemoryPage />}

        {activeTab === 'demo' && <DemoPage setActiveTab={setActiveTab} />}
      </main>

      {/* Enterprise Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-6 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-400">DealMemory</span>
            <span>—</span>
            <span>Negotiation intelligence that learns from every deal.</span>
          </div>

          <div className="text-center sm:text-right">
            <span>Powered by Hindsight Cloud persistent agent memory. All data labelled Synthetic demo data.</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
