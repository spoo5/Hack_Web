import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import ChartComponent from "./ChartComponent";
import ConfidenceComponent from "./ConfidenceComponent";
import "./QueryTab.css";

const QueryTab = ({ datasetInfo }) => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);
  const [queryHistory, setQueryHistory] = useState([]);

  const handleQuerySubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const result = await axios.post("/api/query", {
        query: query,
        context: queryHistory,
      });

      setResponse(result.data);
      setQueryHistory([...queryHistory, { query, response: result.data }]);
      setQuery("");
    } catch (err) {
      console.error("Query error:", err);
      setError(err.response?.data?.detail || "Failed to process query");
    } finally {
      setLoading(false);
    }
  };

  const suggestedQuestions = datasetInfo?.suggested_questions || [
    "What is the total number of records?",
    "Show distribution by category",
    "What is the average value?",
  ];

  const handleSuggestedClick = (question) => {
    setQuery(question);
  };

  return (
    <div className="query-tab">
      {/* Query Input Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="query-input-section glass-card"
      >
        <h2 className="section-title">
          <span className="title-icon">💬</span>
          Ask Your Question
        </h2>

        <form onSubmit={handleQuerySubmit} className="query-form">
          <div className="input-wrapper">
            <input
              type="text"
              className="query-input"
              placeholder="E.g., What is the churn rate by gender?"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              disabled={loading}
            />
            <button
              type="submit"
              className="query-submit-btn"
              disabled={loading || !query.trim()}
            >
              {loading ? (
                <span className="spinner-small"></span>
              ) : (
                <span>→</span>
              )}
            </button>
          </div>
        </form>

        {/* Suggested Questions */}
        {!response && suggestedQuestions.length > 0 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="suggested-questions"
          >
            <p className="suggested-label">Suggested questions:</p>
            <div className="suggested-list">
              {suggestedQuestions.map((q, idx) => (
                <motion.button
                  key={idx}
                  className="suggested-btn"
                  onClick={() => handleSuggestedClick(q)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {q}
                </motion.button>
              ))}
            </div>
          </motion.div>
        )}

        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="error-box"
          >
            ⚠️ {error}
          </motion.div>
        )}
      </motion.div>

      {/* Loading State */}
      {loading && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="loading-section glass-card"
        >
          <div className="loading-content">
            <div className="spinner"></div>
            <p className="loading-text">Analyzing your question...</p>
            <div className="loading-steps">
              <div className="loading-step">✓ Parsing query</div>
              <div className="loading-step">⟳ Executing logic</div>
              <div className="loading-step">⟳ Computing results</div>
            </div>
          </div>
        </motion.div>
      )}

      {/* Response Section - 4 Mandatory Sections */}
      <AnimatePresence>
        {response && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -30 }}
            transition={{ duration: 0.5 }}
            className="response-container"
          >
            {/* Section 1: Natural Language Answer */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.1 }}
              className="response-section glass-card"
            >
              <div className="section-header">
                <h3 className="section-number">① </h3>
                <h3 className="section-title-large">Data-Backed Answer</h3>
              </div>
              <div
                className="answer-content"
                dangerouslySetInnerHTML={{
                  __html: response.answer
                    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                    .replace(/\n/g, "<br />"),
                }}
              />
              <ConfidenceComponent score={response.confidence_score} />
            </motion.div>

            {/* Section 2: SQL/Query Logic */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.2 }}
              className="response-section glass-card"
            >
              <div className="section-header">
                <h3 className="section-number">② </h3>
                <h3 className="section-title-large">Executed Query Logic</h3>
              </div>
              <div className="sql-block">
                <pre className="sql-code">{response.sql_logic}</pre>
              </div>
              <p className="sql-note">
                <span className="note-icon">ℹ️</span>
                This query was generated dynamically for your question
              </p>
            </motion.div>

            {/* Section 3: Derivation */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
              className="response-section glass-card"
            >
              <div className="section-header">
                <h3 className="section-number">③ </h3>
                <h3 className="section-title-large">
                  How the Answer Was Derived
                </h3>
              </div>
              <div className="derivation-content">
                <div className="derivation-stats">
                  <div className="derivation-stat">
                    <div className="stat-icon">📊</div>
                    <div className="stat-info">
                      <div className="stat-value">
                        {response.derivation.rows_analyzed?.toLocaleString()}
                      </div>
                      <div className="stat-label">Rows Analyzed</div>
                    </div>
                  </div>
                  <div className="derivation-stat">
                    <div className="stat-icon">📋</div>
                    <div className="stat-info">
                      <div className="stat-value">
                        {response.derivation.columns_used?.length || 0}
                      </div>
                      <div className="stat-label">Columns Used</div>
                    </div>
                  </div>
                </div>

                {response.derivation.formula && (
                  <div className="formula-box">
                    <div className="formula-label">Formula:</div>
                    <code className="formula-code">
                      {response.derivation.formula}
                    </code>
                  </div>
                )}

                {response.derivation.calculations && (
                  <div className="calculations-list">
                    <div className="calculations-label">Calculation Steps:</div>
                    {response.derivation.calculations.map((calc, idx) => (
                      <div key={idx} className="calculation-item">
                        <span className="calc-group">{calc.group}:</span>
                        <code className="calc-formula">{calc.calculation}</code>
                        <span className="calc-result">= {calc.result}</span>
                      </div>
                    ))}
                  </div>
                )}

                {response.derivation.calculation_steps && (
                  <div className="steps-list">
                    {response.derivation.calculation_steps.map((step, idx) => (
                      <div key={idx} className="step-item">
                        <span className="step-number">{idx + 1}.</span>
                        <span className="step-text">{step}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </motion.div>

            {/* Section 4: Visualization */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="response-section glass-card"
            >
              <div className="section-header">
                <h3 className="section-number">④ </h3>
                <h3 className="section-title-large">Visualization</h3>
              </div>
              <ChartComponent
                type={response.visualization_type}
                data={response.chart_data}
              />
            </motion.div>

            {/* Section 5: Grounding Badge */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="grounding-section glass-card"
            >
              <div className="grounding-badge">
                <span className="grounding-icon">🔒</span>
                <div className="grounding-text">
                  <strong>Data Grounding:</strong> {response.grounding_info}
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default QueryTab;
