import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import "./DepartmentSelectionPage.css";

const DepartmentSelectionPage = () => {
  const navigate = useNavigate();
  const [selectedDepartment, setSelectedDepartment] = useState(null);

  const departments = [
    {
      id: "sales",
      name: "Sales Analytics",
      icon: "📈",
      description:
        "Track revenue trends, analyze customer segments, monitor sales performance, and forecast growth opportunities.",
      color: "#4CAF50",
      insights: [
        "Revenue by Region",
        "Customer Acquisition Cost",
        "Churn Analysis",
        "Sales Funnel Conversion",
      ],
    },
    {
      id: "marketing",
      name: "Marketing Intelligence",
      icon: "🎯",
      description:
        "Measure campaign effectiveness, understand customer behavior, optimize marketing spend, and track ROI.",
      color: "#FF6B6B",
      insights: [
        "Campaign Performance",
        "Lead Generation",
        "Customer Lifetime Value",
        "Channel Attribution",
      ],
    },
    {
      id: "finance",
      name: "Finance Analytics",
      icon: "💰",
      description:
        "Analyze financial performance, track expenses, manage budgets, and generate comprehensive financial reports.",
      color: "#FFC107",
      insights: [
        "Cash Flow Analysis",
        "Cost Breakdown",
        "Budget Variance",
        "Profit Margins",
      ],
    },
    {
      id: "business",
      name: "Business Intelligence",
      icon: "🎓",
      description:
        "Get executive insights, strategic metrics, cross-functional analytics, and high-level business performance data.",
      color: "#9C27B0",
      insights: [
        "KPI Dashboard",
        "Business Growth Trends",
        "Market Analysis",
        "Strategic Planning",
      ],
    },
    {
      id: "operations",
      name: "Operations Analytics",
      icon: "⚙️",
      description:
        "Optimize processes, track efficiency metrics, manage supply chain, and improve operational performance.",
      color: "#03A9F4",
      insights: [
        "Process Efficiency",
        "Resource Utilization",
        "Supply Chain Metrics",
        "Production Analysis",
      ],
    },
    {
      id: "hr",
      name: "HR Analytics",
      icon: "👥",
      description:
        "Analyze workforce data, track employee performance, measure engagement, and optimize talent management.",
      color: "#FF5722",
      insights: [
        "Employee Turnover",
        "Performance Metrics",
        "Recruitment Analytics",
        "Workforce Planning",
      ],
    },
  ];

  const handleDepartmentSelect = (dept) => {
    setSelectedDepartment(dept.id);
    // Store department selection in localStorage
    localStorage.setItem("selectedDepartment", JSON.stringify(dept));

    // Navigate to upload page with department context
    setTimeout(() => {
      navigate("/upload", { state: { department: dept } });
    }, 300);
  };

  const handleLogout = () => {
    localStorage.removeItem("authToken");
    localStorage.removeItem("userData");
    localStorage.removeItem("selectedDepartment");
    navigate("/");
  };

  const userData = JSON.parse(localStorage.getItem("userData") || "{}");

  return (
    <div className="department-selection-page">
      {/* Header */}
      <header className="dept-header">
        <div className="dept-header-content">
          <div className="logo-section">
            <h1 className="logo-text">
              <span className="logo-data">Data</span>
              <span className="logo-sage">Sage</span>
            </h1>
          </div>

          <div className="user-section">
            <div className="user-info">
              <span className="user-name">{userData.name || "User"}</span>
              <span className="user-email">{userData.email || ""}</span>
            </div>
            <button className="logout-btn" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="dept-main-content">
        <motion.div
          className="dept-intro"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="dept-title">Choose Your Analytics Domain</h2>
          <p className="dept-subtitle">
            Select the department you want to analyze. I'll tailor insights and
            queries specifically for your domain.
          </p>
        </motion.div>

        <div className="departments-grid">
          {departments.map((dept, index) => (
            <motion.div
              key={dept.id}
              className={`department-card ${selectedDepartment === dept.id ? "selected" : ""}`}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              whileHover={{
                scale: 1.03,
                transition: { duration: 0.2 },
              }}
              onClick={() => handleDepartmentSelect(dept)}
            >
              <div className="dept-card-header">
                <span
                  className="dept-icon"
                  style={{
                    background: `linear-gradient(135deg, ${dept.color}22, ${dept.color}11)`,
                    border: `1px solid ${dept.color}33`,
                  }}
                >
                  {dept.icon}
                </span>
                <h3 className="dept-name">{dept.name}</h3>
              </div>

              <p className="dept-description">{dept.description}</p>

              <div className="dept-insights">
                <span className="insights-label">Key Insights:</span>
                <div className="insights-tags">
                  {dept.insights.slice(0, 3).map((insight, idx) => (
                    <span
                      key={idx}
                      className="insight-tag"
                      style={{
                        borderColor: `${dept.color}44`,
                        color: dept.color,
                      }}
                    >
                      {insight}
                    </span>
                  ))}
                </div>
              </div>

              <div
                className="dept-card-border"
                style={{ background: dept.color }}
              />
            </motion.div>
          ))}
        </div>

        {/* Info Section */}
        <motion.div
          className="dept-info-section"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8, duration: 0.6 }}
        >
          <div className="info-card">
            <div className="info-icon">💡</div>
            <div className="info-content">
              <h4>Smart Context</h4>
              <p>
                Your selection helps me provide department-specific insights and
                understand your queries better.
              </p>
            </div>
          </div>

          <div className="info-card">
            <div className="info-icon">🔄</div>
            <div className="info-content">
              <h4>Switch Anytime</h4>
              <p>
                You can change departments later to analyze data from different
                business perspectives.
              </p>
            </div>
          </div>

          <div className="info-card">
            <div className="info-icon">📊</div>
            <div className="info-content">
              <h4>Custom Analytics</h4>
              <p>
                Get tailored metrics, KPIs, and visualizations designed for your
                specific domain.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default DepartmentSelectionPage;
