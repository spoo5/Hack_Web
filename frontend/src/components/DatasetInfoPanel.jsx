import { motion } from "framer-motion";
import "./DatasetInfoPanel.css";

const DatasetInfoPanel = ({ datasetInfo }) => {
  if (!datasetInfo) return null;

  const { filename, row_count, column_count, schema } = datasetInfo;

  return (
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="dataset-info-panel glass-card"
    >
      <div className="info-header">
        <div className="info-title">
          <span className="info-icon">📊</span>
          <h3>Dataset Overview</h3>
        </div>
        <div className="info-status">
          <span className="status-indicator active"></span>
          <span className="status-text">Active</span>
        </div>
      </div>

      <div className="info-content">
        {/* File Info */}
        <div className="info-section">
          <div className="info-label">Dataset Name</div>
          <div className="info-value filename">
            {filename || "Untitled Dataset"}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">📝</div>
            <div className="stat-content">
              <div className="stat-number">{row_count?.toLocaleString()}</div>
              <div className="stat-text">Total Rows</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">📋</div>
            <div className="stat-content">
              <div className="stat-number">{column_count}</div>
              <div className="stat-text">Columns</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🔢</div>
            <div className="stat-content">
              <div className="stat-number">
                {schema?.numeric_columns?.length || 0}
              </div>
              <div className="stat-text">Numeric</div>
            </div>
          </div>

          <div className="stat-card">
            <div className="stat-icon">🏷️</div>
            <div className="stat-content">
              <div className="stat-number">
                {schema?.categorical_columns?.length || 0}
              </div>
              <div className="stat-text">Categorical</div>
            </div>
          </div>
        </div>

        {/* Schema Details */}
        {schema && (
          <div className="schema-details">
            <div className="schema-section">
              <div className="schema-label">
                <span className="schema-icon">🔢</span>
                Numeric Columns ({schema.numeric_columns?.length || 0})
              </div>
              <div className="column-tags">
                {schema.numeric_columns?.slice(0, 5).map((col, idx) => (
                  <span key={idx} className="column-tag numeric">
                    {col}
                  </span>
                ))}
                {schema.numeric_columns?.length > 5 && (
                  <span className="column-tag more">
                    +{schema.numeric_columns.length - 5} more
                  </span>
                )}
              </div>
            </div>

            <div className="schema-section">
              <div className="schema-label">
                <span className="schema-icon">🏷️</span>
                Categorical Columns ({schema.categorical_columns?.length || 0})
              </div>
              <div className="column-tags">
                {schema.categorical_columns?.slice(0, 5).map((col, idx) => (
                  <span key={idx} className="column-tag categorical">
                    {col}
                  </span>
                ))}
                {schema.categorical_columns?.length > 5 && (
                  <span className="column-tag more">
                    +{schema.categorical_columns.length - 5} more
                  </span>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default DatasetInfoPanel;
