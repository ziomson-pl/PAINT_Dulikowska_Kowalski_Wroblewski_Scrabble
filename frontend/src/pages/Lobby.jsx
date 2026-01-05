import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { gameAPI } from '../services/api';
import '../styles/Lobby.css';

function Lobby() {
  const [games, setGames] = useState([]);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const username = localStorage.getItem('username');

  useEffect(() => {
    if (!username) {
      navigate('/login');
      return;
    }
    loadGames();
    const interval = setInterval(loadGames, 3000); // Refresh every 3 seconds
    return () => clearInterval(interval);
  }, [username, navigate]);

  const loadGames = async () => {
    try {
      const response = await gameAPI.listGames();
      setGames(response.data);
    } catch (err) {
      console.error('Failed to load games:', err);
    }
  };

  const handleCreateGame = async () => {
    try {
      const response = await gameAPI.createGame();
      navigate(`/game/${response.data.id}`);
    } catch (err) {
      setError('Failed to create game');
    }
  };

  const handleJoinGame = async (gameId) => {
    try {
      await gameAPI.joinGame(gameId);
      navigate(`/game/${gameId}`);
    } catch (err) {
      setError('Failed to join game');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    navigate('/login');
  };

  return (
    <div className="lobby-container">
      <header className="lobby-header">
        <h1>Scrabble Lobby</h1>
        <div className="user-info">
          <span>Welcome, {username}!</span>
          <button onClick={() => navigate('/profile')} className="btn-secondary">Profile</button>
          <button onClick={() => navigate('/rankings')} className="btn-secondary">Rankings</button>
          <button onClick={handleLogout} className="btn-secondary">Logout</button>
        </div>
      </header>

      {error && <div className="error-message">{error}</div>}

      <div className="lobby-content">
        <div className="create-game-section">
          <button onClick={handleCreateGame} className="btn-primary btn-large">
            Create New Game
          </button>
        </div>

        <div className="games-list">
          <h2>Available Games</h2>
          {games.length === 0 ? (
            <p className="no-games">No games available. Create one!</p>
          ) : (
            <div className="games-grid">
              {games.map((game) => (
                <div key={game.id} className="game-card">
                  <h3>Game #{game.id}</h3>
                  <p>Status: <span className={`status-${game.status}`}>{game.status}</span></p>
                  <p>Players: {game.players.length}/4</p>
                  <div className="players-list">
                    {game.players.map((player, idx) => (
                      <div key={idx} className="player-tag">
                        {player.username} ({player.score})
                      </div>
                    ))}
                  </div>
                  {game.status === 'waiting' && game.players.length < 4 && (
                    <button 
                      onClick={() => handleJoinGame(game.id)} 
                      className="btn-primary"
                    >
                      Join Game
                    </button>
                  )}
                  {game.status === 'active' && (
                    <button 
                      onClick={() => navigate(`/game/${game.id}`)} 
                      className="btn-secondary"
                    >
                      View Game
                    </button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default Lobby;
