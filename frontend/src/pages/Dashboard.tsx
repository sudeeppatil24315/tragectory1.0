import { useAuth } from '../contexts/AuthContext';
import { useState, useEffect } from 'react';
import {
  getTrajectoryPrediction,
  getBehavioralData,
  getBehavioralInsights,
  getStudentSkills,
  getStudentProfile,
  TrajectoryPrediction,
  BehavioralData,
  BehavioralInsights,
  StudentSkill,
  StudentProfile,
} from '../services/api';
import './Dashboard.css';

export const Dashboard = () => {
  const { user } = useAuth();
  const userName = user?.email?.split('@')[0] || 'Student';

  // State for API data
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<TrajectoryPrediction | null>(null);
  const [behavioralData, setBehavioralData] = useState<BehavioralData[]>([]);
  const [insights, setInsights] = useState<BehavioralInsights | null>(null);
  const [skills, setSkills] = useState<StudentSkill[]>([]);
  const [profile, setProfile] = useState<StudentProfile | null>(null);

  // Fetch all dashboard data
  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch all data in parallel
        const [predictionData, behavioralDataRes, insightsData, skillsData, profileData] =
          await Promise.all([
            getTrajectoryPrediction(),
            getBehavioralData(7),
            getBehavioralInsights(),
            getStudentSkills(),
            getStudentProfile(),
          ]);

        setPrediction(predictionData);
        setBehavioralData(behavioralDataRes);
        setInsights(insightsData);
        setSkills(skillsData);
        setProfile(profileData);
      } catch (err: any) {
        console.error('Error fetching dashboard data:', err);
        setError(err.response?.data?.detail || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  // Calculate wellbeing metrics from behavioral data
  const calculateWellbeingMetrics = () => {
    if (behavioralData.length === 0) {
      return {
        avgScreenTime: 6.2,
        avgFocusScore: 0.65,
        avgSleep: 7.8,
        appBreakdown: { social: 35, entertainment: 30, educational: 25, productivity: 10 },
      };
    }

    const avgScreenTime =
      behavioralData.reduce((sum, d) => sum + d.screen_time_hours, 0) / behavioralData.length;
    const avgFocusScore =
      behavioralData.reduce((sum, d) => sum + (d.focus_score || 0.5), 0) / behavioralData.length;
    const avgSleep =
      behavioralData.reduce((sum, d) => sum + (d.sleep_duration_hours || 7), 0) /
      behavioralData.length;

    // Calculate app breakdown percentages
    const totalAppTime = behavioralData.reduce(
      (sum, d) =>
        sum +
        d.social_media_hours +
        d.entertainment_hours +
        d.educational_app_hours +
        d.productivity_hours,
      0
    );

    const appBreakdown = {
      social: Math.round(
        (behavioralData.reduce((sum, d) => sum + d.social_media_hours, 0) / totalAppTime) * 100
      ),
      entertainment: Math.round(
        (behavioralData.reduce((sum, d) => sum + d.entertainment_hours, 0) / totalAppTime) * 100
      ),
      educational: Math.round(
        (behavioralData.reduce((sum, d) => sum + d.educational_app_hours, 0) / totalAppTime) * 100
      ),
      productivity: Math.round(
        (behavioralData.reduce((sum, d) => sum + d.productivity_hours, 0) / totalAppTime) * 100
      ),
    };

    return { avgScreenTime, avgFocusScore, avgSleep, appBreakdown };
  };

  const wellbeingMetrics = calculateWellbeingMetrics();

  // Loading state
  if (loading) {
    return (
      <div className="export-wrapper">
        <div className="sidebar">
          <div className="logo">
            <iconify-icon icon="lucide:layout-dashboard" style={{ fontSize: '24px' }}></iconify-icon>
          </div>
        </div>
        <div className="main-content">
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <div style={{ textAlign: 'center' }}>
              <iconify-icon icon="lucide:loader-2" style={{ fontSize: '48px', animation: 'spin 1s linear infinite' }}></iconify-icon>
              <p style={{ marginTop: '16px', color: 'var(--text-muted)' }}>Loading dashboard...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="export-wrapper">
        <div className="sidebar">
          <div className="logo">
            <iconify-icon icon="lucide:layout-dashboard" style={{ fontSize: '24px' }}></iconify-icon>
          </div>
        </div>
        <div className="main-content">
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
            <div style={{ textAlign: 'center', maxWidth: '400px' }}>
              <iconify-icon icon="lucide:alert-circle" style={{ fontSize: '48px', color: 'var(--danger)' }}></iconify-icon>
              <p style={{ marginTop: '16px', color: 'var(--text-main)' }}>{error}</p>
              <button
                onClick={() => window.location.reload()}
                style={{
                  marginTop: '16px',
                  padding: '8px 16px',
                  background: 'var(--primary)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                }}
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="export-wrapper">
      {/* Sidebar */}
      <div className="sidebar">
        <div className="logo">
          <iconify-icon icon="lucide:layout-dashboard" style={{ fontSize: '24px' }}></iconify-icon>
        </div>
        <div className="nav-item active">
          <iconify-icon icon="lucide:home" style={{ fontSize: '24px' }}></iconify-icon>
        </div>
        <div className="nav-item">
          <iconify-icon icon="lucide:bar-chart-2" style={{ fontSize: '24px' }}></iconify-icon>
        </div>
        <div className="nav-item">
          <iconify-icon icon="lucide:users" style={{ fontSize: '24px' }}></iconify-icon>
        </div>
        <div className="nav-item">
          <iconify-icon icon="lucide:target" style={{ fontSize: '24px' }}></iconify-icon>
        </div>
        <div className="nav-item" style={{ marginTop: 'auto' }}>
          <iconify-icon icon="lucide:settings" style={{ fontSize: '24px' }}></iconify-icon>
        </div>
      </div>

      {/* Main Content */}
      <div className="main-content">
        {/* Header */}
        <header className="header">
          <div className="header-left">
            <div className="header-breadcrumbs">
              <span>Dashboard</span>
              <iconify-icon icon="lucide:chevron-right" style={{ fontSize: '14px' }}></iconify-icon>
              <span>Student Overview</span>
            </div>
            <h1>{userName}</h1>
          </div>
          <div className="header-right">
            <div className="date-range">
              <iconify-icon icon="lucide:calendar" style={{ fontSize: '16px' }}></iconify-icon>
              <span>Last updated: 2 hours ago</span>
            </div>
            <div style={{ width: '1px', height: '24px', background: 'var(--card-border)' }}></div>
            <div className="user-profile">
              <img
                src="https://storage.googleapis.com/banani-avatars/avatar%2Fmale%2F20%2FSouth%20Asian%2F5"
                className="avatar"
                alt="Profile"
              />
              <div>
                <div style={{ fontSize: '14px', fontWeight: 500 }}>{userName}</div>
                <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>CS Major • Sem 7</div>
              </div>
              <iconify-icon icon="lucide:chevron-down" style={{ fontSize: '16px', color: 'var(--text-muted)' }}></iconify-icon>
            </div>
          </div>
        </header>

        {/* Dashboard Grid */}
        <div className="dashboard-grid">
          {/* Trajectory Score Card */}
          <div className="card col-span-4">
            <div className="card-header">
              <h3 className="card-title">
                <iconify-icon icon="lucide:trending-up" style={{ color: 'var(--primary)' }}></iconify-icon>
                Trajectory Score
              </h3>
              <div className={`badge ${prediction && prediction.trajectory_score >= 70 ? 'badge-success' : 'badge-warning'}`}>
                {prediction && prediction.trajectory_score >= 70 ? 'Good' : 'Fair'}
              </div>
            </div>
            <div className="score-container">
              <div className="score-circle">
                <div className="score-value">
                  <div className="score-number">{prediction ? Math.round(prediction.trajectory_score) : 0}</div>
                  <div className="score-label">/100</div>
                  <div className="score-trend">
                    <iconify-icon
                      icon={prediction?.trend === 'improving' ? 'lucide:arrow-up' : prediction?.trend === 'declining' ? 'lucide:arrow-down' : 'lucide:minus'}
                      style={{ fontSize: '12px' }}
                    ></iconify-icon>
                    {prediction?.velocity ? `${prediction.velocity > 0 ? '+' : ''}${prediction.velocity.toFixed(1)} pts` : 'Stable'}
                  </div>
                </div>
              </div>
            </div>
            <div style={{ textAlign: 'center', marginBottom: '24px' }}>
              <p style={{ fontSize: '14px', color: 'var(--text-main)', marginBottom: '4px' }}>
                {prediction?.interpretation || 'Loading...'}
              </p>
              <p style={{ fontSize: '12px', color: 'var(--text-muted)', margin: 0 }}>
                Similar to alumni placed at {prediction?.predicted_tier || 'Tier 2'} companies.
              </p>
            </div>
            <div className="score-details">
              <div className="detail-row">
                <span style={{ color: 'var(--text-muted)' }}>Confidence</span>
                <span style={{ fontWeight: 500 }}>
                  {prediction
                    ? `${Math.round((prediction.confidence - prediction.margin_of_error / 100) * 100)} - ${Math.round((prediction.confidence + prediction.margin_of_error / 100) * 100)}% (${prediction.confidence > 0.7 ? 'High' : 'Medium'})`
                    : 'N/A'}
                </span>
              </div>
              <div className="detail-row">
                <span style={{ color: 'var(--text-muted)' }}>Placement Likelihood</span>
                <span style={{ fontWeight: 500 }}>
                  {prediction ? `${Math.round(prediction.confidence * 100)}%` : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Component Breakdown */}
          <div className="card col-span-8">
            <div className="card-header">
              <h3 className="card-title">
                <iconify-icon icon="lucide:pie-chart" style={{ color: 'var(--primary)' }}></iconify-icon>
                Component Breakdown
              </h3>
              <button style={{ background: 'transparent', border: '1px solid var(--card-border)', color: 'var(--text-muted)', padding: '4px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '12px' }}>
                View Details
              </button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-around', height: '100%' }}>
              {/* Academic */}
              <div className="breakdown-row">
                <div className="breakdown-header">
                  <span>Academic <span style={{ color: 'var(--text-muted)', fontSize: '12px', fontWeight: 'normal' }}>({prediction ? Math.round(prediction.component_weights.academic * 100) : 25}% weight)</span></span>
                  <span style={{ color: prediction && prediction.component_scores.academic >= 70 ? 'var(--success)' : 'var(--warning)' }}>
                    {prediction ? Math.round(prediction.component_scores.academic) : 0}/100 • {prediction && prediction.component_scores.academic >= 70 ? 'Strong' : 'Fair'}
                  </span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill academic" style={{ width: `${prediction ? prediction.component_scores.academic : 0}%` }}></div>
                </div>
                <div className="breakdown-stats">
                  <span>GPA: {profile?.gpa?.toFixed(1) || 'N/A'}</span>
                  <span>•</span>
                  <span>Attendance: {profile?.attendance ? Math.round(profile.attendance) : 'N/A'}%</span>
                  <span>•</span>
                  <span>Backlogs: 0</span>
                </div>
              </div>
              {/* Behavioral */}
              <div className="breakdown-row">
                <div className="breakdown-header">
                  <span>Behavioral <span style={{ color: 'var(--text-muted)', fontSize: '12px', fontWeight: 'normal' }}>({prediction ? Math.round(prediction.component_weights.behavioral * 100) : 35}% weight)</span></span>
                  <span style={{ color: prediction && prediction.component_scores.behavioral >= 60 ? 'var(--success)' : 'var(--warning)' }}>
                    {prediction ? Math.round(prediction.component_scores.behavioral) : 0}/100 • {prediction && prediction.component_scores.behavioral >= 60 ? 'Good' : 'Needs Work'}
                  </span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill behavioral" style={{ width: `${prediction ? prediction.component_scores.behavioral : 0}%` }}></div>
                </div>
                <div className="breakdown-stats">
                  <span>Study: {profile?.study_hours_per_week ? Math.round(profile.study_hours_per_week / 7) : 0}h/day</span>
                  <span>•</span>
                  <span>Screen: {wellbeingMetrics.avgScreenTime.toFixed(1)}h</span>
                  <span>•</span>
                  <span>Focus: {wellbeingMetrics.avgFocusScore.toFixed(2)}</span>
                </div>
              </div>

              {/* Skills */}
              <div className="breakdown-row" style={{ marginBottom: 0 }}>
                <div className="breakdown-header">
                  <span>Skills <span style={{ color: 'var(--text-muted)', fontSize: '12px', fontWeight: 'normal' }}>({prediction ? Math.round(prediction.component_weights.skills * 100) : 40}% weight)</span></span>
                  <span style={{ color: prediction && prediction.component_scores.skills >= 60 ? 'var(--success)' : 'var(--warning)' }}>
                    {prediction ? Math.round(prediction.component_scores.skills) : 0}/100 • {prediction && prediction.component_scores.skills >= 60 ? 'Good' : 'Fair'}
                  </span>
                </div>
                <div className="progress-track">
                  <div className="progress-fill skills" style={{ width: `${prediction ? prediction.component_scores.skills : 0}%` }}></div>
                </div>
                <div className="breakdown-stats">
                  <span>Projects: {profile?.project_count || 0}</span>
                  <span>•</span>
                  <span>Skills: {skills.length}</span>
                  <span>•</span>
                  <span>Avg Score: {skills.length > 0 ? Math.round(skills.reduce((sum, s) => sum + s.proficiency_score, 0) / skills.length) : 0}</span>
                </div>
              </div>
            </div>
          </div>

          {/* Digital Wellbeing - Full Width */}
          <div className="card col-span-12">
            <div className="card-header">
              <h3 className="card-title">
                <iconify-icon icon="lucide:smartphone" style={{ color: 'var(--primary)' }}></iconify-icon>
                Digital Wellbeing Metrics
                <span style={{ marginLeft: '8px', fontSize: '12px', fontWeight: 400, color: 'var(--text-muted)' }}>
                  Last 7 days data from mobile app
                </span>
              </h3>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: behavioralData.length > 0 ? 'var(--success)' : 'var(--warning)' }}></div>
                {behavioralData.length > 0 ? 'Synced' : 'No Data'}
              </div>
            </div>
            <div className="wellbeing-grid">
              {/* Screen Time */}
              <div className="metric-box">
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: 'var(--text-muted)' }}>
                  <span>Screen Time</span>
                  <iconify-icon icon="lucide:clock" style={{ opacity: 0.5 }}></iconify-icon>
                </div>
                <div className="metric-value" style={{ color: wellbeingMetrics.avgScreenTime > 8 ? 'var(--danger)' : wellbeingMetrics.avgScreenTime > 6 ? 'var(--warning)' : 'var(--success)' }}>
                  {wellbeingMetrics.avgScreenTime.toFixed(1)}h<span style={{ fontSize: '12px', fontWeight: 400, color: 'var(--text-muted)' }}>/ day</span>
                </div>
                <div style={{ fontSize: '11px', color: wellbeingMetrics.avgScreenTime > 8 ? 'var(--danger)' : 'var(--text-muted)' }}>
                  {wellbeingMetrics.avgScreenTime > 8 ? '⚠️ High vs Target (5h)' : 'Target: <8h'}
                </div>
                <div className="metric-trend">
                  {behavioralData.slice(0, 7).reverse().map((data, i) => {
                    const height = Math.min((data.screen_time_hours / 12) * 100, 100);
                    return <div key={i} className="trend-bar" style={{ height: `${height}%` }}></div>;
                  })}
                </div>
              </div>

              {/* Focus Score */}
              <div className="metric-box">
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: 'var(--text-muted)' }}>
                  <span>Focus Score</span>
                  <iconify-icon icon="lucide:crosshair" style={{ opacity: 0.5 }}></iconify-icon>
                </div>
                <div className="metric-value" style={{ color: wellbeingMetrics.avgFocusScore < 0.5 ? 'var(--danger)' : wellbeingMetrics.avgFocusScore < 0.7 ? 'var(--warning)' : 'var(--success)' }}>
                  {wellbeingMetrics.avgFocusScore.toFixed(2)}
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Target: &gt;0.8</div>
                <div className="metric-trend">
                  {behavioralData.slice(0, 7).reverse().map((data, i) => {
                    const height = ((data.focus_score || 0.5) / 1.0) * 100;
                    return <div key={i} className="trend-bar" style={{ height: `${height}%`, background: 'var(--warning)' }}></div>;
                  })}
                </div>
              </div>

              {/* Sleep */}
              <div className="metric-box">
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: 'var(--text-muted)' }}>
                  <span>Sleep Avg</span>
                  <iconify-icon icon="lucide:moon" style={{ opacity: 0.5 }}></iconify-icon>
                </div>
                <div className="metric-value" style={{ color: wellbeingMetrics.avgSleep < 6 ? 'var(--danger)' : wellbeingMetrics.avgSleep < 7 ? 'var(--warning)' : 'var(--success)' }}>
                  {wellbeingMetrics.avgSleep.toFixed(1)}h
                </div>
                <div style={{ fontSize: '11px', color: wellbeingMetrics.avgSleep >= 7 ? 'var(--success)' : 'var(--warning)' }}>
                  {wellbeingMetrics.avgSleep >= 7 ? '✅ Good range' : '⚠️ Below target'}
                </div>
                <div className="metric-trend">
                  {behavioralData.slice(0, 7).reverse().map((data, i) => {
                    const height = ((data.sleep_duration_hours || 7) / 10) * 100;
                    return <div key={i} className="trend-bar" style={{ height: `${height}%`, background: 'var(--success)' }}></div>;
                  })}
                </div>
              </div>

              {/* App Breakdown */}
              <div className="metric-box">
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', color: 'var(--text-muted)', marginBottom: '12px' }}>
                  <span>App Usage</span>
                  <iconify-icon icon="lucide:grid" style={{ opacity: 0.5 }}></iconify-icon>
                </div>
                <div style={{ display: 'flex', height: '12px', borderRadius: '6px', overflow: 'hidden', marginBottom: '12px' }}>
                  <div style={{ width: `${wellbeingMetrics.appBreakdown.social}%`, background: 'var(--danger)' }}></div>
                  <div style={{ width: `${wellbeingMetrics.appBreakdown.entertainment}%`, background: 'var(--primary)' }}></div>
                  <div style={{ width: `${wellbeingMetrics.appBreakdown.educational}%`, background: 'var(--success)' }}></div>
                  <div style={{ width: `${wellbeingMetrics.appBreakdown.productivity}%`, background: 'var(--text-muted)' }}></div>
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '11px', color: 'var(--text-muted)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--danger)' }}></div>
                    Social ({wellbeingMetrics.appBreakdown.social}%)
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--primary)' }}></div>
                    Entertain ({wellbeingMetrics.appBreakdown.entertainment}%)
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--success)' }}></div>
                    Edu ({wellbeingMetrics.appBreakdown.educational}%)
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--text-muted)' }}></div>
                    Prod ({wellbeingMetrics.appBreakdown.productivity}%)
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* AI Recommendations */}
          <div className="card col-span-8">
            <div className="card-header">
              <h3 className="card-title">
                <iconify-icon icon="lucide:sparkles" style={{ color: 'var(--primary)' }}></iconify-icon>
                AI Recommendations
              </h3>
              <button
                onClick={() => window.location.reload()}
                style={{ background: 'var(--primary)', border: 'none', color: 'white', padding: '6px 16px', borderRadius: '20px', fontSize: '12px', fontWeight: 500, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
              >
                <iconify-icon icon="lucide:refresh-cw"></iconify-icon>
                Regenerate
              </button>
            </div>
            {insights && insights.recommendations.length > 0 ? (
              insights.recommendations.slice(0, 3).map((rec, index) => {
                const isHighImpact = rec.toLowerCase().includes('urgent') || rec.toLowerCase().includes('reduce screen');
                const isMediumImpact = !isHighImpact;
                const iconMap: { [key: string]: string } = {
                  'reduce screen': 'lucide:layout-dashboard',
                  'urgent': 'lucide:alert-triangle',
                  'sleep': 'lucide:moon',
                  'focus': 'lucide:crosshair',
                  'default': 'lucide:code-2',
                };
                const icon = Object.keys(iconMap).find((key) => rec.toLowerCase().includes(key)) || 'default';

                return (
                  <div key={index} className="rec-item">
                    <div
                      className="rec-icon"
                      style={{
                        background: isHighImpact ? 'rgba(239, 68, 68, 0.1)' : 'rgba(234, 179, 8, 0.1)',
                        color: isHighImpact ? 'var(--danger)' : 'var(--warning)',
                      }}
                    >
                      <iconify-icon icon={iconMap[icon]}></iconify-icon>
                    </div>
                    <div className="rec-content" style={{ flex: 1 }}>
                      <h4>
                        {rec.split('.')[0]}
                        <span className={`impact-badge ${isHighImpact ? 'impact-high' : 'impact-medium'}`}>
                          {isHighImpact ? 'High Impact' : 'Medium Impact'}
                        </span>
                      </h4>
                      <p>{rec}</p>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center' }}>
                      <button style={{ background: 'transparent', border: '1px solid var(--card-border)', color: 'var(--text-muted)', width: '32px', height: '32px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer' }}>
                        <iconify-icon icon="lucide:check"></iconify-icon>
                      </button>
                    </div>
                  </div>
                );
              })
            ) : (
              <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
                No recommendations available. Keep up the good work!
              </div>
            )}
          </div>

          {/* Similar Alumni */}
          <div className="card col-span-4">
            <div className="card-header">
              <h3 className="card-title">
                <iconify-icon icon="lucide:users" style={{ color: 'var(--primary)' }}></iconify-icon>
                Similar Alumni
              </h3>
              <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Top {prediction?.similar_alumni.length || 0} Matches</span>
            </div>
            {prediction && prediction.similar_alumni.length > 0 ? (
              <>
                {prediction.similar_alumni.slice(0, 3).map((alumni, index) => {
                  const colors = ['#3b82f6', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981'];
                  const initials = `A${index + 1}`;
                  return (
                    <div key={alumni.alumni_id} className="alumni-item">
                      <div className="alumni-avatar" style={{ background: colors[index % colors.length] }}>
                        {initials}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontSize: '14px', fontWeight: 500 }}>
                          Alumni {index + 1}{' '}
                          <span style={{ color: 'var(--success)', fontSize: '12px' }}>
                            {Math.round(alumni.similarity_score * 100)}% Match
                          </span>
                        </div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                          {alumni.company_tier} • Score: {Math.round(alumni.outcome_score)}
                        </div>
                      </div>
                      <iconify-icon icon="lucide:chevron-right" style={{ color: 'var(--text-muted)' }}></iconify-icon>
                    </div>
                  );
                })}
                <button style={{ marginTop: 'auto', background: 'transparent', border: '1px solid var(--card-border)', width: '100%', padding: '8px', borderRadius: '8px', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '12px' }}>
                  View All Matches
                </button>
              </>
            ) : (
              <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
                No similar alumni found yet.
              </div>
            )}
          </div>

          {/* Gap Analysis */}
          <div className="card col-span-8">
            <div className="card-header">
              <h3 className="card-title">
                <iconify-icon icon="lucide:git-pull-request" style={{ color: 'var(--primary)' }}></iconify-icon>
                Gap Analysis
              </h3>
              <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                <span style={{ color: 'var(--primary)' }}>■ You</span> vs <span style={{ color: 'var(--success)' }}>| Successful Alumni</span>
              </div>
            </div>
            {insights && insights.comparison ? (
              <>
                {/* Screen Time Gap */}
                <div className="gap-row">
                  <div className="gap-label">
                    <div>Screen Time</div>
                    <div style={{ fontSize: '11px', color: insights.comparison.screen_time.status === 'poor' ? 'var(--danger)' : 'var(--success)' }}>
                      {insights.comparison.screen_time.status === 'poor' ? 'High Impact' : 'Good'}
                    </div>
                  </div>
                  <div className="gap-chart">
                    <div
                      className="gap-bar-student"
                      style={{
                        width: `${Math.min((insights.comparison.screen_time.student / 12) * 100, 100)}%`,
                        background: insights.comparison.screen_time.status === 'poor' ? 'var(--danger)' : 'var(--success)',
                      }}
                    ></div>
                    <div className="gap-marker-alumni" style={{ left: `${Math.min((insights.comparison.screen_time.optimal / 12) * 100, 100)}%` }}></div>
                  </div>
                  <div className="gap-stats">
                    <div>
                      {insights.comparison.screen_time.student.toFixed(1)}h vs {insights.comparison.screen_time.optimal.toFixed(1)}h
                    </div>
                    <div style={{ color: insights.comparison.screen_time.status === 'poor' ? 'var(--danger)' : 'var(--success)' }}>
                      {insights.comparison.screen_time.student > insights.comparison.screen_time.optimal
                        ? `+${(insights.comparison.screen_time.student - insights.comparison.screen_time.optimal).toFixed(1)}h Gap`
                        : `${(insights.comparison.screen_time.student - insights.comparison.screen_time.optimal).toFixed(1)}h Ahead`}
                    </div>
                  </div>
                </div>

                {/* Focus Score Gap */}
                <div className="gap-row">
                  <div className="gap-label">
                    <div>Focus Score</div>
                    <div style={{ fontSize: '11px', color: insights.comparison.focus_score.status === 'poor' ? 'var(--warning)' : 'var(--success)' }}>
                      {insights.comparison.focus_score.status === 'poor' ? 'Medium Impact' : 'Good'}
                    </div>
                  </div>
                  <div className="gap-chart">
                    <div
                      className="gap-bar-student"
                      style={{
                        width: `${insights.comparison.focus_score.student * 100}%`,
                        background: insights.comparison.focus_score.status === 'poor' ? 'var(--warning)' : 'var(--success)',
                      }}
                    ></div>
                    <div className="gap-marker-alumni" style={{ left: `${insights.comparison.focus_score.optimal * 100}%` }}></div>
                  </div>
                  <div className="gap-stats">
                    <div>
                      {insights.comparison.focus_score.student.toFixed(2)} vs {insights.comparison.focus_score.optimal.toFixed(2)}
                    </div>
                    <div style={{ color: insights.comparison.focus_score.status === 'poor' ? 'var(--warning)' : 'var(--success)' }}>
                      {insights.comparison.focus_score.student < insights.comparison.focus_score.optimal
                        ? `${(insights.comparison.focus_score.student - insights.comparison.focus_score.optimal).toFixed(2)} Gap`
                        : `+${(insights.comparison.focus_score.student - insights.comparison.focus_score.optimal).toFixed(2)} Ahead`}
                    </div>
                  </div>
                </div>

                {/* Sleep Gap */}
                <div className="gap-row">
                  <div className="gap-label">
                    <div>Sleep</div>
                    <div style={{ fontSize: '11px', color: insights.comparison.sleep.status === 'poor' ? 'var(--warning)' : 'var(--success)' }}>
                      {insights.comparison.sleep.status === 'poor' ? 'Medium Impact' : 'Strength'}
                    </div>
                  </div>
                  <div className="gap-chart">
                    <div
                      className="gap-bar-student"
                      style={{
                        width: `${Math.min((insights.comparison.sleep.student / 10) * 100, 100)}%`,
                        background: insights.comparison.sleep.status === 'poor' ? 'var(--warning)' : 'var(--success)',
                      }}
                    ></div>
                    <div className="gap-marker-alumni" style={{ left: `${Math.min((insights.comparison.sleep.optimal / 10) * 100, 100)}%` }}></div>
                  </div>
                  <div className="gap-stats">
                    <div>
                      {insights.comparison.sleep.student.toFixed(1)}h vs {insights.comparison.sleep.optimal.toFixed(1)}h
                    </div>
                    <div style={{ color: insights.comparison.sleep.status === 'poor' ? 'var(--warning)' : 'var(--success)' }}>
                      {insights.comparison.sleep.student < insights.comparison.sleep.optimal
                        ? `${(insights.comparison.sleep.student - insights.comparison.sleep.optimal).toFixed(1)}h Gap`
                        : `+${(insights.comparison.sleep.student - insights.comparison.sleep.optimal).toFixed(1)}h Ahead`}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div style={{ padding: '20px', textAlign: 'center', color: 'var(--text-muted)' }}>
                No comparison data available yet.
              </div>
            )}
          </div>

          {/* Progress & Streak */}
          <div className="card col-span-4">
            <div className="card-header">
              <h3 className="card-title">
                <iconify-icon icon="lucide:award" style={{ color: 'var(--primary)' }}></iconify-icon>
                Progress &amp; Streak
              </h3>
              <div className="badge" style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--danger)', display: 'flex', alignItems: 'center', gap: '4px' }}>
                <iconify-icon icon="lucide:flame"></iconify-icon> 7 Days
              </div>
            </div>
            <div style={{ height: '100px', width: '100%', display: 'flex', alignItems: 'flex-end', gap: '4px', marginBottom: '20px' }}>
              {[40, 45, 50, 48, 55, 60, 73].map((height, i) => (
                <div
                  key={i}
                  style={{
                    width: '12%',
                    height: `${height}%`,
                    background: i === 6 ? 'var(--primary)' : `rgba(99, 102, 241, ${0.2 + i * 0.1})`,
                    borderRadius: '4px 4px 0 0'
                  }}
                ></div>
              ))}
            </div>
            <div style={{ fontSize: '13px', fontWeight: 500, marginBottom: '12px' }}>Recent Achievements</div>
            <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
                🏆
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '13px' }}>Score 70+ Club</div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Reached 73 trajectory score</div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'rgba(234, 179, 8, 0.1)', color: 'var(--warning)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '20px', border: '1px solid rgba(234, 179, 8, 0.3)' }}>
                ⚡
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '13px' }}>Consistency King</div>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>7 day login streak</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
