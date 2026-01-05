import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth API
export const authAPI = {
  register: (username, email, password) =>
    api.post('/api/auth/register', { username, email, password }),

  login: (username, password) =>
    api.post('/api/auth/login', { username, password }),
};

// Game API
export const gameAPI = {
  createGame: () => api.post('/api/games', {}),
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
  getHistory: () => api.get('/api/history'),
};

export default api;
