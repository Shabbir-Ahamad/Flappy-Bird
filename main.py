import pygame as pg
import sys, time, os
from bird import Bird
from pipe import Pipe

pg.init()
pg.mixer.init()

WHITE = (255, 255, 255)
RED = (220, 20, 60)

class Game:
    def __init__(self):
        self.width = 600
        self.height = 768
        self.scale_factor = 1.5
        self.win = pg.display.set_mode((self.width, self.height))
        pg.display.set_caption("Flappy Bird")
        self.clock = pg.time.Clock()
        self.move_speed = 250

        # -------- SOUNDS --------
        self.flap_sound = pg.mixer.Sound("assets/sfx/flap.wav")
        self.score_sound = pg.mixer.Sound("assets/sfx/score.wav")
        self.dead_sound = pg.mixer.Sound("assets/sfx/dead.wav")

        # -------- FONTS --------
        self.font = pg.font.Font("assets/font.ttf", 48)
        self.small_font = pg.font.Font("assets/font.ttf", 32)

        self.load_high_score()
        self.reset_game()
        self.setUpBgAndGround()
        self.gameLoop()

    # ================= HIGH SCORE =================
    def load_high_score(self):
        if not os.path.exists("highscore.txt"):
            with open("highscore.txt", "w") as f:
                f.write("0")

        with open("highscore.txt", "r") as f:
            self.high_score = int(f.read())

    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            with open("highscore.txt", "w") as f:
                f.write(str(self.high_score))

    # ================= RESET =================
    def reset_game(self):
        self.bird = Bird(self.scale_factor)
        self.bird.rect.center = (100, 300)
        self.bird.update_on = False

        self.is_enter_pressed = False
        self.game_over = False
        self.paused = False

        self.score = 0
        self.pipes = []
        self.pipe_generate_counter = 71

        self.is_night = False

        self.restart_btn = pg.Rect(200, 420, 200, 60)

    # ================= GAME LOOP =================
    def gameLoop(self):
        last_time = time.time()

        while True:
            dt = time.time() - last_time
            last_time = time.time()

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()

                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_SPACE and not self.game_over:
                        self.is_enter_pressed = True
                        self.bird.update_on = True
                        self.bird.flap(dt)
                        self.flap_sound.play()

                    if event.key == pg.K_RETURN and not self.game_over:
                        self.is_enter_pressed = True
                        self.bird.update_on = True

                    if event.key == pg.K_p:
                        self.paused = not self.paused

                    if event.key == pg.K_n:
                        self.is_night = not self.is_night

                if event.type == pg.MOUSEBUTTONDOWN and self.game_over:
                    if self.restart_btn.collidepoint(event.pos):
                        self.reset_game()

            if not self.game_over and not self.paused:
                self.updateEverything(dt)
                self.checkCollisions()

            self.drawEverything()
            pg.display.update()
            self.clock.tick(60)

    # ================= COLLISION =================
    def checkCollisions(self):
        if self.bird.rect.bottom > 568:
            self.trigger_game_over()

        for pipe in self.pipes:
            if self.bird.rect.colliderect(pipe.rect_up) or \
               self.bird.rect.colliderect(pipe.rect_down):
                self.trigger_game_over()

            if pipe.rect_up.right < self.bird.rect.left and not hasattr(pipe, "scored"):
                pipe.scored = True
                self.score += 1
                self.score_sound.play()

                if self.score % 10 == 0:
                    self.is_night = not self.is_night

    # ================= GAME OVER =================
    def trigger_game_over(self):
        if not self.game_over:
            self.dead_sound.play()
            self.save_high_score()

        self.game_over = True
        self.is_enter_pressed = False
        self.bird.update_on = False

    # ================= UPDATE =================
    def updateEverything(self, dt):
        if self.is_enter_pressed:
            self.ground1_rect.x -= int(self.move_speed * dt)
            self.ground2_rect.x -= int(self.move_speed * dt)

            if self.ground1_rect.right < 0:
                self.ground1_rect.x = self.ground2_rect.right
            if self.ground2_rect.right < 0:
                self.ground2_rect.x = self.ground1_rect.right

            if self.pipe_generate_counter > 70:
                self.pipes.append(Pipe(self.scale_factor, self.move_speed))
                self.pipe_generate_counter = 0

            self.pipe_generate_counter += 1

            for pipe in self.pipes:
                pipe.update(dt)

            if self.pipes and self.pipes[0].rect_up.right < 0:
                self.pipes.pop(0)

        self.bird.update(dt)

    # ================= DRAW =================
    def drawEverything(self):
        bg = self.night_bg if self.is_night else self.day_bg
        self.win.blit(bg, (0, -300))

        for pipe in self.pipes:
            pipe.drawPipe(self.win)

        ground_img = self.night_ground_img if self.is_night else self.day_ground_img
        self.win.blit(ground_img, self.ground1_rect)
        self.win.blit(ground_img, self.ground2_rect)

        self.win.blit(self.bird.image, self.bird.rect)

        self.win.blit(
            self.small_font.render(f"Score : {self.score}", True, WHITE),
            (20, 20)
        )

        self.win.blit(
            self.small_font.render(f"High : {self.high_score}", True, WHITE),
            (20, 55)
        )

        if self.paused:
            self.win.blit(self.font.render("PAUSED", True, WHITE), (190, 300))

        if self.game_over:
            self.drawGameOver()

    def drawGameOver(self):
        self.win.blit(self.font.render("GAME OVER", True, RED), (130, 320))
        pg.draw.rect(self.win, RED, self.restart_btn, border_radius=10)
        self.win.blit(
            self.small_font.render("Restart", True, WHITE),
            (self.restart_btn.x + 13, self.restart_btn.y + 15)
        )

    # ================= ASSETS =================
    def setUpBgAndGround(self):
        self.day_bg = pg.transform.scale_by(
            pg.image.load("assets/bg.png").convert(),
            self.scale_factor
        )

        self.night_bg = pg.transform.scale_by(
            pg.image.load("assets/night_bg.png").convert(),
            self.scale_factor
        )

        self.day_ground_img = pg.transform.scale_by(
            pg.image.load("assets/ground.png").convert(),
            self.scale_factor
        )

        self.night_ground_img = pg.transform.scale_by(
            pg.image.load("assets/night_ground.png").convert(),
            self.scale_factor
        )

        self.ground1_rect = self.day_ground_img.get_rect()
        self.ground2_rect = self.day_ground_img.get_rect()

        self.ground1_rect.x = 0
        self.ground2_rect.x = self.ground1_rect.right
        self.ground1_rect.y = 568
        self.ground2_rect.y = 568


Game()
