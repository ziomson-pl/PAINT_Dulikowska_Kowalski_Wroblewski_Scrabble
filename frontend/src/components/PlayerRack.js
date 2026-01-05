import React, { useState } from 'react';
import '../styles/PlayerRack.css';

function PlayerRack({ rack, selectedTiles, setSelectedTiles, disabled }) {
  const [selectedRackTiles, setSelectedRackTiles] = useState([]);

  const handleTileClick = (tile, index) => {
    if (disabled) return;

    if (selectedRackTiles.includes(index)) {
      // Deselect
      setSelectedRackTiles(selectedRackTiles.filter(i => i !== index));
    } else {
      // Select
      setSelectedRackTiles([...selectedRackTiles, index]);
    }
  };

  const handlePlaceTile = (row, col) => {
    if (selectedRackTiles.length === 0) return;

    const newTiles = selectedRackTiles.map(index => ({
      letter: rack[index],
      row: row,
      col: col,
      is_blank: rack[index] === '_'
    }));

    setSelectedTiles([...selectedTiles, ...newTiles]);
    setSelectedRackTiles([]);
  };

  return (
    <div className="rack-container">
      <h3>Your Tiles</h3>
      <div className="rack">
        {rack && rack.length > 0 ? (
          rack.map((tile, index) => (
            <div
              key={index}
              className={`rack-tile ${selectedRackTiles.includes(index) ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
              onClick={() => handleTileClick(tile, index)}
            >
              {tile}
              <span className="tile-value">{getTileValue(tile)}</span>
            </div>
          ))
        ) : (
          <p>No tiles in rack</p>
        )}
      </div>
      {selectedRackTiles.length > 0 && (
        <div className="rack-info">
          Selected {selectedRackTiles.length} tile(s). Click on board to place.
        </div>
      )}
    </div>
  );
}

const getTileValue = (letter) => {
  const values = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4,
    'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3,
    'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8,
    'Y': 4, 'Z': 10, '_': 0
  };
  return values[letter] || 0;
};

export default PlayerRack;
