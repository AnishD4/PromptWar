# Prompt Wars

A 2D retro-style multiplayer fighting game where players type prompts to forge AI-generated weapons and battle on floating platforms!

## 🎮 Game Overview

Prompt Wars is inspired by Super Smash Bros. Players fight on platforms, can be knocked off edges, and use AI-generated weapons forged from text prompts. Built for a 4-hour hackathon using Pygame.

## 🚀 Features

- **AI Weapon Generation**: Type creative prompts to forge unique weapons
- **Platform Fighting**: Jump between platforms and knock opponents off the stage
- **Multiplayer**: Support for up to 4 players
- **Health & Knockback System**: Strategic combat with damage and knockback mechanics
- **Round Timer**: 3-minute rounds with score tracking

## 📁 Project Structure

```
PromptWars/
├── main.py                 # Main game loop
├── settings.py             # Global constants and settings
├── modules/
│   ├── player.py          # Player movement, health, knockback (T1)
│   ├── weapon.py          # Weapon properties and collision (T2)
│   ├── ai_client.py       # AI weapon generation (T2)
│   ├── ui.py              # HUD, health bars, timer, input (T3)
│   └── game_manager.py    # Round management, game state (T1)
├── assets/
│   ├── images/            # Sprites and graphics
│   ├── sounds/            # Sound effects
│   └── fonts/             # Custom fonts
├── backgrounds/           # Background images
└── requirements.txt       # Python dependencies
```

## 🛠️ Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the game:
   ```bash
   python main.py
   ```

## 🎯 Team Roles

- **T1 (Gameplay/Player)**: Player movement, knockback, health, respawn logic
- **T2 (AI Weapons)**: Weapon generation, AI integration, weapon stats
- **T3 (UI)**: HUD, health bars, timer, weapon prompt input, notifications

## 🎮 Controls

- **Arrow Keys / WASD**: Move player
- **Space**: Jump
- **Click Input Box**: Type weapon prompt
- **Enter / Click Forge**: Create weapon from prompt

## 📝 Weapon Prompts

Try creative prompts like:
- "massive fire sword"
- "swift lightning spear"
- "heavy ice hammer"
- "quick wind blade"

The AI generates weapon stats based on your description!

## 🔧 TODO

- [ ] Connect to actual AI API for weapon generation
- [ ] Add sound effects and music
- [ ] Implement power-ups
- [ ] Add character sprites
- [ ] Network multiplayer support
- [ ] Menu system

## 📄 License

MIT License - Built for educational purposes during hackathon.

