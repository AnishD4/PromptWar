# 🎮 PROMPT WARS - MULTIPLAYER GUIDE

## 🌐 How to Play Multiplayer on Same WiFi

### Quick Start Guide

#### **Player 1 (HOST):**
1. Launch the game
2. Click **"CREATE ROOM"**
3. Enter a room name (e.g., "EPIC_BATTLE")
4. Click **"START GAME"**
5. **Share your IP address** (displayed on screen) with Player 2
6. Share the room name with Player 2
7. Wait for Player 2 to connect - you'll see them appear!

#### **Player 2 (CLIENT):**
1. Launch the game
2. Click **"JOIN ROOM"**
3. Enter the **HOST's IP address** (ask Player 1)
4. Enter the **room code/name** (same as Player 1)
5. Click **"JOIN"**
6. You're in! Start fighting!

---

## 🎯 Controls

### Host (Player 1):
- **Move:** A/D keys
- **Jump:** W key
- **Forge Weapon:** Click input box, type prompt, click "Forge Weapon"

### Client (Player 2):
- **Move:** Arrow keys (←/→)
- **Jump:** Arrow key (↑)
- **Forge Weapon:** Click input box, type prompt, click "Forge Weapon"

---

## 🔧 Technical Details

### Network Setup:
- **Protocol:** TCP/IP over local network
- **Default Port:** 5555
- **Update Rate:** ~30 updates per second
- **Synced Data:** Player position, velocity, health, alive status

### Finding Your IP Address:
The game automatically displays your local IP when hosting. If you need to find it manually:

**Windows (cmd):**
```
ipconfig
```
Look for "IPv4 Address" under your active network adapter.

**Example:** 192.168.1.100

---

## 🐛 Troubleshooting

### Connection Failed?
1. **Same WiFi?** Both players MUST be on the same WiFi network
2. **Firewall:** Windows Firewall may block the connection. Allow Python through firewall:
   - Windows Security → Firewall → Allow app through firewall
   - Find Python and check both Private and Public networks
3. **Wrong IP?** Make sure you're using the host's LOCAL IP (192.168.x.x or 10.x.x.x)
4. **Port Blocked?** Port 5555 must be available

### Can't Join Room?
- Double-check the room name matches EXACTLY
- Make sure the host started their game first
- Verify IP address is correct

### Lag or Stuttering?
- This is normal for a hackathon project! 
- Network updates run at ~30 Hz for performance
- Close other network-heavy applications

---

## 🎪 Gameplay Tips

1. **Communication:** Use voice chat or text to coordinate with your opponent
2. **Weapon Forging:** Each player can forge their own AI-generated weapons
3. **Platform Fighting:** Knock your opponent off platforms to deal damage!
4. **Health Bars:** Watch both players' health at the top of the screen
5. **Round Timer:** You have limited time per round - make it count!

---

## 🏗️ Architecture (For Developers)

### Files Modified:
- `main.py` - Added network initialization and multiplayer game loop
- `modules/menu.py` - Added IP input field and network UI
- `modules/network.py` - Server/Client implementation (already existed)

### How It Works:
1. Host creates a GameServer instance and GameClient connects to localhost
2. Client connects to host's IP and joins the same room code
3. Both players send position/state updates every 33ms
4. Remote player state is interpolated for smooth movement
5. Local player controls their own character, network syncs the other

### Key Functions:
- `start_server()` - Starts TCP server on port 5555
- `GameClient.connect(ip)` - Connect to host
- `GameClient.create_room(code)` - Host creates room
- `GameClient.join_room(code)` - Client joins room
- `GameClient.send_update(data)` - Send player state
- `GameClient.get_game_state()` - Receive remote player state

---

## 📝 Notes

- **Current Limitation:** Only 2 players supported per game
- **Weapon Sync:** Weapon spawning is local-only (not synced) for hackathon simplicity
- **No Reconnect:** If connection drops, return to menu and rejoin
- **LAN Only:** This implementation is for local network play only

---

## 🚀 Future Enhancements

If you want to extend this:
- [ ] Add weapon synchronization across network
- [ ] Support 3-4 players
- [ ] Add latency compensation/prediction
- [ ] Internet play with port forwarding
- [ ] In-game chat
- [ ] Connection status indicator
- [ ] Lobby system with player list

---

## ✨ Have Fun!

Now go forge some weapons and battle your friends! 

**Made for hackathon with ❤️**

