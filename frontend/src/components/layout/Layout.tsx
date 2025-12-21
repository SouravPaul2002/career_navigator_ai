import React from "react";
import Navbar from "../ui/Navbar";
import Header from "../ui/Header";

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="dashboard-layout">
      <Navbar />
      <main className="main-content">
        <div className="dashboard-container">
          <Header />
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
