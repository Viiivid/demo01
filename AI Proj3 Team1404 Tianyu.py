import requests
import math

# API Configuration
USER_ID = '3594'
API_KEY = 'e48cc3bbb8c4642b3000'
TEAM_ID = '1404'  # Your Team ID
HEADERS = {
    'x-api-key': API_KEY,
    'userId': USER_ID,
    'Content-Type': 'application/x-www-form-urlencoded',
    'User-Agent': 'PostmanRuntime/7.37.0',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': '*/*',
    'Connection': 'keep-alive'
}
BASE_URL = "https://www.notexponential.com/aip2pgaming/api/index.php"

def get_game_state(game_id):
    params = {'type': 'boardString', 'gameId': game_id}
    response = requests.get(BASE_URL, headers=HEADERS, params=params)
    if response.ok:
        board_string = response.json()['output']
        print("Fetched board string:", board_string)
        board = [list(row) for row in board_string.strip().split('\n')]
        return board
    else:
        print(f"Error fetching game state: {response.text}")
        return None

def post_move(game_id, move):
    x, y = move
    payload = {
        'type': 'move',
        'gameId': game_id,
        'teamId': TEAM_ID,
        'move': f"{x},{y}",
    }
    response = requests.post(BASE_URL, headers=HEADERS, data=payload)
    if response.ok and response.json().get('code') == 'OK':
        print("Move posted successfully.")
    else:
        print(f"Error posting move: {response.text}")

def is_winner(board, size, target, player):
    directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]
    for x in range(size):
        for y in range(size):
            if board[x][y] == player:
                for dx, dy in directions:
                    win = True
                    for step in range(1, target):
                        nx, ny = x + dx * step, y + dy * step
                        if 0 <= nx < size and 0 <= ny < size and board[nx][ny] == player:
                            continue
                        win = False
                        break
                    if win:
                        return True
    return False

def heuristic_evaluation(board, size, target, player):
    opponent = 'O' if player == 'X' else 'X'
    score = 0
    sequences_to_check = [(1, 0), (0, 1), (1, 1), (1, -1)]

    def count_sequences(x, y, dx, dy, check_player):
        count = 0
        for step in range(1, target):
            nx, ny = x + dx * step, y + dy * step
            if 0 <= nx < size and 0 <= ny < size:
                if board[nx][ny] == check_player:
                    count += 1
                elif board[nx][ny] == '-':
                    break
            else:
                break
        return count

    # 优化的评分系统：阻止对手或者助攻自己
    for x in range(size):
        for y in range(size):
            if board[x][y] == '-':
                for dx, dy in sequences_to_check:
                    player_count = count_sequences(x, y, dx, dy, player)
                    opponent_count = count_sequences(x, y, dx, dy, opponent)

                    # 如果对手即将赢得比赛，则大幅减分来阻止
                    if opponent_count == target - 2:
                        score -= 100000000
                    # 如果己方即将赢得比赛，则大幅加分
                    elif player_count == target - 2:
                        score += 50000
                    # 通用评分逻辑：推进自己的连线或者打断对手的连线
                    else:
                        score += player_count * 10 - opponent_count * 20

    return score


def minimax(board, size, target, player, depth, alpha, beta, is_maximizing, initial_depth=4):
    if depth == 0 or is_winner(board, size, target, player) or is_winner(board, size, target, 'O' if player == 'X' else 'X'):
        return None, heuristic_evaluation(board, size, target, player)

    if is_maximizing:
        max_eval = float('-inf')
        best_move = None
        for x in range(size):
            for y in range(size):
                if board[x][y] == '-':
                    board[x][y] = player
                    _, eval = minimax(board, size, target, 'O' if player == 'X' else 'X', depth - 1, alpha, beta, False, initial_depth)
                    board[x][y] = '-'
                    if eval > max_eval:
                        max_eval = eval
                        best_move = (x, y)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
        return best_move, max_eval
    else:
        min_eval = float('inf')
        best_move = None
        for x in range(size):
            for y in range(size):
                if board[x][y] == '-':
                    board[x][y] = 'O' if player == 'X' else 'X'
                    _, eval = minimax(board, size, target, player, depth - 1, alpha, beta, True, initial_depth)
                    board[x][y] = '-'
                    if eval < min_eval:
                        min_eval = eval
                        best_move = (x, y)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
        return best_move, min_eval

def play_tic_tac_toe(game_id, size, target):
    board = get_game_state(game_id)
    if not board:
        return
    if is_winner(board, size, target, 'O') or is_winner(board, size, target, 'X'):
        print(f"Game over. {'O' if is_winner(board, size, target, 'O') else 'X'} wins.")
        return

    move, score = minimax(board, size, target, "X", 4, float('-inf'), float('inf'), True, 4)
    if move and board[move[0]][move[1]] == '-':
        print(f"Final best move: {move} with score: {score}")
        post_move(game_id, move)
        get_game_state(game_id)
    else:
        print("No valid moves available or game is over.")

if __name__ == "__main__":
    # Example usage
    play_tic_tac_toe("4993", 10, 5)