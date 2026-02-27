import { useState, useRef, useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import "./LandingPage.css";

const LandingPage = ({ onDatasetLoaded }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [preview, setPreview] = useState(null);
  const [error, setError] = useState(null);
  const [selectedDepartment, setSelectedDepartment] = useState(null);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Get department from navigation state or localStorage
    const dept =
      location.state?.department ||
      JSON.parse(localStorage.getItem("selectedDepartment") || "null");
    setSelectedDepartment(dept);
  }, [location]);

  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.name.endsWith(".csv")) {
      setFile(droppedFile);
      setError(null);
    } else {
      setError("Please upload a valid CSV file");
    }
  };

  const handleFileSelect = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.name.endsWith(".csv")) {
      setFile(selectedFile);
      setError(null);
    } else {
      setError("Please upload a valid CSV file");
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError("Please select a file first");
      return;
    }

    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("/api/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      const data = response.data;
      setPreview(data);
      onDatasetLoaded(data);

      // Navigate to dashboard after short delay
      setTimeout(() => {
        navigate("/dashboard");
      }, 1500);
    } catch (err) {
      console.error("Upload error:", err);
      setError(
        err.response?.data?.detail ||
          "Failed to upload file. Please try again.",
      );
      setUploading(false);
    }
  };

  return (
    <div className="landing-page">
      {/* Animated background */}
      <div className="bg-gradient"></div>
      <div className="bg-grid"></div>

      {/* Department Header */}
      {selectedDepartment && (
        <div className="dept-info-header">
          <button className="back-btn" onClick={() => navigate("/departments")}>
            ← Back to Departments
          </button>
          <div className="current-dept">
            <span className="dept-icon-small">{selectedDepartment.icon}</span>
            <span className="dept-name-small">{selectedDepartment.name}</span>
          </div>
        </div>
      )}

      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="landing-content"
        >
          {/* Header */}
          <div className="header">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
              className="logo-badge"
            >
              <span className="logo-icon">🧠</span>
            </motion.div>

            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="main-title"
            >
              Data<span className="text-gold">Sage</span>
            </motion.h1>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="subtitle"
            >
              Conversational Data Intelligence Platform
            </motion.p>

            <motion.p
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.7 }}
              className="description"
            >
              Upload your dataset. Ask questions in plain English. Get
              data-backed, hallucination-free answers.
            </motion.p>
          </div>

          {/* Feature Pills */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="feature-pills"
          >
            <div className="pill">
              <span className="pill-icon">✓</span>
              Dataset Agnostic
            </div>
            <div className="pill">
              <span className="pill-icon">✓</span>
              Zero Hallucination
            </div>
            <div className="pill">
              <span className="pill-icon">✓</span>
              Explainable AI
            </div>
            <div className="pill">
              <span className="pill-icon">✓</span>
              Auto Visualization
            </div>
          </motion.div>

          {/* Upload Section */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 1 }}
            className="upload-section"
          >
            {!preview ? (
              <>
                <div
                  className={`upload-dropzone ${isDragging ? "dragging" : ""} ${file ? "has-file" : ""}`}
                  onDragEnter={handleDragEnter}
                  onDragLeave={handleDragLeave}
                  onDragOver={handleDragOver}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current?.click()}
                >
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    onChange={handleFileSelect}
                    style={{ display: "none" }}
                  />

                  <div className="dropzone-content">
                    {uploading ? (
                      <>
                        <div className="spinner"></div>
                        <p className="dropzone-text">Analyzing dataset...</p>
                      </>
                    ) : file ? (
                      <>
                        <div className="file-icon">📊</div>
                        <p className="dropzone-text">{file.name}</p>
                        <p className="dropzone-subtext">
                          {(file.size / 1024).toFixed(2)} KB
                        </p>
                      </>
                    ) : (
                      <>
                        <div className="upload-icon">☁️</div>
                        <p className="dropzone-text">
                          {isDragging
                            ? "Drop your CSV here"
                            : "Drag & drop your CSV file here"}
                        </p>
                        <p className="dropzone-subtext">or click to browse</p>
                      </>
                    )}
                  </div>
                </div>

                {error && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="error-message"
                  >
                    ⚠️ {error}
                  </motion.div>
                )}

                {file && !uploading && (
                  <motion.button
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="btn-primary upload-btn"
                    onClick={handleUpload}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                  >
                    Analyze Dataset →
                  </motion.button>
                )}
              </>
            ) : (
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                className="preview-section glass-card"
              >
                <div className="preview-header">
                  <div className="success-icon">✓</div>
                  <h3>Dataset Loaded Successfully!</h3>
                </div>

                <div className="dataset-stats">
                  <div className="stat-item">
                    <div className="stat-value">
                      {preview.row_count.toLocaleString()}
                    </div>
                    <div className="stat-label">Rows</div>
                  </div>
                  <div className="stat-divider"></div>
                  <div className="stat-item">
                    <div className="stat-value">{preview.column_count}</div>
                    <div className="stat-label">Columns</div>
                  </div>
                </div>

                <div className="preview-data">
                  <h4>Schema Preview:</h4>
                  <div className="column-list">
                    {preview.columns.slice(0, 8).map((col, idx) => (
                      <div key={idx} className="column-tag">
                        {col}
                      </div>
                    ))}
                    {preview.columns.length > 8 && (
                      <div className="column-tag more">
                        +{preview.columns.length - 8} more
                      </div>
                    )}
                  </div>
                </div>

                <p className="redirect-text">Redirecting to dashboard...</p>
              </motion.div>
            )}
          </motion.div>

          {/* Footer */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
            className="landing-footer"
          >
            <p className="footer-text">
              Powered by FastAPI, Pandas, and deterministic computation
            </p>
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
};

export default LandingPage;
