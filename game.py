#1 引入需要的模塊
import pygame
import random
#1 配置圖片地址
IMAGE_PATH = 'imgs/'
#1 設置頁面寬高
scrrr_width=800
scrrr_height =560
#1 創建控制遊戲結束的狀態
GAMEOVER = False
#4 圖片加載報錯處理
LOG = '文件:{}中的方法:{}出錯'.format(__file__,__name__)
#3 創建地圖類
class Map():
    #3 存儲兩張不同顏色的圖片名稱
    map_names_list = [IMAGE_PATH + 'map1.png', IMAGE_PATH + 'map2.png']
    #3 初始化地圖
    def __init__(self, x, y, img_index):
        self.image = pygame.image.load(Map.map_names_list[img_index])
        self.position = (x, y)
        # 是否能夠種植
        self.can_grow = True
    #3 加載地圖
    def load_map(self):
         MainGame.window.blit(self.image,self.position)
#4 植物類
class Plant(pygame.sprite.Sprite):
    def __init__(self):
        super(Plant, self).__init__()
        self.live=True

    # 加載圖片
    def load_image(self):
        if hasattr(self, 'image') and hasattr(self, 'rect'):
            MainGame.window.blit(self.image, self.rect)
        else:
            print(LOG)
#5 向日葵類
class Sunflower(Plant):
    def __init__(self,x,y):
        super(Sunflower, self).__init__()
        self.image = pygame.image.load('imgs/sunflower.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.price = 50
        self.hp = 100
        #5 時間計數器
        self.time_count = 0

    #5 新增功能：生成陽光
    def produce_money(self):
        self.time_count += 1
        if self.time_count == 25:
            MainGame.money += 5
            self.time_count = 0
    #5 向日葵加入到窗口中
    def display_sunflower(self):
        MainGame.window.blit(self.image,self.rect)
#6 豌豆射手類
class PeaShooter(Plant):
    def __init__(self,x,y):
        super(PeaShooter, self).__init__()
        # self.image 為一個 surface
        self.image = pygame.image.load('imgs/peashooter.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.price = 50
        self.hp = 200
        #6 發射計數器
        self.shot_count = 0

    #6 增加射擊方法
    def shot(self):
        #6 記錄是否應該射擊
        should_fire = False
        for zombie in MainGame.zombie_list:
            if zombie.rect.y == self.rect.y and zombie.rect.x < 800 and zombie.rect.x > self.rect.x:
                should_fire = True
        #6 如果活著
        if self.live and should_fire:
            self.shot_count += 1
            #6 計數器到25發射一次
            if self.shot_count == 25:
                #6 基於當前豌豆射手的位置，創建子彈
                peabullet = PeaBullet(self)
                #6 將子彈存儲到子彈列表中
                MainGame.peabullet_list.append(peabullet)
                self.shot_count = 0

    #6 將豌豆射手加入到窗口中的方法
    def display_peashooter(self):
        MainGame.window.blit(self.image,self.rect)

#7 豌豆子彈類
class PeaBullet(pygame.sprite.Sprite):
    def __init__(self,peashooter):
        self.live = True
        self.image = pygame.image.load('imgs/peabullet.png')
        self.damage = 70
        self.speed  = 40
        self.rect = self.image.get_rect()
        self.rect.x = peashooter.rect.x + 60
        self.rect.y = peashooter.rect.y + 15

    def move_bullet(self):
        #7 在屏幕範圍內，實現往右移動
        if self.rect.x < scrrr_width:
            self.rect.x += self.speed
        else:
            self.live = False

    #7 新增，子彈與僵屍的碰撞
    def hit_zombie(self):
        for zombie in MainGame.zombie_list:
            if pygame.sprite.collide_rect(self,zombie):
                #打中僵屍之後，修改子彈的狀態，
                self.live = False
                #僵屍掉血
                zombie.hp -= self.damage
                if zombie.hp <= 0:
                    zombie.live = False
                    self.nextLevel()
    #7闖關方法
    def nextLevel(self):
        MainGame.score += 20
        MainGame.remnant_score -=20
        for i in range(1,100):
            if MainGame.score==100*i and MainGame.remnant_score==0:
                    MainGame.remnant_score=100*i
                    MainGame.shaoguan+=1
                    MainGame.produce_zombie+=50



    def display_peabullet(self):
        MainGame.window.blit(self.image,self.rect)
#9 僵屍類
class Zombie(pygame.sprite.Sprite):
    def __init__(self,x,y):
        super(Zombie, self).__init__()
        self.image = pygame.image.load('imgs/zombie.png')
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.hp = 1000
        self.damage = 2
        self.speed = 1
        self.live = True
        self.stop = False
    #9 僵屍的移動
    def move_zombie(self):
        if self.live and not self.stop:
            self.rect.x -= self.speed
            if self.rect.x < -80:
                #8 調用遊戲結束方法
                MainGame().gameOver()

    #9 判斷僵屍是否碰撞到植物，如果碰撞，調用攻擊植物的方法
    def hit_plant(self):
        for plant in MainGame.plants_list:
            if pygame.sprite.collide_rect(self,plant):
                #8  僵屍移動狀態的修改
                self.stop = True
                self.eat_plant(plant)
    #9 僵屍攻擊植物
    def eat_plant(self,plant):
        #9 植物生命值減少
        plant.hp -= self.damage
        #9 植物死亡後的狀態修改，以及地圖狀態的修改
        if plant.hp <= 0:
            a = plant.rect.y // 80 - 1
            b = plant.rect.x // 80
            map = MainGame.map_list[a][b]
            map.can_grow = True
            plant.live = False
            #8 修改僵屍的移動狀態
            self.stop = False



    #9 將僵屍加載到地圖中
    def display_zombie(self):
        MainGame.window.blit(self.image,self.rect)
#1 主程序
class MainGame():
    #2 創建關數，得分，剩余分數，錢數
    shaoguan = 1
    score = 0
    remnant_score = 100
    money = 200
    #3 存儲所有地圖坐標點
    map_points_list = []
    #3 存儲所有的地圖塊
    map_list = []
    #4 存儲所有植物的列表
    plants_list = []
    #7 存儲所有豌豆子彈的列表
    peabullet_list = []
    #9 新增存儲所有僵屍的列表
    zombie_list = []
    count_zombie = 0
    produce_zombie = 100
    #1 加載遊戲窗口
    def init_window(self):
        #1 調用顯示模塊的初始化
        pygame.display.init()
        #1 創建窗口
        MainGame.window = pygame.display.set_mode([scrrr_width,scrrr_height])

    #2 文本繪制
    def draw_text(self, content, size, color):
        pygame.font.init()
        font = pygame.font.SysFont('kaiti', size)
        text = font.render(content, True, color)
        return text

    #2 加載幫助提示
    def load_help_text(self):
        text1 = self.draw_text('1.按左鍵創建向日葵 2.按右鍵創建豌豆射手', 26, (255, 0, 0))
        MainGame.window.blit(text1, (5, 5))

    #3 初始化坐標點
    def init_plant_points(self):
        for y in range(1, 7):
            points = []
            for x in range(10):
                point = (x, y)
                points.append(point)
            MainGame.map_points_list.append(points)
            print("MainGame.map_points_list", MainGame.map_points_list)

    #3 初始化地圖
    def init_map(self):
        for points in MainGame.map_points_list:
            temp_map_list = list()
            for point in points:
                # map = None
                if (point[0] + point[1]) % 2 == 0:
                    map = Map(point[0] * 80, point[1] * 80, 0)
                else:
                    map = Map(point[0] * 80, point[1] * 80, 1)
                # 將地圖塊加入到窗口中
                temp_map_list.append(map)
                print("temp_map_list", temp_map_list)
            MainGame.map_list.append(temp_map_list)
        print("MainGame.map_list", MainGame.map_list)

    #3 將地圖加載到窗口中
    def load_map(self):
        for temp_map_list in MainGame.map_list:
            for map in temp_map_list:
                map.load_map()

    #6 增加豌豆射手發射處理
    def load_plants(self):
        for plant in MainGame.plants_list:
            #6 優化加載植物的處理邏輯
            if plant.live:
                if isinstance(plant, Sunflower):
                    plant.display_sunflower()
                    plant.produce_money()
                elif isinstance(plant, PeaShooter):
                    plant.display_peashooter()
                    plant.shot()
            else:
                MainGame.plants_list.remove(plant)

    #7 加載所有子彈的方法
    def load_peabullets(self):
        for b in MainGame.peabullet_list:
            if b.live:
                b.display_peabullet()
                b.move_bullet()
                # v1.9 調用子彈是否打中僵屍的方法
                b.hit_zombie()
            else:
                MainGame.peabullet_list.remove(b)

    #8事件處理

    def deal_events(self):
        #8 獲取所有事件
        eventList = pygame.event.get()
        #8 遍歷事件列表，判斷
        for e in eventList:
            if e.type == pygame.QUIT:
                self.gameOver()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                # print('按下鼠標按鍵')
                print(e.pos)
                # print(e.button)#左鍵1  按下滾輪2 上轉滾輪為4 下轉滾輪為5  右鍵 3

                x = e.pos[0] // 80
                y = e.pos[1] // 80
                print(x, y)
                map = MainGame.map_list[y - 1][x]
                print(map.position)
                #8 增加創建時候的地圖裝填判斷以及金錢判斷
                if e.button == 1:
                    if map.can_grow and MainGame.money >= 50:
                        sunflower = Sunflower(map.position[0], map.position[1])
                        MainGame.plants_list.append(sunflower)
                        print('當前植物列表長度:{}'.format(len(MainGame.plants_list)))
                        map.can_grow = False
                        MainGame.money -= 50
                elif e.button == 3:
                    if map.can_grow and MainGame.money >= 50:
                        peashooter = PeaShooter(map.position[0], map.position[1])
                        MainGame.plants_list.append(peashooter)
                        print('當前植物列表長度:{}'.format(len(MainGame.plants_list)))
                        map.can_grow = False
                        MainGame.money -= 50

    #9 新增初始化僵屍的方法
    def init_zombies(self):
        for i in range(1, 7):
            dis = random.randint(1, 5) * 200
            zombie = Zombie(800 + dis, i * 80)
            MainGame.zombie_list.append(zombie)

    #9將所有僵屍加載到地圖中
    def load_zombies(self):
        for zombie in MainGame.zombie_list:
            if zombie.live:
                zombie.display_zombie()
                zombie.move_zombie()
                # v2.0 調用是否碰撞到植物的方法
                zombie.hit_plant()
            else:
                MainGame.zombie_list.remove(zombie)
    #1 開始遊戲
    def start_game(self):
        #1 初始化窗口
        self.init_window()
        #3 初始化坐標和地圖
        self.init_plant_points()
        self.init_map()
        #9 調用初始化僵屍的方法
        self.init_zombies()
        #1 只要遊戲沒結束，就一直循環
        while not GAMEOVER:
            #1 渲染白色背景
            MainGame.window.fill((255, 255, 255))
            #2 渲染的文字和坐標位置
            MainGame.window.blit(self.draw_text('當前錢數$: {}'.format(MainGame.money), 26, (255, 0, 0)), (500, 40))
            MainGame.window.blit(self.draw_text(
                '當前關數{}，得分{},距離下關還差{}分'.format(MainGame.shaoguan, MainGame.score, MainGame.remnant_score), 26,
                (255, 0, 0)), (5, 40))
            self.load_help_text()

            #3 需要反覆加載地圖
            self.load_map()
            #6 調用加載植物的方法
            self.load_plants()
            #7  調用加載所有子彈的方法
            self.load_peabullets()
            #8 調用事件處理的方法
            self.deal_events()
            #9 調用展示僵屍的方法
            self.load_zombies()
            #9 計數器增長，每數到100，調用初始化僵屍的方法
            MainGame.count_zombie += 1
            if MainGame.count_zombie == MainGame.produce_zombie:
                self.init_zombies()
                MainGame.count_zombie = 0
            #9 pygame自己的休眠
            pygame.time.wait(10)
            #1 實時更新
            pygame.display.update()

    #10 程序結束方法
    def gameOver(self):
        MainGame.window.blit(self.draw_text('遊戲結束', 50, (255, 0, 0)), (300, 200))
        print('遊戲結束')
        pygame.time.wait(400)
        global GAMEOVER
        GAMEOVER = True
#1 啟動主程序
if __name__ == '__main__':
    game = MainGame()
    game.start_game()