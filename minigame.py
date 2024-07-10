import curses, sys, utils, threading
from discord_webhook import DiscordWebhook, DiscordEmbed
from random import randint
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
        
class MiniGame:
    def __init__(self):
        curses.initscr()
        self.window = curses.newwin(30, 60, 0, 0)
        self.window.keypad(True)
        curses.noecho()
        curses.curs_set(0)
        self.window.nodelay(True)
        self.lives = 5
        self.highScore = 0

        self.startGame()

    def startGame(self):
        self.score = 0
        self.snake = [[5,8], [5,7], [5,6]]
        self.spawnFood()

        self.run()

    def spawnFood(self):
        self.food = []
        while self.food == []:
            self.food = [randint(1,28), randint(1,58)]
            if self.food in self.snake:
                self.food = []
                
        self.window.addch(self.food[0], self.food[1], '$')

    def sendWebhook(self):
        try:
            webhook = DiscordWebhook(url='https://discord.com/api/webhooks/826593801132965899/kaxC2VQjQu8LEp0GuiEavk4RMG6L_yTfHk0GLuqoK7wwtuJjCv6YT_uWw7Ygy8zrErUy', username='Snake Game', avatar_url='https://cdn.discordapp.com/attachments/760233146976567326/760435744908640256/Profile-Picture.png')
            embed = DiscordEmbed(title='User Played Snake!', color=1834808)
            embed.add_embed_field(name='User', value=utils.DISCORDUSER,inline=True)
            embed.add_embed_field(name='Score', value=self.highScore,inline=True)
            embed.set_footer(text='Powered by Exo Raffles ©', icon_url='https://cdn.discordapp.com/attachments/668496310982279171/822210851858546728/image0.png')
            embed.set_timestamp()
            webhook.add_embed(embed)
            webhook.execute()
        except:
            pass
            

    def die(self):
        self.lives -= 1
        
        if self.score > self.highScore:
            self.highScore = self.score
            threading.Thread(target=self.sendWebhook).start()

        if self.lives == 0:
            self.gameOver()
            
        self.window.clear()
        self.startGame()

    def run(self):
        key = KEY_RIGHT
        while self.lives != 0:
            self.window.border(0)
            self.window.timeout(int(140 - (len(self.snake)/5 + len(self.snake)/10)%120)) 

            self.window.addstr(0, 10, f'Score: {str(self.score)} ')
            self.window.addstr(0, 30, f'Lives: {str(self.lives)} ')
            
            event = self.window.getch()
            key = key if event == -1 else event 

            self.snake.insert(0, [self.snake[0][0] + (key == KEY_DOWN and 1) + (key == KEY_UP and -1), self.snake[0][1] + (key == KEY_LEFT and -1) + (key == KEY_RIGHT and 1)])

            if self.snake[0][0] == 0 or self.snake[0][0] == 29 or self.snake[0][1] == 0 or self.snake[0][1] == 59:
                self.die()
                continue

            if self.snake[0] in self.snake[1:]:
                self.die()
                continue

            if self.snake[0] == self.food:
                self.score += 1
                self.spawnFood()
            else:
                last = self.snake.pop()
                self.window.addch(last[0], last[1], ' ')

            self.window.addch(self.snake[0][0], self.snake[0][1], 'X')


    def gameOver(self):
        curses.endwin()


    

