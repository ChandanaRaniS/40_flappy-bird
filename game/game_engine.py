import pygame
from .bird import Bird
from .pipe import Pipe
from .sound_effects import SoundEffects

# Game Engine

WHITE = (255, 255, 255)
GREEN = (0, 150, 0)
RED = (190, 55, 55)

DIFFICULTIES = {
    "Easy": (3, 180),
    "Medium": (4, 150),
    "Hard": (6, 120),
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.pipe_interval = 90  # frames between pipe spawns
        self.font = pygame.font.SysFont("Arial", 30)
        self.game_over_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.game_over_prompt_font = pygame.font.SysFont("Arial", 22)
        self.game_over_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        self.game_over_overlay.fill((0, 0, 0, 160))
        self.game_over_options = self._make_game_over_options()
        self.sound_effects = SoundEffects()
        self.restart("Medium")

    def _make_game_over_options(self):
        labels = ("Easy", "Medium", "Hard", "Exit")
        button_width = 100
        button_height = 44
        button_gap = 8
        total_width = len(labels) * button_width + (len(labels) - 1) * button_gap
        left = (self.width - total_width) // 2
        top = self.height // 2 + 5
        return {
            label: pygame.Rect(
                left + index * (button_width + button_gap),
                top,
                button_width,
                button_height,
            )
            for index, label in enumerate(labels)
        }

    def restart(self, difficulty):
        self.difficulty = difficulty
        self.pipe_speed, self.pipe_gap = DIFFICULTIES[difficulty]
        self.bird = Bird(self.width // 4, self.height // 2)
        self._spawn_timer = 0
        self.pipes = [
            Pipe(
                self.width + 100,
                self.height,
                gap=self.pipe_gap,
                speed=self.pipe_speed,
            )
        ]
        self.score = 0
        self.game_over = False

    def handle_game_over_event(self, event):
        if not self.game_over:
            return None

        if event.type == pygame.KEYDOWN:
            key_selections = {
                pygame.K_1: "Easy",
                pygame.K_2: "Medium",
                pygame.K_3: "Hard",
                pygame.K_4: "Exit",
                pygame.K_ESCAPE: "Exit",
            }
            return key_selections.get(event.key)

        if event.type == pygame.MOUSEBUTTONDOWN:
            for label, rect in self.game_over_options.items():
                if rect.collidepoint(event.pos):
                    return label

        return None

    def handle_event(self, event):
        if self.game_over:
            return

        # Flap is edge-triggered (KEYDOWN / MOUSEBUTTONDOWN), not held.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.bird.flap()
            self.sound_effects.play_flap()
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.bird.flap()
            self.sound_effects.play_flap()

    def _end_game(self):
        if not self.game_over:
            self.game_over = True
            self.sound_effects.play_death()

    def handle_input(self):
        # Reserved for continuously-held-key input; flapping is handled
        # in handle_event instead, so there's nothing to poll here.
        pass

    def update(self):
        if self.game_over:
            return

        self.bird.update()

        if self.bird.y - self.bird.radius <= 0 or self.bird.y + self.bird.radius >= self.height:
            self._end_game()
            return

        self._spawn_timer += 1
        if self._spawn_timer >= self.pipe_interval:
            self._spawn_timer = 0
            self.pipes.append(Pipe(self.width, self.height, speed=self.pipe_speed))

        for pipe in self.pipes:
            pipe.move()

            bird_rect = self.bird.rect()
            if bird_rect.colliderect(pipe.top_rect()) or bird_rect.colliderect(pipe.bottom_rect()):
                self._end_game()

            if not pipe.scored and pipe.x + pipe.width < self.bird.x:
                pipe.scored = True
                self.score += 1
                self.sound_effects.play_score()

        self.pipes = [p for p in self.pipes if not p.off_screen()]

    def render(self, screen):
        for pipe in self.pipes:
            pygame.draw.rect(screen, GREEN, pipe.top_rect())
            pygame.draw.rect(screen, GREEN, pipe.bottom_rect())

        pygame.draw.circle(screen, WHITE, (int(self.bird.x), int(self.bird.y)), self.bird.radius)

        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if self.game_over:
            screen.blit(self.game_over_overlay, (0, 0))

            title = self.game_over_font.render("Game Over", True, WHITE)
            final_score = self.font.render(f"Final Score: {self.score}", True, WHITE)
            prompt = self.game_over_prompt_font.render(
                "Press 1-3 or click a difficulty; 4 or Esc to exit", True, WHITE
            )
            screen.blit(title, title.get_rect(center=(self.width // 2, self.height // 2 - 110)))
            screen.blit(final_score, final_score.get_rect(center=(self.width // 2, self.height // 2 - 58)))
            for label, rect in self.game_over_options.items():
                button_color = RED if label == "Exit" else GREEN
                pygame.draw.rect(screen, button_color, rect, border_radius=4)
                option = self.game_over_prompt_font.render(label, True, WHITE)
                screen.blit(option, option.get_rect(center=rect.center))
            screen.blit(prompt, prompt.get_rect(center=(self.width // 2, self.height // 2 + 72)))
