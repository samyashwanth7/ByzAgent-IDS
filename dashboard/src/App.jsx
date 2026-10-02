import React, { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink, Link } from 'react-router-dom';
import { Shield, LayoutDashboard, Activity, Brain, BarChart2 } from 'lucide-react';
import Hero from './sections/Hero';
import Problem from './sections/Problem';
import Architecture from './sections/Architecture';
import Footer from './sections/Footer';
import Results from './sections/Results';
import LiveDemo from './sections/LiveDemo';
import Reasoning from './sections/Reasoning';

// --- LANDING PAGE ---
function LandingPage() {
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            entry.target.classList.add('visible');
          }
        });
      },
      { threshold: 0.1, rootMargin: '0px 0px -50px 0px' }
    );
    document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
    return () => observer.disconnect();
  }, []);

  return (
    <div style={{ overflowX: 'clip' }}>
      <nav className="navbar">
        <Link to="/" className="nav-brand">
          <Shield size={22} />
          ByzAgent
        </Link>
        <ul className="nav-links" style={{ alignItems: 'center' }}>
          <li><a href="#problem">Problem</a></li>
          <li><a href="#architecture">Architecture</a></li>
          <li>
            <Link to="/dashboard" className="btn btn-primary" style={{ padding: '8px 16px' }}>
              Launch Dashboard →
            </Link>
          </li>
        </ul>
      </nav>
      <Hero />
      <Problem />
      <Architecture />
      <Footer />
    </div>
  );
}

// --- DASHBOARD LAYOUT ---
function DashboardLayout({ children }) {
  return (
    <div className="dashboard-layout">
      <aside className="dashboard-sidebar">
        <Link to="/" className="brand">
          <Shield size={24} />
          ByzAgent-IDS
        </Link>
        <nav className="sidebar-nav">
          <NavLink to="/dashboard" end className={({isActive}) => isActive ? "sidebar-link active" : "sidebar-link"}>
            <LayoutDashboard size={18} />
            Overview
          </NavLink>
          <NavLink to="/dashboard/analytics" className={({isActive}) => isActive ? "sidebar-link active" : "sidebar-link"}>
            <BarChart2 size={18} />
            Deep Analytics
          </NavLink>
          <NavLink to="/dashboard/live" className={({isActive}) => isActive ? "sidebar-link active" : "sidebar-link"}>
            <Activity size={18} />
            Live Feed
          </NavLink>
          <NavLink to="/dashboard/agent" className={({isActive}) => isActive ? "sidebar-link active" : "sidebar-link"}>
            <Brain size={18} />
            Agent Log
          </NavLink>
        </nav>
      </aside>
      <main className="dashboard-main">
        {children}
      </main>
    </div>
  );
}

// --- DASHBOARD PAGES ---
function DashboardOverview() {
  return (
    <div>
      <div className="dashboard-header">
        <h1>Overview</h1>
        <p>Federated intrusion detection performance under Sybil poisoning attacks.</p>
      </div>
      <Results />
    </div>
  );
}

function DashboardLive() {
  return (
    <div>
      <div className="dashboard-header">
        <h1>Live Intrusions</h1>
        <p>Real-time packet classification from simulated client nodes.</p>
      </div>
      <LiveDemo />
    </div>
  );
}

function DashboardAgent() {
  return (
    <div>
      <div className="dashboard-header">
        <h1>Agent Trust Arbiter</h1>
        <p>The internal reasoning monologue of the ByzAgent LLM.</p>
      </div>
      <Reasoning />
    </div>
  );
}

// Analytics requires a dedicated complex component, I'll put it here for now
import DashboardAnalytics from './pages/DashboardAnalytics';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/dashboard" element={<DashboardLayout><DashboardOverview /></DashboardLayout>} />
        <Route path="/dashboard/analytics" element={<DashboardLayout><DashboardAnalytics /></DashboardLayout>} />
        <Route path="/dashboard/live" element={<DashboardLayout><DashboardLive /></DashboardLayout>} />
        <Route path="/dashboard/agent" element={<DashboardLayout><DashboardAgent /></DashboardLayout>} />
      </Routes>
    </Router>
  );
}

export default App;
