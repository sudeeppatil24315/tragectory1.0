// API Configuration
// This file manages the backend API URL for different environments

/**
 * Get the API base URL based on environment
 * - Development: Uses localhost by default
 * - Demo/Production: Uses environment variable (Cloudflare Tunnel URL)
 */
export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * API endpoints
 */
export const API_ENDPOINTS = {
  // Authentication
  AUTH: {
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
  },
  
  // Student Profile
  STUDENT: {
    PROFILE: '/api/student/profile',
    BEHAVIORAL: '/api/student/behavioral',
    SKILLS: '/api/student/skills',
  },
  
  // Prediction
  PREDICTION: {
    CALCULATE: '/api/predict',
  },
  
  // Skills
  SKILLS: {
    QUIZ: '/api/skills/quiz',
    VOICE_EVAL: '/api/skills/voice-eval',
    ANALYZE_DEMAND: '/api/skills/analyze-demand',
    LIST: '/api/skills/',
  },
  
  // Behavioral Analysis
  BEHAVIORAL: {
    CORRELATIONS: '/api/behavioral/correlations',
    AT_RISK: '/api/behavioral/at-risk',
    COMPARISON: '/api/behavioral/comparison',
    INSIGHTS: '/api/behavioral/insights',
  },
  
  // Admin
  ADMIN: {
    IMPORT_ALUMNI: '/api/admin/import-alumni',
    ALUMNI_TEMPLATE: '/api/admin/alumni-template',
    ALUMNI_TEMPLATE_INFO: '/api/admin/alumni-template/info',
    HEALTH: '/api/admin/health',
  },
};

/**
 * Check if we're using Cloudflare Tunnel
 */
export const isUsingTunnel = () => {
  return API_BASE_URL.includes('trycloudflare.com');
};

/**
 * Log current API configuration (for debugging)
 */
if (import.meta.env.DEV) {
  console.log('🔧 API Configuration:');
  console.log('  Base URL:', API_BASE_URL);
  console.log('  Using Tunnel:', isUsingTunnel());
  console.log('  Environment:', import.meta.env.MODE);
}
