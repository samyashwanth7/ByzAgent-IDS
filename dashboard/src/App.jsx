import React, { useEffect } from 'react';
import { Shield } from 'lucide-react';
import Hero from './sections/Hero';
import Problem from './sections/Problem';
import Architecture from './sections/Architecture';
import Results from './sections/Results';
import LiveDemo from './sections/LiveDemo';
import Reasoning from './sections/Reasoning';
import Footer from './sections/Footer';

function App() {
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
      {/* Sticky Navbar */}
      <nav className="navbar">
        <a href="#" className="nav-brand">
          <Shield size={22} />
          ByzAgent
        </a>
        <ul className="nav-links">
          <li><a href="#problem">Problem</a></li>
          <li><a href="#architecture">Architecture</a></li>
          <li><a href="#results">Results</a></li>
          <li><a href="#demo">Live Demo</a></li>
          <li><a href="#reasoning">Agent Log</a></li>
          <li>
            <a href="https://github.com/samyashwanth7/ByzAgent-IDS" target="_blank" rel="noreferrer" style={{ color: 'var(--accent)' }}>
              GitHub ↗
            </a>
          </li>
        </ul>
      </nav>

      <Hero />
      <Problem />
      <Architecture />
      <Results />
      <LiveDemo />
      <Reasoning />
      <Footer />
    </div>
  );
}

export default App;
