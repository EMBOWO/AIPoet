import os
import random
import pygame
import textwrap

def get_all_poem_files():
    poem_dir = "poems"
    author_folders = [os.path.join(poem_dir, folder) for folder in ["Cummings", "Plath", "Shakespeare", "Hughes", "Dickinson"]]
    poem_files = []
    for author_folder in author_folders:
        for i in range(1, 7):
            poem_file = os.path.join(author_folder, f"pair{i}.txt")
            if os.path.exists(poem_file):
                poem_files.append(poem_file)
    return poem_files

def parse_poem_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='latin-1') as f:
            content = f.read()
    poems = content.split("\n\nBREAK\n\n")
    if len(poems) != 2:
        return None, None
    return poems[0], poems[1]

def display_poems_side_by_side(poem_left, poem_right, labels):
    pygame.init()
    WIDTH, HEIGHT = 1200, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Poetry Turing Test")

    BG_COLOR = (245, 245, 250)
    TEXT_COLOR = (30, 30, 30)
    BORDER_COLOR = (60, 60, 90)
    FONT = pygame.font.SysFont('times new roman', 22)
    INFO_FONT = pygame.font.SysFont('arial', 18)
    TITLE_FONT = pygame.font.SysFont('times new roman', 26, bold=True)

    def wrap_text(text):
        lines = []
        for line in text.split('\n'):
            lines.extend(textwrap.wrap(line, 40) or [''])
        return lines

    lines_left = wrap_text(poem_left)
    lines_right = wrap_text(poem_right)

    scroll_y = 0
    scroll_speed = 20
    line_height = 30
    padding = 40
    running = True
    voted = False
    result_text = ""

    max_lines = max(len(lines_left), len(lines_right))
    max_scroll = max(0, max_lines * line_height - (HEIGHT - 2 * padding))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    running = False
                elif event.key == pygame.K_DOWN:
                    scroll_y = min(max_scroll, scroll_y + scroll_speed)
                elif event.key == pygame.K_UP:
                    scroll_y = max(0, scroll_y - scroll_speed)
                elif event.key == pygame.K_1 and not voted:
                    voted = True
                    result_text = f"Left: {labels['left'].capitalize()} | Right: {labels['right'].capitalize()}"
                elif event.key == pygame.K_2 and not voted:
                    voted = True
                    result_text = f"Left: {labels['left'].capitalize()} | Right: {labels['right'].capitalize()}"
            elif event.type == pygame.MOUSEWHEEL:
                scroll_y = min(max_scroll, max(0, scroll_y - event.y * scroll_speed))

        screen.fill(BG_COLOR)
        pygame.draw.rect(screen, BORDER_COLOR, (20, 20, WIDTH - 40, HEIGHT - 40), 2)

        y_start = padding - scroll_y

        for i in range(max_lines):
            y_pos = y_start + i * line_height
            if padding <= y_pos <= HEIGHT - padding:
                if i < len(lines_left):
                    line_surface = FONT.render(lines_left[i], True, TEXT_COLOR)
                    screen.blit(line_surface, (50, y_pos))
                if i < len(lines_right):
                    line_surface = FONT.render(lines_right[i], True, TEXT_COLOR)
                    screen.blit(line_surface, (WIDTH // 2 + 50, y_pos))

        inst = "Vote: Press 1 for Left, 2 for Right. ESC to exit. Use UP/DOWN or scroll wheel to scroll."
        inst_surface = INFO_FONT.render(inst, True, TEXT_COLOR)
        screen.blit(inst_surface, (WIDTH // 2 - inst_surface.get_width() // 2, HEIGHT - 40))

        if voted:
            result_surface = TITLE_FONT.render(result_text, True, (120, 30, 30))
            screen.blit(result_surface, (WIDTH // 2 - result_surface.get_width() // 2, 10))

        pygame.display.flip()

    pygame.quit()

def main():
    files = get_all_poem_files()
    if not files:
        print("No poem files found.")
        return

    file_path = random.choice(files)
    human, ai = parse_poem_file(file_path)
    if not human or not ai:
        print("Invalid poem format.")
        return

    poems = [(human, 'human'), (ai, 'ai')]
    random.shuffle(poems)
    labels = {'left': poems[0][1], 'right': poems[1][1]}
    display_poems_side_by_side(poems[0][0], poems[1][0], labels)

if __name__ == "__main__":
    main()
