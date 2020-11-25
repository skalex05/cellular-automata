import pygame,time, random , math, copy

screensize = (500,500)

boardsize = (100,100)

board = []
for y in range(boardsize[1]):
    row = []
    for x in range(boardsize[0]):
        row.append(0)
    board.append(row)

cellsize = (int(screensize[0] / boardsize[0]),int(screensize[1] / boardsize[1]))

pygame.init()
screen = pygame.display.set_mode(screensize)

generationSpeed = 0.01
fps = 60

lastFrame = time.time()
lastGeneration = time.time()

def clamp(x,y):
    if x >= boardsize[0]:
        x -= boardsize[0]
    elif x < 0:
        x = boardsize[0] + x
    if y >= boardsize[1]:
        y -= boardsize[1]
    elif y < 0:
        y = boardsize[1] + y
    return x,y



def GetNeighbours(x,y,Board):
    count = 0
    for yoffset in range(-1,2):
        for xoffset in range(-1,2):
            tx,ty = x - xoffset,y - yoffset
            tx,ty = clamp(tx,ty)
            if (tx,ty) != (x,y):
                count += board[ty][tx]
    return count

paused = False

while True:
    #events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                lastGeneration = time.time()
                paused = not paused
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                board = []
                for y in range(boardsize[1]):
                    row = []
                    for x in range(boardsize[0]):
                        row.append(0)
                    board.append(row)
    if pygame.mouse.get_pressed()[0]:
        pos = pygame.mouse.get_pos()
        pos = (pos[0] / screensize[0],pos[1] / screensize[1])
        pos = (int(boardsize[0] * pos[0]),int(boardsize[1] * pos[1]))
        board[pos[1]][pos[0]] = 1
        lastGeneration = time.time()
    elif pygame.mouse.get_pressed()[2]:
        pos = pygame.mouse.get_pos()
        pos = (pos[0] / screensize[0],pos[1] / screensize[1])
        pos = (int(boardsize[0] * pos[0]),int(boardsize[1] * pos[1]))
        board[pos[1]][pos[0]] = 0
        lastGeneration = time.time()

    #fps limiter
    if time.time() - lastFrame < 1/fps: continue
    #generations
    if time.time() - lastGeneration > generationSpeed and not paused:
        newBoard = copy.deepcopy(board)
        for y in range(0,boardsize[1]):
            for x in range(0,boardsize[0]):
                n = GetNeighbours(x,y,board)
                if n == 3 or (n == 2 and board[y][x] == 1):
                    newBoard[y][x] = 1
                else:
                    newBoard[y][x] = 0
        board = newBoard
        lastGeneration = time.time()
    #render
    for y in range(boardsize[1]):
        for x in range(boardsize[0]):
            if board[y][x]:
                pygame.draw.rect(screen,(142,219,87),(cellsize[0] * x,cellsize[1] * y,cellsize[0],cellsize[1]))
            else:
                pygame.draw.rect(screen,(114,111,95),(cellsize[0] * x,cellsize[1] * y,cellsize[0],cellsize[1]))
    pygame.display.flip()
    lastFrame = time.time()
