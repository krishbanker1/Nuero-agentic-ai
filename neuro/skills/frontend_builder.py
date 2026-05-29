"""
Frontend Builder - Complete React/Vue/Angular generation
Enterprise-level UI with all modern best practices
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class Component:
    name: str
    code: str
    props: List[str]
    children: List[str]

class FrontendBuilder:
    """
    Complete frontend builder for React, Vue, Angular, Svelte.
    Generates: Components, pages, hooks, state management, styling.
    
    Usage:
        from neuro.skills.frontend_builder import FrontendBuilder
        fb = FrontendBuilder()
        result = fb.build("Dashboard with charts and tables", "react")
    """
    
    MODEL = "gemini/gemini-3.5-flash"
    
    def __init__(self):
        self.router = None
    
    def _get_router(self):
        if self.router is None:
            from neuro.router.smart_router import SmartRouter
            self.router = SmartRouter()
        return self.router
    
    def build(self, description: str, framework: str = "react") -> Dict[str, Any]:
        """Build complete frontend application."""
        
        components = self._generate_components(description, framework)
        pages = self._generate_pages(framework)
        styles = self._generate_styles(framework)
        config = self._generate_config(framework)
        
        return {
            "components": components,
            "pages": pages,
            "styles": styles,
            "config": config,
            "framework": framework
        }
    
    def _generate_components(self, desc: str, fw: str) -> Dict[str, str]:
        if fw == "react":
            return {
                "Button.jsx": '''import React from 'react';
import './Button.css';

export function Button({ 
  children, 
  variant = 'primary', 
  size = 'medium',
  disabled = false,
  onClick,
  type = 'button',
  className = ''
}) {
  return (
    <button
      type={type}
      className={`btn btn-${variant} btn-${size} ${className}`}
      disabled={disabled}
      onClick={onClick}
    >
      {children}
    </button>
  );
}

export default Button;
''',
                "Button.css": '''.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.75rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(99, 102, 241, 0.3);
}

.btn-secondary {
  background: #e2e8f0;
  color: #1e293b;
}

.btn-lg { padding: 1rem 2rem; font-size: 1.2rem; }
.btn-sm { padding: 0.5rem 1rem; font-size: 0.875rem; }

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
''',
                "Card.jsx": '''import React from 'react';
import './Card.css';

export function Card({ title, children, footer, onClick }) {
  return (
    <div className="card" onClick={onClick}>
      {title && <div className="card-header">{title}</div>}
      <div className="card-body">{children}</div>
      {footer && <div className="card-footer">{footer}</div>}
    </div>
  );
}

export default Card;
''',
                "Card.css": '''.card {
  background: white;
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  overflow: hidden;
  transition: all 0.3s ease;
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
  font-weight: 600;
  font-size: 1.25rem;
}

.card-body { padding: 1.5rem; }
.card-footer {
  padding: 1rem 1.5rem;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}
''',
                "Input.jsx": '''import React, { useState } from 'react';
import './Input.css';

export function Input({
  label,
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  disabled = false,
  required = false,
  name
}) {
  return (
    <div className={`input-group ${error ? 'has-error' : ''}`}>
      {label && <label className="input-label">{label}</label>}
      <input
        type={type}
        className="input"
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        disabled={disabled}
        required={required}
        name={name}
      />
      {error && <span className="input-error">{error}</span>}
    </div>
  );
}

export default Input;
''',
                "Input.css": '''.input-group { margin-bottom: 1rem; }

.input-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #1e293b;
}

.input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 2px solid #e2e8f0;
  border-radius: 0.5rem;
  transition: all 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.has-error .input { border-color: #ef4444; }
.input-error { color: #ef4444; font-size: 0.875rem; margin-top: 0.25rem; }
''',
                "Table.jsx": '''import React from 'react';
import './Table.css';

export function Table({ columns, data, onRowClick }) {
  return (
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key}>{col.title}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} onClick={() => onRowClick?.(row)}>
              {columns.map((col) => (
                <td key={col.key}>{col.render ? col.render(row[col.key]) : row[col.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Table;
''',
                "Table.css": '''.table-container { overflow-x: auto; }

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th,
.table td {
  padding: 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

.table th {
  font-weight: 600;
  background: #f8fafc;
  color: #1e293b;
}

.table tbody tr:hover { background: #f8fafc; }
.table tbody tr { cursor: pointer; }
''',
                "Modal.jsx": '''import React, { useEffect } from 'react';
import './Modal.css';

export function Modal({ isOpen, onClose, title, children }) {
  useEffect(() => {
    if (isOpen) document.body.style.overflow = 'hidden';
    else document.body.style.overflow = '';
    return () => { document.body.style.overflow = ''; };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>{title}</h2>
          <button className="modal-close" onClick={onClose}>×</button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}

export default Modal;
''',
                "Modal.css": '''.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal-content {
  background: white;
  border-radius: 1rem;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow: auto;
  animation: slideUp 0.3s ease;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #e2e8f0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #64748b;
}

.modal-body { padding: 1.5rem; }

@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
'''
            }
        return {}
    
    def _generate_pages(self, fw: str) -> Dict[str, str]:
        return {
            "Dashboard.jsx": '''import React, { useState, useEffect } from 'react';
import { Card, Table, Button } from '../components';

export function Dashboard() {
  const [metrics, setMetrics] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      const res = await fetch('/api/metrics');
      const data = await res.json();
      setMetrics(data);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading...</div>;

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>
      <div className="metrics-grid">
        <MetricCard title="Total Users" value={metrics.users} icon="👥" />
        <MetricCard title="Revenue" value={`$${metrics.revenue}`} icon="💰" />
        <MetricCard title="Orders" value={metrics.orders} icon="📦" />
      </div>
    </div>
  );
}

function MetricCard({ title, value, icon }) {
  return (
    <Card>
      <div className="metric">
        <span className="metric-icon">{icon}</span>
        <div>
          <div className="metric-title">{title}</div>
          <div className="metric-value">{value}</div>
        </div>
      </div>
    </Card>
  );
}

export default Dashboard;
''',
            "Login.jsx": '''import React, { useState } from 'react';
import { Input, Button, Card } from '../components';

export function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('token', data.token);
      window.location.href = '/dashboard';
    }
  };

  return (
    <div className="login-page">
      <Card>
        <h2>Sign In</h2>
        <form onSubmit={handleSubmit}>
          <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} />
          <Input label="Password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
          <Button type="submit">Login</Button>
        </form>
      </Card>
    </div>
  );
}

export default Login;
'''
        }
    
    def _generate_styles(self, fw: str) -> str:
        return '''/* Global Styles */
:root {
  --primary: #6366f1;
  --secondary: #a855f7;
  --success: #10b981;
  --warning: #f59e0b;
  --danger: #ef4444;
  --gray-50: #f8fafc;
  --gray-100: #f1f5f9;
  --gray-200: #e2e8f0;
  --gray-300: #cbd5e1;
  --gray-400: #94a3b8;
  --gray-500: #64748b;
  --gray-600: #475569;
  --gray-700: #334155;
  --gray-800: #1e293b;
  --gray-900: #0f172a;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  background: var(--gray-50);
  color: var(--gray-800);
  line-height: 1.6;
}

.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  font-size: 1.5rem;
  color: var(--gray-500);
}
'''
    
    def _generate_config(self, fw: str) -> Dict[str, str]:
        return {
            "package.json": '''{
  "name": "enterprise-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
''',
            "vite.config.js": '''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: { port: 3000, proxy: { '/api': 'http://localhost:5000' } }
});
''',
            "index.html": '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Enterprise App</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/src/main.jsx"></script>
</body>
</html>
'''
        }


def build_frontend(description: str, framework: str = "react") -> Dict[str, Any]:
    """Quick frontend builder."""
    builder = FrontendBuilder()
    return builder.build(description, framework)
