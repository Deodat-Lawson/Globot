import React, { useState } from 'react';
import { Shield, TrendingUp, AlertTriangle, FileText, Activity, Fuel, DollarSign, Globe } from 'lucide-react';
import '../styles/financial-hedge.css';

interface RiskResponse {
  market_regime?: string;
  urgency?: string;
  total_exposure_usd?: number;
  total_var_95_usd?: number;
  var_as_pct_of_exposure?: number;
  risk_breakdown?: Record<string, unknown>;
  recommendations?: Record<string, unknown>;
}

interface StrategyResponse {
  regime?: string;
  fuel_hedging?: Record<string, unknown>;
  currency_hedging?: Record<string, unknown>;
  freight_strategy?: Record<string, unknown>;
  summary?: Record<string, unknown>;
  execution_timeline?: Record<string, unknown>;
}

interface ReportResponse {
  report?: string;
  timestamp?: string;
}

const DEFAULT_PARAMS = {
  fuel_consumption_monthly: 1000,
  revenue_foreign_monthly: 1800000,
  fx_pair: 'EUR',
  monthly_voyages: 4,
  current_route: 'Shanghai → Rotterdam',
};

export const FinancialHedgePage: React.FC = () => {
  const [params, setParams] = useState(DEFAULT_PARAMS);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [risk, setRisk] = useState<RiskResponse | null>(null);
  const [strategy, setStrategy] = useState<StrategyResponse | null>(null);
  const [report, setReport] = useState<ReportResponse | null>(null);

  const handleChange = (key: keyof typeof DEFAULT_PARAMS, value: string | number) => {
    setParams(prev => ({ ...prev, [key]: value }));
  };

  const runRequest = async (path: string, body: object) => {
    const response = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(text || `Request failed: ${response.status}`);
    }

    return response.json();
  };

  const handleAssessRisk = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await runRequest('/api/hedge/assess-risk', params);
      setRisk(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleRecommend = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await runRequest('/api/hedge/recommend', params);
      setStrategy(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  const handleReport = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await runRequest('/api/hedge/report', params);
      setReport(data);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="hedge-page">
      <div className="hedge-hero">
        <div className="hedge-hero-content">
          <div className="hedge-badge">
            <Shield className="w-4 h-4" />
            <span>Financial Risk Hedge</span>
          </div>
          <h1>Financial Risk Hedge Console</h1>
          <p>
            Analyze fuel, FX, and freight exposure, then generate hedging strategies
            and executive reports powered by the Financial Hedge Agent.
          </p>
          <div className="hedge-hero-actions">
            <button className="primary" onClick={handleAssessRisk} disabled={loading}>
              <Activity className="w-4 h-4" /> Assess Risk
            </button>
            <button className="secondary" onClick={handleRecommend} disabled={loading}>
              <TrendingUp className="w-4 h-4" /> Recommend Strategy
            </button>
            <button className="ghost" onClick={handleReport} disabled={loading}>
              <FileText className="w-4 h-4" /> Generate Report
            </button>
          </div>
          {error && (
            <div className="hedge-error">
              <AlertTriangle className="w-4 h-4" />
              <span>{error}</span>
            </div>
          )}
        </div>
        <div className="hedge-hero-panel">
          <div className="panel-header">Operational Inputs</div>
          <div className="panel-grid">
            <label>
              Fuel Consumption (tons / month)
              <input
                type="number"
                value={params.fuel_consumption_monthly}
                onChange={e => handleChange('fuel_consumption_monthly', Number(e.target.value))}
              />
            </label>
            <label>
              Revenue (foreign / month)
              <input
                type="number"
                value={params.revenue_foreign_monthly}
                onChange={e => handleChange('revenue_foreign_monthly', Number(e.target.value))}
              />
            </label>
            <label>
              FX Pair
              <input
                type="text"
                value={params.fx_pair}
                onChange={e => handleChange('fx_pair', e.target.value)}
              />
            </label>
            <label>
              Monthly Voyages
              <input
                type="number"
                value={params.monthly_voyages}
                onChange={e => handleChange('monthly_voyages', Number(e.target.value))}
              />
            </label>
            <label className="full">
              Current Route
              <input
                type="text"
                value={params.current_route}
                onChange={e => handleChange('current_route', e.target.value)}
              />
            </label>
          </div>
        </div>
      </div>

      <div className="hedge-section">
        <div className="section-card">
          <div className="section-title">
            <Fuel className="w-4 h-4" /> Risk Snapshot
          </div>
          {risk ? (
            <div className="stat-grid">
              <div className="stat">
                <span>Market Regime</span>
                <strong>{risk.market_regime || '-'}</strong>
              </div>
              <div className="stat">
                <span>Urgency</span>
                <strong>{risk.urgency || '-'}</strong>
              </div>
              <div className="stat">
                <span>Total Exposure</span>
                <strong>${risk.total_exposure_usd?.toLocaleString() || '-'}</strong>
              </div>
              <div className="stat">
                <span>VaR 95%</span>
                <strong>${risk.total_var_95_usd?.toLocaleString() || '-'}</strong>
              </div>
            </div>
          ) : (
            <div className="empty-state">Run “Assess Risk” to view exposure analytics.</div>
          )}
        </div>

        <div className="section-card">
          <div className="section-title">
            <DollarSign className="w-4 h-4" /> Strategy Summary
          </div>
          {strategy ? (
            <pre className="json-view">{JSON.stringify(strategy.summary || strategy, null, 2)}</pre>
          ) : (
            <div className="empty-state">Run “Recommend Strategy” to preview hedge actions.</div>
          )}
        </div>

        <div className="section-card">
          <div className="section-title">
            <Globe className="w-4 h-4" /> Executive Report
          </div>
          {report?.report ? (
            <pre className="report-view">{report.report}</pre>
          ) : (
            <div className="empty-state">Generate a report for board-ready briefing output.</div>
          )}
        </div>
      </div>
    </div>
  );
};
