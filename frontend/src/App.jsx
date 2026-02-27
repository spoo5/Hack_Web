import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { useState } from "react";
import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import DepartmentSelectionPage from "./pages/DepartmentSelectionPage";
import LandingPage from "./pages/LandingPage";
import DashboardPage from "./pages/DashboardPage";

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const authToken = localStorage.getItem("authToken");
  return authToken ? children : <Navigate to="/login" replace />;
};

function App() {
  const [datasetInfo, setDatasetInfo] = useState(null);

  return (
    <Router>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<HomePage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Protected Routes */}
        <Route
          path="/departments"
          element={
            <ProtectedRoute>
              <DepartmentSelectionPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="/upload"
          element={
            <ProtectedRoute>
              <LandingPage onDatasetLoaded={setDatasetInfo} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <DashboardPage datasetInfo={datasetInfo} />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;
