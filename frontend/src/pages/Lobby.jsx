import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { gameAPI } from '../services/api';
import '../styles/Lobby.css';

function Lobby() {
  const [games, setGames] = useState([]);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [gameName, setGameName] = useState('');
  const [dictionary, setDictionary] = useState('PL');
  const [loading, setLoading] = useState(false);
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

  const handleCreateGame = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const response = await gameAPI.createGame({
        game_name: gameName || null,
        dictionary: dictionary
      });
      setGameName('');
      setDictionary('PL');
      setShowCreateForm(false);
      navigate(`/game/${response.data.id}`);
    } catch (err) {
      setError('Failed to create game');
      console.error(err);
    } finally {
      setLoading(false);
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
        <h1>Lobby</h1>
        <div className="user-info">
          <span>Witaj, {username}!</span>
          <button onClick={() => navigate('/profile')} className="btn-secondary">Profil</button>
          <button onClick={() => navigate('/rankings')} className="btn-secondary">Rankingi</button>
          <button onClick={handleLogout} className="btn-secondary">Wyloguj</button>
        </div>
      </header>

      {error && <div className="error-message">{error}</div>}

      <div className="lobby-content">
        <div className="create-game-section">
          {!showCreateForm ? (
            <button onClick={() => setShowCreateForm(true)} className="btn-primary btn-large">
              Stwórz nową grę
            </button>
          ) : (
            <form onSubmit={handleCreateGame} className="create-game-form">
              <h3>Stwórz nową grę</h3>
              <div className="form-group">
                <label htmlFor="gameName">Nazwa gry (opcjonalne):</label>
                <input
                  type="text"
                  id="gameName"
                  value={gameName}
                  onChange={(e) => setGameName(e.target.value)}
                  placeholder="e.g., Friendly Match"
                  maxLength="100"
                />
              </div>
              <div className="form-group">
                <label htmlFor="dictionary">Słownik:</label>
                <select
                  id="dictionary"
                  value={dictionary}
                  onChange={(e) => setDictionary(e.target.value)}
                >
                  <option value="PL">Polski</option>
                  <option value="EN">Angielski</option>
                </select>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn-primary" disabled={loading}>
                  {loading ? 'Creating...' : 'Create Game'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="btn-secondary"
                  disabled={loading}
                >
                  Analuj
                </button>
              </div>
            </form>
          )}
        </div>

        <div className="games-list">
          <h2>Dostępne gry</h2>
          {games.length === 0 ? (
            <p className="no-games">Brak dostępnych gier. Stwórz nową!</p>
          ) : (
            <div className="games-grid">
              {games.map((game) => (
                <div key={game.id} className="game-card">
                  <h3>{game.game_name ? game.game_name : `Game #${game.id}`}</h3>
                  <p>DSłownik: <span className="dict-tag">{game.dictionary}</span></p>
                  <p>Status: <span className={`status-${game.status}`}>{game.status}</span></p>
                  <p>Gracze: {game.players.length}/4</p>
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
                      Dołącz
                    </button>
                  )}
                  {game.status === 'active' && (
                    <button 
                      onClick={() => navigate(`/game/${game.id}`)} 
                      className="btn-secondary"
                    >
                      Zobacz
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
