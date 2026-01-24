import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || (typeof window !== 'undefined' && window.location.hostname === 'localhost' ? 'http://localhost:8000' : 'http://scrabble_backend:8000');

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests (but not for auth endpoints)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  // Don't add token to auth endpoints
  if (token && !config.url?.includes('/api/auth/')) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 errors - clear invalid tokens
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear invalid token
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      // Only redirect if not already on login/register page
      if (!window.location.pathname.includes('/login') && 
          !window.location.pathname.includes('/register')) {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (username, email, password) =>
    api.post('/api/auth/register', { username, email, password }),

  login: (username, password) =>
    api.post('/api/auth/login', { username, password }),
};

// Game API
export const gameAPI = {
  createGame: (gameData = {}) => api.post('/api/games', gameData),
  listGames: () => api.get('/api/games'),
  getGame: (gameId) => api.get(`/api/games/${gameId}`),
  joinGame: (gameId) => api.post(`/api/games/${gameId}/join`),
  startGame: (gameId) => api.post(`/api/games/${gameId}/start`),
  makeMove: (gameId, moveData) =>
    api.post(`/api/games/${gameId}/moves`, moveData),
  getMoves: (gameId) => api.get(`/api/games/${gameId}/moves`),
  getMessages: (gameId) => api.get(`/api/games/${gameId}/messages`),
  endGame: (gameId) => api.post(`/api/games/${gameId}/end`),
};

// Profile API
export const profileAPI = {
  getProfile: () => api.get('/api/profile'),
  getRankings: () => api.get('/api/rankings'),
  updateTotalScore: (userId, score) =>
    api.post(`/api/rankings/${userId}/score`, { score }),
  getHistory: () => api.get('/api/history'),
};

export default api;
