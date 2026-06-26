import React, { useState, useEffect } from 'react';
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

// Fallback Mock Data (used if backend hasn't populated data yet)
const fallbackVisitorData = [
  { name: 'Jan', postReactions: 120, mediaViews: 200, impressions: 300 },
  { name: 'Feb', postReactions: 130, mediaViews: 210, impressions: 320 },
  { name: 'Mar', postReactions: 150, mediaViews: 190, impressions: 310 },
  { name: 'Apr', postReactions: 180, mediaViews: 250, impressions: 380 },
  { name: 'May', postReactions: 170, mediaViews: 240, impressions: 350 },
  { name: 'Jun', postReactions: 240, mediaViews: 300, impressions: 390 },
];

const fallbackReactionTypes = [
  { type: 'HAHA', percentage: 20, color: '#E687D8' },
  { type: 'WOW', percentage: 15, color: '#0F2F65' },
  { type: 'Sad', percentage: 10, color: '#799CE5' },
  { type: 'Angry', percentage: 10, color: '#E687D8' },
  { type: 'Love', percentage: 25, color: '#0F2F65' },
  { type: 'Like', percentage: 20, color: '#799CE5' },
];

const fallbackEngagementData = [
  { week: 'W1', thisMonth: 800, lastMonth: 600 },
  { week: 'W2', thisMonth: 1200, lastMonth: 800 },
  { week: 'W3', thisMonth: 900, lastMonth: 750 },
  { week: 'W4', thisMonth: 1604, lastMonth: 854 },
];

// Formatting helper for standardizing event dates (YYYY-MM-DD)
const formatDateString = (date: Date) => {
  const offset = date.getTimezoneOffset()
  const adjustedDate = new Date(date.getTime() - (offset*60*1000))
  return adjustedDate.toISOString().split('T')[0]
}

const monthNames = [
  "January", "February", "March", "April", "May", "June", 
  "July", "August", "September", "October", "November", "December"
];

export const Dashboard: React.FC = () => {
  // --- Backend Data States ---
  const [visitorData, setVisitorData] = useState(fallbackVisitorData);
  const [reactionTypes, setReactionTypes] = useState(fallbackReactionTypes);
  const [engagementWeeklyData, setEngagementWeeklyData] = useState(fallbackEngagementData);
  const [unfollowsWeeklyData, setUnfollowsWeeklyData] = useState(fallbackEngagementData);
  const [followsWeeklyData, setFollowsWeeklyData] = useState(fallbackEngagementData);
  const [calendarEventsData, setCalendarEventsData] = useState<any[]>([]);
  
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // --- Dynamic Calendar State ---
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date | null>(new Date());

  // --- Fetch Backend Insights ---
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const userId = localStorage.getItem('user_id');
        if (!userId) {
          throw new Error("User not authenticated.");
        }

        // Adjust base URL to match your FastAPI server configuration (assuming 8000 default)
        const response = await fetch(`http://localhost:8000/api/dashboard/insights?user_id=${userId}`);
        
        if (!response.ok) {
          throw new Error("Failed to fetch dashboard insights");
        }

        const result = await response.json();
        const data = result.data;
        
        // Map backend data to frontend states if available, else keep fallback
        if (data && data.visitorData) setVisitorData(data.visitorData);
        if (data && data.reactionTypes) setReactionTypes(data.reactionTypes);
        if (data && data.engagementData) setEngagementWeeklyData(data.engagementData);
        if (data && data.calendarEvents) setCalendarEventsData(data.calendarEvents);

      } catch (err: any) {
        console.error("Dashboard Fetch Error:", err);
        setError(err.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // --- Calendar Logic ---
  const handlePrevMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  const handleNextMonth = () => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));

  const generateCalendarDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const firstDayOfMonth = new Date(year, month, 1).getDay(); 
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const daysInPrevMonth = new Date(year, month, 0).getDate();

    const today = new Date();
    const isCurrentMonthThisMonth = today.getFullYear() === year && today.getMonth() === month;

    const days = [];

    // Fill previous month padding
    for (let i = 0; i < firstDayOfMonth; i++) {
      const dayNum = daysInPrevMonth - firstDayOfMonth + i + 1;
      days.push({
        date: dayNum,
        fullDate: new Date(year, month - 1, dayNum),
        isCurrentMonth: false,
        isToday: false,
      });
    }

    // Fill current month
    for (let i = 1; i <= daysInMonth; i++) {
      days.push({
        date: i,
        fullDate: new Date(year, month, i),
        isCurrentMonth: true,
        isToday: isCurrentMonthThisMonth && i === today.getDate(),
      });
    }

    // Fill next month padding
    const totalCells = days.length > 35 ? 42 : 35;
    const extraDays = totalCells - days.length;

    for (let i = 1; i <= extraDays; i++) {
      days.push({
        date: i,
        fullDate: new Date(year, month + 1, i),
        isCurrentMonth: false,
        isToday: false,
      });
    }

    return days;
  };

  const calendarDays = generateCalendarDays();

  // Highlight selected cell
  const isSelected = (dayDate: Date) => {
    if (!selectedDate) return false;
    return formatDateString(dayDate) === formatDateString(selectedDate);
  }

  return (
    <div className="dashboard-container">
      {/* Optional: Add a lightweight error/loading banner at the top */}
      {error && <div style={{ color: 'red', padding: '10px', textAlign: 'center' }}>Warning: Using cached data. {error}</div>}
      
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
                    <Tooltip contentStyle={{ borderRadius: '10px', border: 'none', boxShadow: '0px 10px 20px rgba(0,0,0,0.05)' }} />
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
                  <span className="pie-center-value">
                    {/* Sum up all reactions dynamically */}
                    {reactionTypes.reduce((acc, curr) => acc + curr.percentage, 0)}%
                  </span>
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

          {/* Right Column: Calendar */}
          <div className="right-panel">
            <div className="card calendar-widget">
              <div className="calendar-header">
                <div className="calendar-nav">
                  <button className="nav-btn" onClick={handlePrevMonth}>{'<'}</button>
                  <h3>{monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}</h3>
                  <button className="nav-btn" onClick={handleNextMonth}>{'>'}</button>
                </div>
              </div>

              <div className="calendar-grid">
                <div className="days-row">
                  <span>Sun</span><span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span>
                </div>
                <div className="dates-grid">
                  {calendarDays.map((dayObj, i) => {
                    const formattedDayDate = formatDateString(dayObj.fullDate);
                    
                    // Match events dynamically by true date string
                    const eventsForDay = calendarEventsData.filter(e => e.date === formattedDayDate);

                    return (
                      <div 
                        key={i} 
                        onClick={() => setSelectedDate(dayObj.fullDate)}
                        style={{ cursor: 'pointer' }}
                        className={`date-cell ${!dayObj.isCurrentMonth ? 'other-month' : ''} 
                                   ${dayObj.isToday ? 'active' : ''} 
                                   ${isSelected(dayObj.fullDate) && !dayObj.isToday ? 'selected' : ''}`}
                      >
                        <span className="date-number">{dayObj.date}</span>
                        <div className="cell-events">
                          {eventsForDay.map((evt, idx) => (
                            <div key={idx} className={`mini-event event-${evt.color || 'blue'}`}>
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
        
        {/* Header Cards Row (Bottom) */}
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
                  <Tooltip cursor={{ stroke: 'rgba(0,0,0,0.05)', strokeWidth: 2 }} />
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
                  <Tooltip cursor={{ stroke: 'rgba(0,0,0,0.05)', strokeWidth: 2 }} />
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
                  <Tooltip cursor={{ stroke: 'rgba(0,0,0,0.05)', strokeWidth: 2 }} />
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