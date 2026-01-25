import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { DndContext, useSensor, useSensors, PointerSensor } from '@dnd-kit/core';
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
  const [exchangeMode, setExchangeMode] = useState(false);
  const [selectedExchangeTiles, setSelectedExchangeTiles] = useState([]);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  useEffect(() => {
    loadGame();
    loadProfile();
  
    const interval = setInterval(loadGame, 2000);
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
      setError('Nie udało się rozpocząć gry');
    }
  };

  const handleEndGame = async () => {
    if (!window.confirm("Czy na pewno chcesz zakończyć grę?")) return;
    try {
      await gameAPI.endGame(gameId);
  
      const response = await gameAPI.getGame(gameId);
      const finishedGame = response.data;
      setGame(finishedGame);

      if (finishedGame.players && finishedGame.players.length > 0) {
        await Promise.all(
          finishedGame.players.map(player =>
            profileAPI.updateTotalScore(player.id, player.score)
          )
        );
      }
  
      loadProfile();
  
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Nie udało się zakończyć gry';
      setError(errorMsg);
    }
  };
  

  const handlePass = async () => {
    try {
      await gameAPI.makeMove(gameId, { tiles: [], is_pass: true });
      setSelectedTiles([]);
      setError('');
      // Refresh game state to get updated turn
      await loadGame();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Ruch nieprawidłowy';
      setError(errorMsg);
      // Refresh game state even on error to get latest turn info
      loadGame();
    }
  };

  const handleExchange = async () => {
    if (selectedExchangeTiles.length === 0) {
      setError('Nie wybrano liter do wymiany');
      return;
    }

    try {
      const tilesToExchange = selectedExchangeTiles.map(index => game.rack[index]);
      await gameAPI.makeMove(gameId, {
        tiles: [],
        is_exchange: true,
        exchange_tiles: tilesToExchange
      });
      setSelectedExchangeTiles([]);
      setExchangeMode(false);
      setError('');
      await loadGame();
    } catch (err) {
      const errorMsg = err.response?.data?.detail || 'Wymiana liter nie udała się';
      setError(errorMsg);
      loadGame();
    }
  };

  const toggleExchangeMode = () => {
    if (exchangeMode) {
      setSelectedExchangeTiles([]);
    }
    setExchangeMode(!exchangeMode);
  };

  const toggleExchangeTile = (index) => {
    if (selectedExchangeTiles.includes(index)) {
      setSelectedExchangeTiles(selectedExchangeTiles.filter(i => i !== index));
    } else {
      setSelectedExchangeTiles([...selectedExchangeTiles, index]);
    }
  };

  const handlePlayWord = async () => {
    if (selectedTiles.length === 0) {
      setError('Nie wybrano liter');
      return;
    }

    // Remap selectedTiles to expected format (remove rackIndex if backend doesn't need it)
    // IMPORTANT: Ensure row and col are integers, not strings
    const tilesToSend = selectedTiles.map(({ letter, row, col, is_blank }) => ({
      letter, 
      row: parseInt(row), 
      col: parseInt(col), 
      is_blank: Boolean(is_blank)
    }));

    try {
      await gameAPI.makeMove(gameId, { tiles: tilesToSend, is_pass: false });
      // Only clear selected tiles and error after successful move
      setSelectedTiles([]);
      setError('');
      // Refresh game state to show updated board
      await loadGame();
    } catch (err) {
      // On error, keep selected tiles so user can fix and retry
      setError(err.response?.data?.detail || 'Ruch nieprawidłowy');
      // Still refresh game state in case turn changed
      loadGame();
    }
  };

  const handleDragEnd = (event) => {
    const { active, over } = event;

    if (over && over.data.current) {
      const { row, col } = over.data.current;
      const { tile, index: rackIndex, fromBoard, row: boardRow, col: boardCol, isPlacedThisTurn } = active.data.current;

      // Check if cell is occupied by board tile (permanent)
      if (game.board_state[row][col]) {
        return;
      }

      let newTile;
      let newSelectedTiles = [...selectedTiles];

      if (fromBoard && isPlacedThisTurn) {

        const oldPlacementIndex = newSelectedTiles.findIndex(t => t.row === boardRow && t.col === boardCol);
        if (oldPlacementIndex >= 0) {
          newSelectedTiles.splice(oldPlacementIndex, 1);
        }

        const oldTile = newSelectedTiles.find(t => t.row === boardRow && t.col === boardCol) || 
                       selectedTiles.find(t => t.row === boardRow && t.col === boardCol);
        
        newTile = {
          letter: tile,
          row,
          col,
          is_blank: tile === '_',
          rackIndex: oldTile?.rackIndex 
        };
      } else {
        // Dragging from rack
        newTile = {
          letter: tile,
          row,
          col,
          is_blank: tile === '_',
          rackIndex // Track which tile from rack is used
        };

        // Remove any previous placement of THIS same tile from rack
        const previousPlacementIndex = newSelectedTiles.findIndex(t => t.rackIndex === rackIndex);
        if (previousPlacementIndex >= 0) {
          newSelectedTiles.splice(previousPlacementIndex, 1);
        }
      }

      // If dropped on occupied cell (by selection), replace it
      const occupiedBySelection = newSelectedTiles.findIndex(t => t.row === row && t.col === col);
      if (occupiedBySelection >= 0) {
        newSelectedTiles.splice(occupiedBySelection, 1);
      }

      newSelectedTiles.push(newTile);
      setSelectedTiles(newSelectedTiles);
    }
  };

  const isMyTurn = () => {
    if (!game || !profile) return false;
    const currentPlayer = game.players.find(
      p => p.player_order === (game.current_turn % game.players.length)
    );
    return currentPlayer && currentPlayer.id === profile.id;
  };

  // Filter rack tiles to hide ones that are already placed
  const getVisibleRack = () => {
    if (!game.rack) return [];
    // We map the rack to objects or keep indices to know what is what
    // But Game.jsx doesn't see "rack objects", just array of strings.
    // However, selectedTiles has 'rackIndex'.
    // We can pass the full rack to PlayerRack, but we need to tell it which indices are used.
    // Actually, I modified PlayerRack to map purely based on index.
    // So if selectedTiles has { rackIndex: 0 }, PlayerRack should know rack[0] is used.
    // Wait, PlayerRack renders DraggableTile. If I remove it from DOM, drag might break?
    // No, unmounting is fine.

    // Instead of filtering the array (which shifts indices), let's pass all tiles 
    // but tell PlayerRack which ones to hide/disable style.
    // But PlayerRack implementation I wrote maps `rack`. 
    // If I filter `rack`, indices change. I MUST NOT filter `rack`.
    // I should pass `rack` as is, and pass `usedIndices` to PlayerRack?
    // My previous PlayerRack implementation didn't have `usedIndices` prop.
    // I can filter `rack` by replacing used letters with null? No, confusing.

    // Let's modify available rack:
    const displayRack = [...(game.rack || [])];
    selectedTiles.forEach(t => {
      if (t.rackIndex !== undefined && t.rackIndex < displayRack.length) {
        displayRack[t.rackIndex] = null; // Mark as used
      }
    });
    return displayRack;
    // But PlayerRack renders `tile`. If `tile` is null, it might crash or render empty.
    // My PlayerRack checks `rack && rack.length`.
    // I should update PlayerRack to handle nulls? 
    // Or, cleaner: I can't easily change PlayerRack without another tool call.
    // Let's see PlayerRack again.
    // `rack.map((tile, index) => ... {tile})`. Use `{tile || ''}`?
    // If I pass null, it renders nothing. But the div is still there?
    // `DraggableTile` renders `tile`. If tile is null/false, it renders empty string.
    // I should probably filter out from `selectedTiles` in `Game.jsx` logic BEFORE passing to `PlayerRack`?
    // No, indices must match.
    // I'll stick to: used tiles are removed from `selectedTiles` list? No.
    // Let's just pass the raw rack and let PlayerRack render all. 
    // Visually, the user sees "A" in rack and "A" on board. That's confusing.
    // I need to hide it in Rack.
    // I'll update `Game.jsx` logic to filter `displayRack` to actually Remove items? 
    // No, then indices shift and `rackIndex` becomes invalid for subsequent moves.
    // Correct approach: `PlayerRack` creates `Draggable` items. 
    // If I unmount a Draggable item while it's "dragged" (or dropped), dnd-kit might complain or it's fine.
    // I entered a predicament. I didn't add a prop to PlayerRack to hide specific indices.
    // I can modify PlayerRack again OR I can just pass empty strings for used tiles and CSS hide them?
    // PlayerRack renders `<div ...>{tile}<span...>`. If tile is null, it renders empty.
    // Let's try passing `null` in place of used tiles.
  }

  // Helper to sync rack state
  const getDisplayRack = () => {
    if (!game || !game.rack) return [];
    return game.rack.map((tile, idx) => {
      const isUsed = selectedTiles.some(t => t.rackIndex === idx);
      return isUsed ? null : tile;
    });
  };

  if (loading) {
    return <div className="loading">Ładowanie gry...</div>;
  }

  if (!game) {
    return <div className="error">Nie znaleziono gry</div>;
  }

  return (
    <DndContext onDragEnd={handleDragEnd} sensors={sensors}>
      <div className="game-container">
        <header className="game-header">
          <h1>Scrabble {game.game_name ? game.game_name : `Gra #${gameId}`}</h1>
          <div className="game-meta">
            <span className="dict-badge">Słownik: {game.dictionary || 'PL'}</span>
          </div>
          <button onClick={() => navigate('/lobby')} className="btn-secondary">
            Powrót do Lobby
          </button>
        </header>

        <div className="game-content">
          <div className="game-main">
            <div className="game-info">
              <h3>Status: {game.status === 'waiting' ? 'Oczekiwanie' : game.status === 'active' ? 'W toku' : 'Zakończona'}</h3>
              <h3>Tura: {game.current_turn + 1}</h3>
              {game.status === 'active' && isMyTurn() && (
                <div className="turn-indicator">Twoja kolej!</div>
              )}
            </div>

            {error && <div className="error-message">{error}</div>}

            {game.status === 'waiting' && (
              <div className="waiting-section">
                <p>Oczekiwanie na graczy... ({game.players.length}/4)</p>
                {game.players.length >= 2 && (
                  <button onClick={handleStartGame} className="btn-primary">
                    Rozpocznij Grę
                  </button>
                )}
              </div>
            )}

            {game.status === 'active' && (
              <>
                <GameBoard
                  board={game.board_state}
                  selectedTiles={selectedTiles}
                />

                <PlayerRack
                  rack={getDisplayRack()}
                  disabled={!isMyTurn()}
                  isExchangeMode={exchangeMode}
                  selectedExchangeTiles={selectedExchangeTiles}
                  onToggleExchangeTile={toggleExchangeTile}
                />

                <div className="game-controls">
                  {!exchangeMode ? (
                    <>
                      <button
                        onClick={handlePlayWord}
                        disabled={!isMyTurn() || selectedTiles.length === 0}
                        className="btn-primary"
                      >
                        Zagraj Słowo
                      </button>
                      <button
                        onClick={handlePass}
                        disabled={!isMyTurn()}
                        className="btn-secondary"
                      >
                        Pasuj
                      </button>
                      <button
                        onClick={toggleExchangeMode}
                        disabled={!isMyTurn()}
                        className="btn-secondary"
                      >
                        Wymień Litery
                      </button>
                      <button
                        onClick={() => setSelectedTiles([])}
                        className="btn-secondary"
                      >
                        Wyczyść
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        onClick={handleExchange}
                        disabled={selectedExchangeTiles.length === 0}
                        className="btn-primary"
                      >
                        Potwierdź Wymianę ({selectedExchangeTiles.length})
                      </button>
                      <button
                        onClick={toggleExchangeMode}
                        className="btn-secondary"
                      >
                        Anuluj
                      </button>
                    </>
                  )}
                  <button
                    onClick={handleEndGame}
                    className="btn-danger"
                    style={{ marginLeft: 'auto', backgroundColor: '#dc3545', color: 'white' }}
                  >
                    Zakończ Grę
                  </button>
                </div>

                <div className="remaining-tiles">
                  Pozostało liter: {game.remaining_tiles || 0}
                </div>
              </>
            )}

            {game.status === 'finished' && (
              <div className="game-finished">
                <h2>Gra Zakończona!</h2>
                <p>Sprawdź wyniki poniżej.</p>
              </div>
            )}

            <div className="players-info">
              <h3>Gracze</h3>
              {game.players.map((player, idx) => (
                <div key={idx} className="player-info">
                  <span className="player-name">{player.username}</span>
                  <span className="player-score">Wynik: {player.score}</span>
                  {game.status === 'active' &&
                    player.player_order === (game.current_turn % game.players.length) && (
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
    </DndContext>
  );
}

export default Game;
