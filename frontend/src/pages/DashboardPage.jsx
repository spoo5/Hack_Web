import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import QueryTab from "../components/QueryTab";
import InsightsTab from "../components/InsightsTab";
import DatasetInfoPanel from "../components/DatasetInfoPanel";
import "./DashboardPage.css";

const DashboardPage = ({ datasetInfo: initialDatasetInfo }) => {
  const [activeTab, setActiveTab] = useState("query");
  const [datasetInfo, setDatasetInfo] = useState(initialDatasetInfo);
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    // Get selected department from localStorage
    const dept = JSON.parse(
      localStorage.getItem("selectedDepartment") || "null",
    );
    setSelectedDepartment(dept);

    // If no dataset info, fetch it or redirect to home
    if (!datasetInfo) {
      fetchDatasetInfo();
    }
  }, []);

  const fetchDatasetInfo = async () => {
    try {
      const response = await axios.get("/api/dataset/info");
      setDatasetInfo(response.data);
    } catch (error) {
      console.error("No dataset loaded:", error);
      navigate("/");
    }
  };

  const tabs = [
    { id: "query", label: "Query & Logic", icon: "🔍" },
    { id: "overview", label: "Overview", icon: "📊" },
    { id: "insights", label: "Insights", icon: "💡" },
  ];

  return (
    <div className="dashboard-page">
      {/* Header */}
      <header className="dashboard-header">
        <div className="container">
          <div className="header-content">
            <div className="header-left">
              <motion.div
                className="logo-small"
                whileHover={{ scale: 1.05 }}
                onClick={() => navigate("/")}
              >
                <span className="logo-icon">🧠</span>
                <span className="logo-text">
                  Data<span className="text-gold">Sage</span>
                </span>
              </motion.div>
            </div>

            <div className="header-right">
              {selectedDepartment && (
                <div className="department-badge">
                  <span className="dept-icon">{selectedDepartment.icon}</span>
                  <span className="dept-text">{selectedDepartment.name}</span>
                </div>
              )}
              {datasetInfo && (
                <div className="dataset-badge">
                  <span className="badge-icon">📊</span>
                  <span className="badge-text">
                    {datasetInfo.filename || "Dataset"} •{" "}
                    {datasetInfo.row_count?.toLocaleString()} rows
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="dashboard-content">
        <div className="container">
          {/* Dataset Info Panel */}
          {datasetInfo && <DatasetInfoPanel datasetInfo={datasetInfo} />}

          {/* Tabs */}
          <div className="tabs-container">
            <div className="tabs-header">
              {tabs.map((tab) => (
                <motion.button
                  key={tab.id}
                  className={`tab-button ${activeTab === tab.id ? "active" : ""}`}
                  onClick={() => setActiveTab(tab.id)}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span className="tab-icon">{tab.icon}</span>
                  <span className="tab-label">{tab.label}</span>
                  {activeTab === tab.id && (
                    <motion.div
                      className="tab-indicator"
                      layoutId="activeTab"
                      transition={{
                        type: "spring",
                        stiffness: 300,
                        damping: 30,
                      }}
                    />
                  )}
                </motion.button>
              ))}
            </div>

            <div className="tabs-content">
              <AnimatePresence mode="wait">
                {activeTab === "query" && (
                  <motion.div
                    key="query"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <QueryTab datasetInfo={datasetInfo} />
                  </motion.div>
                )}

                {activeTab === "overview" && (
                  <motion.div
                    key="overview"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                    className="tab-content-placeholder"
                  >
                    <div className="glass-card">
                      <h2>📊 Dataset Overview</h2>
                      <p className="text-secondary">
                        Statistical summary and distribution analysis coming
                        soon.
                      </p>
                      {datasetInfo && (
                        <div className="overview-stats">
                          <div className="stat-box">
                            <div className="stat-value">
                              {datasetInfo.row_count?.toLocaleString()}
                            </div>
                            <div className="stat-label">Total Rows</div>
                          </div>
                          <div className="stat-box">
                            <div className="stat-value">
                              {datasetInfo.column_count}
                            </div>
                            <div className="stat-label">Total Columns</div>
                          </div>
                          <div className="stat-box">
                            <div className="stat-value">
                              {datasetInfo.schema?.numeric_columns?.length || 0}
                            </div>
                            <div className="stat-label">Numeric Columns</div>
                          </div>
                          <div className="stat-box">
                            <div className="stat-value">
                              {datasetInfo.schema?.categorical_columns
                                ?.length || 0}
                            </div>
                            <div className="stat-label">
                              Categorical Columns
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}

                {activeTab === "insights" && (
                  <motion.div
                    key="insights"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <InsightsTab
                      datasetInfo={datasetInfo}
                      department={selectedDepartment}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
