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
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow address reuse
        self.host = socket.gethostbyname(socket.gethostname())
        self.rooms = {}  # {room_code: {'players': [], 'player_names': [], 'game_state': {}}}
        self.running = False

    def start(self):
        """Start the server."""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            self.server_socket.settimeout(1.0)  # Add timeout to prevent blocking
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
            except socket.timeout:
                continue  # Just check if still running
            except:
                break

    def _handle_client(self, conn, addr):
        """Handle individual client connection."""
        conn.settimeout(5.0)  # Set timeout for client connections
        try:
            while self.running:
                data = conn.recv(4096)
                if not data:
                    break

                message = pickle.loads(data)
                response = self._process_message(message, conn)

                if response:
                    conn.send(pickle.dumps(response))
        except socket.timeout:
            print(f"Client {addr} timed out")
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            conn.close()

    def _process_message(self, message, conn):
        """Process client messages."""
        msg_type = message.get('type')

        if msg_type == 'create_room':
            room_code = message['room_code']
            player_name = message.get('player_name', 'Host')
            self.rooms[room_code] = {
                'players': [conn],
                'player_names': [player_name],
                'game_state': {'player_count': 1}
            }
            return {'status': 'success', 'player_id': 0, 'room_code': room_code, 'players': [player_name]}

        elif msg_type == 'join_room':
            room_code = message['room_code']
            player_name = message.get('player_name', f'Player{len(self.rooms.get(room_code, {}).get("players", [])) + 1}')
            if room_code in self.rooms:
                player_id = len(self.rooms[room_code]['players'])
                self.rooms[room_code]['players'].append(conn)
                self.rooms[room_code]['player_names'].append(player_name)
                self.rooms[room_code]['game_state']['player_count'] = player_id + 1

                # Notify all players about new player
                player_list = self.rooms[room_code]['player_names']
                for i, player_conn in enumerate(self.rooms[room_code]['players']):
                    try:
                        notify_msg = {
                            'type': 'player_joined',
                            'players': player_list,
                            'new_player': player_name
                        }
                        player_conn.send(pickle.dumps(notify_msg))
                    except:
                        pass

                return {'status': 'success', 'player_id': player_id, 'room_code': room_code, 'players': player_list}
            return {'status': 'error', 'message': 'Room not found'}

        elif msg_type == 'get_lobby':
            room_code = message['room_code']
            if room_code in self.rooms:
                return {
                    'status': 'success',
                    'players': self.rooms[room_code]['player_names'],
                    'player_count': len(self.rooms[room_code]['players'])
                }
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
        self.client_socket.settimeout(10.0)  # Set 10 second timeout to prevent infinite blocking
        self.connected = False
        self.player_id = None
        self.room_code = None
        self.host = None
        self.port = 5555
        self.game_state = {}
        self.lobby_players = []
        self.receive_thread = None
        self.on_player_joined = None  # Callback for when player joins
        self.response_lock = threading.Lock()
        self.pending_response = None

    def connect(self, host):
        """Connect to server."""
        try:
            self.host = host
            print(f"Connecting to {host}:{self.port}...")
            self.client_socket.connect((host, self.port))
            self.connected = True
            print(f"✓ Socket connected to server at {host}")

            # Start receiving messages in background thread
            self.receive_thread = threading.Thread(target=self._receive_messages, daemon=True)
            self.receive_thread.start()

            # Give the thread a moment to start
            time.sleep(0.1)

            print(f"✓ Connected to server at {host}")
            return True
        except socket.timeout:
            print(f"✗ Connection timeout - server didn't respond")
            return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False

    def create_room(self, room_code, player_name='Host'):
        """Create a new room."""
        try:
            message = {'type': 'create_room', 'room_code': room_code, 'player_name': player_name}
            print(f"Sending create_room request for: {room_code}")
            self.client_socket.send(pickle.dumps(message))

            # Wait for response with timeout
            print("Waiting for server response...")
            start_time = time.time()
            while time.time() - start_time < 5.0:  # 5 second timeout
                with self.response_lock:
                    if self.pending_response and self.pending_response.get('type') == 'create_room_response':
                        response = self.pending_response
                        self.pending_response = None

                        if response['status'] == 'success':
                            self.player_id = response['player_id']
                            self.room_code = response['room_code']
                            self.lobby_players = response.get('players', [player_name])
                            print(f"✓ Room created: {room_code}, Player ID: {self.player_id}")
                            return True
                        return False
                time.sleep(0.05)  # Small delay to prevent busy waiting

            print("✗ Timeout waiting for create_room response")
            return False
        except Exception as e:
            print(f"✗ Create room error: {e}")
            return False

    def join_room(self, room_code, player_name='Player'):
        """Join an existing room."""
        try:
            message = {'type': 'join_room', 'room_code': room_code, 'player_name': player_name}
            print(f"Sending join_room request for: {room_code}")
            self.client_socket.send(pickle.dumps(message))

            # Wait for response with timeout
            print("Waiting for server response...")
            start_time = time.time()
            while time.time() - start_time < 5.0:  # 5 second timeout
                with self.response_lock:
                    if self.pending_response and self.pending_response.get('type') == 'join_room_response':
                        response = self.pending_response
                        self.pending_response = None

                        if response['status'] == 'success':
                            self.player_id = response['player_id']
                            self.room_code = response['room_code']
                            self.lobby_players = response.get('players', [])
                            print(f"✓ Joined room: {room_code}, Player ID: {self.player_id}")
                            return True
                        else:
                            print(f"✗ {response.get('message', 'Failed to join')}")
                            return False
                time.sleep(0.05)  # Small delay to prevent busy waiting

            print("✗ Timeout waiting for join_room response")
            return False
        except Exception as e:
            print(f"✗ Join room error: {e}")
            return False

    def get_lobby_info(self):
        """Get current lobby information."""
        try:
            message = {'type': 'get_lobby', 'room_code': self.room_code}
            self.client_socket.send(pickle.dumps(message))

            # Wait for response with timeout
            start_time = time.time()
            while time.time() - start_time < 3.0:
                with self.response_lock:
                    if self.pending_response and self.pending_response.get('type') == 'get_lobby_response':
                        response = self.pending_response
                        self.pending_response = None

                        if response['status'] == 'success':
                            self.lobby_players = response['players']
                            return response
                        return None
                time.sleep(0.05)
            return None
        except Exception as e:
            print(f"Get lobby error: {e}")
            return None

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
        self.client_socket.settimeout(1.0)  # Use timeout in receive loop
        while self.connected:
            try:
                data = self.client_socket.recv(4096)
                if data:
                    message = pickle.loads(data)
                    msg_type = message.get('type')

                    if msg_type == 'update':
                        # Update game state with received data
                        self.game_state = message.get('data', {})
                    elif msg_type == 'player_joined':
                        # Update lobby players list
                        self.lobby_players = message.get('players', [])
                        if self.on_player_joined:
                            self.on_player_joined(message.get('new_player'))
                    else:
                        # Store response for pending requests
                        with self.response_lock:
                            # Tag the response type for easier matching
                            if message.get('status') in ['success', 'error']:
                                # This is a response to a request
                                self.pending_response = message
                                # Infer response type from context
                                if 'player_id' in message:
                                    if self.room_code is None:
                                        message['type'] = 'create_room_response'
                                    else:
                                        message['type'] = 'join_room_response'
                                elif 'player_count' in message:
                                    message['type'] = 'get_lobby_response'
                else:
                    break
            except socket.timeout:
                continue  # Just check if still connected
            except Exception as e:
                if self.connected:
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


# Utility functions
def start_server():
    """Start a game server."""
    try:
        server = GameServer()
        if server.start():
            # Store server instance globally so it stays running
            globals()['_game_server'] = server
            return True
        return False
    except Exception as e:
        print(f"✗ Failed to start server: {e}")
        return False


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
