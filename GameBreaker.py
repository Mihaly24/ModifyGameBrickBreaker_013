import tkinter as tk

class GameObject(object):
    """A generic game object."""
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        """Get the position of the object."""
        return self.canvas.coords(self.item)

    def move(self, x, y):
        """Move the object by x, y."""
        self.canvas.move(self.item, x, y)

    def delete(self):
        """Delete the object."""
        self.canvas.delete(self.item)


class Ball(GameObject):
    """A ball that bounces and moves."""
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 10
        item = canvas.create_oval(x-self.radius, y-self.radius,
                                  x+self.radius, y+self.radius,
                                  fill='#B6FFFA')
        super(Ball, self).__init__(canvas, item)

    def update(self):
        """Update the position of the ball."""
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        """Check for collisions with the game objects."""
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    """A paddle that can move left and right."""
    def __init__(self, canvas, x, y):
        self.width = 50
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#6528F7')
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        """Set the ball that is attached to the paddle."""
        self.ball = ball

    def move(self, offset):
        """Move the paddle by offset."""
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    """A brick that can be hit and destroyed."""
    COLORS = {1: '#15F5BA', 2: '#836FFF', 3: '#211951', 4: '#000000'}

    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = Brick.COLORS[hits]
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        """Hit the brick and decrease its hits."""
        self.hits -= 1
        if self.hits <= 0:
            self.animate_delete()
        else:
            new_color = Brick.COLORS.get(self.hits, '')
            self.canvas.itemconfig(self.item, fill=new_color)

    def animate_delete(self):
        """Animate the brick before deleting it."""
        for i in range(5):
            self.canvas.after(i * 100, lambda: self.canvas.itemconfig(self.item, fill='red'))
            self.canvas.after(i * 100 + 50, lambda: self.canvas.itemconfig(self.item, fill=''))
        self.canvas.after(500, lambda: self.delete())


class Game(tk.Frame):
    """The main game class."""
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 1
        self.score = 0
        self.width = 830
        self.height = 400
        self.canvas = tk.Canvas(self, bg='#FF78F0',
                                width=self.width,
                                height=self.height,)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width/2, 326)
        self.items[self.paddle.item] = self.paddle
        for x in range(5, self.width - 5, 75):
            self.add_brick(x + 37.5, 30, 4)
            self.add_brick(x + 37.5, 50, 4)
            self.add_brick(x + 37.5, 70, 3)
            self.add_brick(x + 37.5, 90, 3)
            self.add_brick(x + 37.5, 110, 2)
            self.add_brick(x + 37.5, 130, 2)
            self.add_brick(x + 37.5, 150, 1)
            self.add_brick(x + 37.5, 170, 1)

        self.hud = None
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>',
                         lambda _: self.paddle.move(-15))
        self.canvas.bind('<Right>',
                         lambda _: self.paddle.move(15))

    def setup_game(self):
        """Set up the game by creating the ball and drawing the HUD."""
        self.add_ball()
        self.update_hud()
        self.text = self.draw_text(400, 200,
                                   'Press Space to start')
        self.canvas.bind('<space>', lambda _: self.start_game())

    def add_ball(self):
        """Add a new ball to the game."""
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 310)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        """Add a new brick to the game."""
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='40'):
        """Draw text on the canvas."""
        font = ('Calibri', size, 'bold')
        return self.canvas.create_text(x, y, text=text,
                                       font=font)

    def update_hud(self):
        """Update the HUD by drawing the score and lives."""
        lives_text = 'Lives: %s' % self.lives
        score_text = 'Score: %s' % self.score
        if self.hud is None:
            self.hud = {}
            self.hud['lives'] = self.draw_text(50, 10, lives_text, 15)
            self.hud['score'] = self.draw_text(775, 10, score_text, 15)
        else:
            self.canvas.itemconfig(self.hud['lives'], text=lives_text)
            self.canvas.itemconfig(self.hud['score'], text=score_text)

    def start_game(self):
        """Start the game by unbinding the space key and deleting the start text."""
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        """The main game loop that updates the ball and checks for collisions."""
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0: 
            self.ball.speed = None
            self.draw_text(400, 200, 'Congratulations! You Won!\nScore: %s' % self.score)
        elif self.ball.get_position()[3] >= self.height: 
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(400, 200, '👎Loser! Game Over!👎\nScore: %s' % self.score)
            else:
                self.animate_ball_fall()
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def animate_ball_fall(self):
        """Animate the ball when it falls to the ground."""
        for i in range(5):
            self.canvas.after(i * 100, lambda: self.canvas.itemconfig(self.ball.item, fill='red'))
            self.canvas.after(i * 100 + 50, lambda: self.canvas.itemconfig(self.ball.item, fill=''))

    def check_collisions(self):
        """Check for collisions between the ball and the game objects."""
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)
        for obj in objects:
            if isinstance(obj, Brick):
                self.score += 10
                if obj.hits <= 0:
                    self.score += 10
                self.update_hud()

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Ball Brick Breaker (Expert Mode 😈)')
    game = Game(root)
    game.mainloop()


