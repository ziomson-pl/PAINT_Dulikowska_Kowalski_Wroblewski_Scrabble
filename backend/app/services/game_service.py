import random
import re
from typing import List, Dict, Optional, Tuple
from collections import Counter
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
from app.models import Game, GamePlayer, Dictionary, GameMove
from app.services.ranking_service import RankingService

# Polish Scrabble tile distribution (100 tiles)
POLISH_TILE_DISTRIBUTION = {
    'A': 9, 'I': 8, 'E': 7, 'O': 6, 'Z': 5, 'N': 5, 'R': 4, 'W': 4,
    'S': 4, 'C': 3, 'T': 3, 'Y': 4, 'K': 3, 'D': 3, 'P': 3, 'M': 3,
    'U': 2, 'J': 2, 'L': 3, 'Ł': 2, 'G': 2, 'B': 2, 'H': 2, 'Ą': 1,
    'Ę': 1, 'F': 1, 'Ś': 1, 'Ż': 1, 'Ź': 1, 'Ć': 1, 'Ń': 1, 'Ó': 1,
    '_': 2  # Blanks
}

# Polish Letter values
POLISH_LETTER_VALUES = {
    'A': 1, 'I': 1, 'E': 1, 'O': 1, 'Z': 1, 'N': 1, 'R': 1, 'W': 1, 'S': 1,
    'C': 2, 'T': 2, 'Y': 2, 'K': 2, 'D': 2, 'P': 2, 'M': 2, 'U': 3, 'J': 3,
    'L': 2, 'Ł': 3, 'G': 3, 'B': 3, 'H': 3, 'F': 5, 'Ą': 5, 'Ę': 5, 'Ś': 5,
    'Ż': 5, 'Ź': 9, 'Ć': 6, 'Ń': 7, 'Ó': 5, '_': 0
}

# English Scrabble tile distribution (100 tiles)
ENGLISH_TILE_DISTRIBUTION = {
    'A': 9, 'B': 2, 'C': 2, 'D': 4, 'E': 12, 'F': 2, 'G': 3, 'H': 2, 'I': 9,
    'J': 1, 'K': 1, 'L': 4, 'M': 2, 'N': 6, 'O': 8, 'P': 2, 'Q': 1, 'R': 6,
    'S': 4, 'T': 6, 'U': 4, 'V': 2, 'W': 2, 'X': 1, 'Y': 2, 'Z': 1, '_': 2  # Blanks
}

# English Letter values
ENGLISH_LETTER_VALUES = {
    'A': 1, 'B': 3, 'C': 3, 'D': 2, 'E': 1, 'F': 4, 'G': 2, 'H': 4, 'I': 1,
    'J': 8, 'K': 5, 'L': 1, 'M': 3, 'N': 1, 'O': 1, 'P': 3, 'Q': 10, 'R': 1,
    'S': 1, 'T': 1, 'U': 1, 'V': 4, 'W': 4, 'X': 8, 'Y': 4, 'Z': 10, '_': 0
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

    def _get_tile_distribution(self, dictionary: str = "PL") -> Dict[str, int]:
        """Get tile distribution based on dictionary language"""
        if dictionary == "EN":
            return ENGLISH_TILE_DISTRIBUTION
        return POLISH_TILE_DISTRIBUTION

    def _get_letter_values(self, dictionary: str = "PL") -> Dict[str, int]:
        """Get letter values based on dictionary language"""
        if dictionary == "EN":
            return ENGLISH_LETTER_VALUES
        return POLISH_LETTER_VALUES

    def create_game(self, game_name: str = None, dictionary: str = "PL") -> Game:
        """Create a new game with empty board and full tile bag"""
        board_state = [[None for _ in range(15)] for _ in range(15)]
        bag_tiles = self._initialize_bag(dictionary)
        
        game = Game(
            game_name=game_name,
            dictionary=dictionary,
            status="waiting",
            current_turn=0,
            board_state=board_state,
            bag_tiles=bag_tiles
        )
        self.db.add(game)
        self.db.commit()
        self.db.refresh(game)
        return game

    def _initialize_bag(self, dictionary: str = "PL") -> List[str]:
        """Initialize the tile bag with proper distribution based on dictionary"""
        tile_dist = self._get_tile_distribution(dictionary)
        bag = []
        for letter, count in tile_dist.items():
            bag.extend([letter] * count)
        random.shuffle(bag)
        return bag

    def join_game(self, game_id: int, user_id: int) -> Optional[GamePlayer]:
        """Add a player to a game"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game or game.status != "waiting":
            return None
        
        existing = self.db.query(GamePlayer).filter(
            GamePlayer.game_id == game_id,
            GamePlayer.user_id == user_id
        ).first()
        if existing:
            return existing
        
        player_count = self.db.query(GamePlayer).filter(GamePlayer.game_id == game_id).count()
        if player_count >= 4:
            return None
        
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

    from datetime import datetime, timezone

    def end_game(self, game_id: int, user_id: int) -> bool:
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return False

        player = self.db.query(GamePlayer).filter(
            GamePlayer.game_id == game_id,
            GamePlayer.user_id == user_id
        ).first()
        if not player:
            return False

        if game.status == "finished":
            return False

        if game.status not in ["waiting", "active"]:
            return False

        players = (
            self.db.query(GamePlayer)
            .filter(GamePlayer.game_id == game_id)
            .all()
        )
        if not players:
            return False

        try:
            game.status = "finished"
            game.finished_at = datetime.utcnow()

            max_score = max(p.score for p in players)
            ranking_service = RankingService(self.db)

            for gp in players:
                ranking_service.update_after_game(
                    user_id=gp.user_id,
                    score=gp.score,
                    is_winner=(gp.score == max_score)
                )

            self.db.commit()
            return True

        except Exception as e:
            self.db.rollback()
            print("END GAME ERROR:", e)
            raise


    def _draw_tiles(self, game: Game, count: int) -> List[str]:
        """Draw tiles from the bag"""
        bag = list(game.bag_tiles) if game.bag_tiles else []
        tiles = []
        
        if not bag:
           return []

        for _ in range(min(count, len(bag))):
            idx = random.randint(0, len(bag) - 1)
            tiles.append(bag.pop(idx))
            
        game.bag_tiles = list(bag)
        
        self.db.add(game) 
        
        return tiles

    def make_move(self, game_id: int, user_id: int, tiles_played: List[Dict], is_pass: bool = False, is_exchange: bool = False, exchange_tiles: List[str] = None) -> Tuple[Optional[GameMove], Optional[str]]:
        """Process a player's move"""
        game = self.db.query(Game).filter(Game.id == game_id).first()
        if not game:
            return None, "Game not found"
        if game.status != "active":
            return None, f"Game not active (status: {game.status})"
        
        player = self.db.query(GamePlayer).filter(
            GamePlayer.game_id == game_id,
            GamePlayer.user_id == user_id
        ).first()
        if not player:
            return None, "Player not in game"
        
        self.db.refresh(player)
        
        self.db.refresh(game)
        active_players = self.db.query(GamePlayer).filter(
            GamePlayer.game_id == game_id,
            GamePlayer.is_active == True
        ).order_by(GamePlayer.player_order).all()
        
        if not active_players:
            return None, "No active players in game"
        
        current_player_index = game.current_turn % len(active_players)
        current_player_id = active_players[current_player_index].id
        
        if player.id != current_player_id:
            return None, "Not your turn"
        
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
        
        if is_exchange and exchange_tiles:
            rack = player.rack or []
            for tile in exchange_tiles:
                if tile in rack:
                    rack.remove(tile)
                    game.bag_tiles.append(tile)
            
            new_tiles = self._draw_tiles(game, len(exchange_tiles))
            rack.extend(new_tiles)
            player.rack = rack
            flag_modified(player, "rack")
            flag_modified(game, "bag_tiles")
            
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
        
        board = [row[:] for row in game.board_state] if game.board_state else [[None for _ in range(15)] for _ in range(15)]
        rack = player.rack or []
        
        is_first_move = all(all(cell is None for cell in row) for row in board)
        
        tiles_to_place = [t['letter'] for t in tiles_played]
        rack_counter = Counter(rack)
        tiles_counter = Counter(tiles_to_place)
        
        for tile, count in tiles_counter.items():
            if rack_counter[tile] < count:
                return None, f"Not enough {tile} tiles in rack"
        
        temp_rack = rack.copy()
        for tile in tiles_to_place:
            temp_rack.remove(tile)
        
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
        
        if is_first_move:
            goes_through_center = any(row == 7 and col == 7 for row, col in placed_positions)
            if not goes_through_center:
                for row, col in placed_positions:
                    board[row][col] = None
                return None, "First move must go through the center square (7,7)"
        else:
            has_connection = self._tiles_connect_to_existing(board, placed_positions)
            if not has_connection:
                for row, col in placed_positions:
                    board[row][col] = None
                return None, "Tiles must connect to existing words on the board"
        
        words = self._find_words(board, placed_positions)
        if not words:
            for row, col in placed_positions:
                board[row][col] = None
            return None, "No valid words formed. Tiles must form at least one valid word."
        
        for word in words:
            if not self._is_valid_word(word, game.dictionary):
                for row, col in placed_positions:
                    board[row][col] = None
                return None, f"Invalid word: {word}"
        
        score = self._calculate_score(board, placed_positions, tiles_played, game.dictionary)
        
        game.board_state = [row[:] for row in board]
        flag_modified(game, "board_state")
        player.score += score
        player.rack = temp_rack
        flag_modified(player, "rack")
        
        new_tiles = self._draw_tiles(game, len(tiles_played))
        player.rack.extend(new_tiles)
        
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
        
        if not player.rack and not game.bag_tiles:
            game.status = "finished"
        
        self.db.commit()
        return move, None

    def _find_words(self, board: List[List], placed_positions: List[Tuple[int, int]]) -> List[str]:
        """Find all words formed by the placed tiles"""
        words = []
        
        if not placed_positions:
            return words
        
        rows = sorted([pos[0] for pos in placed_positions])
        cols = sorted([pos[1] for pos in placed_positions])
        
        same_row = len(set(rows)) == 1
        same_col = len(set(cols)) == 1
        
        if not same_row and not same_col:
            return words
        
        if same_row:
            row = rows[0]
            min_col = min(cols)
            max_col = max(cols)
            
            for col in range(min_col, max_col + 1):
                if board[row][col] is None:
                    return words
            
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
            
            for row, col in placed_positions:
                vertical_word = self._get_vertical_word(board, row, col)
                if len(vertical_word) > 1:
                    words.append(vertical_word)
        
        elif same_col:
            col = cols[0]
            min_row = min(rows)
            max_row = max(rows)
            
            for row in range(min_row, max_row + 1):
                if board[row][col] is None:
                    return words
            
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

    def _tiles_connect_to_existing(self, board: List[List], placed_positions: List[Tuple[int, int]]) -> bool:
        """Check if placed tiles connect to existing tiles on the board"""
        for row, col in placed_positions:
            # Check adjacent positions (up, down, left, right)
            adjacent_positions = [
                (row - 1, col),  # up
                (row + 1, col),  # down
                (row, col - 1),  # left
                (row, col + 1)   # right
            ]
            
            for adj_row, adj_col in adjacent_positions:
                if 0 <= adj_row < 15 and 0 <= adj_col < 15:
                    if board[adj_row][adj_col] is not None:
                        if (adj_row, adj_col) not in placed_positions:
                            return True
        
        return False

    def _calculate_score(self, board: List[List], placed_positions: List[Tuple[int, int]], tiles_played: List[Dict], dictionary: str = "PL") -> int:
        """Calculate score for placed tiles based on dictionary"""
        letter_values = self._get_letter_values(dictionary)
        score = 0
        word_multiplier = 1
        
        for row, col in placed_positions:
            tile = board[row][col]
            letter_value = letter_values.get(tile['letter'], 0)
            
            if (row, col) in TRIPLE_LETTER:
                letter_value *= 3
            elif (row, col) in DOUBLE_LETTER:
                letter_value *= 2
            
            score += letter_value
            
            if (row, col) in TRIPLE_WORD:
                word_multiplier *= 3
            elif (row, col) in DOUBLE_WORD:
                word_multiplier *= 2
        
        score *= word_multiplier
        
        if len(tiles_played) == 7:
            score += 50
        
        return score

    def _is_valid_word(self, word: str, dictionary: str = "PL") -> bool:
        """Check if word exists in dictionary, filtered by language.
        Handles blank tiles (_) by treating them as wildcards."""
        word_upper = word.upper()
        word_len = len(word_upper)
        
        if '_' not in word_upper:
            return self.db.query(Dictionary).filter(
                Dictionary.word == word_upper,
                Dictionary.language == dictionary
            ).first() is not None
        
        from sqlalchemy import func
        matching_words = self.db.query(Dictionary.word).filter(
            Dictionary.language == dictionary,
            func.length(Dictionary.word) == word_len
        ).all()
        
        pattern = word_upper.replace('_', '.')
        regex = re.compile(f'^{pattern}$')
        
        return any(regex.match(row[0]) for row in matching_words)
