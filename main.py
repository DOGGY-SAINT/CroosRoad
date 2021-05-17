import random

import pygame as pg
from pygame.color import THECOLORS

IMAGE_PATH = 'imgs/'
centre = (400, 400)
CGAP = 400
# 1 创建控制游戏结束的状态
GAMEOVER = False
# 4 图片加载报错处理
LOG = '文件:{}中的方法:{}出错'.format(__file__, __name__)

direction = {'up': 0, 'left': 1, 'down': 2, 'right': 3}  # 上左下右 在上方
SCREENRECT = pg.Rect(0, 0, 800, 800)
CHANGELIGHTEVENT = pg.USEREVENT
CENTERGAP = 100

fontName = "arial"


def dirToI(dir):
    return direction[dir]


class Light(pg.sprite.Sprite):
    dwidth = (200, 20, 200, 20)
    dheight = (20, 200, 20, 200)

    def __init__(self, dir):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.dir = dir
        if dir % 2 == 0:
            self.color = 'green'
        else:
            self.color = "red"
        self.image = pg.Surface([self.dwidth[dir], self.dheight[dir]])
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.image.fill(THECOLORS[self.color])

        if dir == dirToI("up"):
            self.rect.bottomleft = [CGAP - CENTERGAP, CGAP - CENTERGAP]
        elif dir == dirToI("down"):
            self.rect.topright = [CGAP + CENTERGAP, CGAP + CENTERGAP]
        elif dir == dirToI("left"):
            self.rect.topright = [CGAP - CENTERGAP, CGAP - CENTERGAP]
        else:
            self.rect.bottomleft = [CGAP + CENTERGAP, CGAP + CENTERGAP]

    def update(self):
        self.image.fill(THECOLORS[self.color])


class Show(pg.sprite.Sprite):  # 显示框
    def __init__(self, dir, pos):
        self.carwaiting = 0  # 等待数
        pg.sprite.Sprite.__init__(self, CrossRoad.all)
        self.font = pg.font.SysFont(fontName, 30)
        self.font.set_italic(1)
        self.color = pg.Color("white")
        self.update()
        self.rect = self.image.get_rect()
        if dir == 0:
            self.rect.topright = pos
        elif dir == 1:
            self.rect.topleft = pos
        elif dir == 2:
            self.rect.bottomleft = pos
        else:
            self.rect.bottomright = pos

    def update(self):
        msg = "Car Remain: %d" % self.carwaiting
        self.image = self.font.render(msg, 0, self.color)


class Road:
    # 左上角
    offset = [[CGAP - CENTERGAP, 0],
              [0, CGAP - CENTERGAP],
              [CGAP - CENTERGAP, CGAP + CENTERGAP],
              [CGAP + CENTERGAP, CGAP - CENTERGAP]]

    def __init__(self, dir, screen):
        self.dir = dir
        self.carwaiting = []  # 类型表
        tmov = 30
        # 按方向设置数据
        if dir == dirToI("up") or dir == dirToI("down"):
            # 左线
            pg.draw.line(screen, color=THECOLORS["white"],
                         start_pos=self.offset[dir],
                         end_pos=[self.offset[dir][0],
                                  self.offset[dir][1] + CGAP - CENTERGAP])
            # 中线
            pg.draw.line(screen, color=THECOLORS["white"],
                         start_pos=[self.offset[dir][0] + CENTERGAP,
                                    self.offset[dir][1]],
                         end_pos=[self.offset[dir][0] + CENTERGAP,
                                  self.offset[dir][1] + CGAP - CENTERGAP])
            # 右线
            pg.draw.line(screen, color=THECOLORS["white"],
                         start_pos=[self.offset[dir][0] + 2 * CENTERGAP,
                                    self.offset[dir][1]],
                         end_pos=[self.offset[dir][0] + 2 * CENTERGAP,
                                  self.offset[dir][1] + CGAP - CENTERGAP])
            # 车出现的位置
            if dir == dirToI("up"):
                self.carBorn = [CGAP - CENTERGAP / 2 + Car.dwidth[0] / 2, -Car.dheight[0]]
                self.show = Show(dir, [self.offset[dir][0] - tmov, self.offset[dir][1]])  # 不挡线偏移
            else:
                self.carBorn = [CGAP + CENTERGAP / 2 - Car.dwidth[0] / 2, 2 * CGAP + Car.dheight[0]]
                self.show = Show(dir, [self.offset[dir][0] + 2 * CENTERGAP + tmov,  # 不挡线偏移
                                       self.offset[dir][1] + CGAP - CENTERGAP])

        else:
            # 上线
            pg.draw.line(screen, color=THECOLORS["white"],
                         start_pos=self.offset[dir],
                         end_pos=[self.offset[dir][0] + CGAP - CENTERGAP,
                                  self.offset[dir][1]])
            # 中线
            pg.draw.line(screen, color=THECOLORS["white"],
                         start_pos=[self.offset[dir][0],
                                    self.offset[dir][1] + CENTERGAP],
                         end_pos=[self.offset[dir][0] + CGAP - CENTERGAP,
                                  self.offset[dir][1] + CENTERGAP])
            # 下线
            pg.draw.line(screen, color=THECOLORS["white"],
                         start_pos=[self.offset[dir][0],
                                    self.offset[dir][1] + 2 * CENTERGAP],
                         end_pos=[self.offset[dir][0] + CGAP - CENTERGAP,
                                  self.offset[dir][1] + 2 * CENTERGAP])
            # 车出现的位置
            if dir == dirToI("left"):
                self.show = Show(dir, [self.offset[dir][0],
                                       self.offset[dir][1] + 2 * CENTERGAP + tmov])  # 不挡线偏移
                self.carBorn = [-Car.dheight[0], CGAP + CENTERGAP / 2 - Car.dwidth[0] / 2]
            else:
                self.show = Show(dir, [self.offset[dir][0] + CGAP - CENTERGAP - tmov,  # 不挡线偏移
                                       self.offset[dir][1]])
                self.carBorn = [2 * CGAP + Car.dheight[0], CGAP - CENTERGAP / 2 + Car.dwidth[0] / 2]

    def addCar(self):
        if not CrossRoad.carin:  # 不准进
            return
        if len(self.carwaiting) <= 0:
            return
        car = Car(self.dir, self.carwaiting[0], self.carBorn)
        car.move(5)
        for othercar in pg.sprite.spritecollide(car, CrossRoad.cars, False):
            if car != othercar:
                car.kill()
                return
            car.moveBack(4)
        del (self.carwaiting[0])
        self.show.carwaiting = len(self.carwaiting)

    def addCarWaiting(self, type):
        if CrossRoad.randCarMode==1:        #只有普通
            type=0
        elif CrossRoad.randCarMode==2:      #只有警车
            type=1
        self.carwaiting.append(type)
        self.show.carwaiting = len(self.carwaiting)

    @staticmethod
    def randType():
        return random.randint(0, 100) % 5 == 0

    def randCar(self):
        if random.randint(0, (len(self.carwaiting) + 7) * 6) == 0:  # 概率刷新
            type = self.randType()
            self.addCarWaiting(type)



class CrossRoad:
    # 初始化Groups
    lights = pg.sprite.Group()
    cars = pg.sprite.Group()
    all = pg.sprite.RenderUpdates()
    keyDown = [False, False, False, False]
    carin = True  # 车辆入场
    randCarMode=0       #怎么生成车辆，0都有，1只有普通，2只有警车

    def __init__(self, screen):
        self.roads = []
        self.lights = []
        self.lcnt = 0  # 换灯计数
        self.randcar = True  # 随机生成车辆
        self.counter = Counter()  # 计时器

        # 设置所属group
        Light.containers = CrossRoad.lights, CrossRoad.all
        Car.containers = CrossRoad.cars, CrossRoad.all

        # 路初始化
        for i in range(4):
            self.roads.append(Road(i, screen))
            # 灯
            light = Light(i)
            self.lights.append(light)

    def changeLight(self):  # 换灯
        self.lcnt = (self.lcnt + 1) % 2
        for i in range(4):
            if i % 2 == self.lcnt:
                self.lights[i].color = 'green'
            else:
                self.lights[i].color = 'red'

    def update(self):
        for i in range(4):
            if self.randcar:
                self.roads[i].randCar()
            self.roads[i].addCar()


class Counter(pg.sprite.Sprite):  # 计时器
    lightchangegap = 8  # 灯切换间隔

    def __init__(self):
        self.cnt = self.lightchangegap - 1  # 等待数
        pg.sprite.Sprite.__init__(self, CrossRoad.all)
        self.font = pg.font.SysFont(fontName, 40)
        self.font.set_italic(1)
        self.color = pg.Color("white")
        msg = "Count Down: %d" % (self.cnt + 1)
        self.image = self.font.render(msg, 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.topright = [CGAP * 2, 0]
        pg.time.set_timer(CHANGELIGHTEVENT, 1000, -1)

    def count(self):
        self.cnt -= 1
        res = False
        if self.cnt < 0:
            self.cnt = self.lightchangegap - 1
            res = True
        msg = "Count Down: %d" % (self.cnt + 1)
        self.image = self.font.render(msg, 0, self.color)
        return res


class Car(pg.sprite.Sprite):
    dspeed = [6, 8]
    dcolor = ['red', 'green']
    dwidth = [25, 40]
    dheight = [40, 25]
    dspeedDir = [[0, 1], [1, 0], [0, -1], [-1, 0]]
    nCarGap=dspeed[0] * 4
    nLightGap=dspeed[0] * 2
    carGap = [[0, nCarGap], [nCarGap, 0], [0, -1*nCarGap], [-1*nCarGap, 0]]
    lightGap = [[0, nLightGap], [nLightGap, 0], [0, -1 * nLightGap], [-1 * nLightGap, 0]]

    def __init__(self, dir, type, leftdown):  # 0普通1警车,指的是车的左下角的位置，要变换
        pg.sprite.Sprite.__init__(self, self.containers)
        self.type = type
        self.dir = dir
        self.speed = self.dspeed[type]
        self.passed = False

        self.image = pg.Surface([self.dwidth[dir % 2], self.dheight[dir % 2]])
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.image.fill(THECOLORS[self.dcolor[type]])
        pg.draw.rect(self.image, THECOLORS['white'], [0, 0, self.rect.width, self.rect.height], 2)
        if dir == 0:
            self.rect.topright = leftdown
        elif dir == 1:
            self.rect.topleft = leftdown
        elif dir == 2:
            self.rect.bottomleft = leftdown
        else:
            self.rect.bottomright = leftdown

    def update(self):
        trect = self.rect.copy()
        trect.move_ip(self.dspeedDir[self.dir][0] * self.speed, self.dspeedDir[self.dir][1] * self.speed)
        trect.move_ip(self.lightGap[self.dir][0], self.lightGap[self.dir][1])  # 再加间隔
        if (not self.passed) and self.type == 0:  # 普通车
            for light in CrossRoad.lights:
                if light.dir == self.dir and trect.colliderect(light.rect):
                    if light.color == 'red':
                        return
                    trect.move_ip(-1*self.lightGap[self.dir][0], -1*self.lightGap[self.dir][1])  # 减去间隔
                    if trect.colliderect(light.rect):       #一步到红灯
                        self.passed = True

        trect = self.rect.copy()
        trect.move_ip(self.dspeedDir[self.dir][0] * self.speed, self.dspeedDir[self.dir][1] * self.speed)
        trect.move_ip(self.carGap[self.dir][0], self.carGap[self.dir][1])  # 再加间隔

        for car in CrossRoad.cars:
            if car != self and trect.colliderect(car.rect):
                if self.dir == 0:
                    if car.rect.top - self.rect.bottom - self.nCarGap>0:
                        self.move_ip(0, car.rect.top - self.rect.bottom - self.nCarGap)
                elif self.dir == 1:
                    if car.rect.left - self.rect.right - self.nCarGap>0:
                        self.move_ip(car.rect.left - self.rect.right - self.nCarGap, 0)
                elif self.dir == 2:
                    if car.rect.bottom - self.rect.top + self.nCarGap<0:
                        self.move_ip(0, car.rect.bottom - self.rect.top + self.nCarGap)
                else:
                    if car.rect.right - self.rect.left + self.nCarGap<0:
                        self.move_ip(car.rect.right - self.rect.left + self.nCarGap, 0)
                return
        self.move()
        if not SCREENRECT.colliderect(self.rect):
            self.kill()

    def move(self, n=1):
        for i in range(n):
            self.rect.move_ip(self.dspeedDir[self.dir][0] * self.speed, self.dspeedDir[self.dir][1] * self.speed)

    def move_ip(self, x, y):
        self.rect.move_ip(x, y)

    def moveBack(self, n=1):
        for i in range(n):
            self.rect.move_ip(-1 * self.dspeedDir[self.dir][0] * self.speed,
                              -1 * self.dspeedDir[self.dir][1] * self.speed)


def main():
    pg.init()
    # display
    screen = pg.display.set_mode(SCREENRECT.size)
    background = pg.Surface(SCREENRECT.size)
    pg.display.set_caption('CroosRoad')  # 标题

    addCnt = [0, 0, 0, 0]  # 1秒60太快了

    crosssroad = CrossRoad(screen)

    clock = pg.time.Clock()
    global GAMEOVER
    while not GAMEOVER:

        clock.tick(60)  # 帧率设为60

        for event in pg.event.get():
            if event.type == pg.QUIT:  # 推出
                GAMEOVER = True
                return
            elif event.type == pg.KEYDOWN:  # 按下
                if event.key == pg.K_ESCAPE:
                    GAMEOVER = True
                    return
                elif event.key == pg.K_q:  # 按q清空所有车和等待的车
                    for i in range(4):
                        crosssroad.roads[i].carwaiting.clear()
                        crosssroad.roads[i].show.carwaiting = 0
                        crosssroad.roads[i].show.update()
                    for car in CrossRoad.cars:
                        car.kill()
                elif event.key == pg.K_w:
                    crosssroad.randcar = not crosssroad.randcar
                elif event.key == pg.K_e:
                    CrossRoad.carin = not CrossRoad.carin
                elif event.key == pg.K_r:
                    CrossRoad.randCarMode = (CrossRoad.randCarMode+1)%3
                elif event.key == pg.K_UP:
                    CrossRoad.keyDown[0] = not CrossRoad.keyDown[0]
                elif event.key == pg.K_LEFT:
                    CrossRoad.keyDown[1] = not CrossRoad.keyDown[1]
                elif event.key == pg.K_DOWN:
                    CrossRoad.keyDown[2] = not CrossRoad.keyDown[2]
                elif event.key == pg.K_RIGHT:
                    CrossRoad.keyDown[3] = not CrossRoad.keyDown[3]
            elif event.type == CHANGELIGHTEVENT:  # 计时器
                if crosssroad.counter.count():
                    crosssroad.changeLight()

        for i in range(4):
            if CrossRoad.keyDown[i]:
                addCnt[i] += 1
                if addCnt[i] >= 10:  # 1秒6个
                    addCnt[i] = 0
                    crosssroad.roads[i].addCarWaiting(Road.randType())
        CrossRoad.all.clear(screen, background)  # 清屏
        crosssroad.update()
        CrossRoad.all.update()
        CrossRoad.all.draw(screen)
        pg.display.update()


if __name__ == "__main__":
    main()
