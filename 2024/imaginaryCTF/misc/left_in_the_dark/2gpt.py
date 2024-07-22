from pwn import remote
from collections import deque

def printMaze(maze, currPos):
    for row in maze:
        row = list(row)
        for element in row:
            if element == ".":
                print(colored(element, 'yellow'), end="")
            elif element == "@":
                print(colored(element, 'red'), end="")
            else:
                print(element, end="")
        print()

def move(direction, r):
    direction_map = {'up': b'w', 'down': b's', 'left': b'a', 'right': b'd'}
    r.sendline(direction_map[direction])
    result = r.recvuntil(b"\n", timeout=1)
    # print("moveResult:", result)
    return result == b''

def get_possible_moves(maze, visited, loc):
    moves = []
    directions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}
    for direction, (dr, dc) in directions.items():
        new_r, new_c = loc[0] + dr, loc[1] + dc
        if 0 <= new_r < len(maze) and 0 <= new_c < len(maze[0]) and not visited[new_r][new_c] and maze[loc[0]][loc[1]] != '#':
            moves.append((direction, (new_r, new_c)))
    return moves

# Initialize a string direction which represents all the directions.
DIRECTION = "DLRU"
DIRECTION_MAP = {'down': b's', 'left': b'a', 'right': b'd', 'up': b'w'}

# Arrays to represent change in rows and columns
dr = [1, 0, 0, -1]
dc = [0, -1, 1, 0]

def move(maze, next_loc, direction, r):
    if maze[next_loc[0]][next_loc[1]] == '#':
        return False
    # direction_map = {'down': b's', 'left': b'a', 'right': b'd', 'up': b'w'}
    r.sendline(DIRECTION_MAP[direction])
    result = r.recvuntil(b"\n", timeout=1)
    # print("moveResult:", result)
    return result == b''

def solver(loc, maze, ans, current_path, r, n=40):
    if row == n - 1 and col == n - 1:
        ans.append(current_path)
        return
    maze[row][col] = '#'
    for direction in DIRECTION_MAP.keys():
        # Find the next row based on the current row (row)
        # and the dr[] array
        # next_row = row + dr[i]
        # Find the next column based on the current column
        # (col) and the dc[] array
        # next_col = col + dc[i]
        # direction = DIRECTION_MAP[]

                        # Check if the next cell is valid or not
        # if not is_valid(next_row, next_col, n, maze):
        if move(maze, direction, r):
            current_path += direction[0]
            # Recursively call the find_path function for
            # the next cell
            solver(maze, n, ans, current_path, r)
            # Remove the last direction when backtracking
            current_path = current_path[:-1]
    maze[row][col] = '.'


maze = [['.' for _ in range(maze_size)] for _ in range(maze_size)]
result = []
current_path = ""
solver(maze, result, current_path, r)

def bfs_maze_solver(r, maze_size=40):
    maze = [['.' for _ in range(maze_size)] for _ in range(maze_size)]
    visited = [[False for _ in range(maze_size)] for _ in range(maze_size)]
    start = (0, 0)
    queue = deque([start])
    visited[start[0]][start[1]] = True
    parent = {start: None}
    loc = start

    # Initial text
    print(r.recvline())
    print(r.recvline())

    directions = {'up': (-1, 0), 'down': (1, 0), 'left': (0, -1), 'right': (0, 1)}

    while queue:
        current = queue.popleft()

        if maze[current[0]][current[1]] == 'F':
            path = []
            while current:
                path.append(current)
                current = parent[current]
            return path[::-1]
        
        for direction, new_loc in get_possible_moves(maze, visited, current):
            # print("direction:", direction)
            if move(direction, r):
                visited[new_loc[0]][new_loc[1]] = True
                parent[new_loc] = current
                queue.append(new_loc)
                
                if maze[new_loc[0]][new_loc[1]] == 'F':
                    loc = new_loc
                    break
                
                # Mark the move in the maze
                maze[new_loc[0]][new_loc[1]] = '*'
                maze[loc[0]][loc[1]] = '.'
                break
                
                # Move back to the original position
                # back_direction = {v: k for k, v in directions.items()}
                # move(back_direction[(directions[direction][0] * -1, directions[direction][1] * -1)], r)
            else:
                maze[new_loc[0]][new_loc[1]] = '#'

        if get_possible_moves(maze, visited, current) == []:
            back_direction = {v: k for k, v in directions.items()}
            move(back_direction[(directions[direction][0] * -1, directions[direction][1] * -1)], r)
            queue.append(

        for row in maze:
            print(''.join(row))

        print()
        
        # Update the current location

        loc = current

    return None

# Connect to the maze server
r = remote("left-in-the-dark.chal.imaginaryctf.org", 1337)

# Solve the maze
path = bfs_maze_solver(r)

if path:
    print("Path found:")
    for step in path:
        print(step)
else:
    print("No path found.")

r.interactive()
