from turtle import Turtle, setup, bye, title, screensize, delay, onkey, onclick, window_width, window_height, listen, done, hideturtle
from time import sleep
from random import randrange
from math import floor
from threading import Timer


class Button():
    font_height = 10/14
    correction = 3

    def __init__(self, turtle, text="Button", font=("Arial", 12, "normal"), pos=(0, 0), snake=None):
        self.turtle = turtle
        self.text = text
        self.font = font
        self.pos = pos
        self.snake = snake
        self.turtle.setpos(pos)
        self.turtle.write(text, True, align="center", font=font)
        self.rect = {'min_x': round(self.turtle.xcor() - (self.turtle.xcor() - pos[0]) * 2), 'min_y': self.turtle.ycor() + self.correction, 'max_x': self.turtle.xcor(), 'max_y': round(self.turtle.ycor(
        ) + font[1] * self.font_height) + self.correction}

    def onclick(self, fun):
        def callback(pos):
            if self.on_self(pos):
                fun(self)

        if self.snake:
            self.snake.buttons.append(callback)

    def on_self(self, pos):
        if self.rect['min_x'] <= pos[0] <= self.rect['max_x'] and self.rect['min_y'] <= pos[1] <= self.rect['max_y']:
            return True
        return False


class Snake():
    aux_turtle = None
    turtle = None
    screen = None
    buttons = []

    FPS = 80
    TURTLE_ABS_SIZE = 14
    TURTLE_SIZE = 10
    SPEED = 0.2
    WIDTH = TURTLE_SIZE * 50
    HEIGHT = TURTLE_SIZE * 50

    def __init__(self):

        # Turtle setup
        self.turtle = Turtle()
        self.turtle.shape('square')
        self.turtle.resizemode('user')
        self.turtle.shapesize(self.TURTLE_SIZE / self.TURTLE_ABS_SIZE,
                              self.TURTLE_SIZE / self.TURTLE_ABS_SIZE)
        self.turtle.up()

        # Screen setup
        self.screen = self.turtle.getscreen()
        self.screen.setup(width=self.WIDTH, height=self.HEIGHT)
        self.screen.title("Snake")
        self.screen.screensize(self.WIDTH - self.TURTLE_SIZE,
                               self.HEIGHT - self.TURTLE_SIZE)
        self.screen.delay(round(1000/self.FPS))
        # hideturtle()

        # Auxiliar Turtle setup
        self.aux_turtle = Turtle()
        self.aux_turtle.hideturtle()
        self.aux_turtle.up()
        self.aux_turtle.speed(0)

        # Event bindings
        self.screen.onkey(self.turnRight, 'Right')
        self.screen.onkey(self.turnLeft, 'Left')
        self.screen.onkey(self.turnUp, 'Up')
        self.screen.onkey(self.turnDown, 'Down')
        self.screen.onkey(lambda: self.screen.bye(), 'Escape')
        self.screen.onkey(self.restart, 'r')

        self.screen.onclick(self.click_callback)

        self.init_state()

    def init_state(self):
        self.canTurn = True
        self.stamps = []
        self.size = 0
        self.stop = False
        self.target_pos = None
        self.started = False

    def start(self):
        self.spawn_target()
        self.screen.listen()
        self.screen.mainloop()

    def restart(self):
        self.aux_turtle.clear()
        s = self.turtle.speed()
        self.turtle.speed(0)
        self.turtle.setpos(0, 0)
        self.turtle.speed(s)
        self.turtle.showturtle()
        self.init_state()
        self.spawn_target()

    def click_callback(self, *pos):
        for cb in self.buttons:
            cb((*pos, ))

    def gameover(self):
        def test(btn):
            print(btn)

        self.turtle.hideturtle()
        for st in self.stamps:
            self.turtle.clearstamp(st['id'])

        # Clears target
        self.aux_turtle.setpos(self.target_pos)
        self.aux_turtle.dot(self.TURTLE_SIZE, 'white')
        # Writes Game Over and Score text
        # self.aux_turtle.setpos(0, 10)
        # self.aux_turtle.write(
        #     "Game Over", True, align="center", font=("Arial", 14, "bold"))
        game_over_btn = Button(self.aux_turtle, "Game Over",
                               pos=(0, 10), font=("Arial", 14, "bold"), snake=self)
        game_over_btn.onclick(test)
        # self.aux_turtle.setpos(0, -10)
        # self.aux_turtle.write(
        #     f"Score: {self.size}", True, align="center", font=("Arial", 12, "normal"))
        score_btn = Button(self.aux_turtle, f"Score: {self.size}", pos=(
            0, -10), font=("Arial", 12, "normal"), snake=self)
        score_btn.onclick(test)
        self.screen.listen()

    def move(self):
        def fn():
            if len(self.stamps) == self.size and self.size > 0:
                self.turtle.clearstamp(self.stamps.pop(0)['id'])
            if len(self.stamps) < self.size:
                self.stamps.append(
                    {'id': self.turtle.stamp(), "pos": self.turtle.pos()})
            self.turtle.forward(self.TURTLE_SIZE * 2)
            # Check hits on itself
            for st in self.stamps:
                if st['pos'] == self.turtle.pos():
                    self.stop = True
            # Check if target was reached
            if self.is_pos_equal(self.turtle.pos(), self.target_pos):
                self.size += 1
                self.spawn_target(reset=True)
            self.canTurn = True
            self.move()

        if self.in_screen() and not self.stop:
            t = Timer(self.screen.delay() / 1000 * (1/self.SPEED), fn)
            t.daemon = True
            t.start()
        else:
            self.gameover()

    def in_screen(self):
        return self.clamp_down(-(self.screen.window_width() / 2), self.TURTLE_SIZE) < abs(self.turtle.xcor()) < self.clamp_down(self.screen.window_width() / 2, self.TURTLE_SIZE) and self.clamp_down(-(self.screen.window_height() / 2), self.TURTLE_SIZE) < abs(self.turtle.ycor()) < self.clamp_down(self.screen.window_height() / 2, self.TURTLE_SIZE)

    def in_tail(self, x, y):
        for st in self.stamps:
            if self.is_pos_equal((x, y), st['pos']):
                return True
        return False

    def is_pos_equal(self, p1, p2):
        return round(p1[0]) == round(p2[0]) and round(p1[1]) == round(p2[1])

    def spawn_target(self, reset=False):
        x = y = None
        while not x or not y or self.in_tail(x, y):
            x = self.clamp_down(randrange(-round(self.screen.window_width() / 2),
                                          round(self.screen.window_width() / 2)), self.TURTLE_SIZE * 2)
            x = max(min(x, self.clamp_down(self.screen.window_width() / 2, self.TURTLE_SIZE * 2)
                        ), -self.clamp_down(self.screen.window_width() / 2, self.TURTLE_SIZE * 2))

            y = self.clamp_down(randrange(-round(self.screen.window_height() / 2),
                                          round(self.screen.window_height() / 2)), self.TURTLE_SIZE * 2)
            y = max(min(y, self.clamp_down(self.screen.window_height() / 2, self.TURTLE_SIZE * 2)
                        ), -self.clamp_down(self.screen.window_height() / 2, self.TURTLE_SIZE * 2))

        if reset:
            self.aux_turtle.setpos(self.target_pos)
            self.aux_turtle.dot(self.TURTLE_SIZE, 'white')
        self.aux_turtle.setpos(x, y)
        self.aux_turtle.dot(self.TURTLE_SIZE, 'blue')
        self.target_pos = self.aux_turtle.pos()

    def setheading(self, angle):
        min_angle = angle
        max_angle = angle + 180 if angle + 180 < 360 else angle + 180 - 360
        if (self.turtle.heading() == min_angle or self.turtle.heading() == max_angle or not self.canTurn) and self.started:
            return
        s = self.turtle.speed()
        self.turtle.speed(0)
        self.turtle.seth(angle)
        self.turtle.speed(s)
        self.canTurn = False
        if not self.started:
            self.started = True
            self.move()

    def turnRight(self):
        self.setheading(0)

    def turnLeft(self):
        self.setheading(180)

    def turnUp(self):
        self.setheading(90)

    def turnDown(self):
        self.setheading(270)

    def clamp_to(self, value, multiple):
        return round(value / multiple) * multiple

    def clamp_down(self, value, multiple):
        return floor(value / multiple) * multiple


snake = Snake()
snake.start()
