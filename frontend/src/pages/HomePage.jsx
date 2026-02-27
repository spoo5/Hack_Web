import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import "./HomePage.css";

const HomePage = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: "🧠",
      title: "AI-Powered Intelligence",
      description:
        "Ask questions in plain English, get data-backed answers instantly",
    },
    {
      icon: "🔒",
      title: "Zero Hallucination",
      description:
        "All computations verified with deterministic Pandas execution",
    },
    {
      icon: "📊",
      title: "Smart Visualizations",
      description: "Auto-generated charts and insights tailored to your data",
    },
    {
      icon: "🎯",
      title: "Department-Specific",
      description:
        "Customized analytics for Sales, Marketing, Finance, and more",
    },
    {
      icon: "⚡",
      title: "Real-Time Analysis",
      description: "Upload CSV and get instant schema detection and insights",
    },
    {
      icon: "🔍",
      title: "Explainable Results",
      description:
        "See the SQL logic, formula, and derivation behind every answer",
    },
  ];

  const stats = [
    { value: "10K+", label: "Queries Processed" },
    { value: "500+", label: "Companies Trust Us" },
    { value: "99.9%", label: "Accuracy Rate" },
    { value: "24/7", label: "Data Availability" },
  ];

  return (
    <div className="home-page">
      {/* Animated Background */}
      <div className="home-bg-gradient"></div>
      <div className="home-bg-grid"></div>

      {/* Navigation */}
      <nav className="home-nav">
        <div className="container">
          <div className="nav-content">
            <motion.div
              className="nav-logo"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <span className="logo-icon">🧠</span>
              <span className="logo-text">
                Data<span className="text-gold">Sage</span>
              </span>
            </motion.div>

            <motion.div
              className="nav-actions"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
            >
              <button
                className="btn-secondary nav-btn"
                onClick={() => navigate("/login")}
              >
                Sign In
              </button>
              <button
                className="btn-primary nav-btn"
                onClick={() => navigate("/signup")}
              >
                Get Started
              </button>
            </motion.div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="container">
          <motion.div
            className="hero-content"
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <motion.div
              className="hero-badge"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring" }}
            >
              ✨ Conversational Data Intelligence Platform
            </motion.div>

            <motion.h1
              className="hero-title"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
            >
              Turn Your Data Into
              <br />
              <span className="text-gold">Actionable Insights</span>
            </motion.h1>

            <motion.p
              className="hero-description"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              DataSage empowers your team to analyze data using natural
              language.
              <br />
              No SQL required. No hallucinations. Just pure, verified
              intelligence.
            </motion.p>

            <motion.div
              className="hero-cta"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.8 }}
            >
              <button
                className="btn-primary btn-large"
                onClick={() => navigate("/signup")}
              >
                Start Free Trial →
              </button>
              <button
                className="btn-secondary btn-large"
                onClick={() => navigate("/login")}
              >
                Sign In
              </button>
            </motion.div>

            <motion.p
              className="hero-note"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 1 }}
            >
              ✓ No credit card required · ✓ 14-day free trial · ✓ Cancel anytime
            </motion.p>
          </motion.div>

          {/* Hero Visual */}
          <motion.div
            className="hero-visual"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1, duration: 0.8 }}
          >
            <div className="visual-card glass-card">
              <div className="visual-header">
                <div className="visual-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                <span className="visual-title">DataSage Analytics</span>
              </div>
              <div className="visual-content">
                <div className="query-example">
                  <span className="query-icon">💬</span>
                  <span className="query-text">
                    "What is our churn rate by region?"
                  </span>
                </div>
                <div className="result-preview">
                  <div className="result-chart"></div>
                  <div className="result-stats">
                    <div className="stat-bar"></div>
                    <div className="stat-bar"></div>
                    <div className="stat-bar"></div>
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="container">
          <div className="stats-grid">
            {stats.map((stat, idx) => (
              <motion.div
                key={idx}
                className="stat-card"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 1.2 + idx * 0.1 }}
              >
                <div className="stat-value">{stat.value}</div>
                <div className="stat-label">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <motion.div
            className="section-header"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
          >
            <h2 className="section-title">
              Why Choose <span className="text-gold">DataSage</span>?
            </h2>
            <p className="section-subtitle">
              Enterprise-grade analytics that everyone can use
            </p>
          </motion.div>

          <div className="features-grid">
            {features.map((feature, idx) => (
              <motion.div
                key={idx}
                className="feature-card glass-card"
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                whileHover={{ y: -5 }}
              >
                <div className="feature-icon">{feature.icon}</div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <motion.div
            className="cta-card glass-card"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
          >
            <h2 className="cta-title">
              Ready to Transform Your Data Analysis?
            </h2>
            <p className="cta-description">
              Join hundreds of companies making data-driven decisions faster
            </p>
            <div className="cta-buttons">
              <button
                className="btn-primary btn-large"
                onClick={() => navigate("/signup")}
              >
                Get Started Free
              </button>
              <button
                className="btn-secondary btn-large"
                onClick={() => navigate("/login")}
              >
                Sign In
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="home-footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand">
              <span className="logo-icon">🧠</span>
              <span className="logo-text">
                Data<span className="text-gold">Sage</span>
              </span>
            </div>
            <p className="footer-text">
              © 2026 DataSage. Conversational Data Intelligence Platform.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;
