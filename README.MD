# Chess App

Plataforma web de ajedrez construida con Python y Flask.

## Características

- Registro y login de usuarios con contraseñas encriptadas
- Juega contra Stockfish con niveles de dificultad (Fácil, Medio, Difícil, Experto)
- Modo 1v1 online en tiempo real con WebSockets
- Sala de espera para crear o unirse a partidas
- Historial de partidas con reproducción movimiento a movimiento
- Dashboard con estadísticas: victorias, derrotas, empates y tasa de victorias
- Sistema de notas personal por usuario

## Tecnologías

- Python 3 + Flask
- Flask-SQLAlchemy (SQLite)
- Flask-Login
- Flask-SocketIO
- Stockfish WebAssembly
- chessboard.js + chess.js

## Cómo correrla localmente

1. Clona el repositorio
2. Crea y activa el entorno virtual:
   python -m venv venv
   .\venv\Scripts\Activate.ps1
3. Instala dependencias:
   pip install -r requirements.txt
4. Corre la app:
   python run.py
5. Abre http://127.0.0.1:5000