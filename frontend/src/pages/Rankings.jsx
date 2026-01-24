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
    return <div className="loading">Ładowanie...</div>;
  }

  return (
    <div className="rankings-container">
      <header className="rankings-header">
        <h1>Globalne rankingi</h1>
        <button onClick={() => navigate('/lobby')} className="btn-secondary">
          Powrót do Lobby
        </button>
      </header>

      <div className="rankings-table-container">
        <table className="rankings-table">
          <thead>
            <tr>
              <th>Miejsce</th>
              <th>Gracz</th>
              <th>Wynik</th>
              <th>Gry</th>
              <th>Wygrane</th>
              <th>Przegrane</th>
              <th>Procent wygranych</th>
              <th>Całkowity wynik</th>
              <th>Najwyższy wynik</th>
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
