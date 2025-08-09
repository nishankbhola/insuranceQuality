// API Configuration
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/quality/api' 
  : 'http://localhost:8000/api';

export const API_ENDPOINTS = {
  validate: `${API_BASE_URL}/validate`,
  validateCompact: `${API_BASE_URL}/validate-compact`,
  applicationQC: `${API_BASE_URL}/application-qc`,
  health: `${API_BASE_URL}/health`,
};

export default API_BASE_URL; 