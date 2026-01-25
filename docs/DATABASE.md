# Dokumentacja Bazy Danych - Scrabble

## Przegląd

Aplikacja używa **PostgreSQL 15** jako bazy danych. ORM: **SQLAlchemy 2.0**.

## Konfiguracja

### Docker Compose
```yaml
db:
  image: postgres:15-alpine
  container_name: scrabble_db
  environment:
    POSTGRES_DB: scrabble
    POSTGRES_USER: scrabble_user
    POSTGRES_PASSWORD: scrabble_pass
  ports:
    - "5432:5432"
  volumes:
    - postgres_data:/var/lib/postgresql/data
```

### Connection String
```
postgresql://scrabble_user:scrabble_pass@db:5432/scrabble
```

---

## Diagram ERD

```mermaid
erDiagram
    users ||--o{ game_players : "plays"
    users ||--o{ chat_messages : "sends"
    users ||--|| rankings : "has"
    games ||--o{ game_players : "has"
    games ||--o{ game_moves : "contains"
    games ||--o{ chat_messages : "has"
    
    users {
        int id PK
        varchar username UK
        varchar email UK
        varchar hashed_password
        timestamp created_at
    }
    
    games {
        int id PK
        varchar game_name
        varchar dictionary
        varchar status
        int current_turn
        json board_state
        json bag_tiles
        timestamp created_at
        timestamp finished_at
    }
    
    game_players {
        int id PK
        int game_id FK
        int user_id FK
        int player_order
        int score
        json rack
        bool is_active
    }
    
    game_moves {
        int id PK
        int game_id FK
        int user_id FK
        int move_number
        varchar word
        json tiles_played
        int score
        bool is_pass
        bool is_exchange
        timestamp created_at
    }
    
    dictionary {
        int id PK
        varchar word
        varchar language
    }
    
    rankings {
        int id PK
        int user_id FK
        int total_games
        int wins
        int losses
        int total_score
        int highest_score
        int rating
    }
    
    chat_messages {
        int id PK
        int game_id FK
        int user_id FK
        text message
        timestamp created_at
    }
```

---

## Inicjalizacja (seed_database.py)

Skrypt uruchamiany automatycznie przy starcie backendu.

### Kroki
1. Oczekiwanie na bazę (30 prób × 2s)
2. Tworzenie tabel (SQLAlchemy)
3. Ładowanie słowników (PostgreSQL COPY)
4. Tworzenie użytkowników testowych

### Użytkownicy Testowi
| Username | Email | Hasło |
|----------|-------|-------|
| player1 | player1@example.com | password123 |
| player2 | player2@example.com | password123 |
| player3 | player3@example.com | password123 |
| player4 | player4@example.com | password123 |

---

## Relacje

| Tabela nadrzędna | Tabela podrzędna | Relacja | ON DELETE |
|------------------|------------------|---------|-----------|
| users | game_players | 1:N | CASCADE |
| users | rankings | 1:1 | CASCADE |
| users | chat_messages | 1:N | CASCADE |
| games | game_players | 1:N | CASCADE |
| games | game_moves | 1:N | CASCADE |
| games | chat_messages | 1:N | CASCADE |

---


## Backup i Restore

### Backup
```bash
docker exec scrabble_db pg_dump -U scrabble_user scrabble > backup.sql
```

### Restore
```bash
cat backup.sql | docker exec -i scrabble_db psql -U scrabble_user scrabble
```

---

## Healthcheck

```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U scrabble_user -d scrabble"]
  interval: 10s
  timeout: 5s
  retries: 5
```
