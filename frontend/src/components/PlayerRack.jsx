import React from 'react';
import { useDraggable } from '@dnd-kit/core';
import { CSS } from '@dnd-kit/utilities';
import '../styles/PlayerRack.css';

function DraggableTile({ tile, index, disabled }) {
  const { attributes, listeners, setNodeRef, transform } = useDraggable({
    id: `rack-tile-${index}`,
    data: { tile, index, fromRack: true },
    disabled: disabled
  });

  const style = {
    transform: CSS.Translate.toString(transform),
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...listeners}
      {...attributes}
      className={`rack-tile ${disabled ? 'disabled' : ''}`}
    >
      {tile}
      <span className="tile-value">{getTileValue(tile)}</span>
    </div>
  );
}

function PlayerRack({ rack, disabled }) {
  return (
    <div className="rack-container">
      <h3>Twoje Litery</h3>
      <div className="rack">
        {rack && rack.length > 0 ? (
          rack.map((tile, index) => (
            <DraggableTile
              key={`${index}-${tile}`}
              tile={tile}
              index={index}
              disabled={disabled}
            />
          ))
        ) : (
          <p>Brak liter</p>
        )}
      </div>
      <div className="rack-info">
        Przeciągnij litery na planszę, aby ułożyć słowo.
      </div>
    </div>
  );
}

const getTileValue = (letter) => {
  const values = {
    'A': 1, 'I': 1, 'E': 1, 'O': 1, 'Z': 1, 'N': 1, 'R': 1, 'W': 1, 'S': 1,
    'C': 2, 'T': 2, 'Y': 2, 'K': 2, 'D': 2, 'P': 2, 'M': 2, 'U': 3, 'J': 3,
    'L': 2, 'Ł': 3, 'G': 3, 'B': 3, 'H': 3, 'F': 5, 'Ą': 5, 'Ę': 5, 'Ś': 5,
    'Ż': 5, 'Ź': 9, 'Ć': 6, 'Ń': 7, 'Ó': 5, '_': 0
  };
  return values[letter] || 0;
};

export default PlayerRack;
