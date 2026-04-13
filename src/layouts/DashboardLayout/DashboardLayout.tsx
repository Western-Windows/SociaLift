import React, { type ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import logo from '../../assets/SociaLift logo 5.svg';
import userAvatar from '../../assets/user-avatar.png';
import './DashboardLayout.css'; // Just the CSS now!

interface DashboardLayoutProps {
  children: ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const location = useLocation();

  return (
    <div className="layout-container">
      <header className="layout-header">
        <nav className="dashboard-nav">
          <div className="nav-logo">
            <img src={logo} alt="SociaLift" />
          </div>
          <div className="nav-links">
            <Link to="/home" className={location.pathname === "/home" ? "active" : "link-white"}>Home</Link>
            <Link to="/dashboard" className={location.pathname === "/dashboard" ? "active" : "link-white"}>Dashboard & Calendar</Link>
            <Link
              to="/post-gen1-0"
              className={
                ["/post-gen1-0", "/post-gen1-1a", "/post-gen1-1b", "/post-gen1-2"].includes(location.pathname)
                  ? "active"
                  : "link-white"
              }
            >
              Post Generation
            </Link>
          </div>
          <div className="nav-user">
            <img src={userAvatar} alt="User" />
          </div>
        </nav>
      </header>

      <main className="layout-content">
        {children}
      </main>
    </div>
  );
};