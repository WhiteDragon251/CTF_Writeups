from collections import deque

def read_maze(maze_string):
    return [list(line) for line in maze_string.strip().split("\n")]

def find_start_end(maze):
    start = None
    end = None
    for r, row in enumerate(maze):
        for c, char in enumerate(row):
            if char == '@':
                start = (r, c)
            elif char == 'F':
                end = (r, c)
    return start, end

def is_valid_move(maze, visited, row, col):
    if 0 <= row < len(maze) and 0 <= col < len(maze[0]):
        return maze[row][col] != '#' and not visited[row][col]
    return False

def bfs_maze_solver(maze, start, end):
    queue = deque([start])
    visited = [[False] * len(maze[0]) for _ in range(len(maze))]
    visited[start[0]][start[1]] = True
    parent = {start: None}
    
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # up, down, left, right

    while queue:
        current = queue.popleft()
        
        if current == end:
            path = []
            while current:
                path.append(current)
                current = parent[current]
            # for x in visited:
                # print(x)
            return path[::-1]
        
        for direction in directions:
            next_row, next_col = current[0] + direction[0], current[1] + direction[1]
            if is_valid_move(maze, visited, next_row, next_col):
                visited[next_row][next_col] = True
                queue.append((next_row, next_col))
                parent[(next_row, next_col)] = current
    
    return None

def print_maze_with_path(maze, path):
    for row, col in path:
        if maze[row][col] not in '@F':
            maze[row][col] = '-'
    
    for row in maze:
        print(''.join(row))

maze_string = """
@..#.#.#.#..#.........#.#.#.#...#..
##........#...##.##.#........##..#.
.#.#.#.##...#..##..#.#.#.#.#..#.#..
#...#....##..##.#.#...##..#.#.....#
..#..##.#..#......#.#.#.##..#.#.##.
#..#..#...#..#.##..#.....#.#.###...
#.#..###.##.###.#.##.#.##.....#..##
...#.##.##.#.##.##....#...##.#.#...
#.##...............##...#..##....#.
.##..##.#.#.##.#.#...##..##.##.#..#
....#....##.#...#.#.#...#.......#..
#.#.#.#.#...##.#...#..#...#.#.#..##
..#..#...###.....##.#..#.#...#..#..
.#..#..#...#.#.#....###...#.#.#...#
#.##..#..#.##..#.##...##.#.#...#.#.
.....###.##..#..#...#..#....#.#.#..
#.##..#.....#.#.###..##..##.......#
....#..#.#.#......##..##...#.##.#..
#.#.#.#...###.#.#...#...#.##.#...#.
...#...#.#.#.#.#..###.#..#..##.#..#
#.#..#.#.......##....###.##...##.#.
.#..#..#.#.#.#..#.##..##....#...#..
..#.#.#...#..#.#....##...##..#.#.#.
.#..#..#.#..##.#.##...#.#...#..#...
...###..#.##....#.#.###..##..#..#.#
##..#.#...###.#...#.#...##..#.#.#..
...#....#..#.#.#.#...##...#....##.#
.#..#.#..#.....#.#.##..#.##.##.....
#.##..##..#.#.#...#..#.....#...###.
....#...#.#..#.##...#..#.#..##...#.
#.#...####..#....#.#.##..#.#.#.#..#
##..#...#.#...#.#......#..#.....#..
#..#..#....#.###..#.#.#.#.#.#.#..#.
..#.#..##.#.#.#..#..#.#..##..#..#.#
#....#.#.......#..#.#...#...###..#F
"""

maze = read_maze(maze_string)
start, end = find_start_end(maze)
path = bfs_maze_solver(maze, start, end)

if path:
    print("Path found:")
    print_maze_with_path(maze, path)
else:
    print("No path found.")

