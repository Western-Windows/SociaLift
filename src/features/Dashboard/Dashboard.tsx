import React, { useState } from 'react';
import {
  ResponsiveContainer,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Area,
  AreaChart,
  PieChart,
  Pie,
  Cell
} from 'recharts';
import './Dashboard.css';

// Mock Data for Charts
const visitorData = [
  { name: 'Jan', postReactions: 120, mediaViews: 200, impressions: 300 },
  { name: 'Feb', postReactions: 130, mediaViews: 210, impressions: 320 },
  { name: 'Mar', postReactions: 150, mediaViews: 190, impressions: 310 },
  { name: 'Apr', postReactions: 180, mediaViews: 250, impressions: 380 },
  { name: 'May', postReactions: 170, mediaViews: 240, impressions: 350 },
  { name: 'Jun', postReactions: 240, mediaViews: 300, impressions: 390 },
  { name: 'Jul', postReactions: 250, mediaViews: 280, impressions: 400 },
  { name: 'Aug', postReactions: 230, mediaViews: 290, impressions: 360 },
  { name: 'Sep', postReactions: 280, mediaViews: 340, impressions: 430 },
  { name: 'Oct', postReactions: 310, mediaViews: 330, impressions: 460 },
  { name: 'Nov', postReactions: 350, mediaViews: 360, impressions: 480 },
  { name: 'Dec', postReactions: 380, mediaViews: 390, impressions: 500 },
];

const reactionTypes = [
  { type: 'HAHA', percentage: 20, color: '#E687D8' },
  { type: 'WOW', percentage: 15, color: '#0F2F65' },
  { type: 'Sad', percentage: 10, color: '#799CE5' },
  { type: 'Angry', percentage: 10, color: '#E687D8' },
  { type: 'Love', percentage: 25, color: '#0F2F65' },
  { type: 'Like', percentage: 20, color: '#799CE5' },
];

// New Weekly Data for the 3 Stat Cards
const engagementWeeklyData = [
  { week: 'W1', thisMonth: 800, lastMonth: 600 },
  { week: 'W2', thisMonth: 1200, lastMonth: 800 },
  { week: 'W3', thisMonth: 900, lastMonth: 750 },
  { week: 'W4', thisMonth: 1604, lastMonth: 854 },
];

const unfollowsWeeklyData = [
  { week: 'W1', thisMonth: 400, lastMonth: 500 },
  { week: 'W2', thisMonth: 300, lastMonth: 450 },
  { week: 'W3', thisMonth: 350, lastMonth: 300 },
  { week: 'W4', thisMonth: 190, lastMonth: 250 },
];

const followsWeeklyData = [
  { week: 'W1', thisMonth: 1000, lastMonth: 800 },
  { week: 'W2', thisMonth: 1500, lastMonth: 1100 },
  { week: 'W3', thisMonth: 1300, lastMonth: 1000 },
  { week: 'W4', thisMonth: 1830, lastMonth: 1300 },
];

// In a real app, these would likely have full date strings (e.g., '2026-04-15') 
// rather than just a day number to match against the exact month/year.
const calendarEventsData = [
  { date: 15, time: '11:00 AM', title: 'Seminar Demo', color: 'green' }
];

const monthNames = [
  "January", "February", "March", "April", "May", "June", 
  "July", "August", "September", "October", "November", "December"
];

export const Dashboard: React.FC = () => {
  // --- Dynamic Calendar State & Logic ---
  const [currentDate, setCurrentDate] = useState(new Date());

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const generateCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const firstDayOfMonth = new Date(year, month, 1).getDay(); // 0 (Sun) to 6 (Sat)
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const daysInPrevMonth = new Date(year, month, 0).getDate();

    const today = new Date();
    const isCurrentMonthThisMonth = today.getFullYear() === year && today.getMonth() === month;

    const days = [];

    // Fill in days from the previous month
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push({
        date: daysInPrevMonth - firstDayOfMonth + i + 1,
        isCurrentMonth: false,
        isToday: false,
      });
    }

    // Fill in days for the current month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push({
        date: i,
        isCurrentMonth: true,
        isToday: isCurrentMonthThisMonth && i === today.getDate(),
      });
    }

    // Fill in days for the next month to complete the grid (ensure 35 or 42 cells total)
    const totalCells = days.length > 35 ? 42 : 35;
    const extraDays = totalCells - days.length;

    for (let i = 1; i <= extraDays; i++) {
      days.push({
        date: i,
        isCurrentMonth: false,
        isToday: false,
      });
    }

    return days;
  };

  const calendarDays = generateCalendarDays();

  return (
    <div className="dashboard-container">
      <main className="dashboard-main">
        {/* Two Column Layout */}
        <div className="content-grid">
          {/* Left Column */}
          <div className="left-panel">
            {/* Visitor Insights */}
            <div className="card visitor-insights">
              <div className="card-header">
                <h2>Visitor Insights</h2>
              </div>

              <div className="chart-legend">
                <span className="legend-item"><span className="dot impressions" />Impressions</span>
                <span className="legend-item"><span className="dot views" />Media views</span>
                <span className="legend-item"><span className="dot reactions" />Post Reactions</span>
              </div>

              <div className="chart-container">
                <ResponsiveContainer width="100%" height={280}>
                  <AreaChart data={visitorData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorImpressions" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#4318FF" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#4318FF" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorViews" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#39B8FF" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#39B8FF" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorReactions" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#E9EDF7" stopOpacity={0.8} />
                        <stop offset="95%" stopColor="#E9EDF7" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#A3AED0', fontSize: 12 }} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#A3AED0', fontSize: 12 }} />
                    <Tooltip
                      contentStyle={{ borderRadius: '10px', border: 'none', boxShadow: '0px 10px 20px rgba(0,0,0,0.05)' }}
                    />
                    <Area type="monotone" dataKey="impressions" stroke="#4318FF" strokeWidth={3} fillOpacity={1} fill="url(#colorImpressions)" />
                    <Area type="monotone" dataKey="mediaViews" stroke="#39B8FF" strokeWidth={3} fillOpacity={1} fill="url(#colorViews)" />
                    <Area type="monotone" dataKey="postReactions" stroke="#CBD5E1" strokeWidth={3} fillOpacity={1} fill="url(#colorReactions)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Reactions Chart */}
            <div className="card Total-reactions">
              <div className="reactions-header">
                <h2>Total Reactions</h2>
              </div>
              <div className="reactions-pie-wrapper" style={{ display: 'flex', justifyContent: 'center', marginBottom: '24px', position: 'relative' }}>

                <div className="pie-center-label">
                  <span className="pie-center-title">Total Reactions</span>
                  <span className="pie-center-value">150</span>
                </div>

                <PieChart width={250} height={250}>
                  <Pie
                    data={reactionTypes}
                    cx="50%"
                    cy="50%"
                    innerRadius={80}
                    outerRadius={115}
                    paddingAngle={6}
                    cornerRadius={12}
                    dataKey="percentage"
                    nameKey="type"
                    stroke="none"
                  >
                    {reactionTypes.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => `${value}%`}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0px 4px 10px rgba(0,0,0,0.1)' }}
                  />
                </PieChart>
              </div>
              <div className="reactions-legend">
                {reactionTypes.map((rt) => (
                  <div key={rt.type} className="reaction-stat">
                    <span className="dot" style={{ backgroundColor: rt.color }} />
                    <span className="type">{rt.type}</span>
                    <span className="percent">{rt.percentage}%</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column */}
          <div className="right-panel">
            <div className="card calendar-widget">
              <div className="calendar-header">
                <div className="calendar-nav">
                  <button className="nav-btn" onClick={handlePrevMonth}>{'<'}</button>
                  <h3>{monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}</h3>
                  <button className="nav-btn" onClick={handleNextMonth}>{'>'}</button>
                </div>
                <div className="calendar-filters">
                  <button>Month</button>
                  <button className="active">Week</button>
                  <button>Day</button>
                  <button>List</button>
                </div>
              </div>

              <div className="calendar-grid">
                {/* Standardized Sunday -> Saturday layout to match JavaScript's native date mapping */}
                <div className="days-row">
                  <span>Sun</span><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span>
                </div>
                <div className="dates-grid">
                  {calendarDays.map((dayObj, i) => {
                    // Find events for this date (Note: simplified to just match the day number)
                    const eventsForDay = calendarEventsData.filter(e => e.date === dayObj.date && dayObj.isCurrentMonth);

                    return (
                      <div 
                        key={i} 
                        className={`date-cell ${!dayObj.isCurrentMonth ? 'other-month' : ''} ${dayObj.isToday ? 'active' : ''}`}
                      >
                        <span className="date-number">{dayObj.date}</span>
                        <div className="cell-events">
                          {eventsForDay.map((evt, idx) => (
                            <div key={idx} className={`mini-event event-${evt.color}`}>
                              {evt.time} {evt.title}
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Header Cards */}
        <section className="stats-row">
          {/* Engagement Card */}
          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-title-section">
                <h3>Engagement</h3>
              </div>
              <div className="stat-numbers-compact">
                <div className="stat-number-item">
                  <span className="amount">4,504</span>
                  <span className="label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#799CE5' }} />
                    This Month
                  </span>
                </div>
                <div className="stat-number-item">
                  <span className="amount previous">3,004</span>
                  <span className="label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#E687D8' }} />
                    Last Month
                  </span>
                </div>
              </div>
            </div>
            <div className="stat-sparkline-large">
              <ResponsiveContainer width="100%" height={120}>
                <AreaChart data={engagementWeeklyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="week" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#A3AED0' }} dy={5} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#A3AED0' }} />
                  <Tooltip
                    cursor={{ stroke: 'rgba(0,0,0,0.05)', strokeWidth: 2 }}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0px 4px 10px rgba(0,0,0,0.1)' }}
                  />
                  <Area type="monotone" dataKey="thisMonth" name="This Month" stroke="#799CE5" fill="#799CE5" fillOpacity={0.1} strokeWidth={3} />
                  <Area type="monotone" dataKey="lastMonth" name="Last Month" stroke="#E687D8" fill="none" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Unfollows Card */}
          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-title-section">
                <h3>Unfollows</h3>
              </div>
              <div className="stat-numbers-compact">
                <div className="stat-number-item">
                  <span className="amount">1,240</span>
                  <span className="label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#799CE5' }} />
                    This Month
                  </span>
                </div>
                <div className="stat-number-item">
                  <span className="amount previous">1,500</span>
                  <span className="label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#E687D8' }} />
                    Last Month
                  </span>
                </div>
              </div>
            </div>
            <div className="stat-sparkline-large">
              <ResponsiveContainer width="100%" height={120}>
                <AreaChart data={unfollowsWeeklyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="week" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#A3AED0' }} dy={5} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#A3AED0' }} />
                  <Tooltip
                    cursor={{ stroke: 'rgba(0,0,0,0.05)', strokeWidth: 2 }}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0px 4px 10px rgba(0,0,0,0.1)' }}
                  />
                  <Area type="monotone" dataKey="thisMonth" name="This Month" stroke="#799CE5" fill="#799CE5" fillOpacity={0.1} strokeWidth={3} />
                  <Area type="monotone" dataKey="lastMonth" name="Last Month" stroke="#E687D8" fill="none" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Follows Card */}
          <div className="stat-card">
            <div className="stat-card-header">
              <div className="stat-title-section">
                <h3>Follows</h3>
              </div>
              <div className="stat-numbers-compact">
                <div className="stat-number-item">
                  <span className="amount">5,630</span>
                  <span className="label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#799CE5' }} />
                    This Month
                  </span>
                </div>
                <div className="stat-number-item">
                  <span className="amount previous">4,200</span>
                  <span className="label" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#E687D8' }} />
                    Last Month
                  </span>
                </div>
              </div>
            </div>
            <div className="stat-sparkline-large">
              <ResponsiveContainer width="100%" height={120}>
                <AreaChart data={followsWeeklyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <XAxis dataKey="week" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#A3AED0' }} dy={5} />
                  <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#A3AED0' }} />
                  <Tooltip
                    cursor={{ stroke: 'rgba(0,0,0,0.05)', strokeWidth: 2 }}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0px 4px 10px rgba(0,0,0,0.1)' }}
                  />
                  <Area type="monotone" dataKey="thisMonth" name="This Month" stroke="#799CE5" fill="#799CE5" fillOpacity={0.1} strokeWidth={3} />
                  <Area type="monotone" dataKey="lastMonth" name="Last Month" stroke="#E687D8" fill="none" strokeWidth={2} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
};