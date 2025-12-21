import { useState } from "react";
import { useLocation } from "react-router-dom";

const Navbar: React.FC = () => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
  const location = useLocation();

  const toggleSidebar = () => {
    setIsSidebarCollapsed(!isSidebarCollapsed);
  };

  // Function to determine if a link is active
  const isActiveLink = (path: string) => {
    return location.pathname === path;
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
      </nav>
    </aside>
  );
};

export default Navbar;
