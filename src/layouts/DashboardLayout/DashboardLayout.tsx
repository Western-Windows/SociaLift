import React, { type ReactNode } from 'react';
import logo from '../../assets/SociaLift logo 5.svg';
import userAvatar from '../../assets/user-avatar.png';
import mainBg from '../../assets/main-bg.png';
import './DashboardLayout.css';

interface DashboardLayoutProps {
  children: ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  return (
    <div className="layout-container">
      <header className="layout-header">
        <div className="nav-background">
          <img src={mainBg} alt="Nav Background" />
        </div>
        <nav className="dashboard-nav">
          <div className="nav-logo">
            <img src={logo} alt="SociaLift" />
          </div>
          <div className="nav-links">
            <a href="#home" className="link-white">Home</a>
            <a href="#dashboard" className="active">Dashboard & Calendar</a>
            <a href="#post-gen" className="link-white">Post Generation</a>
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
