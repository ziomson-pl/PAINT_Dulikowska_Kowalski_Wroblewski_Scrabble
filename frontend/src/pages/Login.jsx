import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import '../styles/Auth.css';

function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await authAPI.login(username, password);
      
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
      
      // Build error message
      let errorMessage = 'Login failed';
      
      if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err.response?.status === 401) {
        errorMessage = 'Incorrect username or password';
      } else if (err.response?.status) {
        errorMessage = `Error: ${err.response.status}`;
      } else if (err.request) {
        errorMessage = 'Cannot connect to server';
      }
      
      setError(errorMessage);
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
