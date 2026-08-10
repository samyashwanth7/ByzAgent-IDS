import React from 'react';
import { BrowserRouter as Router, Routes, Route, NavLink } from 'react-router-dom';
import { Shield, Activity, BarChart2, GitMerge } from 'lucide-react';
import Home from './pages/Home';
import Alerts from './pages/Alerts';
import Explain from './pages/Explain';
import Compare from './pages/Compare';

function App() {
  return (
    <Router>
      <div className="app-container">
        {/* Sidebar */}
        <aside className="sidebar">
          <div className="brand">
            <Shield size={32} color="var(--accent-cyan)" />
            <span>XFed-IDS</span>
          </div>
          
          <nav className="nav-links">
            <NavLink to="/" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <Activity size={20} />
              Overview
            </NavLink>
            <NavLink to="/alerts" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <Shield size={20} />
              Alerts
            </NavLink>
            <NavLink to="/explain" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <BarChart2 size={20} />
              Explainability
            </NavLink>
            <NavLink to="/compare" className={({isActive}) => isActive ? "nav-item active" : "nav-item"}>
              <GitMerge size={20} />
              Federated Compare
            </NavLink>
          </nav>
        </aside>

        {/* Main Content */}
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/explain" element={<Explain />} />
            <Route path="/compare" element={<Compare />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
