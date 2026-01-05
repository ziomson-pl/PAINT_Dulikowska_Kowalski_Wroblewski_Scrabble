import React, { useState } from 'react';
import '../styles/GameBoard.css';

// Premium square positions
const TRIPLE_WORD = [[0,0],[0,7],[0,14],[7,0],[7,14],[14,0],[14,7],[14,14]];
const DOUBLE_WORD = [[1,1],[2,2],[3,3],[4,4],[1,13],[2,12],[3,11],[4,10],
                     [13,1],[12,2],[11,3],[10,4],[13,13],[12,12],[11,11],[10,10]];
const TRIPLE_LETTER = [[1,5],[1,9],[5,1],[5,5],[5,9],[5,13],[9,1],[9,5],
                       [9,9],[9,13],[13,5],[13,9]];
const DOUBLE_LETTER = [[0,3],[0,11],[2,6],[2,8],[3,0],[3,7],[3,14],[6,2],
                       [6,6],[6,8],[6,12],[7,3],[7,11],[8,2],[8,6],[8,8],
                       [8,12],[11,0],[11,7],[11,14],[12,6],[12,8],[14,3],[14,11]];

function GameBoard({ board, selectedTiles, setSelectedTiles }) {
  const [selectedCell, setSelectedCell] = useState(null);

  if (!board || board.length === 0) {
    return <div>Loading board...</div>;
  }

  const handleCellClick = (row, col) => {
    // Only allow placing on empty cells
    if (board[row][col]) {
      return;
    }

    setSelectedCell({ row, col });
  };

  const handleTilePlacement = (letter) => {
    if (!selectedCell) return;

    const newTile = {
      letter: letter,
      row: selectedCell.row,
      col: selectedCell.col,
      is_blank: false
    };

    // Check if tile already placed at this position
    const existingIndex = selectedTiles.findIndex(
      t => t.row === selectedCell.row && t.col === selectedCell.col
    );

    if (existingIndex >= 0) {
      const updated = [...selectedTiles];
      updated[existingIndex] = newTile;
      setSelectedTiles(updated);
    } else {
      setSelectedTiles([...selectedTiles, newTile]);
    }

    setSelectedCell(null);
  };

  const getCellClass = (row, col) => {
    const classes = ['board-cell'];
    
    // Check if tile is placed here
    const tile = board[row][col];
    if (tile) {
      classes.push('filled');
      return classes.join(' ');
    }

    // Check if this is a selected position
    const isSelected = selectedTiles.some(t => t.row === row && t.col === col);
    if (isSelected) {
      classes.push('selected-placement');
      return classes.join(' ');
    }

    // Add premium square classes
    const pos = `${row},${col}`;
    if (row === 7 && col === 7) {
      classes.push('center-star');
    } else if (isTripleWord(row, col)) {
      classes.push('triple-word');
    } else if (isDoubleWord(row, col)) {
      classes.push('double-word');
    } else if (isTripleLetter(row, col)) {
      classes.push('triple-letter');
    } else if (isDoubleLetter(row, col)) {
      classes.push('double-letter');
    }

    return classes.join(' ');
  };

  const isTripleWord = (row, col) => {
    return TRIPLE_WORD.some(([r, c]) => r === row && c === col);
  };

  const isDoubleWord = (row, col) => {
    return DOUBLE_WORD.some(([r, c]) => r === row && c === col);
  };

  const isTripleLetter = (row, col) => {
    return TRIPLE_LETTER.some(([r, c]) => r === row && c === col);
  };

  const isDoubleLetter = (row, col) => {
    return DOUBLE_LETTER.some(([r, c]) => r === row && c === col);
  };

  const getTileToDisplay = (row, col) => {
    // Check if there's a selected tile at this position
    const selectedTile = selectedTiles.find(t => t.row === row && t.col === col);
    if (selectedTile) {
      return selectedTile.letter;
    }

    // Check if there's a board tile
    const boardTile = board[row][col];
    if (boardTile) {
      return boardTile.letter;
    }

    return null;
  };

  return (
    <div className="board-container">
      <div className="board">
        {board.map((row, rowIndex) => (
          <div key={rowIndex} className="board-row">
            {row.map((cell, colIndex) => {
              const tileToDisplay = getTileToDisplay(rowIndex, colIndex);
              return (
                <div
                  key={colIndex}
                  className={getCellClass(rowIndex, colIndex)}
                  onClick={() => handleCellClick(rowIndex, colIndex)}
                >
                  {tileToDisplay && (
                    <div className="tile-on-board">
                      {tileToDisplay}
                    </div>
                  )}
                  {!tileToDisplay && rowIndex === 7 && colIndex === 7 && (
                    <span className="star">★</span>
                  )}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}

export default GameBoard;
