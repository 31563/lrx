# -*- coding: utf-8 -*-
"""
Created on Mon Jun  3 22:24:13 2024

@author: 31563
"""
import pygame
import random
import sys

from pygame.sprite import Sprite

#1 设置页面宽高
screen_width=800
screen_height =560
#1 创建控制游戏结束的状态
GAMEOVER = False
#3 创建地图类
class Map():

    map_names_list = ['imgs/map1.png','imgs/map2.png']                      #建立列表，存储两种颜色的地图
    #3 初始化地图
    def __init__(self, x, y, img_index):
        self.image = pygame.image.load(Map.map_names_list[img_index])
        self.position = (x, y)
        # 是否能够种植
        self.can_grow = True

    def load_map(self):                                                     #把地图画出来
         MainGame.screen.blit(self.image,self.position)

#4 植物类
class Plant(Sprite):
    def __init__(self):
        super().__init__()                                #继承父类，Sprits（精灵）是python自带的类
        self.live = True

    def load_image(self):                                                   #把图片画出来
        if hasattr(self, 'image') and hasattr(self, 'rect'):               #hasattr内置检查函数，(self,'image')：self有没有image这个属性
            MainGame.screen.blit(self.image, self.rect)

#5 向日葵类
class Sunflower(Plant):
    def __init__(self,x,y):
        super().__init__()

        self.image = pygame.image.load('imgs/sunflower.png')                        #获取图片并赋予属性
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.price = 50                                              #价格，即阳光消耗量
        self.hp = 100

        self.time_count = 0                                          #生产计数器

    def produce_sun(self):                                             #功能：生成阳光
        self.time_count += 1
        if self.time_count == 25:
            MainGame.sun += 5
            self.time_count = 0                                   #重置计数器

    def display_sunflower(self):                                      #放置向日葵
        MainGame.screen.blit(self.image,self.rect)

#6 豌豆射手类
class PeaShooter(Plant):
    def __init__(self,x,y):
        super().__init__()

        self.image = pygame.image.load('imgs/peashooter.png')                   #获取图片
        self.rect = self.image.get_rect()                                      #获取对象属性

        self.rect.x = x
        self.rect.y = y
        self.price = 50
        self.hp = 200

        self.shot_count = 0                                             #发射计数器

    def shot(self):                                                    
        should_fire = False                                            #初始状态下不开枪
        for zombie in MainGame.zombie_list:                          #有僵尸存在
            if zombie.rect.y == self.rect.y and zombie.rect.x < 800 and zombie.rect.x > self.rect.x:  #僵尸在自己这行并且在自己右边
                should_fire = True

        if self.live and should_fire:                          #活着并且僵尸未灭
            self.shot_count += 1
            if self.shot_count == 25:                           #依旧是计数器到25一次攻击
                peabullet = PeaBullet(self)                         #基于豌豆射手的位置创建子弹
                MainGame.peabullet_list.append(peabullet)                #将子弹存储在子弹列表中
                self.shot_count = 0                                     #重置计数器

    def display_peashooter(self):                                      #放置豌豆射手
        MainGame.screen.blit(self.image,self.rect)

class Qiang(Plant):                                      #坚果墙类
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load('imgs/qiang.png')
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y
        self.price = 50
        self.hp = 2000

    def display_qiang(self):                                      #放置坚果
        MainGame.screen.blit(self.image,self.rect)

# 豌豆子弹类
class PeaBullet(Sprite):
    def __init__(self,peashooter):
        self.live = True
        self.image = pygame.image.load('imgs/bullet1.png')
        self.damage = 40                                                    #伤害效果
        self.speed = 5
        # self.level = 1
        # self.fire = []
        self.rect = self.image.get_rect()
        self.rect.x = peashooter.rect.x + 60
        self.rect.y = peashooter.rect.y 

    def move_bullet(self):                                                #子弹向右移动，但是不超过屏幕
        if self.rect.x < screen_width:
            self.rect.x += self.speed
        else:
            self.live = False

    def hit_zombie(self):                                                        #子弹与僵尸的碰撞
        for zombie in MainGame.zombie_list:
            if pygame.sprite.collide_rect(self,zombie):
                #打中僵尸之后，修改子弹的状态，
                self.live = False                                              #子弹消失
                zombie.hp -= self.damage                                     #扣血
                if zombie.hp <= 0:
                    zombie.live = False
                    self.nextLevel()

    def nextLevel(self):                                               #关卡记录
        MainGame.score += 20
        MainGame.remnant_score -= 20
        for i in range(1,100):
            if MainGame.score == 100*i and MainGame.remnant_score == 0:
                    MainGame.remnant_score = 100 * i
                    MainGame.guanshu += 1

                    MainGame.produce_zombie += 100

    def display_peabullet(self):                                    #画出子弹
        MainGame.screen.blit(self.image,self.rect)

#9 僵尸类
class Zombie(Sprite):
    def __init__(self,x,y):
        super().__init__()
        self.image = pygame.image.load('imgs/zombie.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = 800
        self.damage = 2                                                      #伤害
        self.speed = 0.6                                                     #速度
        self.live = True                                                         #存活
        self.stop = False                                                      #是否停止

    def move_zombie(self):                                             #僵尸移动
        if self.live and not self.stop:
            self.rect.x -= self.speed
            if self.rect.x < -80:                                                     #进入屏幕左边，则游戏结束
                MainGame().gameOver()

    def hit_plant(self):                                                       #僵尸与植物的碰撞
        for plant in MainGame.plants_list:
            if pygame.sprite.collide_rect(self,plant):
                self.stop = True                                                    #僵尸停止
                self.eat_plant(plant)                                              #僵尸吃植物

    def eat_plant(self,plant):                                       #僵尸的攻击
        plant.hp -= self.damage                                           #植物减血
        #9 植物死亡后的状态修改，以及地图状态的修改
        if plant.hp <= 0:
            a = plant.rect.y // 80 - 1
            b = plant.rect.x // 80
            map = MainGame.map_list[a][b]
            map.can_grow = True
            plant.live = False
            self.stop = False                                     #植物死亡后，僵尸继续移动

    def display_zombie(self):
        MainGame.screen.blit(self.image,self.rect)                   #把僵尸画出来

class MainGame():                                               #记录游戏数据的类
    #创建关数，得分，剩余分数，钱数
    guanshu = 1
    score = 0
    remnant_score = 100
    sun = 300
    #存储所有地图坐标点
    map_points_list = []
    #存储所有的地图块
    map_list = []
    #存储所有植物的列表
    plants_list = []
    #存储所有豌豆子弹的列表
    peabullet_list = []
    #新增存储所有僵尸的列表
    zombie_list = []
    count_zombie = 0
    produce_zombie = 100
    #加载游戏窗口
    def init_screen(self):
        #1 调用显示模块的初始化
        pygame.display.init()
        MainGame.screen = pygame.display.set_mode([screen_width, screen_height])  #圈定屏幕的大小

    def draw_text(self, content, size, color):              #绘制要显示的文本
        pygame.font.init()                                  #初始化pygame的字体模块
        font = pygame.font.SysFont('kaiti', size)           #楷体
        text = font.render(content, True, color)            #创建一个包含文本的图像，true表示启用抗锯齿
        return text
    #加载帮助提示
    def load_help_text(self):
        text1 = self.draw_text('左键向日葵，右键豌豆射手，下划坚果', 20, (255, 0, 0))  #字体大小为 20，颜色为红色
        MainGame.screen.blit(text1, (5, 5))
    #为地图上的每个潜在植物放置位置创建和存储坐标点
    def init_plant_points(self):                                       #将坐标点画出来
        for y in range(1, 7):                                          #y轴分成六份
            points = []                                               #每一份都有一个列表points来存
            for x in range(10):                                        #x轴分十份
                point = (x, y)
                points.append(point)                                     #分别存入列表points中
            MainGame.map_points_list.append(points)                         #然后把points列表存入map_poings_list属性中
            print("MainGame.map_points_list", MainGame.map_points_list)

    def init_map(self):                                                        # 创建地图
        for points in MainGame.map_points_list:                               #points中存的是坐标点
            temp_map_list = list()
            for point in points:                           #根据坐标奇偶性创建地图块可以保证每个地图相邻的不会是相同的地图
                if (point[0] + point[1]) % 2 == 0:
                    map = Map(point[0] * 80, point[1] * 80, 0)          #坐标乘以 80 是因为每个地图块的大小设定为 80 像素 
                else:
                    map = Map(point[0] * 80, point[1] * 80, 1)
                # 将地图块加入到窗口中
                temp_map_list.append(map)
                print("temp_map_list", temp_map_list)
            MainGame.map_list.append(temp_map_list)                      #将临时列表添加到全局地图列表
        print("MainGame.map_list", MainGame.map_list)                

    def load_map(self):                                          # 将地图加载到窗口中
        for temp_map_list in MainGame.map_list:
            for map in temp_map_list:
                map.load_map()

    def load_plants(self):                                                              #加载植物
        for plant in MainGame.plants_list:
            #6 优化加载植物的处理逻辑
            if plant.live:
                #用isinstance 函数检查游戏中的植物对象属于哪个具体的类
                if isinstance(plant, Sunflower):
                    plant.display_sunflower()
                    plant.produce_sun()
                elif isinstance(plant, PeaShooter):
                    plant.display_peashooter()
                    plant.shot()
                elif isinstance(plant,Qiang):
                    plant.display_qiang()
            else:
                MainGame.plants_list.remove(plant)                   #移除死亡的植物

    #7 加载所有子弹的方法
    def load_peabullets(self):
        for b in MainGame.peabullet_list:
            if b.live:
                b.display_peabullet()
                b.move_bullet()
                #调用子弹是否打中僵尸的方法
                b.hit_zombie()
            else:
                MainGame.peabullet_list.remove(b)

    def deal_events(self):
        #8 获取所有事件
        eventList = pygame.event.get()
        #8 遍历事件列表，判断
        for e in eventList:
            if e.type == pygame.QUIT:
                self.gameOver()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                #1. 打印鼠标点击位置
                print(e.pos)
                x = e.pos[0] // 80
                y = e.pos[1] // 80
                #2. 打印计算后的地图块索引
                print(x, y)
                map = MainGame.map_list[y - 1][x]       #此处是二维的索引性质
                #3. 打印地图块的位置
                print(map.position)
                #左键1 按下滚轮2 右键 3
                if e.button == 1:
                    if map.can_grow and MainGame.sun >= 50:
                        sunflower = Sunflower(map.position[0], map.position[1])
                        MainGame.plants_list.append(sunflower)
                        #4. 打印当前植物列表的长度
                        print('当前植物列表长度:{}'.format(len(MainGame.plants_list)))
                        map.can_grow = False
                        MainGame.sun -= 50
                elif e.button == 2:
                    if map.can_grow and MainGame.sun >= 50:
                        qiang = Qiang(map.position[0], map.position[1])
                        MainGame.plants_list.append(qiang)
                        print('当前植物列表长度:{}'.format(len(MainGame.plants_list)))
                        map.can_grow = False
                        MainGame.sun -= 50
                elif e.button == 3:
                    if map.can_grow and MainGame.sun >= 50:
                        peashooter = PeaShooter(map.position[0], map.position[1])
                        MainGame.plants_list.append(peashooter)
                        print('当前植物列表长度:{}'.format(len(MainGame.plants_list)))
                        map.can_grow = False
                        MainGame.sun -= 50

    #9 新增初始化僵尸的方法
    def init_zombies(self):
        for i in range(1, 7):
            dis = random.randint(1, 5) * 200             #向右随机偏移200~1000像素
            zombie = Zombie(800 + dis, i * 80)
            MainGame.zombie_list.append(zombie)

    #9将所有僵尸加载到地图中
    def load_zombies(self):
        for zombie in MainGame.zombie_list:
            if zombie.live:
                zombie.display_zombie()
                zombie.move_zombie()
                #调用是否碰撞到植物的方法
                zombie.hit_plant()
            else:
                MainGame.zombie_list.remove(zombie)

    def start_game(self):                #此处是游戏的主循环
        #初始化窗口
        self.init_screen()
        #初始化坐标和地图
        self.init_plant_points()
        self.init_map()
        #调用初始化僵尸的方法
        self.init_zombies()
        #只要游戏没结束，就一直循环
        while not GAMEOVER:
            #渲染白色背景
            MainGame.screen.fill((255, 255, 255))
            #渲染的文字和坐标位置
            MainGame.screen.blit(self.draw_text('当前阳光: {}'.format(MainGame.sun), 26, (255, 0, 0)), (500, 40))
            MainGame.screen.blit(self.draw_text(
                '当前关数{}，得分{},距离下关还差{}分'.format(MainGame.guanshu, MainGame.score, MainGame.remnant_score), 26,
                (255, 0, 0)), (5, 40))
            self.load_help_text()
            #需要反复加载地图
            self.load_map()
            #调用加载植物的方法
            self.load_plants()
            #调用加载所有子弹的方法
            self.load_peabullets()
            #调用事件处理的方法
            self.deal_events()
            #调用展示僵尸的方法
            self.load_zombies()
            #计数器增长，每数到100，调用初始化僵尸的方法
            MainGame.count_zombie += 1
            if MainGame.count_zombie == MainGame.produce_zombie:
                self.init_zombies()
                MainGame.count_zombie = 0
            #pygame自己的休眠
            pygame.time.wait(10)
            #实时更新
            pygame.display.update()

    #程序结束方法
    def gameOver(self):
        sys.exit()

#1 启动主程序
if __name__ == '__main__':
    game = MainGame()
    game.start_game()