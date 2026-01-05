import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { profileAPI } from '../services/api';
import '../styles/Profile.css';

function Profile() {
  const [profile, setProfile] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadProfile();
    loadHistory();
  }, []);

  const loadProfile = async () => {
    try {
      const response = await profileAPI.getProfile();
      setProfile(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load profile:', err);
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await profileAPI.getHistory();
      setHistory(response.data);
    } catch (err) {
      console.error('Failed to load history:', err);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="profile-container">
      <header className="profile-header">
        <h1>Profile</h1>
        <button onClick={() => navigate('/lobby')} className="btn-secondary">
          Back to Lobby
        </button>
      </header>

      {profile && (
        <div className="profile-info">
          <h2>{profile.username}</h2>
          <p>Email: {profile.email}</p>
          <p>Member since: {new Date(profile.created_at).toLocaleDateString()}</p>
        </div>
      )}

      <div className="game-history">
        <h2>Game History</h2>
        {history.length === 0 ? (
          <p>No games played yet.</p>
        ) : (
          <table className="history-table">
            <thead>
              <tr>
                <th>Game #</th>
                <th>Status</th>
                <th>Your Score</th>
                <th>Rank</th>
                <th>Players</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {history.map((game) => (
                <tr key={game.id}>
                  <td>{game.id}</td>
                  <td>{game.status}</td>
                  <td>{game.player_score}</td>
                  <td>{game.player_rank}/{game.total_players}</td>
                  <td>{game.total_players}</td>
                  <td>{new Date(game.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Profile;
