import os
import random
import pygame
import textwrap
import argparse

def get_all_poem_files():
    poem_files = []
    poem_dir = "poems"
    author_folders = [os.path.join(poem_dir, folder) for folder in ["Cummings", "Plath", "Shakespeare", "Hughes", "Dickinson"]]
    for author_folder in author_folders:
        for i in range(1, 7):
            poem_file = os.path.join(author_folder, f"pair{i}.txt")
            if os.path.exists(poem_file):
                poem_files.append(poem_file)
    return poem_files

def get_read_poems():
    read_file = os.path.join("poems", "read.txt")
    if not os.path.exists(read_file):
        return set()
    with open(read_file, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    entries = set()
    for line in lines:
        try:
            author, pair_str, index_str = line.split(",")
            entries.add((author.strip(), int(pair_str), int(index_str)))
        except ValueError:
            print(f"Invalid entry in read.txt: {line}")
    return entries

def parse_poem_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None, None
    poems = content.split("\n\nBREAK\n\n")
    if len(poems) != 2:
        print(f"Warning: {file_path} does not have the expected format.")
        return None, None
    return poems[0], poems[1]

def select_random_unread_poem(ignore_read=False):
    poem_files = get_all_poem_files()
    read_entries = set() if ignore_read else get_read_poems()
    unread_poems = []
    
    for file_path in poem_files:
        author = os.path.basename(os.path.dirname(file_path))
        pair_name = os.path.splitext(os.path.basename(file_path))[0]  # e.g., "pair3"
        try:
            pair_number = int(pair_name.replace("pair", ""))
        except ValueError:
            continue
        
        human_poem, ai_poem = parse_poem_file(file_path)
        
        if human_poem and (ignore_read or (author, pair_number, 1) not in read_entries):
            unread_poems.append((human_poem, file_path, "human", author, pair_number, 1))
        if ai_poem and (ignore_read or (author, pair_number, 2) not in read_entries):
            unread_poems.append((ai_poem, file_path, "ai", author, pair_number, 2))

    if not unread_poems:
        return None, None, None, None, None, None
    return random.choice(unread_poems)

def add_to_read_file(author, pair_number, index):
    read_file = os.path.join("poems", "read.txt")
    with open(read_file, 'a', encoding='utf-8') as f:
        f.write(f"{author},{pair_number},{index}\n")

def display_poem_pygame(poem, source_file, poem_type):
    pygame.init()
    WIDTH, HEIGHT = 800, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Random Poem")

    BACKGROUND = (240, 240, 245)
    TEXT_COLOR = (40, 40, 40)
    TITLE_COLOR = (20, 20, 100)
    BORDER_COLOR = (80, 80, 100)
    SCROLLBAR_COLOR = (120, 120, 140)
    SCROLLBAR_BG = (200, 200, 210)
    AUTHOR_COLOR = (100, 20, 60)

    title_font = pygame.font.SysFont('times new roman', 36, bold=True)
    poem_font = pygame.font.SysFont('times new roman', 22)
    info_font = pygame.font.SysFont('arial', 16)
    author_font = pygame.font.SysFont('times new roman', 24, italic=True)

    try:
        title_line, poem_content = poem.split("\n\n", 1)
    except ValueError:
        title_line = "Untitled"
        poem_content = poem

    author_folder = os.path.basename(os.path.dirname(source_file))
    author_names = {
        "Shakespeare": "William Shakespeare",
        "Hughes": "Langston Hughes",
        "Plath": "Sylvia Plath",
        "Dickinson": "Emily Dickinson",
        "Cummings": "E. E. Cummings"
    }
    author = author_names.get(author_folder, author_folder)

    max_width = WIDTH - 120
    poem_lines = []
    for line in poem_content.split('\n'):
        if line.strip():
            wrapped_lines = textwrap.fill(line, width=60).split('\n')
            poem_lines.extend(wrapped_lines)
        else:
            poem_lines.append('')

    poem_area_top = 100
    poem_area_height = HEIGHT - poem_area_top - 50
    line_height = 30

    total_poem_height = len(poem_lines) * line_height
    scrolling_needed = total_poem_height > poem_area_height
    scroll_position = 0
    max_scroll = max(0, total_poem_height - poem_area_height)
    scroll_speed = 20

    scrollbar_width = 10
    scrollbar_track_height = poem_area_height

    key_s_held = key_h_held = key_o_held = show_author_info = False

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                    running = False
                elif event.key == pygame.K_DOWN and scrolling_needed:
                    scroll_position = min(max_scroll, scroll_position + scroll_speed)
                elif event.key == pygame.K_UP and scrolling_needed:
                    scroll_position = max(0, scroll_position - scroll_speed)
                elif event.key == pygame.K_PAGEDOWN and scrolling_needed:
                    scroll_position = min(max_scroll, scroll_position + poem_area_height)
                elif event.key == pygame.K_PAGEUP and scrolling_needed:
                    scroll_position = max(0, scroll_position - poem_area_height)
                elif event.key == pygame.K_HOME and scrolling_needed:
                    scroll_position = 0
                elif event.key == pygame.K_END and scrolling_needed:
                    scroll_position = max_scroll
                elif event.key == pygame.K_s:
                    key_s_held = True
                elif event.key == pygame.K_h:
                    key_h_held = True
                elif event.key == pygame.K_o:
                    key_o_held = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_s:
                    key_s_held = False
                elif event.key == pygame.K_h:
                    key_h_held = False
                elif event.key == pygame.K_o:
                    key_o_held = False
            elif event.type == pygame.MOUSEWHEEL and scrolling_needed:
                scroll_change = -event.y * scroll_speed
                scroll_position = max(0, min(max_scroll, scroll_position + scroll_change))

        show_author_info = key_s_held and key_h_held and key_o_held
        screen.fill(BACKGROUND)
        pygame.draw.rect(screen, BORDER_COLOR, (20, 20, WIDTH - 40, HEIGHT - 40), 2)

        title_surface = title_font.render(title_line, True, TITLE_COLOR)
        screen.blit(title_surface, (WIDTH // 2 - title_surface.get_width() // 2, 40))

        if show_author_info:
            author_text = f"by {author}" if poem_type == 'human' else f"by ChatGPT in the style of {author}"
            author_surface = author_font.render(author_text, True, AUTHOR_COLOR)
            poem_type_text = "Human-written poem" if poem_type == 'human' else "AI-generated poem"
            poem_type_surface = info_font.render(poem_type_text, True, AUTHOR_COLOR)
            screen.blit(author_surface, (WIDTH - author_surface.get_width() - 40, 30))
            screen.blit(poem_type_surface, (WIDTH - poem_type_surface.get_width() - 40, 60))

        poem_rect = pygame.Rect(30, poem_area_top, WIDTH - 60, poem_area_height)
        screen.set_clip(poem_rect)
        y_pos = poem_area_top - scroll_position
        for line in poem_lines:
            if y_pos + line_height >= poem_area_top and y_pos <= poem_area_top + poem_area_height:
                if line.strip():
                    line_surface = poem_font.render(line, True, TEXT_COLOR)
                    screen.blit(line_surface, (50, y_pos))
            y_pos += line_height
        screen.set_clip(None)

        if scrolling_needed:
            track_rect = pygame.Rect(WIDTH - 40, poem_area_top, scrollbar_width, scrollbar_track_height)
            pygame.draw.rect(screen, SCROLLBAR_BG, track_rect)
            if max_scroll > 0:
                thumb_height = max(30, scrollbar_track_height * poem_area_height / total_poem_height)
                thumb_pos = poem_area_top + (scroll_position / max_scroll) * (scrollbar_track_height - thumb_height)
                thumb_rect = pygame.Rect(WIDTH - 40, thumb_pos, scrollbar_width, thumb_height)
                pygame.draw.rect(screen, SCROLLBAR_COLOR, thumb_rect)

        instructions = "Use UP/DOWN arrows, mouse wheel, or HOME/END to scroll. Press ENTER or ESC to close." \
            if scrolling_needed else "Press ENTER or ESC to close"
        inst_surface = info_font.render(instructions, True, TEXT_COLOR)
        screen.blit(inst_surface, (WIDTH // 2 - inst_surface.get_width() // 2, HEIGHT - 40))

        pygame.display.flip()

    pygame.quit()
    return title_line

def main():
    parser = argparse.ArgumentParser(description="Display a random poem.")
    parser.add_argument('--ignore-read', action='store_true', help="Ignore read.txt and show any poem.")
    args = parser.parse_args()

    result = select_random_unread_poem(ignore_read=args.ignore_read)
    if not result or result[0] is None:
        print("All poems have been read! Reset the read.txt file to start over.")
        return

    poem, source_file, poem_type, author, pair_number, index = result
    title = display_poem_pygame(poem, source_file, poem_type)

    if not args.ignore_read:
        add_to_read_file(author, pair_number, index)
        print(f"\nThe poem '{title}' has been marked as read.")
    else:
        print(f"\nThe poem '{title}' was shown (ignoring read.txt).")

if __name__ == "__main__":
    main()
