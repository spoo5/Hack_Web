import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import axios from "axios";
import "./AuthPages.css";

const SignupPage = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    company: "",
    password: "",
    confirmPassword: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
    setError("");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    setError("");

    try {
      // Call backend API
      const response = await axios.post("/api/auth/signup", {
        name: formData.name,
        email: formData.email,
        company: formData.company,
        password: formData.password,
      });

      // Store auth data
      localStorage.setItem("authToken", response.data.token);
      localStorage.setItem("userData", JSON.stringify(response.data.user));

      // Navigate to department selection
      setTimeout(() => {
        navigate("/departments");
      }, 500);
    } catch (err) {
      setError(
        err.response?.data?.detail || "Signup failed. Please try again.",
      );
      setLoading(false);
    }
  };

  const handleGoogleSignup = async () => {
    setLoading(true);
    try {
      // In production, this would use Google OAuth SDK
      const mockGoogleData = {
        email: "user@company.com",
        name: "Demo User",
      };

      const response = await axios.post("/api/auth/google", mockGoogleData);

      localStorage.setItem("authToken", response.data.token);
      localStorage.setItem("userData", JSON.stringify(response.data.user));
      navigate("/departments");
    } catch (err) {
      setError("Google signup failed. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-bg-gradient"></div>
      <div className="auth-bg-grid"></div>

      {/* Navigation */}
      <nav className="auth-nav">
        <div className="nav-logo" onClick={() => navigate("/")}>
          <span className="logo-icon">🧠</span>
          <span className="logo-text">
            Data<span className="text-gold">Sage</span>
          </span>
        </div>
      </nav>

      <div className="auth-container">
        <motion.div
          className="auth-card glass-card"
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Header */}
          <div className="auth-header">
            <h1 className="auth-title">Get Started Free</h1>
            <p className="auth-subtitle">Create your DataSage account</p>
          </div>

          {/* Google Sign Up */}
          <button
            className="btn-google"
            onClick={handleGoogleSignup}
            disabled={loading}
          >
            <svg className="google-icon" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            {loading ? "Creating account..." : "Continue with Google"}
          </button>

          {/* Divider */}
          <div className="auth-divider">
            <span>or create with email</span>
          </div>

          {/* Signup Form */}
          <form onSubmit={handleSubmit} className="auth-form">
            {error && (
              <motion.div
                className="error-message"
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
              >
                ⚠️ {error}
              </motion.div>
            )}

            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                name="name"
                className="input-field"
                placeholder="John Doe"
                value={formData.name}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Work Email</label>
              <input
                type="email"
                name="email"
                className="input-field"
                placeholder="you@company.com"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Company Name</label>
              <input
                type="text"
                name="company"
                className="input-field"
                placeholder="Your Company Inc."
                value={formData.company}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label">Password</label>
              <input
                type="password"
                name="password"
                className="input-field"
                placeholder="Create a strong password"
                value={formData.password}
                onChange={handleChange}
                required
                minLength={8}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Confirm Password</label>
              <input
                type="password"
                name="confirmPassword"
                className="input-field"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={handleChange}
                required
              />
            </div>

            <div className="form-options">
              <label className="checkbox-label">
                <input type="checkbox" required />
                <span>
                  I agree to the{" "}
                  <Link to="/terms" className="link-text">
                    Terms
                  </Link>{" "}
                  and{" "}
                  <Link to="/privacy" className="link-text">
                    Privacy Policy
                  </Link>
                </span>
              </label>
            </div>

            <button
              type="submit"
              className="btn-primary btn-full"
              disabled={loading}
            >
              {loading ? "Creating account..." : "Create Account"}
            </button>
          </form>

          {/* Footer */}
          <div className="auth-footer">
            <p>
              Already have an account?{" "}
              <Link to="/login" className="link-text">
                Sign in
              </Link>
            </p>
          </div>
        </motion.div>

        {/* Side Info */}
        <motion.div
          className="auth-info"
          initial={{ opacity: 0, x: 30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
        >
          <div className="info-content glass-card">
            <div className="info-icon">🚀</div>
            <h3 className="info-title">Start Your Free Trial</h3>
            <p className="info-text">
              Get started with DataSage today. No credit card required.
            </p>
            <div className="info-features">
              <div className="info-feature">
                <span className="feature-check">✓</span>
                <span>14-day free trial</span>
              </div>
              <div className="info-feature">
                <span className="feature-check">✓</span>
                <span>No credit card required</span>
              </div>
              <div className="info-feature">
                <span className="feature-check">✓</span>
                <span>Cancel anytime</span>
              </div>
              <div className="info-feature">
                <span className="feature-check">✓</span>
                <span>24/7 customer support</span>
              </div>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default SignupPage;
