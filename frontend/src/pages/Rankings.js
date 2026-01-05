import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { profileAPI } from '../services/api';
import '../styles/Rankings.css';

function Rankings() {
  const [rankings, setRankings] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadRankings();
  }, []);

  const loadRankings = async () => {
    try {
      const response = await profileAPI.getRankings();
      setRankings(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load rankings:', err);
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="rankings-container">
      <header className="rankings-header">
        <h1>Global Rankings</h1>
        <button onClick={() => navigate('/lobby')} className="btn-secondary">
          Back to Lobby
        </button>
      </header>

      <div className="rankings-table-container">
        <table className="rankings-table">
          <thead>
            <tr>
              <th>Rank</th>
              <th>Player</th>
              <th>Rating</th>
              <th>Games</th>
              <th>Wins</th>
              <th>Losses</th>
              <th>Win Rate</th>
              <th>Total Score</th>
              <th>Highest Score</th>
            </tr>
          </thead>
          <tbody>
            {rankings.map((ranking, index) => {
              const winRate = ranking.total_games > 0 
                ? ((ranking.wins / ranking.total_games) * 100).toFixed(1)
                : '0.0';
              
              return (
                <tr key={ranking.id} className={index < 3 ? `top-${index + 1}` : ''}>
                  <td>{index + 1}</td>
                  <td>{ranking.username}</td>
                  <td>{ranking.rating}</td>
                  <td>{ranking.total_games}</td>
                  <td>{ranking.wins}</td>
                  <td>{ranking.losses}</td>
                  <td>{winRate}%</td>
                  <td>{ranking.total_score}</td>
                  <td>{ranking.highest_score}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default Rankings;
