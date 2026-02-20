/**
 * API Service Layer
 * Handles all backend API calls with authentication
 */

import axios, { AxiosInstance } from 'axios';
import { API_BASE_URL } from '../config';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============================================================================
// TYPE DEFINITIONS
// ============================================================================

export interface TrajectoryPrediction {
  trajectory_score: number;
  component_scores: {
    academic: number;
    behavioral: number;
    skills: number;
  };
  component_weights: {
    academic: number;
    behavioral: number;
    skills: number;
  };
  confidence: number;
  margin_of_error: number;
  trend: string;
  velocity: number;
  predicted_tier: string;
  interpretation: string;
  similar_alumni_count: number;
  similar_alumni: Array<{
    alumni_id: number;
    similarity_score: number;
    company_tier: string;
    outcome_score: number;
  }>;
}

export interface BehavioralData {
  id: number;
  date: string;
  screen_time_hours: number;
  educational_app_hours: number;
  social_media_hours: number;
  entertainment_hours: number;
  productivity_hours: number;
  focus_score: number | null;
  sleep_duration_hours: number | null;
  sleep_quality: string | null;
  synced_at: string;
}

export interface BehavioralInsights {
  correlations: {
    screen_time_vs_gpa: number;
    focus_score_vs_trajectory: number;
    sleep_vs_academic: number;
    sample_size: number;
    optimal_ranges: {
      screen_time: { min: number; max: number };
      focus_score: { min: number; max: number };
      sleep: { min: number; max: number };
    };
    interpretation: {
      screen_time_vs_gpa: string;
      focus_score_vs_trajectory: string;
      sleep_vs_academic: string;
    };
  };
  at_risk_flags: Array<{
    flag: string;
    severity: string;
    description: string;
    metric_value?: number;
    threshold?: number;
  }>;
  comparison: {
    screen_time: { student: number; optimal: number; status: string };
    focus_score: { student: number; optimal: number; status: string };
    sleep: { student: number; optimal: number; status: string };
  };
  recommendations: string[];
}

export interface StudentSkill {
  id: number;
  skill_name: string;
  proficiency_score: number;
  quiz_score: number | null;
  voice_score: number | null;
  market_weight: number;
  last_assessed_at: string;
  created_at: string;
}

export interface StudentProfile {
  id: number;
  user_id: number;
  name: string;
  major: string;
  semester: number | null;
  gpa: number | null;
  attendance: number | null;
  study_hours_per_week: number | null;
  project_count: number | null;
  vector_id: string | null;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// API FUNCTIONS
// ============================================================================

/**
 * Get trajectory prediction for current student
 */
export const getTrajectoryPrediction = async (): Promise<TrajectoryPrediction> => {
  const response = await apiClient.post('/api/predict', {});
  return response.data;
};

/**
 * Get behavioral data for current student
 */
export const getBehavioralData = async (days: number = 7): Promise<BehavioralData[]> => {
  const response = await apiClient.get(`/api/student/behavioral?days=${days}`);
  return response.data.data;
};

/**
 * Get behavioral insights (recommendations, at-risk patterns, comparison)
 */
export const getBehavioralInsights = async (): Promise<BehavioralInsights> => {
  const response = await apiClient.get('/api/behavioral/insights');
  return response.data;
};

/**
 * Get student skills
 */
export const getStudentSkills = async (): Promise<StudentSkill[]> => {
  const response = await apiClient.get('/api/student/skills');
  return response.data.skills;
};

/**
 * Get student profile
 */
export const getStudentProfile = async (): Promise<StudentProfile> => {
  const response = await apiClient.get('/api/student/profile');
  return response.data;
};

/**
 * Get comparison to successful alumni
 */
export const getAlumniComparison = async () => {
  const response = await apiClient.get('/api/behavioral/comparison');
  return response.data;
};

export default apiClient;
