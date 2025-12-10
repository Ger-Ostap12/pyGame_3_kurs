"""UI-состояния игры: ввод никнейма, меню, экран поражения."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from .config import FONT_NAME, FONT_SIZE
from .database import db

if TYPE_CHECKING:
    from .game import Game
    from .states import GameStateId


class NicknameState:
    """Состояние ввода никнейма (стартовый экран)."""
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.nickname = ""
        self.max_length = 15
        self.cursor_visible = True
        self.cursor_timer = 0.0
    
    @property
    def id(self):
        from .states import GameStateId
        return GameStateId.NICKNAME
    
    def enter(self) -> None:
        """При входе сбрасываем никнейм."""
        self.nickname = ""
        self.cursor_visible = True
        self.cursor_timer = 0.0
    
    def exit(self) -> None:
        pass
    
    def handle_event(self, event: pygame.event.Event) -> None:
        from .states import GameStateId
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                # Подтверждение никнейма
                if len(self.nickname) > 0:
                    db.set_current_player(self.nickname)
                    self.game.change_state(GameStateId.MENU)
            elif event.key == pygame.K_BACKSPACE:
                # Удаление символа
                self.nickname = self.nickname[:-1]
            elif event.key == pygame.K_ESCAPE:
                # Выход из игры
                self.game.stop()
            else:
                # Добавление символа
                if len(self.nickname) < self.max_length:
                    char = event.unicode
                    # Разрешаем только буквы, цифры и некоторые символы
                    if char.isalnum() or char in "_-":
                        self.nickname += char
    
    def update(self, dt: float) -> None:
        # Мигание курсора
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0.0
            self.cursor_visible = not self.cursor_visible
    
    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(self.game.bg_color)
        
        w, h = self.game.size
        
        # Заголовок
        title_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE * 2)
        title = title_font.render("ASTEROIDS", True, pygame.Color("yellow"))
        screen.blit(title, (w // 2 - title.get_width() // 2, h // 4))
        
        # Подзаголовок
        font = self.game.font
        subtitle = font.render("Enter your nickname:", True, self.game.text_color)
        screen.blit(subtitle, (w // 2 - subtitle.get_width() // 2, h // 2 - 50))
        
        # Поле ввода никнейма
        input_text = self.nickname
        if self.cursor_visible:
            input_text += "_"
        
        # Рамка для ввода
        input_width = 300
        input_height = 40
        input_x = w // 2 - input_width // 2
        input_y = h // 2
        
        pygame.draw.rect(screen, pygame.Color(50, 50, 50), 
                        (input_x, input_y, input_width, input_height))
        pygame.draw.rect(screen, self.game.text_color, 
                        (input_x, input_y, input_width, input_height), 2)
        
        # Текст никнейма
        nickname_surface = font.render(input_text, True, pygame.Color("green"))
        text_x = input_x + 10
        text_y = input_y + (input_height - nickname_surface.get_height()) // 2
        screen.blit(nickname_surface, (text_x, text_y))
        
        # Подсказки
        hint1 = font.render("Enter - confirm", True, pygame.Color("gray"))
        hint2 = font.render("Esc - exit", True, pygame.Color("gray"))
        screen.blit(hint1, (w // 2 - hint1.get_width() // 2, h // 2 + 80))
        screen.blit(hint2, (w // 2 - hint2.get_width() // 2, h // 2 + 110))
        
        # Таблица лидеров
        leaderboard = db.get_leaderboard(5)
        if leaderboard:
            lb_title = font.render("TOP 5:", True, pygame.Color("yellow"))
            screen.blit(lb_title, (w // 2 - lb_title.get_width() // 2, h // 2 + 160))
            
            for i, (name, score) in enumerate(leaderboard):
                lb_text = font.render(f"{i+1}. {name}: {score:,}", True, self.game.text_color)
                screen.blit(lb_text, (w // 2 - lb_text.get_width() // 2, h // 2 + 190 + i * 25))


class MenuState:
    """Состояние главного меню."""
    
    def __init__(self, game: Game) -> None:
        self.game = game
    
    @property
    def id(self):
        from .states import GameStateId
        return GameStateId.MENU
    
    def enter(self) -> None:
        pass
    
    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        from .states import GameStateId
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.game.change_state(GameStateId.PLAYING)
            elif event.key == pygame.K_ESCAPE:
                self.game.stop()

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(self.game.bg_color)
        
        w, h = self.game.size
        
        # Заголовок
        title_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE * 2)
        title = title_font.render("ASTEROIDS", True, pygame.Color("yellow"))
        screen.blit(title, (w // 2 - title.get_width() // 2, h // 4))
        
        font = self.game.font
        
        # Информация об игроке
        player_name = db.get_current_player() or "Unknown"
        best_score = db.get_best_score()
        
        player_text = font.render(f"Player: {player_name}", True, pygame.Color("cyan"))
        best_text = font.render(f"Best Score: {best_score:,}", True, pygame.Color("yellow"))
        
        screen.blit(player_text, (w // 2 - player_text.get_width() // 2, h // 2 - 30))
        screen.blit(best_text, (w // 2 - best_text.get_width() // 2, h // 2))
        
        # Подсказки
        hint1 = font.render("Enter - start game", True, self.game.text_color)
        hint2 = font.render("Esc - exit", True, self.game.text_color)
        
        screen.blit(hint1, (w // 2 - hint1.get_width() // 2, h // 2 + 60))
        screen.blit(hint2, (w // 2 - hint2.get_width() // 2, h // 2 + 90))


class GameOverState:
    """Состояние экрана поражения."""
    
    def __init__(self, game: Game) -> None:
        self.game = game
        self.is_new_record = False
        self.final_score = 0
        self.best_score = 0
    
    @property
    def id(self):
        from .states import GameStateId
        return GameStateId.GAME_OVER
    
    def enter(self) -> None:
        """При входе сохраняем результат в базу данных."""
        self.final_score = self.game.last_score
        self.is_new_record = db.save_score(self.final_score)
        self.best_score = db.get_best_score()
    
    def exit(self) -> None:
        pass

    def handle_event(self, event: pygame.event.Event) -> None:
        from .states import GameStateId
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.game.change_state(GameStateId.PLAYING)
            elif event.key == pygame.K_ESCAPE:
                self.game.change_state(GameStateId.MENU)

    def update(self, dt: float) -> None:
        pass

    def draw(self) -> None:
        screen = self.game.screen
        screen.fill(self.game.bg_color)

        font = self.game.font
        title_font = pygame.font.SysFont(FONT_NAME, FONT_SIZE * 2)
        
        w, h = self.game.size
        y_offset = h // 4

        # Заголовок
        title = title_font.render("GAME OVER", True, pygame.Color("red"))
        screen.blit(title, (w // 2 - title.get_width() // 2, y_offset))
        y_offset += 80
        
        # Никнейм игрока
        player_name = db.get_current_player() or "Unknown"
        player_text = font.render(f"Player: {player_name}", True, pygame.Color("cyan"))
        screen.blit(player_text, (w // 2 - player_text.get_width() // 2, y_offset))
        y_offset += 40
        
        # Финальный счёт
        score_text = font.render(f"Score: {self.final_score:,}", True, self.game.text_color)
        screen.blit(score_text, (w // 2 - score_text.get_width() // 2, y_offset))
        y_offset += 40
        
        # Лучший результат
        best_text = font.render(f"Best: {self.best_score:,}", True, pygame.Color("yellow"))
        screen.blit(best_text, (w // 2 - best_text.get_width() // 2, y_offset))
        y_offset += 40
        
        # Новый рекорд!
        if self.is_new_record:
            record_text = title_font.render("NEW RECORD!", True, pygame.Color("gold"))
            screen.blit(record_text, (w // 2 - record_text.get_width() // 2, y_offset))
            y_offset += 60
        else:
            y_offset += 30
        
        # Подсказки
        hint1 = font.render("R - restart", True, self.game.text_color)
        hint2 = font.render("Esc - menu", True, self.game.text_color)
        screen.blit(hint1, (w // 2 - hint1.get_width() // 2, y_offset))
        screen.blit(hint2, (w // 2 - hint2.get_width() // 2, y_offset + 30))

