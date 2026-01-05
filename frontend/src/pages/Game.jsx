import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { gameAPI, profileAPI } from '../services/api';
import GameBoard from '../components/GameBoard';
import PlayerRack from '../components/PlayerRack';
import Chat from '../components/Chat';
import '../styles/Game.css';

function Game() {
  const { gameId } = useParams();
  const navigate = useNavigate();
  const [game, setGame] = useState(null);
  const [profile, setProfile] = useState(null);
  const [selectedTiles, setSelectedTiles] = useState([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadGame();
    loadProfile();
    const interval = setInterval(loadGame, 2000); // Refresh every 2 seconds
    return () => clearInterval(interval);
  }, [gameId]);

  const loadGame = async () => {
    try {
      const response = await gameAPI.getGame(gameId);
      setGame(response.data);
      setLoading(false);
    } catch (err) {
      console.error('Failed to load game:', err);
      setLoading(false);
    }
  };

  const loadProfile = async () => {
    try {
      const response = await profileAPI.getProfile();
      setProfile(response.data);
    } catch (err) {
      console.error('Failed to load profile:', err);
    }
  };

  const handleStartGame = async () => {
    try {
      await gameAPI.startGame(gameId);
      loadGame();
    } catch (err) {
      setError('Failed to start game');
    }
  };

  const handlePass = async () => {
    try {
      await gameAPI.makeMove(gameId, { tiles: [], is_pass: true });
      setSelectedTiles([]);
      loadGame();
    } catch (err) {
      setError(err.response?.data?.detail || 'Move failed');
    }
  };

  const handlePlayWord = async () => {
    if (selectedTiles.length === 0) {
      setError('No tiles selected');
      return;
    }

    try {
      await gameAPI.makeMove(gameId, { tiles: selectedTiles, is_pass: false });
      setSelectedTiles([]);
      setError('');
      loadGame();
    } catch (err) {
      setError(err.response?.data?.detail || 'Move failed');
    }
  };

  const isMyTurn = () => {
    if (!game || !profile) return false;
    const currentPlayer = game.players.find(
      p => p.player_order === (game.current_turn % game.players.length)
    );
    return currentPlayer && currentPlayer.id === profile.id;
  };

  if (loading) {
    return <div className="loading">Loading game...</div>;
  }

  if (!game) {
    return <div className="error">Game not found</div>;
  }

  return (
    <div className="game-container">
      <header className="game-header">
        <h1>Scrabble Game #{gameId}</h1>
        <button onClick={() => navigate('/lobby')} className="btn-secondary">
          Back to Lobby
        </button>
      </header>

      <div className="game-content">
        <div className="game-main">
          <div className="game-info">
            <h3>Status: {game.status}</h3>
            <h3>Turn: {game.current_turn + 1}</h3>
            {isMyTurn() && <div className="turn-indicator">Your Turn!</div>}
          </div>

          {error && <div className="error-message">{error}</div>}

          {game.status === 'waiting' && (
            <div className="waiting-section">
              <p>Waiting for players... ({game.players.length}/4)</p>
              {game.players.length >= 2 && (
                <button onClick={handleStartGame} className="btn-primary">
                  Start Game
                </button>
              )}
            </div>
          )}

          {game.status === 'active' && (
            <>
              <GameBoard 
                board={game.board_state} 
                selectedTiles={selectedTiles}
                setSelectedTiles={setSelectedTiles}
              />

              <PlayerRack 
                rack={game.rack || []} 
                selectedTiles={selectedTiles}
                setSelectedTiles={setSelectedTiles}
                disabled={!isMyTurn()}
              />

              <div className="game-controls">
                <button 
                  onClick={handlePlayWord} 
                  disabled={!isMyTurn() || selectedTiles.length === 0}
                  className="btn-primary"
                >
                  Play Word
                </button>
                <button 
                  onClick={handlePass} 
                  disabled={!isMyTurn()}
                  className="btn-secondary"
                >
                  Pass Turn
                </button>
                <button 
                  onClick={() => setSelectedTiles([])}
                  className="btn-secondary"
                >
                  Clear Selection
                </button>
              </div>

              <div className="remaining-tiles">
                Remaining tiles: {game.remaining_tiles || 0}
              </div>
            </>
          )}

          {game.status === 'finished' && (
            <div className="game-finished">
              <h2>Game Finished!</h2>
              <p>Check the scores below.</p>
            </div>
          )}

          <div className="players-info">
            <h3>Players</h3>
            {game.players.map((player, idx) => (
              <div key={idx} className="player-info">
                <span className="player-name">{player.username}</span>
                <span className="player-score">Score: {player.score}</span>
                {player.player_order === (game.current_turn % game.players.length) && (
                  <span className="current-turn-marker">▶</span>
                )}
              </div>
            ))}
          </div>
        </div>

        <div className="game-sidebar">
          <Chat gameId={gameId} />
        </div>
      </div>
    </div>
  );
}

export default Game;
