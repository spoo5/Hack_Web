import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import axios from "axios";
import "./InsightsTab.css";

const InsightsTab = ({ datasetInfo, department }) => {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (datasetInfo) {
      generateInsights();
    }
  }, [datasetInfo, department]);

  const generateInsights = async () => {
    setLoading(true);

    // Generate department-specific insights based on dataset schema
    const generatedInsights = [];

    if (!datasetInfo?.schema) {
      setLoading(false);
      return;
    }

    const { numeric_columns, categorical_columns, date_columns } =
      datasetInfo.schema;

    // Department-specific insights
    if (department) {
      switch (department.id) {
        case "sales":
          generatedInsights.push({
            title: "Revenue Analysis Opportunity",
            description:
              "Your dataset contains numeric columns that could represent revenue metrics. Consider analyzing trends over time and by customer segments.",
            type: "opportunity",
            icon: "💰",
            suggestedQueries: [
              "What is the total revenue by region?",
              "Show me revenue trends over time",
              "Which customer segment generates the most revenue?",
            ],
          });
          if (date_columns && date_columns.length > 0) {
            generatedInsights.push({
              title: "Time-Based Sales Patterns",
              description: `Detected ${date_columns.length} date column(s). You can analyze seasonal patterns, monthly trends, and year-over-year growth.`,
              type: "insight",
              icon: "📅",
              suggestedQueries: [
                "What are the sales trends by month?",
                "Show me year-over-year growth",
                "Which quarter had the highest sales?",
              ],
            });
          }
          break;

        case "marketing":
          generatedInsights.push({
            title: "Campaign Performance Metrics",
            description:
              "Analyze campaign effectiveness by tracking conversions, engagement rates, and ROI across different channels.",
            type: "opportunity",
            icon: "🎯",
            suggestedQueries: [
              "What is the conversion rate by channel?",
              "Which campaign has the best ROI?",
              "Show me customer acquisition cost trends",
            ],
          });
          if (categorical_columns && categorical_columns.length > 0) {
            generatedInsights.push({
              title: "Segmentation Opportunities",
              description: `Found ${categorical_columns.length} categorical columns. Use these for customer segmentation and targeted marketing analysis.`,
              type: "insight",
              icon: "🎨",
              suggestedQueries: [
                "Show me customer segments by behavior",
                "Which segment has the highest engagement?",
                "Compare conversion rates across segments",
              ],
            });
          }
          break;

        case "finance":
          generatedInsights.push({
            title: "Financial Health Indicators",
            description:
              "Track key financial metrics like cash flow, profit margins, and cost efficiency to monitor business health.",
            type: "opportunity",
            icon: "💵",
            suggestedQueries: [
              "What is the total cost breakdown?",
              "Show me profit margin trends",
              "Which category has the highest expenses?",
            ],
          });
          if (numeric_columns && numeric_columns.length >= 2) {
            generatedInsights.push({
              title: "Cost-Benefit Analysis",
              description: `With ${numeric_columns.length} numeric columns, you can perform detailed financial analysis and variance reports.`,
              type: "insight",
              icon: "📊",
              suggestedQueries: [
                "Compare budget vs actual spending",
                "What is the ROI by project?",
                "Show me cost variance analysis",
              ],
            });
          }
          break;

        case "business":
          generatedInsights.push({
            title: "Strategic KPI Dashboard",
            description:
              "Monitor high-level business metrics including growth rates, market share, and operational efficiency.",
            type: "opportunity",
            icon: "📈",
            suggestedQueries: [
              "What is the overall growth rate?",
              "Show me key performance indicators",
              "Compare performance across business units",
            ],
          });
          break;

        case "operations":
          generatedInsights.push({
            title: "Operational Efficiency",
            description:
              "Identify bottlenecks, optimize resource allocation, and improve process efficiency metrics.",
            type: "opportunity",
            icon: "⚙️",
            suggestedQueries: [
              "What is the resource utilization rate?",
              "Show me process efficiency metrics",
              "Which operation has the highest cost?",
            ],
          });
          break;

        case "hr":
          generatedInsights.push({
            title: "Workforce Analytics",
            description:
              "Analyze employee performance, retention rates, and identify trends in workforce data.",
            type: "opportunity",
            icon: "👥",
            suggestedQueries: [
              "What is the employee turnover rate?",
              "Show me performance metrics by department",
              "Which team has the highest retention?",
            ],
          });
          break;
      }
    }

    // Generic dataset insights
    if (numeric_columns && numeric_columns.length > 0) {
      generatedInsights.push({
        title: "Numeric Column Analysis",
        description: `Your dataset has ${numeric_columns.length} numeric columns. You can perform aggregations, statistical analysis, and trend identification.`,
        type: "info",
        icon: "🔢",
        columns: numeric_columns.slice(0, 5),
      });
    }

    if (categorical_columns && categorical_columns.length > 0) {
      generatedInsights.push({
        title: "Categorical Breakdowns",
        description: `Found ${categorical_columns.length} categorical columns perfect for grouping and segmentation analysis.`,
        type: "info",
        icon: "🏷️",
        columns: categorical_columns.slice(0, 5),
      });
    }

    // Data quality insight
    generatedInsights.push({
      title: "Data Quality",
      description: `Dataset contains ${datasetInfo.row_count?.toLocaleString()} rows across ${datasetInfo.column_count} columns. All queries are grounded in actual data with zero hallucination.`,
      type: "success",
      icon: "✅",
    });

    setInsights(generatedInsights);
    setLoading(false);
  };

  const getInsightCardClass = (type) => {
    const baseClass = "insight-card";
    switch (type) {
      case "opportunity":
        return `${baseClass} opportunity`;
      case "insight":
        return `${baseClass} insight`;
      case "success":
        return `${baseClass} success`;
      default:
        return `${baseClass} info`;
    }
  };

  if (loading) {
    return (
      <div className="insights-loading">
        <div className="spinner-large"></div>
        <p>Generating insights...</p>
      </div>
    );
  }

  return (
    <div className="insights-tab">
      <div className="insights-header">
        <h2 className="insights-title">
          <span className="title-icon">💡</span>
          AI-Powered Insights
        </h2>
        <p className="insights-subtitle">
          Automatically generated insights based on your{" "}
          {department?.name || "data"} and dataset structure
        </p>
      </div>

      <div className="insights-grid">
        {insights.map((insight, index) => (
          <motion.div
            key={index}
            className={getInsightCardClass(insight.type)}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1, duration: 0.4 }}
          >
            <div className="insight-header">
              <span className="insight-icon">{insight.icon}</span>
              <h3 className="insight-title">{insight.title}</h3>
            </div>

            <p className="insight-description">{insight.description}</p>

            {insight.suggestedQueries && (
              <div className="suggested-queries">
                <span className="queries-label">Try asking:</span>
                {insight.suggestedQueries.map((query, idx) => (
                  <div key={idx} className="query-suggestion">
                    <span className="query-bullet">→</span>
                    <span className="query-text">{query}</span>
                  </div>
                ))}
              </div>
            )}

            {insight.columns && (
              <div className="column-list">
                <span className="columns-label">Available columns:</span>
                <div className="column-tags">
                  {insight.columns.map((col, idx) => (
                    <span key={idx} className="column-tag">
                      {col}
                    </span>
                  ))}
                  {insight.columns.length === 5 && (
                    <span className="column-tag more">+more</span>
                  )}
                </div>
              </div>
            )}
          </motion.div>
        ))}
      </div>

      <div className="insights-footer">
        <div className="footer-card">
          <div className="footer-icon">🤖</div>
          <div className="footer-content">
            <h4>How It Works</h4>
            <p>
              Insights are generated by analyzing your dataset's structure,
              column types, and your selected department focus. Ask any question
              to get precise, data-backed answers.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default InsightsTab;
