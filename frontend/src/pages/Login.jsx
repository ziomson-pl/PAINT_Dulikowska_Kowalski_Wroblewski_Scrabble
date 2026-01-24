import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import '../styles/Auth.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [debugInfo, setDebugInfo] = useState('');
  const [showDebug, setShowDebug] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      console.log('Attempting login for:', username);
      const response = await authAPI.login(username, password);
      console.log('Login successful:', response.data);
      
      // Clear any old invalid tokens first
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      // Set new token
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('username', username);
      navigate('/lobby');
    } catch (err) {
      // Clear any invalid tokens on login failure
      localStorage.removeItem('token');
      localStorage.removeItem('username');
      
      // Detailed error logging
      const errorDetails = {
        message: err.message,
        status: err.response?.status,
        statusText: err.response?.statusText,
        data: err.response?.data,
        config: {
          url: err.config?.url,
          method: err.config?.method,
          baseURL: err.config?.baseURL,
          fullURL: err.config?.baseURL + err.config?.url,
        },
        request: err.request,
      };
      
      console.error('Login error:', errorDetails);
      
      // Build detailed error message
      let errorMessage = 'Login failed. ';
      
      if (err.response) {
        // Server responded with error
        const status = err.response.status;
        const detail = err.response.data?.detail;
        
        errorMessage += `[Status: ${status}] `;
        
        if (detail) {
          errorMessage += detail;
        } else if (status === 401) {
          errorMessage += 'Incorrect username or password';
        } else if (status === 404) {
          errorMessage += 'Login endpoint not found. Check API URL.';
        } else if (status === 500) {
          errorMessage += 'Server error. Check backend logs.';
        } else {
          errorMessage += `Server error (${status})`;
        }
      } else if (err.request) {
        // Request made but no response
        errorMessage += 'No response from server. Check if backend is running at ' + 
                       (import.meta.env.VITE_API_URL || 'http://localhost:8000');
      } else {
        // Error setting up request
        errorMessage += 'Failed to send request: ' + err.message;
      }
      
      setError(errorMessage);
      setDebugInfo(JSON.stringify(errorDetails, null, 2));
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-box">
        <h1>Scrabble</h1>
        <h2>Logowanie</h2>
        {/* {error && (
          <div className="error-message">
            <div>{error}</div>
            <button 
              type="button"
              onClick={() => setShowDebug(!showDebug)}
              style={{ 
                marginTop: '10px', 
                fontSize: '12px', 
                padding: '5px 10px',
                cursor: 'pointer'
              }}
            >
              {showDebug ? 'Hide' : 'Show'} Debug Info
            </button>
            {showDebug && debugInfo && (
              <pre style={{ 
                marginTop: '10px', 
                padding: '10px', 
                backgroundColor: '#f5f5f5', 
                borderRadius: '4px',
                fontSize: '11px',
                overflow: 'auto',
                maxHeight: '300px'
              }}>
                {debugInfo}
              </pre>
            )}
          </div>
        )} */}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Nazwa użytkownika:</label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>Hasło:</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit" className="btn-primary">Zaloguj</button>
        </form>
        <p>
          Nie masz konta? <a href="/register">Zarejestruj się</a>
        </p>
      </div>
    </div>
  );
}

export default Login;
