# Dokumentacja Frontendu - Scrabble

## Przegląd

Frontend aplikacji Scrabble zbudowany w **React 19** z bundlerem **Vite**. Interfejs z drag-and-drop (dnd-kit) i czatem WebSocket.

## Technologie

| Technologia | Wersja | Opis |
|-------------|--------|------|
| React | 19.2.3 | Biblioteka UI |
| Vite | 7.2.4 | Bundler |
| React Router DOM | 7.11.0 | Routing SPA |
| Axios | 1.13.2 | Klient HTTP |
| @dnd-kit/core | 6.1.0 | Drag and Drop |

## Struktura Katalogów

```
frontend/src/
├── main.jsx            # Punkt wejścia
├── App.jsx             # Routing
├── components/
│   ├── GameBoard.jsx   # Plansza 15x15
│   ├── PlayerRack.jsx  # Stojak gracza
│   └── Chat.jsx        # Czat WebSocket
├── pages/
│   ├── Login.jsx       # Logowanie
│   ├── Register.jsx    # Rejestracja
│   ├── Lobby.jsx       # Lista gier
│   ├── Game.jsx        # Widok gry
│   ├── Profile.jsx     # Profil
│   └── Rankings.jsx    # Rankingi
├── services/
│   ├── api.js          # Klient axios
│   └── chat.js         # WebSocket
└── styles/             # CSS
```

## Routing

| Ścieżka | Komponent | Opis |
|---------|-----------|------|
| `/login` | Login | Logowanie |
| `/register` | Register | Rejestracja |
| `/lobby` | Lobby | Lista gier |
| `/game/:gameId` | Game | Widok gry |
| `/profile` | Profile | Profil |
| `/rankings` | Rankings | Rankingi |

## Serwis API (`services/api.js`)

### Konfiguracja
```javascript
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
```

### authAPI
- `register(username, email, password)` - Rejestracja
- `login(username, password)` - Logowanie

### gameAPI
- `createGame(gameData)` - Tworzenie gry
- `listGames()` - Lista gier
- `getGame(gameId)` - Szczegóły gry
- `joinGame(gameId)` - Dołączenie
- `startGame(gameId)` - Start gry
- `makeMove(gameId, moveData)` - Ruch
- `endGame(gameId)` - Zakończenie

### profileAPI
- `getProfile()` - Profil użytkownika
- `getRankings()` - Rankingi
- `getHistory()` - Historia gier

## Serwis Chat (`services/chat.js`)

```javascript
const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';
```

- `connect(gameId, username, userId)` - Połączenie WS
- `sendMessage(message)` - Wysyłanie
- `onMessage(callback)` - Odbiór
- `disconnect()` - Rozłączenie

## Główny Widok Gry (`pages/Game.jsx`)

### Stan
| Zmienna | Opis |
|---------|------|
| `game` | Stan gry z backendu |
| `selectedTiles` | Płytki umieszczone w turze |
| `exchangeMode` | Tryb wymiany liter |

### Funkcje
| Funkcja | Opis |
|---------|------|
| `handleDragEnd()` | Obsługa upuszczenia płytki |
| `handlePlayWord()` | Zagranie słowa |
| `handlePass()` | Pasowanie |
| `handleExchange()` | Wymiana liter |
| `handleEndGame()` | Zakończenie gry |
| `isMyTurn()` | Sprawdzenie czy moja tura |

### Polling
Stan gry odświeżany co 2 sekundy.

## GameBoard (`components/GameBoard.jsx`)

Plansza 15x15 z polami premium.

### Pola Premium
| Klasa | Opis |
|-------|------|
| `triple-word` | 3x słowo |
| `double-word` | 2x słowo |
| `triple-letter` | 3x litera |
| `double-letter` | 2x litera |
| `center-star` | Środek (7,7) |

### Subkomponenty
- `DroppableCell` - Pole z obsługą upuszczania
- `DraggableBoardTile` - Przeciągana płytka

## PlayerRack (`components/PlayerRack.jsx`)

Stojak gracza z 7 literami.

### Props
| Prop | Opis |
|------|------|
| `rack` | Litery (null = użyta) |
| `disabled` | Nie twoja tura |
| `isExchangeMode` | Tryb wymiany |

### Wartości Liter (Polski)
```javascript
{
  'A': 1, 'I': 1, 'E': 1, 'O': 1, 'Z': 1, 'N': 1, 'R': 1, 'W': 1, 'S': 1,
  'C': 2, 'T': 2, 'Y': 2, 'K': 2, 'D': 2, 'P': 2, 'M': 2, 'L': 2,
  'U': 3, 'J': 3, 'Ł': 3, 'G': 3, 'B': 3, 'H': 3,
  'F': 5, 'Ą': 5, 'Ę': 5, 'Ś': 5, 'Ż': 5, 'Ó': 5,
  'Ć': 6, 'Ń': 7, 'Ź': 9, '_': 0
}
```

## Chat (`components/Chat.jsx`)

Czat w czasie rzeczywistym przez WebSocket.

- Ładowanie historii: `GET /api/games/{id}/messages`
- Real-time: WebSocket `/ws/chat/{gameId}`

## Zmienne Środowiskowe

| Zmienna | Domyślna |
|---------|----------|
| `VITE_API_URL` | `http://localhost:8000` |
| `VITE_WS_URL` | `ws://localhost:8000` |

## Docker

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 3000
CMD ["npm", "run", "start"]
```

## Komendy NPM

| Komenda | Opis |
|---------|------|
| `npm run start` | Dev server (port 3000) |
| `npm run build` | Build produkcyjny |
| `npm run lint` | ESLint |

## Lokalizacja (Polski)

Cały interfejs w języku polskim:
- "Logowanie", "Nazwa użytkownika:", "Hasło:", "Zaloguj"
- "Stwórz nową grę", "Słownik:", "Polski", "Angielski"
- "Zagraj Słowo", "Pasuj", "Wymień Litery", "Zakończ Grę"
- "Twoje Litery", "Twoja kolej!", "Wynik:"
- "Czat", "Wpisz wiadomość...", "Wyślij"
