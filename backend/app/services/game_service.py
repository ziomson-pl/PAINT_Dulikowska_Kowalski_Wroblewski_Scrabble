import random
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from app.models import Game, GamePlayer, Dictionary, GameMove

# Scrabble tile distribution
TILE_DISTRIBUTION = {
    'A': 9, 'B': 2, 'C': 2, 'D': 4, 'E': 12, 'F': 2, 'G': 3, 'H': 2,
    'I': 9, 'J': 1, 'K': 1, 'L': 4, 'M': 2, 'N': 6, 'O': 8, 'P': 2,
    'Q': 1, 'R': 6, 'S': 4, 'T': 6, 'U': 4, 'V': 2, 'W': 2, 'X': 1,
    'Y': 2, 'Z': 1, '_': 2  # _ represents blank tiles
}

# Letter values for scoring
LETTER_VALUES = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4,
    'I': 1, 'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3,
    'Q': 10, 'R': 1, 'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8,
    'Y': 4, 'Z': 10, '_': 0
}

# Premium squares on the board
TRIPLE_WORD = [(0, 0), (0, 7), (0, 14), (7, 0), (7, 14), (14, 0), (14, 7), (14, 14)]
DOUBLE_WORD = [(1, 1), (2, 2), (3, 3), (4, 4), (1, 13), (2, 12), (3, 11), (4, 10),
               (13, 1), (12, 2), (11, 3), (10, 4), (13, 13), (12, 12), (11, 11), (10, 10)]
TRIPLE_LETTER = [(1, 5), (1, 9), (5, 1), (5, 5), (5, 9), (5, 13), (9, 1), (9, 5),
                 (9, 9), (9, 13), (13, 5), (13, 9)]
DOUBLE_LETTER = [(0, 3), (0, 11), (2, 6), (2, 8), (3, 0), (3, 7), (3, 14), (6, 2),
                 (6, 6), (6, 8), (6, 12), (7, 3), (7, 11), (8, 2), (8, 6), (8, 8),
                 (8, 12), (11, 0), (11, 7), (11, 14), (12, 6), (12, 8), (14, 3), (14, 11)]

class GameService:
    def __init__(self, db: Session):
        self.db = db

    def create_game(self) -> Game:
        """Create a new game with empty board and full tile bag"""
        board_state = [[None for _ in range(15)] for _ in range(15)]
        bag_tiles = self._initialize_bag()
        
        game = Game(
            status="waiting",
            current_turn=0,
            board_state=board_state,
            bag_tiles=bag_tiles
        )
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        return game

    def _initialize_bag(self) -> List[str]:
        """Initialize the tile bag with standard Scrabble distribution"""
        bag = []
        for letter, count in TILE_DISTRIBUTION.items():
            bag.extend([letter] * count)
        random.shuffle(bag)
        return bag

    def join_game(self, game_id: int, user_id: int) -> Optional[GamePlayer]:
        """Add a player to a game"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game or game.status != "waiting":
            return None
        
        # Check if player already joined
        existing = self.db.query(GamePlayer).filter(
            GamePlayer.game_id == game_id,
            GamePlayer.user_id == user_id
        ).first()
        if existing:
            return existing
        
        # Check player count (max 4)
        player_count = self.db.query(GamePlayer).filter(GamePlayer.game_id == game_id).count()
        if player_count >= 4:
            return None
        
        # Draw initial rack (7 tiles)
        rack = self._draw_tiles(game, 7)
        
        game_player = GamePlayer(
            game_id=game_id,
            user_id=user_id,
            player_order=player_count,
            rack=rack
        )
        self.db.add(game_player)
        self.db.commit()
        self.db.refresh(game_player)
        return game_player

    def start_game(self, game_id: int) -> bool:
        """Start the game if conditions are met"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game or game.status != "waiting":
            return False
        
        player_count = self.db.query(GamePlayer).filter(GamePlayer.game_id == game_id).count()
        if player_count < 2:
            return False
        
        game.status = "active"
        self.db.commit()
        return True

    def _draw_tiles(self, game: Game, count: int) -> List[str]:
        """Draw tiles from the bag"""
        tiles = []
        bag = game.bag_tiles or []
        for _ in range(min(count, len(bag))):
            if bag:
                tiles.append(bag.pop())
        game.bag_tiles = bag
        return tiles

    def make_move(self, game_id: int, user_id: int, tiles_played: List[Dict], is_pass: bool = False, is_exchange: bool = False, exchange_tiles: List[str] = None) -> Tuple[Optional[GameMove], Optional[str]]:
        """Process a player's move"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game or game.status != "active":
            return None, "Game not active"
        
        player = self.db.query(GamePlayer).filter(
            GamePlayer.game_id == game_id,
            GamePlayer.user_id == user_id
        ).first()
        if not player:
            return None, "Player not in game"
        
        # Check if it's player's turn
        current_player_count = self.db.query(GamePlayer).filter(GamePlayer.game_id == game_id).count()
        expected_player_order = game.current_turn % current_player_count
        if player.player_order != expected_player_order:
            return None, "Not your turn"
        
        # Handle pass
        if is_pass:
            move = GameMove(
                game_id=game_id,
                user_id=user_id,
                move_number=game.current_turn,
                is_pass=True,
                score=0
            )
            self.db.add(move)
            game.current_turn += 1
            self.db.commit()
            return move, None
        
        # Handle exchange
        if is_exchange and exchange_tiles:
            rack = player.rack or []
            for tile in exchange_tiles:
                if tile in rack:
                    rack.remove(tile)
                    game.bag_tiles.append(tile)
            
            # Draw new tiles
            new_tiles = self._draw_tiles(game, len(exchange_tiles))
            rack.extend(new_tiles)
            player.rack = rack
            
            move = GameMove(
                game_id=game_id,
                user_id=user_id,
                move_number=game.current_turn,
                is_exchange=True,
                score=0
            )
            self.db.add(move)
            game.current_turn += 1
            self.db.commit()
            return move, None
        
        # Validate and place tiles
        board = game.board_state
        rack = player.rack or []
        
        # Validate tiles are in rack
        tiles_to_place = [t['letter'] for t in tiles_played]
        temp_rack = rack.copy()
        for tile in tiles_to_place:
            if tile in temp_rack:
                temp_rack.remove(tile)
            else:
                return None, f"Tile {tile} not in rack"
        
        # Place tiles on board
        placed_positions = []
        for tile in tiles_played:
            row, col = tile['row'], tile['col']
            if board[row][col] is not None:
                return None, f"Position ({row}, {col}) already occupied"
            board[row][col] = {
                'letter': tile['letter'],
                'is_blank': tile.get('is_blank', False)
            }
            placed_positions.append((row, col))
        
        # Validate word formation
        words = self._find_words(board, placed_positions)
        if not words:
            # Revert board
            for row, col in placed_positions:
                board[row][col] = None
            return None, "No valid words formed"
        
        # Validate all words in dictionary
        for word in words:
            if not self._is_valid_word(word):
                # Revert board
                for row, col in placed_positions:
                    board[row][col] = None
                return None, f"Invalid word: {word}"
        
        # Calculate score
        score = self._calculate_score(board, placed_positions, tiles_played)
        
        # Update game state
        game.board_state = board
        player.score += score
        player.rack = temp_rack
        
        # Draw new tiles
        new_tiles = self._draw_tiles(game, len(tiles_played))
        player.rack.extend(new_tiles)
        
        # Create move record
        main_word = max(words, key=len) if words else ""
        move = GameMove(
            game_id=game_id,
            user_id=user_id,
            move_number=game.current_turn,
            word=main_word,
            tiles_played=tiles_played,
            score=score
        )
        self.db.add(move)
        game.current_turn += 1
        
        # Check if game should end
        if not player.rack and not game.bag_tiles:
            game.status = "finished"
        
        self.db.commit()
        return move, None

    def _find_words(self, board: List[List], placed_positions: List[Tuple[int, int]]) -> List[str]:
        """Find all words formed by the placed tiles"""
        words = []
        
        # Check if tiles are in a line
        if not placed_positions:
            return words
        
        rows = [pos[0] for pos in placed_positions]
        cols = [pos[1] for pos in placed_positions]
        
        # Horizontal word
        if len(set(rows)) == 1:
            row = rows[0]
            min_col = min(cols)
            max_col = max(cols)
            
            # Extend to full word
            while min_col > 0 and board[row][min_col - 1] is not None:
                min_col -= 1
            while max_col < 14 and board[row][max_col + 1] is not None:
                max_col += 1
            
            word = ""
            for c in range(min_col, max_col + 1):
                if board[row][c] is not None:
                    word += board[row][c]['letter']
            
            if len(word) > 1:
                words.append(word)
            
            # Check vertical words for each placed tile
            for row, col in placed_positions:
                vertical_word = self._get_vertical_word(board, row, col)
                if len(vertical_word) > 1:
                    words.append(vertical_word)
        
        # Vertical word
        elif len(set(cols)) == 1:
            col = cols[0]
            min_row = min(rows)
            max_row = max(rows)
            
            # Extend to full word
            while min_row > 0 and board[min_row - 1][col] is not None:
                min_row -= 1
            while max_row < 14 and board[max_row + 1][col] is not None:
                max_row += 1
            
            word = ""
            for r in range(min_row, max_row + 1):
                if board[r][col] is not None:
                    word += board[r][col]['letter']
            
            if len(word) > 1:
                words.append(word)
            
            # Check horizontal words for each placed tile
            for row, col in placed_positions:
                horizontal_word = self._get_horizontal_word(board, row, col)
                if len(horizontal_word) > 1:
                    words.append(horizontal_word)
        
        return words

    def _get_horizontal_word(self, board: List[List], row: int, col: int) -> str:
        """Get horizontal word at position"""
        min_col = col
        max_col = col
        
        while min_col > 0 and board[row][min_col - 1] is not None:
            min_col -= 1
        while max_col < 14 and board[row][max_col + 1] is not None:
            max_col += 1
        
        word = ""
        for c in range(min_col, max_col + 1):
            if board[row][c] is not None:
                word += board[row][c]['letter']
        
        return word

    def _get_vertical_word(self, board: List[List], row: int, col: int) -> str:
        """Get vertical word at position"""
        min_row = row
        max_row = row
        
        while min_row > 0 and board[min_row - 1][col] is not None:
            min_row -= 1
        while max_row < 14 and board[max_row + 1][col] is not None:
            max_row += 1
        
        word = ""
        for r in range(min_row, max_row + 1):
            if board[r][col] is not None:
                word += board[r][col]['letter']
        
        return word

    def _calculate_score(self, board: List[List], placed_positions: List[Tuple[int, int]], tiles_played: List[Dict]) -> int:
        """Calculate score for placed tiles"""
        score = 0
        word_multiplier = 1
        
        for row, col in placed_positions:
            tile = board[row][col]
            letter_value = LETTER_VALUES.get(tile['letter'], 0)
            
            # Apply letter multipliers
            if (row, col) in TRIPLE_LETTER:
                letter_value *= 3
            elif (row, col) in DOUBLE_LETTER:
                letter_value *= 2
            
            score += letter_value
            
            # Apply word multipliers
            if (row, col) in TRIPLE_WORD:
                word_multiplier *= 3
            elif (row, col) in DOUBLE_WORD:
                word_multiplier *= 2
        
        score *= word_multiplier
        
        # Bonus for using all 7 tiles
        if len(tiles_played) == 7:
            score += 50
        
        return score

    def _is_valid_word(self, word: str) -> bool:
        """Check if word exists in dictionary"""
        word_upper = word.upper()
        return self.db.query(Dictionary).filter(Dictionary.word == word_upper).first() is not None
