import pygame
import sys

# Initialize pygame
pygame.init()

# Load your background image
BACKGROUND_PATH = "backgrounds/bg.png"  # Change to your image path
background = pygame.image.load(BACKGROUND_PATH)
SCREEN_WIDTH, SCREEN_HEIGHT = background.get_size()

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Platform Editor - Click and drag to create platforms")

# Platform storage
platforms = []
current_platform = None
drawing = False
start_pos = None

# Colors
PLATFORM_COLOR = (0, 255, 0, 100)  # Green transparent
BORDER_COLOR = (255, 255, 0)  # Yellow border

font = pygame.font.Font(None, 24)
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse button down - start drawing
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                drawing = True
                start_pos = event.pos

        # Mouse button up - finish platform
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and drawing:
                end_pos = event.pos
                x = min(start_pos[0], end_pos[0])
                y = min(start_pos[1], end_pos[1])
                w = abs(end_pos[0] - start_pos[0])
                h = abs(end_pos[1] - start_pos[1])

                if w > 10 and h > 10:  # Minimum size
                    platforms.append(pygame.Rect(x, y, w, h))

                drawing = False
                start_pos = None

        # Keyboard shortcuts
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z and platforms:  # Z = undo
                platforms.pop()
            elif event.key == pygame.K_c:  # C = clear all
                platforms.clear()
            elif event.key == pygame.K_s:  # S = save
                print("\n# Add this to settings.py:")
                print("PLATFORMS = [")
                for p in platforms:
                    print(f"    pygame.Rect({p.x}, {p.y}, {p.width}, {p.height}),")
                print("]\n")

    # Drawing
    screen.blit(background, (0, 0))

    # Draw existing platforms
    for platform in platforms:
        s = pygame.Surface((platform.width, platform.height), pygame.SRCALPHA)
        s.fill(PLATFORM_COLOR)
        screen.blit(s, platform.topleft)
        pygame.draw.rect(screen, BORDER_COLOR, platform, 2)

    # Draw current platform being created
    if drawing and start_pos:
        mouse_pos = pygame.mouse.get_pos()
        x = min(start_pos[0], mouse_pos[0])
        y = min(start_pos[1], mouse_pos[1])
        w = abs(mouse_pos[0] - start_pos[0])
        h = abs(mouse_pos[1] - start_pos[1])
        temp_rect = pygame.Rect(x, y, w, h)
        s = pygame.Surface((w, h), pygame.SRCALPHA)
        s.fill(PLATFORM_COLOR)
        screen.blit(s, (x, y))
        pygame.draw.rect(screen, BORDER_COLOR, temp_rect, 2)

    # Instructions
    instructions = [
        "Click and drag to create platforms",
        f"Platforms: {len(platforms)}",
        "Z = Undo | C = Clear | S = Save to console",
        "Close window when done"
    ]

    y_offset = 10
    for text in instructions:
        surf = font.render(text, True, (255, 255, 0))
        bg = pygame.Surface((surf.get_width() + 10, surf.get_height() + 4))
        bg.fill((0, 0, 0))
        screen.blit(bg, (5, y_offset))
        screen.blit(surf, (10, y_offset + 2))
        y_offset += 25

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
