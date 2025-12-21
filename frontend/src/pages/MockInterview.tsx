import React from "react";
import { Link } from "react-router-dom";

const MockInterview: React.FC = () => {
  return (
    <div className="container min-vh-100 d-flex flex-column align-items-center justify-content-center text-center">
      <div
        className="p-5 rounded-4 shadow-lg"
        style={{
          background: "linear-gradient(145deg, #1e1e2f, #2a2a40)",
          color: "#fff",
          maxWidth: "600px",
        }}
      >
        <div className="mb-4">
          <i className="bi bi-robot display-1 text-primary"></i>
        </div>
        <h1 className="fw-bold mb-3">AI Mock Interview Simulator</h1>
        <p className="lead text-muted mb-4">
          Practice your interview skills with our AI-powered bot. Get real-time
          feedback on your tone, clarity, and technical accuracy.
        </p>
        <div className="badge bg-warning text-dark px-4 py-2 rounded-pill fs-5 mb-4">
          <i className="bi bi-hourglass-split me-2"></i>Coming Soon
        </div>
        <br />
        <Link
          to="/dashboard"
          className="btn btn-outline-light rounded-pill px-4"
        >
          Back to Dashboard
        </Link>
      </div>
    </div>
  );
};

export default MockInterview;
