from pwn import remote
from collections import deque

# Initialize a string direction which represents all the directions.
DIRECTION_MAP = {'down': b's', 'left': b'a', 'right': b'd', 'up': b'w'}
OPPOSITE = {'down': 'up', 'left': 'right', 'right': 'left', 'up': 'down'}
maze_size = 40

# Arrays to represent change in rows and columns
dr = [1, 0, 0, -1]
dc = [0, -1, 1, 0]

def move(next_row, next_col, maze, direction, r):
    if next_row > 40:
        return False

    if next_col > 40:
        return False
    
    if not (0 <= next_row < 40):
        return False
    
    if not (0 <= next_col < 40):
        return False

    if maze[next_row][next_col] == '#':
        return False
    # direction_map = {'down': b's', 'left': b'a', 'right': b'd', 'up': b'w'}
    r.sendline(DIRECTION_MAP[direction])
    result = r.recvuntil(b"\n", timeout=0.7)
    # if result == b'':
        # print(f"Moved {direction}")
    # print("moveResult:", result)
    return result == b''

def move_part2(direction, r):
    r.sendline(DIRECTION_MAP[direction])
    result = r.recvuntil(b"\n", timeout=0.7)
    # if result == b'':
        # print(f"Moved {direction}")
    # print("moveResult:", result)
    return result == b''

def solver(row, col, maze, ans, current_path, r, n=40):

    # for randomshit in maze:
        # print(''.join(randomshit))

    if row == n - 1 and col == n - 1:
        ans.append(current_path)
        return
    maze[row][col] = '#'
    for i, direction in enumerate(DIRECTION_MAP.keys()):
        # Find the next row based on the current row (row)
        # and the dr[] array
        next_row = row + dr[i]
        # Find the next column based on the current column
        # (col) and the dc[] array
        next_col = col + dc[i]
        # direction = DIRECTION_MAP[]

                        # Check if the next cell is valid or not
        # if not is_valid(next_row, next_col, n, maze):
        print(f'move({next_row=}, {next_col=}, maze, {direction=}, r)')
        newResult = move(next_row, next_col, maze, direction, r)
        print(newResult)
        print()
        if newResult:
            current_path += direction[0]
            # Recursively call the find_path function for
            # the next cell
            solver(next_row, next_col, maze, ans, current_path, r)
            # Remove the last direction when backtracking
            move_part2(OPPOSITE[direction], r)
            current_path = current_path[:-1]
    maze[row][col] = '.'


# Connect to the maze server
r = remote("left-in-the-dark.chal.imaginaryctf.org", 1337)
print(r.recvline())
print(r.recvline())

# Solve the maze
maze = [['.' for _ in range(maze_size)] for _ in range(maze_size)]
result = []
current_path = ""
solver(0, 0, maze, result, current_path, r)

print(r.recvline())
print(r.recvuntil(b"}"))
r.interactive()

"""
if current_path:
    print("Path found:")
    for step in current_path:
        print(step)
else:
    print("No path found.")
"""


