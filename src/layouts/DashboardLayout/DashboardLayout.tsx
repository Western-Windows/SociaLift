import React, { type ReactNode } from 'react';
import { Link, useLocation } from 'react-router-dom';
import logo from '../../assets/SociaLift logo 5.svg';
import userAvatar from '../../assets/user-avatar.png';
import './DashboardLayout.css'; // Just the CSS now!
import { useNavigate } from 'react-router-dom';

interface DashboardLayoutProps {
  children: ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const location = useLocation();
  const navigate = useNavigate();

  return (
    <div className="layout-container">
      <header className="layout-header">
        <nav className="dashboard-nav">
          <button className="nav-logo" onClick={() => navigate('/')}>
            <img src={logo} alt="SociaLift" />
          </button>
          <div className="nav-links">
            <Link to="/home" className={location.pathname === "/home" ? "active" : "link-white"}>Home</Link>
            <Link to="/dashboard" className={location.pathname === "/dashboard" ? "active" : "link-white"}>Dashboard & Calendar</Link>
            <Link to="/post-gen" className={ location.pathname === "/post-gen" ? "active" : "link-white"}> Post Generation </Link>
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