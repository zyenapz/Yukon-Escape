# Import libraries =============================================================
try:
    import pygame, os, math, random
    from itertools import repeat
    from data.scripts.sprites import Player, Obstacle, Fracture, Debris, Particle, Shadow, Bouncy
    from data.scripts.constants import *
    from data.scripts.draw import draw_background, draw_text, draw_shadows, draw_bouncies, draw_particles, shake
    from data.scripts.highscores import write_highscores, read_highscores, sort
    from data.scripts.spawners import spawn_obstacle, spawn_fracture, spawn_debris, spawn_bouncies, spawn_shadow, spawn_particles
except ImportError as e:
    print(e)
    exit()

# Initialize pygame ============================================================
pygame.init()
pygame.mouse.set_visible(False) # Hide the mouse

# Directories =================================================================
GAME_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(GAME_DIR, "data")
IMG_DIR = os.path.join(DATA_DIR, "img")
SFX_DIR = os.path.join(DATA_DIR, "sfx")
SCRIPTS_DIR = os.path.join(DATA_DIR, "scripts")
FONT_DIR = os.path.join(DATA_DIR, "font")
scores_path = os.path.join(SCRIPTS_DIR, "scores.dat")

# Fonts =======================================================================

GAME_FONT = os.path.join(FONT_DIR, "prstartk.ttf")

# Initialize the window ========================================================

os.environ['SDL_VIDEO_CENTERED'] = '1'
window = pygame.display.set_mode((WIN_RES["W"], WIN_RES["H"]))
window_rect = window.get_rect()
pygame.display.set_caption(TITLE)

# Images =======================================================================

def load_png(file, directory, scale, convert_alpha=False):
    try:
        path = os.path.join(directory, file)
        if not convert_alpha:
            img = pygame.image.load(path).convert_alpha()
        else:
            img = pygame.image.load(path).convert()
            transColor = img.get_at((0,0))
            img.set_colorkey(transColor)
        img_w = img.get_width()
        img_h = img.get_height()
        img = pygame.transform.scale(img, (img_w*scale, img_h*scale))
        return img
    except Exception as e:
        print(e)
        exit()

window_icon = load_png("logo.png", IMG_DIR, 1)
pygame.display.set_icon(window_icon)

# Player image
player_img = load_png("player.png", IMG_DIR, 4)

# Obstacle images
obstacle_imgs = [load_png("obstacle1.png", IMG_DIR, 6),
                 load_png("obstacle2.png", IMG_DIR, 6),
                 load_png("obstacle3.png", IMG_DIR, 6),
                 load_png("obstacle4.png", IMG_DIR, 6),
                 load_png("obstacle5.png", IMG_DIR, 6),
                 load_png("obstacle6.png", IMG_DIR, 6),
                 load_png("obstacle7.png", IMG_DIR, 6),
                 load_png("obstacle8.png", IMG_DIR, 6)]

# Fracture images
fracture_imgs = dict()
afracture_imgs = [load_png("afracture1.png", IMG_DIR, 6),
                  load_png("afracture2.png", IMG_DIR, 6),
                  load_png("afracture3.png", IMG_DIR, 6),
                  load_png("afracture4.png", IMG_DIR, 6),
                  load_png("afracture5.png", IMG_DIR, 6),
                  load_png("afracture6.png", IMG_DIR, 6),
                  load_png("afracture7.png", IMG_DIR, 6),
                  load_png("afracture8.png", IMG_DIR, 6)]
fracture_imgs["a"] = afracture_imgs

bfracture_imgs = [load_png("bfracture1.png", IMG_DIR, 6),
                  load_png("bfracture2.png", IMG_DIR, 6),
                  load_png("bfracture3.png", IMG_DIR, 6),
                  load_png("bfracture4.png", IMG_DIR, 6),
                  load_png("bfracture5.png", IMG_DIR, 6),
                  load_png("bfracture6.png", IMG_DIR, 6),
                  load_png("bfracture7.png", IMG_DIR, 6),
                  load_png("bfracture8.png", IMG_DIR, 6)]
fracture_imgs["b"] = bfracture_imgs

# Debris images
debris_imgs = dict()
debris_normal_imgs = [load_png("debris1.png", IMG_DIR, 8),
                      load_png("debris2.png", IMG_DIR, 8)]
debris_imgs["normal"] = debris_normal_imgs

debris_impacted_imgs = [load_png("debris1_impacted.png", IMG_DIR, 8),
                        load_png("debris2_impacted.png", IMG_DIR, 8)] 
debris_imgs["impacted"] = debris_impacted_imgs                  

# Other images
logo_img = load_png("logo.png", IMG_DIR, 8, convert_alpha=True)
dev_logo_img = load_png("dev_logo.png", IMG_DIR, 6, convert_alpha=True)

background_img = load_png("background.png", IMG_DIR, 4)
background_rect = background_img.get_rect()

parallax_img = load_png("parallax.png", IMG_DIR, 4)
parallax_rect = parallax_img.get_rect()

alert_forest_img = load_png("alert_forest.png", IMG_DIR, 6)
alert_tectonics_img = load_png("alert_tectonics.png", IMG_DIR, 6)
alert_debris_img = load_png("alert_debris.png", IMG_DIR, 6)
alert_rect = alert_forest_img.get_rect()
alert_rect.centerx = WIN_RES["W"] / 2
alert_rect.y = WIN_RES["H"] * 0.1

# Sounds =======================================================================

def load_sound(filename, sfx_dir, volume):
    path = os.path.join(sfx_dir, filename)
    snd = pygame.mixer.Sound(path)
    snd.set_volume(volume)
    return snd
    
explosions_sfx = [ load_sound("explosion1.wav", SFX_DIR, 0.3),
                   load_sound("explosion2.wav", SFX_DIR, 0.3),
                   load_sound("explosion3.wav", SFX_DIR, 0.3) ]

award_sfx = load_sound("award.wav", SFX_DIR, 0.3)
alarm_sfx = load_sound("alarm.wav", SFX_DIR, 0.3)

pygame.mixer.music.load(os.path.join(SFX_DIR, "Joshua McLean - Mountain Trials.ogg"))
pygame.mixer.music.set_volume(0.10)

# Application loop ====================================================================

def roll_spawn(list_of_enemies, probability):
    roll = None
    
    # Generate choices and get roll
    choices = random.choices(list_of_enemies, probability, k=10)
    roll = random.choice(choices)

    # Run spawner functions
    if roll == "obstacle":
        spawn_obstacle(obstacle_imgs, enemies, obstacles, sprites)
    elif roll == "debris":
        spawn_debris(window, debris_imgs, debris_group, enemies, shadows, sprites)
    elif roll == "fracture":
        spawn_fracture(fracture_imgs, fracture_group, enemies, sprites)

def run_game():
    # Game variables
    hi_scores = sort(read_highscores(scores_path))
    clock = pygame.time.Clock()
    offset = repeat((0, 0)) # For screen shake
    near_misses = list()
    warmup_duration = 3000
    THREATS_WAIT = 20000
    threats_delay = THREATS_WAIT

    # Loop variables
    running = True
    in_titlescreen = True
    in_menu = False
    in_game = False
    in_gameover = False
    played_once = False

    while running:

        # Reset / initialize the score, and others
        hs_saved = False
        score = 0

        fade_timer = pygame.time.get_ticks()
        ts_timer = pygame.time.get_ticks() # Title screen timer
        threats_prompt_timer = pygame.time.get_ticks()
        threats_timer = pygame.time.get_ticks()
        warmup_timer = pygame.time.get_ticks()
        disable_keys_timer = pygame.time.get_ticks()
        threat = "none"
        
        background_y = 0 # For the background's y coordinate
        parallax_x = 0 # For the parallax's x coordinate

        player_group.empty()
        enemies.empty()
        obstacles.empty()
        debris_group.empty()
        impdebris_group.empty()
        fracture_group.empty()
        particles[:] = []
        particles_coins[:] = []
        near_misses[:] = []
        shadows[:] = []

        dev_logo_alpha = 256
        logo_alpha = 0
        has_faded = False # for menu
        
        # Initialize the player
        player = Player(player_img)
        sprites.add(player)
        player_group.add(player)

        # Spawn bouncies for title screen
        spawn_bouncies(window, bouncies)

        while in_titlescreen:

            # Lock the FPS
            clock.tick(FPS)

            # Get input ============================================================
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    in_titlescreen = False
            
            # Draw processes =======================================================
            
            now = pygame.time.get_ticks()
            if now - ts_timer > 3000:
                now = pygame.time.get_ticks()
                if now - fade_timer > 1000:
                    dev_logo_alpha -= 5
                    dev_logo_img.set_alpha(dev_logo_alpha)
                    window.fill(SNOW_WHITE)
                    draw_bouncies(bouncies)
                    window.blit(dev_logo_img, ( (WIN_RES["W"] / 2) - (dev_logo_img.get_width() / 2) * 2.8, WIN_RES["H"] * 0.3) )
                    pygame.display.flip()

                if dev_logo_alpha < 0: # If image has almost faded out
                    # Play the soundtrack
                    pygame.mixer.music.play(loops=-1)
                    pygame.mixer.Channel(0).play(pygame.mixer.Sound(os.path.join(SFX_DIR, "ambience.wav")), -1)
                    in_titlescreen = False
                    in_menu = True
            else:
                window.fill(SNOW_WHITE)
                draw_bouncies(bouncies)
                window.blit(dev_logo_img, ( (WIN_RES["W"] / 2) - (dev_logo_img.get_width() / 2) * 2.8, WIN_RES["H"] * 0.3) )
                draw_text(window, "a game by", 32, GAME_FONT, WIN_RES["W"] / 2.3, WIN_RES["H"] * 0.4, BLACK)
                draw_text(window, "zyenapz", 32, GAME_FONT, WIN_RES["W"] / 2.3, WIN_RES["H"] * 0.45, BLACK)
                draw_text(window, "(c) 2020 zyenapz. All rights reserved.", 14, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.97, BLACK, "centered")
                    
            # Update the window
            pygame.display.flip()
            
        while in_menu:
            
            # Increment the background's and parallax's y positions
            background_y += SPRITE_MOVESPEED
            parallax_x += PARALLAX_MOVESPEED

            # Lock the FPS
            clock.tick(FPS)

            # Get input ============================================================
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    in_menu = False
                elif event.type == pygame.KEYDOWN and has_faded:
                    if event.key == pygame.K_a:
                        in_menu = False
                        in_game = True
                        played_once = True
                        threats_timer = pygame.time.get_ticks()
                        warmup_timer = pygame.time.get_ticks()
                    elif event.key == pygame.K_d:
                        in_menu = False 
                        running = False
            # Update processes =====================================================
            if not played_once:
                if logo_alpha < 255:
                    logo_alpha += 3
                    logo_img.set_alpha(logo_alpha)
            else:
                logo_alpha = 255
                
            if logo_alpha >= 255:
                has_faded = True
            
            # Draw processes =======================================================
            draw_background(window, background_img, background_rect, background_y)
            draw_background(window, parallax_img, parallax_rect, parallax_x, "horizontal")
            window.blit(logo_img, ( (WIN_RES["W"]/2) - (logo_img.get_width() / 2), WIN_RES["H"] * -0.1))
            
            if has_faded:
                draw_text(window, "[A] Play", 32, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.6, BLACK, "centered")
                draw_text(window, "[D] Exit", 32, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.65, BLACK, "centered")
                if hi_scores == []:
                    draw_text(window, "HS 0", 32, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.72, BLACK, "centered")
                else:
                    draw_text(window, f"HS {hi_scores[0]}", 32, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.72, BLACK, "centered")
                draw_text(window, "powered by pygame.", 14, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.93, GRAY, "centered")
                draw_text(window, "Music from Joshua McLean.", 14, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.95, GRAY, "centered")
                draw_text(window, "(c) 2020 zyenapz. All rights reserved.", 14, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.97, GRAY, "centered")

            # Update the window
            pygame.display.flip()

        while in_game:
            
            # Increment the background's and parallax's y positions
            background_y += SPRITE_MOVESPEED
            parallax_x += PARALLAX_MOVESPEED

            # Lock the FPS
            clock.tick(FPS)

            # Get input ============================================================
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    in_game = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_a:
                        if player.spdx <= -4:
                            player.spdx = -6
                        else:
                            player.spdx = -4
                    elif event.key == pygame.K_d:
                        if player.spdx >= 4:
                            player.spdx = 6
                        else:
                            player.spdx = 4

            # Update processes =====================================================

            # Player entry animation
            if not player.spawned:
                player.rect.y -= 3
                if player.rect.bottom <= player.spawn_y:
                    player.spawned = True

            # Check collision between player and enemies
            hits = pygame.sprite.groupcollide(enemies, player_group, False, False, pygame.sprite.collide_circle)
            for hit in hits:
                if type(hit) == Debris:
                    if hit.impacted:
                        player.has_collided = True
                elif type(hit) == Fracture:
                    if hit.fractured:
                        player.has_collided = True
                else:
                    player.has_collided = True

            # Check collision between impacted debris and obstacles
            hits = pygame.sprite.groupcollide(obstacles, impdebris_group, False, False)
            for hit in hits:
                spawn_particles(window, hit.rect.centerx, hit.rect.top, random.randrange(30,40), hit.palette, "explosion", GAME_FONT)
                hit.kill()
            
            # Check for near misses and append to near_misses list
            hits = pygame.sprite.groupcollide(enemies, player_group, False, False)
            for hit in hits:
                if hit not in near_misses:

                    is_collidable = False # Just some bool to check if fractures and debris are in their collidable state

                    if type(hit) == Fracture:
                        if hit.fractured:
                            is_collidable = True
                    elif type(hit) == Debris:
                        if hit.impacted:
                            is_collidable = True
                    elif type(hit) == Obstacle:
                        is_collidable = True
                        
                    distance = hit.radius * 1.5
                    proximity_x = abs(hit.rect.centerx - player.rect.centerx)

                    if is_collidable and proximity_x < distance:
                        near_misses.append(hit)
            
            # Award player for near misses
            for hit in near_misses:
                if not pygame.sprite.collide_rect(hit, player):
                    score += 8
                    spawn_particles(window, hit.rect.centerx, hit.rect.top, 1, [(240,181,65), (255,238,131)], "coins", GAME_FONT)
                    award_sfx.play()
                    near_misses.remove(hit)
                        
            # End the game if player has collided
            if player.has_collided:
                offset = shake(30,5)
                in_game = False
                in_gameover = True
                spawn_particles(window, player.rect.centerx, player.rect.top, random.randrange(30,40), [(125,149,162)], "explosion", GAME_FONT)
                player.spdy = SPRITE_MOVESPEED
                disable_keys_timer = pygame.time.get_ticks()
                random.choice(explosions_sfx).play()

            now = pygame.time.get_ticks()
            if now - warmup_timer > warmup_duration:

                # Roll for threats
                now = pygame.time.get_ticks()
                if now - threats_timer > threats_delay:
                    threats_timer = now
                    if threat != "none":
                        threat = "none"
                        threats_delay = THREATS_WAIT
                    else:
                        threats_roll = random.choices(["tectonics", "forest", "debris"], [3,4,2], k=10)
                        threat = random.choice(threats_roll)
                        threats_delay = 8000
                        alarm_sfx.play()

                # Add score
                score += 0.05
                    
                # Calculate enemy count
                enemy_count = (score**2) / (6**4)

                if enemy_count > 12:
                    enemy_count = 12

                # Spawn enemies
                if threat == "none":
                    if len(enemies) < enemy_count:
                        if score < 100:
                            roll_spawn(["obstacle", "debris", "fracture"], spawn_odds["normal"])
                        else:
                            roll_spawn(["obstacle", "debris", "fracture"], spawn_odds["hard"])
                else:
                    if len(enemies) < MAX_THREAT_ENEMIES[threat]:
                        roll_spawn(["obstacle", "debris", "fracture"], spawn_odds[threat])

            # Produce particle explosion and sound if debris impacted
            for d in debris_group:
                if d.impacted and not d.shaked:
                    offset = shake(15, 5)
                    d.shaked = True
                    debris_group.remove(d)
                    impdebris_group.add(d)
                    enemies.add(d)
                    spawn_particles(window, d.rect.centerx, d.rect.centery, random.randrange(20,30), [(125,149,162)], "explosion", GAME_FONT)
                    random.choice(explosions_sfx).play()

            # Produce shaking and sound if fracture has opened up
            for f in fracture_group:
                if f.fractured:
                    offset = shake(20,5)
                    fracture_group.remove(f)
                    opfracture_group.add(f)
                    enemies.add(f)
                    random.choice(explosions_sfx).play()
                    
            # Spawn trail for player
            spawn_particles(window, player.rect.centerx, player.rect.bottom, 5, [(163,167,194)], "trail", GAME_FONT)

            # Update sprites group
            sprites.update()

            # Draw processes =======================================================

            # Draw the background
            draw_background(window, background_img, background_rect, background_y)

            # Draw the sprites and particles
            fracture_group.draw(window)
            obstacles.draw(window)
            opfracture_group.draw(window)
            draw_shadows(shadows)
            impdebris_group.draw(window)
            draw_particles(particles)
            draw_particles(particles_coins)
            player_group.draw(window)
            debris_group.draw(window)

            # Draw the parallax
            draw_background(window, parallax_img, parallax_rect, parallax_x, "horizontal")

            # Draw the score
            draw_text(window, f"Score", 24, GAME_FONT, 10, 10, BLACK)
            draw_text(window, f"{math.trunc(score)}", 24, GAME_FONT, 10, 50, BLACK)

            # Draw the 'Get Ready Text'
            now = pygame.time.get_ticks()
            if now - warmup_timer < warmup_duration * 0.8:
                draw_text(window, f"Get Ready!", 48, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.4, BLACK, "centered")
            
            # Draw the threats prompt
            if threat != "none":
                if threat == "tectonics":
                    window.blit(alert_tectonics_img, (alert_rect.centerx-48, alert_rect.y - 16))
                elif threat == "debris":
                    window.blit(alert_debris_img, (alert_rect.centerx-48, alert_rect.y - 16))
                elif threat == "forest":
                    window.blit(alert_forest_img, (alert_rect.centerx-48, alert_rect.y - 16))

            window.blit(window, next(offset)) # Screen shake

            # Update the window
            pygame.display.flip()

        while in_gameover:
            
            # Save the high score
            if not hs_saved:
                hi_scores.append(math.trunc(score))
                hi_scores = sort(hi_scores)
                write_highscores(hi_scores, scores_path)
                hs_saved = True

            # Increment the background's and parallax's y positions
            background_y += SPRITE_MOVESPEED
            parallax_x += PARALLAX_MOVESPEED

            # Lock the FPS
            clock.tick(FPS)

            keys_enabled = False
            now = pygame.time.get_ticks()
            if now - disable_keys_timer > 2000:
                keys_enabled = True

            # Get input ============================================================
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    in_gameover = False
                elif event.type == pygame.KEYDOWN and keys_enabled:
                    if event.key == pygame.K_a:
                        in_gameover = False
                        in_menu = True
                    elif event.key == pygame.K_d:
                        in_gameover = False
                        in_game = True

            # Update processes =====================================================

            # Spawn enemies
            enemy_count = (score**2) / (8**4)
            if enemy_count > 10:
                enemy_count = 10
            if len(enemies) < enemy_count:
                roll_spawn(["obstacle", "debris", "fracture"],[10,0,0])

            # Update sprites group
            sprites.update()

            # Draw processes =======================================================

            # Draw the background
            draw_background(window, background_img, background_rect, background_y)

            # Update and draw the particles
            draw_particles(particles)
            draw_particles(particles_coins)

            # Draw the sprites
            fracture_group.draw(window)
            obstacles.draw(window)
            impdebris_group.draw(window)
            opfracture_group.draw(window)
            player_group.draw(window)
            debris_group.draw(window)

            # Draw the parallax
            draw_background(window, parallax_img, parallax_rect, parallax_x, "horizontal")

            # Draw texts
            draw_text(window, f"Score", 24, GAME_FONT, 10, 10, BLACK)
            draw_text(window, f"{math.trunc(score)}", 24, GAME_FONT, 10, 50, BLACK)
            draw_text(window, f"GAME OVER!", 48, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.3, BLACK, "centered")
            draw_text(window, f"Your score", 24, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.4, BLACK, "centered")
            draw_text(window, f"{math.trunc(score)}", 28, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.45, BLACK, "centered")
            if score > hi_scores[0]:
                draw_text(window, "New Hi-Score!", 28, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.50, BLACK, "centered")
            now = pygame.time.get_ticks()
            if keys_enabled:
                draw_text(window, f"[A] Menu", 28, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.55, BLACK, "centered")
                draw_text(window, f" [D] Retry", 28, GAME_FONT, WIN_RES["W"] / 2, WIN_RES["H"] * 0.6, BLACK, "centered")
            window.blit(window, next(offset))

            # Update the window
            pygame.display.flip()

if __name__ == "__main__":
    # Start the game
    run_game()

    # Quit pygame
    pygame.quit()
