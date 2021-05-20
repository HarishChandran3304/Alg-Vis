#IMPORTS
import pygame
from queue import PriorityQueue


#CONSTANTS
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
RED = (255, 0, 0) #Visited but close nodes
GREEN = (0, 255, 0) #Visited and open nodes
BLUE = (0, 0, 255)  #Path nodes
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255) #Empty nodes
BLACK = (0, 0, 0) #Barrier nodes
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0) #Start node
GREY = (128, 128, 128) #Grid lines
TURQUOISE = (64, 224, 208) #Destination node
THEMEGREY = (40, 41, 35) #Theme primary
THEMEPURPLE = (71, 63, 255) #Theme secondary
BTNDARK = (71, 63, 255) #Button normal colour
BTNLIGHT = (86, 99, 233) #Button hover colour
STATERED = (198, 10, 9) #Status red colour
STATEGREEN = (142, 200, 19) #Status green colour


#SETUP
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
icon = pygame.image.load("Logo.svg")
pygame.display.set_icon(icon)
pygame.display.set_caption('Alg-Vis')


#CLASSES
class Node:
	def __init__(self, row, col, width, totalrows):
		'''
		Constructor
		To initialize attributes to a new instance when created
		'''
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.colour = WHITE
		self.neighbours = []
		self.width = width
		self.totalrows = totalrows

    #CLASS METHODS
	def getpos(self):
		'''
		Returns coordinate of a node in the form (row, column)
		'''
		return self.row, self.col

	def reset(self):
		'''
		Resets colour attribute of node back to white
		'''
		self.colour = WHITE


	def isclosed(self):
		'''
		Returns True if a node has been visited but is closed, else returns False
		'''
		return self.colour == YELLOW

	def isopen(self):
		'''
		Returns True if a node has been visited and is open, else returns False
		'''
		return self.colour == GREEN

	def isbarrier(self):
		'''
		Returns True if a node is a barrier node, else returns False
		'''
		return self.colour == BLACK

	def isstart(self):
		'''
		Returns True if a node is the start node, else returns False
		'''
		return self.colour == ORANGE

	def isend(self):
		'''
		Returns True if a node is the destination node, else returns False
		'''
		return self.colour == TURQUOISE

	def ispath(self):
		'''
		Returns True if a node is a part of the path nodes, else returns False
		'''
		self.colour == BLUE


	def makeclosed(self):
		'''
		Changes the colour attribute of a node to Yellow
		'''
		self.colour = YELLOW

	def makeopen(self):
		'''
		Changes the colour attribute of a node to Green
		'''
		self.colour = GREEN

	def makebarrier(self):
		'''
		Changes the colour attribute of a node to Black
		'''
		self.colour = BLACK

	def makestart(self):
		'''
		Changes the colour attribute of a node to Orange
		'''
		self.colour = ORANGE

	def makeend(self):
		'''
		Changes the colour attribute of a node to Turquoise
		'''
		self.colour = TURQUOISE

	def makepath(self):
		'''
		Changes the colour attribute of a node to Blue
		'''
		self.colour = BLUE


	def draw(self, surface):
		'''
		Draws the node on the surface, with the colour self.colour, as a square of side self.width, at self.x, self.y
		'''
		pygame.draw.rect(surface, self.colour, (self.x, self.y, self.width, self.width))

	def updateneighbours(self, grid):
		self.neighbours = []
		if self.row < self.totalrows-1 and not grid[self.row+1][self.col].isbarrier(): #Below Neighbour
			self.neighbours.append(grid[self.row+1][self.col])

		if self.row > 0 and not grid[self.row-1][self.col].isbarrier(): #Above Neighbour
			self.neighbours.append(grid[self.row-1][self.col])

		if self.col < self.totalrows-1 and not grid[self.row][self.col+1].isbarrier(): #Right Neighbour
			self.neighbours.append(grid[self.row][self.col+1])

		if self.col > 0 and not grid[self.row][self.col-1].isbarrier(): #Left Neighbour
			self.neighbours.append(grid[self.row][self.col-1])

class Button():
    def __init__(self, colour, x, y, width, height, text="", font="verdana", fontsize=50, fontcolour=(0,0,0)):
        self.colour = colour
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.font = font
        self.fontsize = fontsize
        self.fontcolour = fontcolour
        
    def draw(self, surface, outlinecolour=None):
        '''
        Draw the button on the screen
        '''
        if outlinecolour:
            pygame.draw.rect(surface, outlinecolour, (self.x-2,self.y-2,self.width+4,self.height+4), 0)
            
        pygame.draw.rect(surface, self.colour, (self.x,self.y,self.width,self.height), 0)
        
        if self.text != '':
            font = pygame.font.SysFont(self.font, self.fontsize)
            text = font.render(self.text, 1, self.fontcolour)
            surface.blit(text, (self.x + (self.width/2 - text.get_width()/2), self.y + (self.height/2 - text.get_height()/2)))

    def isclicked(self, pos):
        '''
        Returns True if the x, y coordinates entered happens to fall on the button
        '''
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False

#BUTTON CLASS INSTANCES
visualizebtn = Button(STATERED, 875, 600, 250, 100, "Visualize")


#HELPER FUNCTIONS
def h(node1, node2):
    '''
    Heuristic function [h(n)] for the algorithm
    #Uses Manhattan-Distance [L-Distance]
    Returns the absolute distance between the current node and the destination node
    '''
    x1, y1 = node1
    x2, y2 = node2
    return abs(x2-x1) + abs(y2-y1)


def algorithm(draw, grid, start, end):
    count = 0
    openset = PriorityQueue()
    openset.put((0, count, start))
    camefrom = {}
    gscore = {node: float("inf") for row in grid for node in row}
    gscore[start] = 0
    fscore = {node: float("inf") for row in grid for node in row}
    fscore[start] = h(start.getpos(), end.getpos())
    
    opensethash = {start}
    
    while not openset.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        current = openset.get()[2]
        opensethash.remove(current)
        
        if current == end:
            drawpath(camefrom, end, draw)
            end.makeend()
            start.makestart()
            return True
        
        for neighbour in current.neighbours:
            tempgscore = gscore[current]+1
            
            if tempgscore < gscore[neighbour]:
                camefrom[neighbour] = current
                gscore[neighbour] = tempgscore
                fscore[neighbour] = tempgscore + h(neighbour.getpos(), end.getpos())
                if neighbour not in opensethash:
                    count += 1
                    openset.put((fscore[neighbour], count, neighbour))
                    opensethash.add(neighbour)
                    neighbour.makeopen()
        
        draw()
        
        if current != start:
            current.makeclosed()
        
    return False

def makegrid(rows, width):
    '''
    Creates the grid and returns it in the form of a 2D list
    '''
    grid = []
    gap = width//rows #Width of each node
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    
    return grid

def drawgrid(surface, rows, width):
    '''
    Draws the lines of the grid in grey color
    '''
    gap = width//rows
    for i in range(rows):
        pygame.draw.line(surface, GREY, (0, i*gap), (width, i*gap))
    for j in range(rows):
        pygame.draw.line(surface, GREY, (j*gap, 0), (j*gap, width))

def drawpath(camefrom, current, draw):
    while current in camefrom:
        current = camefrom[current]
        current.makepath()
        draw()

def draw(surface, grid, rows, width):
    '''
    Main draw function to draw the entire grid
    '''
    pygame.draw.rect(surface, WHITE, pygame.Rect(0, 0, width, width))
    
    for row in grid:
        for node in row:
            node.draw(surface)
    
    drawgrid(surface, rows, width)
    pygame.display.update()

def getclickedpos(pos, rows, width):
    '''
    Returns the row and column of the node that was clicked on
    '''
    gap = width//rows
    y, x = pos
    
    row = y//gap
    col = x//gap
    
    return row, col

def status(surface, state, statecolour, font="verdana", fontsize=30, fontcolour=THEMEPURPLE):
    font1 = pygame.font.SysFont(font, fontsize)
    font2 = pygame.font.SysFont(font, fontsize)
    text1 = font1.render("Status: ", 1, fontcolour) 
    text2 = font2.render(state, 1, statecolour)
    surface.blit(text1, (740, 20))
    surface.blit(text2, (740+text1.get_width(), 20))


#MAIN
def main(surface, width):
    rows = 36 
    grid = makegrid(rows, width)
    
    start = None 
    end = None
    
    state = "Start node missing!"
    statecolour = (198, 10, 9)
    
    run = True
    while run:
        if start and end:
            visualizebtn.colour = STATEGREEN
        else:
            visualizebtn.colour = STATERED
        draw(surface, grid, rows, width)
        pygame.draw.rect(screen, THEMEGREY, pygame.Rect(720, 0, 560, 720))
        visualizebtn.draw(screen, THEMEPURPLE)
        status(screen, state, statecolour)
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            
            if pygame.mouse.get_pressed()[0]: #Left mouse button
                pos = pygame.mouse.get_pos()
                if pos[0] < 720:
                    row, col = getclickedpos(pos, rows, width)
                    node = grid[row][col]
                    
                    if not start and node!=end:
                        start = node
                        start.makestart()
                        if not end:
                            state = "End node missing!"
                            statecolour = (198, 10, 9)
                        else:
                            state = "Ready to visualize!"
                            statecolour = (142, 200, 19)
                    
                    elif not end and node!=start:
                        end = node
                        end.makeend()
                        if not start:
                            state = "Start node missing!"
                            statecolour = (198, 10, 9)
                        else:
                            state = "Ready to visualize!"
                            statecolour = (142, 200, 19)
                    
                    elif node!=start and node!=end:
                        node.makebarrier()
                        for row in grid:
                            for node in row:
                                if node.colour == YELLOW or node.colour == GREEN or node.colour == BLUE:
                                    node.reset()
                                    state = "Ready to visualize!"
                                    statecolour = (142, 200, 19)
                                    
                else:
                    if visualizebtn.isclicked(pos) and start and end:
                        state = "Visualizing..."
                        statecolour = (255, 218, 66)
                        pygame.draw.rect(screen, THEMEGREY, pygame.Rect(720, 0, 560, 720))
                        visualizebtn.color = statecolour
                        visualizebtn.draw(screen, THEMEPURPLE)
                        status(screen, state, statecolour)
                        pygame.display.update()
                        for row in grid:
                            for node in row:
                                if node.colour == YELLOW or node.colour == GREEN or node.colour == BLUE:
                                    node.reset()
                        for row in grid:
                            for node in row:
                                node.updateneighbours(grid)
                            
                        found = algorithm(lambda: draw(surface, grid, rows, width), grid, start, end)
                    
                        if not found:
                            for row in grid:
                                for node in row:
                                    if node.colour == YELLOW:
                                        node.colour = RED
                            state = "No path possible!"
                            statecolour = STATERED
                        else:
                            for row in grid:
                                for node in row:
                                    if node.colour == GREEN:
                                        node.colour = YELLOW
                            state = "Shortest path found!"
                            statecolour = STATEGREEN
                         
            
            elif pygame.mouse.get_pressed()[2]: #Right mouse button
                pos = pygame.mouse.get_pos()
                row, col = getclickedpos(pos, rows, width)
                try:
                    node = grid[row][col]
                    
                    if node == start:
                        start = None
                        state = "Start node missing!"
                        statecolour = (198, 10, 9)
                    
                    elif node == end:
                        end = None
                        state = "End node missing!"
                        statecolour = (198, 10, 9)
                    
                    node.reset()
                
                except:
                    pass
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    state = "Visualizing..."
                    statecolour = (255, 218, 66)
                    pygame.draw.rect(screen, (40, 41, 35), pygame.Rect(720, 0, 560, 720))
                    visualizebtn.color = statecolour
                    visualizebtn.draw(screen, THEMEPURPLE)
                    status(screen, state, statecolour)
                    pygame.display.update()
                    for row in grid:
                        for node in row:
                            if node.colour == YELLOW or node.colour == GREEN or node.colour == BLUE:
                                node.reset()
                    for row in grid:
                        for node in row:
                            node.updateneighbours(grid)
                        
                    found = algorithm(lambda: draw(surface, grid, rows, width), grid, start, end)
                    
                    if not found:
                        for row in grid:
                            for node in row:
                                if node.colour == YELLOW:
                                    node.colour = RED
                        state = "No path possible!"
                        statecolour = STATERED
                    else:
                        for row in grid:
                            for node in row:
                                if node.colour == GREEN:
                                    node.colour = YELLOW
                        state = "Shortest path found!"
                        statecolour = STATEGREEN
                    
                if event.key == pygame.K_r:
                    start = None
                    end = None
                    grid = makegrid(rows, width)
                    state = "Start node missing!"
                    statecolour = (198, 10, 9)
    
    pygame.quit()


#MAIN CALL
if __name__ == "__main__":
    main(screen, 720)