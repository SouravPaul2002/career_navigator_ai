import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

const Navbar: React.FC = () => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  // Function to determine if a link is active
  const isActiveLink = (path: string) => {
    return location.pathname === path;
  };

  const handleLogout = () => {
    // Clear auth data
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
    // Redirect to login
    navigate("/login");
  };

  return (
    <aside className={`sidebar ${isSidebarCollapsed ? "collapsed" : ""}`}>
      <div className="sidebar-header">
        <div className="logo">
          <span className="logo-icon">📄</span>
          <span className={`logo-text ${isSidebarCollapsed ? "hidden" : ""}`}>
            Career Navigator
          </span>
        </div>
        <button
          className="toggle-btn"
          onClick={toggleSidebar}
          aria-label={
            isSidebarCollapsed ? "Expand sidebar" : "Collapse sidebar"
          }
        >
          {isSidebarCollapsed ? "→" : "←"}
        </button>
      </div>

      <nav className="nav-menu">
        <div className="nav-menu-top">
          <ul className="nav-menu-list">
            <li className="nav-item">
              <a
                href="/dashboard"
                className={`nav-link ${
                  isActiveLink("/dashboard") ? "active" : ""
                }`}
              >
                <span className="nav-icon">📊</span>
                <span
                  className={`nav-text ${isSidebarCollapsed ? "hidden" : ""}`}
                >
                  Dashboard
                </span>
              </a>
            </li>
            <li className="nav-item">
              <a
                href="/resume-analysis"
                className={`nav-link ${
                  isActiveLink("/resume-analysis") ? "active" : ""
                }`}
              >
                <span className="nav-icon">📋</span>
                <span
                  className={`nav-text ${isSidebarCollapsed ? "hidden" : ""}`}
                >
                  Resume Analysis
                </span>
              </a>
            </li>
            <li className="nav-item">
              <a
                href="/mock-interview"
                className={`nav-link ${
                  isActiveLink("/mock-interview") ? "active" : ""
                }`}
              >
                <span className="nav-icon">🎤</span>
                <span
                  className={`nav-text ${isSidebarCollapsed ? "hidden" : ""}`}
                >
                  Mock Interview
                </span>
              </a>
            </li>
            <li className="nav-item">
              <a
                href="/career-guidance"
                className={`nav-link ${
                  isActiveLink("/career-guidance") ? "active" : ""
                }`}
              >
                <span className="nav-icon">🧭</span>
                <span
                  className={`nav-text ${isSidebarCollapsed ? "hidden" : ""}`}
                >
                  Career Guidance
                </span>
              </a>
            </li>
          </ul>
        </div>

        <div className="nav-menu-bottom mt-auto">
          <ul className="nav-menu-list">
            <li className="nav-item">
              <button
                onClick={handleLogout}
                className="nav-link w-100 text-start border-0 bg-transparent"
                style={{ cursor: "pointer" }}
              >
                <span className="nav-icon">🚪</span>
                <span
                  className={`nav-text ${isSidebarCollapsed ? "hidden" : ""}`}
                >
                  Logout
                </span>
              </button>
            </li>
          </ul>
        </div>
      </nav>
    </aside>
  );
};

export default Navbar;
