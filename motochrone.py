import pygame, sys, random, math, shelve
from pygame.locals import *

FPS = 60
W_HEIGHT = 775
W_WIDTH = 800
BOARD_HEIGHT = 7
BOARD_WIDTH = 9
TILE_SIZE = 58
TILE_SPACE = 12
MARGIN_X = (W_WIDTH - (TILE_SPACE + TILE_SIZE) * BOARD_WIDTH) / 2
MARGIN_Y = (W_HEIGHT - (TILE_SPACE + TILE_SIZE) * BOARD_HEIGHT) / 2

NORMAL = "normal"
RANDOM = "random"
FAST = "fast"
STILL = "still"

UP = "up"
DOWN = "down"
LEFT = "left"
RIGHT = "right"
STAY = "stay"

class Enemy():
    def __init__(self, direc, kind):
        self.kind = kind
        if direc == RIGHT:
            self.tilex = -1
            self.tiley = random.randint(0, BOARD_HEIGHT-1)
        if direc == LEFT:
            self.tilex = BOARD_WIDTH
            self.tiley = random.randint(0, BOARD_HEIGHT-1)
        if direc == UP:
            self.tilex = random.randint(0, BOARD_WIDTH-1)
            self.tiley = BOARD_HEIGHT
        if direc == DOWN:
            self.tilex = random.randint(0, BOARD_WIDTH-1)
            self.tiley = -1
        self.moving = False
        self.counter = 0
        self.moveCounter = 0
        self.moveDuration = 15
        self.speed = 1
        self.color = (200, 60, 30)
        self.arrowColor = (255, 230, 230)
        if kind == FAST:
            self.speed = 2
            self.color = (200, 200, 0)
        elif kind == STILL:
            self.color = (150, 100, 100)
        elif kind == RANDOM:
            self.color = (250, 100, 250)
        self.direction = direc
        self.destroy = False

    def getRect(self):
        return pygame.Rect(MARGIN_X + (TILE_SIZE + TILE_SPACE) * self.tilex, MARGIN_Y + (TILE_SIZE + TILE_SPACE) * self.tiley, TILE_SIZE, TILE_SIZE)

    def setMove(self, player):
        if not self.moving:
            self.moving = True
            if self.kind == STILL:
                if random.random() < 0.33 or (abs(player.tilex-self.tilex)+abs(player.tiley-self.tiley))<=3:
                    self.moving = False

    def update(self):
        self.counter += 1
        if self.moving:
            self.moveCounter += 1
            if self.direction == UP:
                self.tiley -= self.speed/self.moveDuration
            if self.direction == DOWN:
                self.tiley += self.speed/self.moveDuration
            if self.direction == LEFT:
                self.tilex -= self.speed/self.moveDuration
            if self.direction == RIGHT:
                self.tilex += self.speed/self.moveDuration
            if self.moveCounter >= self.moveDuration:
                self.moving = False
                self.moveCounter = 0
                self.tilex = round(self.tilex)
                self.tiley = round(self.tiley)
                if self.kind == RANDOM:
                    if random.random() < 0.75:
                        self.direction = random.choice([UP, DOWN, LEFT, RIGHT])
                if not (0 <= self.tilex <= BOARD_WIDTH-1 and 0 <= self.tiley <= BOARD_HEIGHT-1):
                    self.destroy = True

    def drawBase(self, screen, frames, waitTime, waitMax):
        b = int(4*((frames-waitTime)/waitMax)**2)
        posx = random.randint(-b,b) + int(MARGIN_X + TILE_SIZE * (self.tilex + 0.5) + TILE_SPACE * (self.tilex))
        posy = random.randint(-b,b) + int(MARGIN_Y + TILE_SIZE * (self.tiley + 0.5) + TILE_SPACE * (self.tiley))
        pygame.draw.circle(screen, self.color, (posx, posy), int(TILE_SIZE*0.45), int(TILE_SIZE*0.30))
        
    def drawArrow(self, screen, player):
        posx = int(MARGIN_X + TILE_SIZE * (self.tilex + 0.5) + TILE_SPACE * (self.tilex))
        posy = int(MARGIN_Y + TILE_SIZE * (self.tiley + 0.5) + TILE_SPACE * (self.tiley))
        if not self.kind == RANDOM and not (self.kind == STILL and (abs(player.tilex-self.tilex)+abs(player.tiley-self.tiley))<=3):
            if self.direction == LEFT:
                pygame.draw.circle(screen, self.arrowColor, (posx-int(TILE_SIZE*0.30), posy), int(TILE_SIZE*0.13))
            if self.direction == RIGHT:
                pygame.draw.circle(screen, self.arrowColor, (posx+int(TILE_SIZE*0.30), posy), int(TILE_SIZE*0.13))
            if self.direction == UP:
                pygame.draw.circle(screen, self.arrowColor, (posx, posy-int(TILE_SIZE*0.30)), int(TILE_SIZE*0.13))
            if self.direction == DOWN:
                pygame.draw.circle(screen, self.arrowColor, (posx, posy+int(TILE_SIZE*0.30)), int(TILE_SIZE*0.13))
        elif self.kind == RANDOM:
            pygame.draw.circle(screen, self.arrowColor, (posx+int(TILE_SIZE*0.30*math.cos(self.counter*0.1)), posy+int(TILE_SIZE*0.30*math.sin(self.counter*0.1))), int(TILE_SIZE*0.13))

        
class Player():
    def __init__(self, tx, ty):
        self.tilex = tx
        self.tiley = ty
        self.moving = False
        self.moveCounter = 0
        self.moveDuration = 15
        self.nextMove = None
        self.color = (100, 160, 255)

    def getRect(self):
        return pygame.Rect(MARGIN_X + (TILE_SIZE + TILE_SPACE) * self.tilex, MARGIN_Y + (TILE_SIZE + TILE_SPACE) * self.tiley, TILE_SIZE, TILE_SIZE)

    def setMove(self, direc):
        if not self.moving:
            if not (direc in self.prohibitedMoves()):
                self.moving = True
                self.direction = direc
        elif 1 <= self.tilex <= BOARD_WIDTH-2 and 1 <= self.tiley <= BOARD_HEIGHT-2:
            self.nextMove = direc
        if self.direction == STAY:
                self.moveCounter = self.moveDuration

    def prohibitedMoves(self):
        ans = []
        if 0 >= self.tilex:
            ans.append(LEFT)
        if self.tilex >= BOARD_WIDTH-1:
            ans.append(RIGHT)
        if 0 >= self.tiley:
            ans.append(UP)
        if self.tiley >= BOARD_HEIGHT-1:
            ans.append(DOWN)
        return ans

    def update(self):
        '''returns true when player finishes moving'''
        if self.moving:
            self.moveCounter += 1
            if self.direction == UP:
                self.tiley -= 1/self.moveDuration
            if self.direction == DOWN:
                self.tiley += 1/self.moveDuration
            if self.direction == LEFT:
                self.tilex -= 1/self.moveDuration
            if self.direction == RIGHT:
                self.tilex += 1/self.moveDuration
            if self.moveCounter >= self.moveDuration:
                self.moving = False
                self.moveCounter = 0
                self.tilex = round(self.tilex)
                self.tiley = round(self.tiley)
                if self.nextMove != None:
                    self.moving = True
                    self.direction = self.nextMove
                    self.nextMove = None
                return True
        return False

    def draw(self, screen):
        posx = int(MARGIN_X + TILE_SIZE * (self.tilex + 0.5) + TILE_SPACE * (self.tilex))
        posy = int(MARGIN_Y + TILE_SIZE * (self.tiley + 0.5) + TILE_SPACE * (self.tiley))
        pygame.draw.circle(screen, self.color, (posx, posy), int(TILE_SIZE*0.45), int(TILE_SIZE*0.30))
        
def main():
    shelf = shelve.open("score")
    try:
        highscore = shelf['highscore']
    except:
        highscore = 0
    
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((W_WIDTH, W_HEIGHT))
    
    font = pygame.font.Font("coolfont.TTF", 200)

    pygame.mixer.music.load("motochrone_title.wav")
    pygame.mixer.music.play(-1)
    point = pygame.mixer.Sound("ding.wav")
    point2 = pygame.mixer.Sound("ding2.wav")
    point3 = pygame.mixer.Sound("ding3.wav")
    point4 = pygame.mixer.Sound("ding4.wav")
    point5 = pygame.mixer.Sound("ding5.wav")
    point6 = pygame.mixer.Sound("ding6.wav")
    point7 = pygame.mixer.Sound("ding7.wav")
    death = pygame.mixer.Sound("hurt.wav")
    shift = pygame.mixer.Sound("shift.wav")
    
    startScreen = True
    i = 300
    j = 600
    while startScreen:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_RETURN or event.key == K_SPACE):
                startScreen = False
        DISPLAYSURF.fill((0,0,0))
        topscore = 0
        font = pygame.font.Font("coolfont.TTF", i)
        i = j
        if i > 100:
            j -= 1
        text = font.render("MOTOCHRONE", True, (0, 255, 0))
        DISPLAYSURF.blit(text, (W_WIDTH//2 - text.get_width() // 2, W_HEIGHT//2 - text.get_height() / 2))
        font2 = pygame.font.Font("coolfont.TTF", 30)
        text2 = font2.render('press "enter" to start', True, (0, 255, 0))
        DISPLAYSURF.blit(text2, (W_WIDTH//2 - text.get_width() // 2, 100+W_HEIGHT//2 - text.get_height() / 2))
        pygame.display.update()

    pygame.mixer.music.stop()

    while True:
        font = pygame.font.Font("coolfont.TTF", 150)
        player = Player(BOARD_WIDTH//2, BOARD_HEIGHT//2)
        enemies = []
        addEnemy(enemies, NORMAL)
        greens = []
        for i in range(0, 2):
            addGreen(greens)

        moves = 0
        frames = 0
        waitStart = 0
        waitMax = 1000000
        score = 0
        screen = "game"
        
        while screen != "restart":
            FPSCLOCK.tick(FPS)
            
            for event in pygame.event.get():
                if event.type == QUIT:
                    shelf['highscore'] = max(highscore, topscore)
                    shelf.close()
                    pygame.quit()
                    sys.exit()
                if event.type == KEYDOWN:
                    waitStart = frames
                    shift.stop()
                    shift.play()
                    if event.key == K_w or event.key == K_UP:
                        player.setMove(UP)
                    if event.key == K_s or event.key == K_DOWN:
                        player.setMove(DOWN)
                    if event.key == K_a or event.key == K_LEFT:
                        player.setMove(LEFT)
                    if event.key == K_d or event.key == K_RIGHT:
                        player.setMove(RIGHT)
                    if event.key == K_SPACE:
                        pass
                        #player.setMove(STAY)
                    if event.key == K_RETURN and screen == "gameover":
                        highscore = max(score, highscore)
                        topscore = max(score, topscore)
                        screen = "restart"
            if screen == "game":
                if frames-waitStart > waitMax or player.update():
                    if frames-waitStart > waitMax:
                        score -= 1
                    waitStart = frames
                    shift.stop()
                    shift.play()
                    moves += 1
                    score += 1
                    for enemy in enemies:
                        enemy.setMove(player)
                    for i in range(0, score//100 +4):
                        if random.random() < 0.2:
                            addEnemy(enemies, NORMAL)
                    if score > 50:
                        for i in range(0, score//150 +2):
                            if random.random() < 0.05:
                                addEnemy(enemies, STILL)
                    if score > 150:
                        for i in range(0, score//150 +2):
                            if random.random() < 0.1:
                                addEnemy(enemies, FAST)
                    if score > 200:
                        for i in range(0, score//150 +1):
                            if random.random() < 0.075:
                                addEnemy(enemies, RANDOM)
                    if random.random() < 0.15 or (len(greens)<2 and random.random()<0.75):
                        addGreen(greens)
                
                for enemy in enemies:
                    enemy.update()
                for enemy in enemies:
                    if (abs(player.tilex - enemy.tilex) < 0.1) and (abs(player.tiley - enemy.tiley) < 0.1):
                        screen = "gameover"
                        point.stop()
                        point2.stop()
                        point3.stop()
                        point4.stop()
                        point5.stop()
                        point6.stop()
                        point7.stop()
                        death.play()
                i = 0
                while i < len(greens):
                    if (abs(player.tilex - greens[i][0]) < 0.3) and (abs(player.tiley - greens[i][1]) < 0.3):
                        score += 10
                        greens.remove(greens[i])
                        screen = "addPoint"
                        x = random.randint(1,7)
                        if x == 1:
                            point.play()
                        elif x == 2:
                            point2.play()
                        elif x == 3:
                            point3.play()
                        elif x == 4:
                            point4.play()
                        elif x == 5:
                            point5.play()
                        elif x == 6:
                            point6.play()
                        elif x == 7:
                            point7.play()
                    else:
                        i += 1
                enemies = [enemy for enemy in enemies if not enemy.destroy]

            DISPLAYSURF.fill((0,0,0))
            
            scoreText = font.render(str(score), True, (0, 255, 0))
            DISPLAYSURF.blit(scoreText, (W_WIDTH//2 - scoreText.get_width() // 2, MARGIN_Y//2 - scoreText.get_height() / 2))
            highFont = pygame.font.Font("coolfont.TTF", 110)
            highText = highFont.render(str(highscore), True, (100, 255, 0))
            DISPLAYSURF.blit(highText, (W_WIDTH - MARGIN_X*3//2 - highText.get_width() // 2, MARGIN_Y//2 - highText.get_height() / 2))
            topFont = pygame.font.Font("coolfont.TTF", 90)
            topText = topFont.render(str(topscore), True, (100, 255, 0))
            DISPLAYSURF.blit(topText, (MARGIN_X*3//2 - topText.get_width() // 2, MARGIN_Y//2 - topText.get_height() / 2))
            nameFont = pygame.font.Font("coolfont.TTF", 70)
            nameText = nameFont.render("MOTOCHRONE", True, (0, 255, 0))
            DISPLAYSURF.blit(nameText, (W_WIDTH//2 - nameText.get_width() // 2,W_HEIGHT - MARGIN_Y//2 - nameText.get_height() / 2))
            drawBoard(DISPLAYSURF)
            player.draw(DISPLAYSURF)
            for green in greens:
                posx = int(MARGIN_X + TILE_SIZE * (green[0] + 0.5) + TILE_SPACE * (green[0]))
                posy = int(MARGIN_Y + TILE_SIZE * (green[1] + 0.5) + TILE_SPACE * (green[1]))
                pygame.draw.circle(DISPLAYSURF, (0, 180+int(40*math.sin(frames*0.05)),40+int(40*math.sin(frames*0.13))), (posx, posy), int(TILE_SIZE*0.3), int(TILE_SIZE*0.3))
            for enemy in enemies:
                enemy.drawBase(DISPLAYSURF, frames, waitStart, waitMax)
            for enemy in enemies:
                enemy.drawArrow(DISPLAYSURF, player)

            if screen == "game":
                pygame.display.update()
            if screen == "gameover":
                waitStart = frames
                surf = DISPLAYSURF.convert_alpha()
                surf.fill((255, 30, 30, 80))
                DISPLAYSURF.blit(surf, (0,0))
                pygame.display.update()
            if screen == "addPoint":
                surf = DISPLAYSURF.convert_alpha()
                surf.fill((30, 255, 30, 80))
                DISPLAYSURF.blit(surf, (0,0))
                pygame.display.update()
                pygame.time.wait(30)
                screen = "game"
                pygame.display.update()

            frames += 1

        
def addEnemy(enemies, kind):
    x = random.random()
    if x < 0.25:
        enemies.append(Enemy(RIGHT, kind))
    elif x < 0.5:
        enemies.append(Enemy(LEFT, kind))
    elif x < 0.75:
        enemies.append(Enemy(DOWN, kind))
    else:
        enemies.append(Enemy(UP, kind))

def addGreen(greens):
    x = random.randint(0, BOARD_WIDTH-1)
    y = random.randint(0, BOARD_HEIGHT-1)
    greens.append((x, y))

def drawBoard(screen):
    for i in range(0, BOARD_WIDTH):
        for j in range(0, BOARD_HEIGHT):
            posx = MARGIN_X + i*(TILE_SIZE+TILE_SPACE)
            posy = MARGIN_Y + j*(TILE_SIZE+TILE_SPACE)
            pygame.draw.rect(screen, (0, 34, 64), (posx, posy, TILE_SIZE, TILE_SIZE))

if __name__ == "__main__":
    main()
