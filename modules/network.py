# modules/network.py
# Network module for online multiplayer

import socket
import pickle
import threading
import time


class GameServer:
    """Server for hosting multiplayer games."""

    def __init__(self, port=5555):
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = socket.gethostbyname(socket.gethostname())
        self.rooms = {}  # {room_code: {'players': [], 'game_state': {}}}
        self.running = False

    def start(self):
        """Start the server."""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            self.running = True
            print(f"✓ Server started on {self.host}:{self.port}")

            # Start accepting connections in a thread
            threading.Thread(target=self._accept_connections, daemon=True).start()
            return True
        except Exception as e:
            print(f"✗ Server error: {e}")
            return False

    def _accept_connections(self):
        """Accept incoming client connections."""
        while self.running:
            try:
                conn, addr = self.server_socket.accept()
                print(f"✓ Connection from {addr}")
                threading.Thread(target=self._handle_client, args=(conn, addr), daemon=True).start()
            except:
                break

    def _handle_client(self, conn, addr):
        """Handle individual client connection."""
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break

                message = pickle.loads(data)
                response = self._process_message(message, conn)

                if response:
                    conn.send(pickle.dumps(response))
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            conn.close()

    def _process_message(self, message, conn):
        """Process client messages."""
        msg_type = message.get('type')

        if msg_type == 'create_room':
            room_code = message['room_code']
            self.rooms[room_code] = {
                'players': [conn],
                'game_state': {'player_count': 1}
            }
            return {'status': 'success', 'player_id': 0, 'room_code': room_code}

        elif msg_type == 'join_room':
            room_code = message['room_code']
            if room_code in self.rooms:
                player_id = len(self.rooms[room_code]['players'])
                self.rooms[room_code]['players'].append(conn)
                self.rooms[room_code]['game_state']['player_count'] = player_id + 1
                return {'status': 'success', 'player_id': player_id, 'room_code': room_code}
            return {'status': 'error', 'message': 'Room not found'}

        elif msg_type == 'update':
            room_code = message['room_code']
            if room_code in self.rooms:
                # Broadcast to all players in room
                for player_conn in self.rooms[room_code]['players']:
                    if player_conn != conn:
                        try:
                            player_conn.send(pickle.dumps(message))
                        except:
                            pass
                return {'status': 'ok'}

        return {'status': 'unknown'}

    def stop(self):
        """Stop the server."""
        self.running = False
        self.server_socket.close()


class GameClient:
    """Client for connecting to multiplayer games."""

    def __init__(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.player_id = None
        self.room_code = None
        self.host = None
        self.port = 5555
        self.game_state = {}
        self.receive_thread = None

    def connect(self, host):
        """Connect to server."""
        try:
            self.host = host
            self.client_socket.connect((host, self.port))
            self.connected = True

            # Start receiving messages
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()

            print(f"✓ Connected to server at {host}")
            return True
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False

    def create_room(self, room_code):
        """Create a new room."""
        try:
            message = {'type': 'create_room', 'room_code': room_code}
            self.client_socket.send(pickle.dumps(message))

            response = pickle.loads(self.client_socket.recv(4096))
            if response['status'] == 'success':
                self.player_id = response['player_id']
                self.room_code = response['room_code']
                print(f"✓ Room created: {room_code}, Player ID: {self.player_id}")
                return True
            return False
        except Exception as e:
            print(f"✗ Create room error: {e}")
            return False

    def join_room(self, room_code):
        """Join an existing room."""
        try:
            message = {'type': 'join_room', 'room_code': room_code}
            self.client_socket.send(pickle.dumps(message))

            response = pickle.loads(self.client_socket.recv(4096))
            if response['status'] == 'success':
                self.player_id = response['player_id']
                self.room_code = response['room_code']
                print(f"✓ Joined room: {room_code}, Player ID: {self.player_id}")
                return True
            else:
                print(f"✗ {response.get('message', 'Failed to join')}")
                return False
        except Exception as e:
            print(f"✗ Join room error: {e}")
            return False

    def send_update(self, data):
        """Send game state update to server."""
        try:
            message = {
                'type': 'update',
                'room_code': self.room_code,
                'player_id': self.player_id,
                'data': data
            }
            self.client_socket.send(pickle.dumps(message))
        except Exception as e:
            print(f"Send error: {e}")

    def _receive_messages(self):
        """Receive messages from server."""
        while self.connected:
            try:
                data = self.client_socket.recv(4096)
                if data:
                    message = pickle.loads(data)
                    if message.get('type') == 'update':
                        # Update game state with received data
                        self.game_state = message.get('data', {})
            except Exception as e:
                print(f"Receive error: {e}")
                break

    def get_game_state(self):
        """Get current game state."""
        return self.game_state

    def disconnect(self):
        """Disconnect from server."""
        self.connected = False
        try:
            self.client_socket.close()
        except:
            pass


# Global server instance
_server_instance = None

def start_server():
    """Start global server instance."""
    global _server_instance
    if _server_instance is None:
        _server_instance = GameServer()
        return _server_instance.start()
    return True

def get_local_ip():
    """Get local IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return socket.gethostbyname(socket.gethostname())

