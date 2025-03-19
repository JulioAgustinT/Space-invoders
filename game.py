#importamos las librerias como siempre
import pygame
import random
import math

#iniciamos el pygame
pygame.init()

#configuramos el tamaño de la pantalla
screen_width = 1024
screen_height = 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Space Invoders")#nombre de la ventana

#los colores que voy a usar con sus codigos html
BLANCO = (255, 255, 255)
VERDE = (0, 255, 0)
ROJO = (255, 0, 0)
AZUL = (0, 0, 255)
NEGRO =(0,0,0)
#Fuentes que voy a usar (ninguna porque no quiero trabajar con archivos externos)
score_font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 36)
menu_font = pygame.font.Font(None, 36)

# Variables del jugador
player_width = 64 
player_height = 16
player_color = AZUL
player_X = screen_width // 2 - player_width // 2
player_Y = screen_height - player_height - 10
player_speed = 0.4  #a que velocidad me muevo hacia los costados

#variables de los aliens
invader_width = 30#ancho de los aliens
invader_height = 30#altura de los aliens
invader_color = VERDE
invader_X_change = 0.3#velocidad de los aliens para los costados
invader_Y_change = 30#que tanto bajan los aliens cuando tocan el borde
invader_direction = 1#para donde van los aliens al empezar el juego, (0 no se mueven, 1 a la derecha y -1 a la izquierda)

# con esta lista elijo la posición de donde empiezan los aliens para darle forma (me costo un huevo que lo tome bien)
aliens_presentes = [
    [False, False, True, False, False, False, False, False, True, False, False],
    [False, False, False, True, False, False, False, True, False, False, False],
    [False, False, True, True, True, True, True, True, True, False, False],
    [False, True, True, False, True, True, True, False, True, True, False],
    [True, True, True, True, True, True, True, True, True, True, True],
    [True, False, True, True, True, True, True, True, True, False, True],
    [True, False, True, False, False, False, False, False, True, False, True],
    [False, False, False, True, True, False, True, True, False, False, False]
]

#con esto elijo que espacio hay entre los aliens 
invader_gap = 5
invader_start_x = (screen_width - (len(aliens_presentes[0]) * (invader_width + invader_gap))) // 2
invader_start_y = 50

class Alien:
    def __init__(self, x, y):#iniciamos la posicion del alien
        self.x = x
        self.y = y

    def draw(self):#dibujamos el alien en la pantalla usando las coordenadas (x, y) y el color que elegimos
        pygame.draw.rect(screen, invader_color, (self.x, self.y, invader_width, invader_height))

#inicializamos los aliens como objetos
aliens = []
for row in range(len(aliens_presentes)):
    for col in range(len(aliens_presentes[row])):
        if aliens_presentes[row][col]:
            alien_x = invader_start_x + col * (invader_width + invader_gap)
            alien_y = invader_start_y + row * (invader_height + invader_gap)
            aliens.append(Alien(alien_x, alien_y))

#variables del proyectil disparado
bullet_width = 8 #ancho de la bala
bullet_height = 24#altura de la bala
bullet_color = ROJO#color de la bala
bullet_X = 0#desde que ancho empieza segun el jugador (esto hace que empiece desde el centro del personaje)
bullet_Y = screen_height - player_height - 10
bullet_X_change = 0#con esto hago que solo vaya para arriba
bullet_Y_change = 0.7  #con esto puedo modificar la velocidad de la bala
bullet_state = "ready"

#compruebo el estado del juego 
game_paused = False
game_over = False
victory = False
score_val = 0

#defino para mostrar el puntaje (se actualiza con cada alien muerto)
def show_score(x, y):
    score = score_font.render("Puntos: " + str(score_val), True, BLANCO)
    screen.blit(score, (x, y))

#defino para mostrar el mensaje de victoria
def victory_text(message):
    victory_surface = game_over_font.render(message, True, BLANCO)
    screen.blit(victory_surface, (100, 250))

#defino para poder mostrar el game over
def game_over_text(message):
    game_over_surface = game_over_font.render(message, True, BLANCO)
    screen.blit(game_over_surface, (100, 250))

#definimos el menú de pausa
def pause_menu():
    menu_text = menu_font.render("Juego pausado - Presiona Escape para reanudar, R para reiniciar, X para salir", True, BLANCO)
    screen.blit(menu_text, (screen_width // 2 - menu_text.get_width() // 2, screen_height // 2 - menu_text.get_height() // 2))

#definimos el menú principal
def main_menu():
    screen.fill(NEGRO)
    menu_text = menu_font.render("Bienvenido a Space Invaders", True, BLANCO)
    screen.blit(menu_text, (screen_width // 2 - menu_text.get_width() // 2, 100))
    start_text = menu_font.render("Presiona S para empezar", True, BLANCO)
    screen.blit(start_text, (screen_width // 2 - start_text.get_width() // 2, 300))
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s:
                    return True

#dibujamos al jugador
def draw_player(x, y):
    pygame.draw.rect(screen, player_color, (x, y, player_width, player_height))

#con esta función defino el disparo de la nave
def fire_bullet(x, y):
    global bullet_state
    bullet_state = "fire"
    pygame.draw.rect(screen, bullet_color, (x + player_width // 2 - bullet_width // 2, y - bullet_height, bullet_width, bullet_height))

#con esta funcion detecto colisiones
def isCollision(x1, x2, y1, y2):
    distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    if distance < 27:
        return True
    else:
        return False

#defino la opción de reiniciar el juego 
def restart_game():
    global player_X, player_Y, bullet_Y, bullet_state, game_over, victory, score_val, aliens, game_paused

    #reiniciamos las variables del juego 
    player_X = screen_width // 2 - player_width // 2
    player_Y = screen_height - player_height - 10
    bullet_Y = screen_height - player_height - 10
    bullet_state = "ready"#esto checkea que el disparo esté listo, no se como hacer para disparar sin que la bala haya desaparecido primero
    game_over = False
    victory = False
    score_val = 0
    game_paused = False  #este hace que el juego salga de la pausa cuando lo reiniciamos

    #reiniciamos los aliens si se reinicia el juego
    aliens.clear()
    for row in range(len(aliens_presentes)):
        for col in range(len(aliens_presentes[row])):
            if aliens_presentes[row][col]:
                alien_x = invader_start_x + col * (invader_width + invader_gap)
                alien_y = invader_start_y + row * (invader_height + invader_gap)
                aliens.append(Alien(alien_x, alien_y))

#menú principal
if main_menu():
    #este es el bucle del juego
    running = True
    while running:
        screen.fill(NEGRO)#pantalla en negro

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if game_paused:
                        game_paused = False
                    else:
                        game_paused = True
                elif event.key == pygame.K_x:
                    if game_paused:
                        running = False
                elif event.key == pygame.K_r:
                    if game_paused:
                        restart_game()

        if not game_paused and not game_over and not victory:#comprueba que el juego no este en pausa
            #definimos los controles de nuestra nave, flechas para movernos, espacio para disparar
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player_X -= player_speed
            if keys[pygame.K_RIGHT]:
                player_X += player_speed
            if keys[pygame.K_SPACE]:
                if bullet_state == "ready":
                    bullet_X = player_X
                    fire_bullet(bullet_X, bullet_Y)

            #evitamos que el personaje nuestro no se salga de los bordes con esto
            if player_X <= 0:
                player_X = 0
            elif player_X >= screen_width - player_width:
                player_X = screen_width - player_width

            #actualizamos la posicion de los aliens y verificamos si todos fueron eliminados
            all_invaders_eliminated = True  
            for alien in aliens[:]:  # uso [:] para copiar la lista y permitir la eliminación mientras seguimos iterando
                alien.x += invader_X_change * invader_direction

                #este if verifica que no nos hayan tocado los aliens, si nos tocan perdemos
                if alien.y + invader_height >= player_Y:
                    game_over = True
                    break

                #esto hace que cambie de dirección cuando chocan con el borde
                if alien.x <= 0 or alien.x >= screen_width - invader_width:
                    invader_direction *= -1
                    for a in aliens:
                        a.y += invader_Y_change

                #esto verifica si el alien hizo contacto con la bala (su ancho por eso el eje x)
                collision = isCollision(bullet_X, alien.x, bullet_Y, alien.y)
                if collision:
                    score_val += 1
                    bullet_state = "ready"
                    bullet_Y = screen_height - player_height - 10
                    aliens.remove(alien)

                alien.draw()

                #esto checkea si todos los aliens fueron eliminados
                if alien.y < screen_height:
                    all_invaders_eliminated = False

            #movimiento del proyectil
            if bullet_Y <= 0:
                bullet_Y = screen_height - player_height - 10
                bullet_state = "ready"

            if bullet_state == "fire":
                fire_bullet(bullet_X, bullet_Y)
                bullet_Y -= bullet_Y_change

            draw_player(player_X, player_Y)
            show_score(10, 10)

            #esto verifica que todos los aliens esten eliminados
            if all_invaders_eliminated:
                victory = True
        #si desaprobamos  (Perdemos)
        elif game_over:
            game_over_text("Perdiste.")
        #si aprobamos (ganamos)
        elif victory:
            victory_text("¡Felicidades!, presiona Esc para ver las opciones.")

        #esto muestra el menu cuando pausamos
        if game_paused:
            pause_menu()

        pygame.display.update()

    #limpiamos el juego al cerrar la aplicación
    pygame.quit()

#esto crea la ventana emergente cuando se cierra el juego
