import { motion } from "framer-motion";
import "./ConfidenceComponent.css";

const ConfidenceComponent = ({ score }) => {
  const getConfidenceLevel = (score) => {
    if (score >= 90)
      return { level: "high", label: "High Confidence", color: "#4ECDC4" };
    if (score >= 70)
      return { level: "medium", label: "Medium Confidence", color: "#FFB347" };
    return { level: "low", label: "Low Confidence", color: "#FF6B6B" };
  };

  const confidence = getConfidenceLevel(score);

  return (
    <motion.div
      className={`confidence-component confidence-${confidence.level}`}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay: 0.2 }}
    >
      <div className="confidence-header">
        <span className="confidence-icon">
          {confidence.level === "high"
            ? "✓"
            : confidence.level === "medium"
              ? "⚡"
              : "⚠"}
        </span>
        <span className="confidence-label">{confidence.label}</span>
      </div>

      <div className="confidence-bar-container">
        <motion.div
          className="confidence-bar"
          initial={{ width: 0 }}
          animate={{ width: `${score}%` }}
          transition={{ duration: 1, delay: 0.3, ease: "easeOut" }}
          style={{ backgroundColor: confidence.color }}
        />
      </div>

      <div className="confidence-score">
        <span className="score-value">{score.toFixed(1)}%</span>
        <span className="score-description">
          {confidence.level === "high" &&
            "This answer is highly reliable and computed from verified data."}
          {confidence.level === "medium" &&
            "This answer is reliable but may have some assumptions."}
          {confidence.level === "low" &&
            "This answer may require additional validation."}
        </span>
      </div>
    </motion.div>
  );
};

export default ConfidenceComponent;
