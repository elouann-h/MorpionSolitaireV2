# Importation des modules nécessaires
import pygame
from pygame.locals import *
import math
import random
import sqlite3
pygame.init()

PATH = "C:\\Users\\eloua\\OneDrive\\Bureau\\Python\\MorpionSolitaireV2\\"

# Constantes
# - Carrés: les petits carrés formés par la grille
SQUARES_LENGTH = 36 # Le nombre de carrés par ligne, et également par colonne (doit être impair)
SQUARE_SIZE = 25 # La taille d'un carré en pixels
SCREEN_SIZE = SQUARES_LENGTH * SQUARE_SIZE # La taille de l'écran est un carré: la taille des carrés fois le nombre de carrés par ligne/colonne

GRID_COLOR = (90, 70, 90) # Couleur de la grille: gris clair
GRID_WIDTH = 1 # Largeur des traits de la grille en pixels
BACKGROUND_COLOR = (20, 10, 20) # Couleur de fond: blanc

BEGINNING_DOTS_COLOR = (220, 80, 80) # Couleur du point de départ: rose
DOT_COLOR = (80, 80, 220) # Couleur des points: bleu
DOT_WIDTH = SQUARE_SIZE // 5 # La largeur d'un point en pixels

SEGMENT_COLOR = (150, 150, 150) # Couleur des segments: noir
SEGMENT_WIDTH = max(0, SQUARE_SIZE // 15) # La largeur d'un segment en pixels

# Variables importantes
dots_placed = [] # Liste des points placés, de la forme [(x1, y1), (x2, y2), ...]
segments = [] # Liste des segments placés, de la forme ( "direction", [(x1, y1), (x2, y2), ...] )

## --------------- Fonctions utiles --------------- ##
def draw_beginning_dots(screen=None):
    """
    Dessine les points de départ
    """
    # On place manuellement les points du cadre de départ
    left_extremity = SQUARES_LENGTH // 2 - 4
    beginning_dots = [
        # Lignes horizontales
        (3, 0), (4, 0), (5, 0), (6, 0), # Top
        (0, 3), (1, 3), (2, 3), (3, 3), # Top gauche
        (6, 3), (7, 3), (8, 3), (9, 3), # Top droit
        (0, 6), (1, 6), (2, 6), (3, 6), # Bottom gauche
        (6, 6), (7, 6), (8, 6), (9, 6), # Bottom droit
        (3, 9), (4, 9), (5, 9), (6, 9), # Bottom
        # Lignes verticales
        (0, 4), (0, 5), # Gauche
        (3, 1), (3, 2), # Top gauche
        (3, 7), (3, 8), # Bottom gauche
        (6, 1), (6, 2), # Top droite
        (6, 7), (6, 8), # Bottom droite
        (9, 4), (9, 5), # Droite
    ]
    # Toutes les lignes verticales
    for dot in beginning_dots:
        # Les coordonnées sont calculées en fonction de la taille des carrés et du nombre de carrés par ligne/colonne
        # On ajoute les coordonnées du point à la liste des points placés
        x, y = left_extremity + dot[0], left_extremity + dot[1]
        # On dessine le point et on l'ajoute à la liste des points placés
        dots_placed.append((x, y))
        if screen:
            pygame.draw.circle(screen, BEGINNING_DOTS_COLOR, (x * SQUARE_SIZE, y * SQUARE_SIZE), DOT_WIDTH)

def draw_screen(screen):
    """
    Dessine l'écran
    """
    screen.fill(BACKGROUND_COLOR) # Couleur de fond: blanc

    # Dessin de la grille
    for i in range(1, SQUARES_LENGTH):
        for j in range(1, SQUARES_LENGTH):
            # Dessin des lignes verticales et horizontales
            # Les coordonnées sont calculées en fonction de la taille des carrés et du nombre de carrés par ligne/colonne
            x, y = i * SQUARE_SIZE, j * SQUARE_SIZE
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_SIZE), GRID_WIDTH)
            pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_SIZE, y), GRID_WIDTH)

    for seg in segments:
        draw_line(seg[1][0], seg[1][4], seg[0], screen)
    
    for dot in dots_placed:
        draw_dot(dot, screen)

    draw_beginning_dots(screen)

    pygame.display.flip()


def segment_already_placed(segment):
    """
    Renvoie True si le segment est déjà placé, False sinon
    """
    for seg in segments:
        if segment[0] == seg[0]:
            for p in seg[1]:
                if p in segment[1]:
                    return True
    return False


def closest_intersect(event):
    """
    Renvoie les coordonnées de l'intersection de la grille la plus proche de la souris
    """
    # On récupère les coordonnées de la souris
    x, y = event.pos
    # On calcule les coordonnées de l'intersection de la grille la plus proche
    four_intersects = [
        (x // SQUARE_SIZE, y // SQUARE_SIZE),
        (x // SQUARE_SIZE + 1, y // SQUARE_SIZE),
        (x // SQUARE_SIZE, y // SQUARE_SIZE + 1),
        (x // SQUARE_SIZE + 1, y // SQUARE_SIZE + 1),
    ]
    # On calcule la distance entre la souris et chaque intersection
    distances = []
    for intersect in four_intersects:
        distances.append((intersect[0] * SQUARE_SIZE - x) ** 2 + (intersect[1] * SQUARE_SIZE - y) ** 2)

    # On récupère l'intersection la plus proche
    closest_intersect = four_intersects[distances.index(min(distances))]
    return closest_intersect


def valid_segment(p1, p2):
    """
    Renvoie si le segment formé par les deux extrémités est valide
    """
    # Si ils sont alignés verticalement (même x) et qu'il y a une distance de 4 entre eux
    if p1[0] == p2[0] and abs(p1[1] - p2[1]) == 4:
        return True
    # Si ils sont alignés horizontalement (même y) et qu'il y a une distance de 4 entre eux
    elif p1[1] == p2[1] and abs(p1[0] - p2[0]) == 4:
        return True
    # Si ils sont bien sur une abscisse et une ordonnée différentes
    elif p1[0] != p2[0] and p1[1] != p2[1]:
        # On regarde le coefficient directeur formé par les deux extrémités, si il vaut 1 ou -1, alors ils sont alignés en diagonale de 45°
        if abs((p2[1] - p1[1]) / (p2[0] - p1[0])) == 1:
            # On vérifie que la distance entre les deux points est bien de 4*sqrt(2) (car la diagonale d'un carré vaut sqrt(2))
            if math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) == 4*math.sqrt(2):
                return True
    # Si aucune des conditions n'est vérifiée, alors le segment n'est pas valide
    return False


def can_be_drawn(p1, p2):
    """
    Renvoie si le segment peut être dessiné, c'est-à-dire si il manque un seul point parmi l'alignement de 5 points
    Si il peut être aligné, alors un tuple est renvoyé de la forme: (point_manquant, liste_des_points_alignés, direction)
    Sinon, False est renvoyé
    """
    # Point manquant
    missing_dot = "None"
    # Liste des points alignés
    full_list = []
    # Direction du segment
    direction = None
    # Si les deux points sont alignés verticalement
    if p1[0] == p2[0]:
        direction = "vertical"
        # On prend tous les points de l'ordonnée la plus petite à l'ordonnée la plus grande (extrémités du segment)
        for i in range(min(p1[1], p2[1]), max(p1[1], p2[1]) + 1):
            if (p1[0], i) not in dots_placed:
                if missing_dot == "None":
                    missing_dot = (p1[0], i)
                else:
                    # Si il y a plus d'un point manquant, alors le segment ne peut pas être dessiné
                    return False
            # On ajoute le point à la liste des points alignés
            full_list.append((p1[0], i))
    # Si les deux points sont alignés horizontalement
    elif p1[1] == p2[1]:
        direction = "horizontal"
        # On prend tous les points de l'abscisse la plus petite à l'abscisse la plus grande (extrémités du segment)
        for i in range(min(p1[0], p2[0]), max(p1[0], p2[0]) + 1):
            if (i, p1[1]) not in dots_placed:
                if missing_dot == "None":
                    missing_dot = (i, p1[1])
                else:
                    # Si il y a plus d'un point manquant, alors le segment ne peut pas être dessiné
                    return False
            # On ajoute le point à la liste des points alignés
            full_list.append((i, p1[1]))
    # Si ils forment une diagonale, on appelle alors une fonction externe qui renvoie la même chose que cette fonction
    elif p1[0] != p2[0] and p1[1] != p2[1]:
        diag = points_on_diagonal(p1, p2)
        return diag
    return (missing_dot, full_list, direction) if missing_dot != "None" else False


def points_on_diagonal(p1, p2):
    """
    Renvoie si le segment peut être dessiné, c'est-à-dire si il manque un seul point parmi l'alignement de 5 points
    Si c'est possible, alors un tuple est renvoyé de la forme: (point_manquant, liste_des_points_alignés, direction)
    Sinon, False est renvoyé
    """
    # Pente de la diagonale
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    m = 0
    if dx != 0:
        m = dy / dx  # Coefficient directeur

    # Ajout des coordonnées des points
    points = []
    missing_one = "None"
    # Si la pente est 1 ou -1, alors on ajoute les points de la diagonale
    if abs(m) == 1:
        # On parcourt les 3 points intermédiaires entre les deux extrémités en utilisant le coefficient directeur
        for i in range(0, 5):
            x = p1[0] + i * (p2[0] - p1[0]) // 4
            y = p1[1] + i * (p2[1] - p1[1]) // 4
            # On ajoute le point à la liste des points alignés
            points.append((x, y))
            # Si le point n'est pas déjà placé, alors on le considère comme manquant
            if (x, y) not in dots_placed:
                if missing_one == "None":
                    missing_one = (x, y)
                else:
                    # Si il y a plus d'un point manquant, alors le segment ne peut pas être dessiné
                    return False
    # On ajoute le dernier point

    return (missing_one, points, "diagonal" + ("1" if m == 1 else "2")) if missing_one != "None" else False


def end():
    """
    Termine le programme
    """
    global loop
    pygame.quit()
    loop = False
    print("Segments: ", len(segments), "| Points: ", len(dots_placed) - 36)


def draw_line(p1, p2, dir, screen):
    """
    Dessine un segment entre deux points
    """
    pygame.draw.line(screen, SEGMENT_COLOR, (p1[0] * SQUARE_SIZE, p1[1] * SQUARE_SIZE), (p2[0] * SQUARE_SIZE, p2[1] * SQUARE_SIZE), SEGMENT_WIDTH + (1 if "diagonal" in dir else 0))


def draw_dot(dot, screen):
    pygame.draw.circle(screen, DOT_COLOR, (dot[0] * SQUARE_SIZE, dot[1] * SQUARE_SIZE), DOT_WIDTH)


def calc_dots(dots=dots_placed, segs=segments):
    """
    Retourne les segments possibles pour chaque points placés
    """
    # Segments verticaux
    straight_segs = []
    vert_segs = []
    for i in range(len(dots)):
        d1 = dots[i]
        for j in range(i, len(dots)):
            dir = None
            d2 = dots[j]
            d1, d2 = list(sorted(list(sorted([d1, d2], key=lambda x: x[0])), key=lambda x: x[1]))

            dist = math.sqrt((d2[0] - d1[0])**2 + (d2[1] - d1[1])**2)

            if dist == 3:
                if d1[0] == d2[0]:
                    dir = "vertical"
                    straight_segs.append(([(d1[0], d1[1]-1), d2], dir))
                    straight_segs.append(([d1, (d2[0], d2[1]+1)], dir))
                elif d1[1] == d2[1]:
                    dir = "horizontal"
                    straight_segs.append(([(d1[0]-1, d1[1]), d2], dir))
                    straight_segs.append(([d1, (d2[0]+1, d2[1])], dir))
            
            if dist == 4:
                if d1[0] == d2[0]:
                    dir = "vertical"
                elif d1[1] == d2[1]:
                    dir = "horizontal"
                straight_segs.append(([d1, d2], dir))
            
            dx = d2[0] - d1[0]
            dy = d2[1] - d1[1]
            if dx == 0:
                continue
            m = dy / dx
            if abs(m) == 1:
                if dist == 4*math.sqrt(2):
                    vert_segs.append(([d1, d2], "diagonal" + ("1" if m == 1 else "2")))
            
            d1calc = calc_vert_segs(d1, dots, segs)
            if d1calc is not None:
                vert_segs.append(d1calc)

    return straight_segs, vert_segs


def calc_vert_segs(d1, dots=dots_placed, segs=segments):
    """
    Retourne la liste des segments diagonaux possibles dont le point manquant se trouve à une extrémité
    """
    possible_dots = [d1]
    scale_to_check = 1
    m = 0
    for d2 in dots:
        dist = math.sqrt((d2[0] - d1[0])**2 + (d2[1] - d1[1])**2)
        if dist == scale_to_check * math.sqrt(2):
            
            dx = d2[0] - d1[0]
            dy = d2[1] - d1[1]
            m2 = 0
            if dx != 0:
                m2 = dy / dx

            if scale_to_check == 1 and m == 0:
                m = m2
            
            if abs(m) == 1 and m2 == m:
                possible_dots.append(d2)
                scale_to_check += 1
        else:
            possible_dots = [d1]
            scale_to_check = 1
            m = 0

        if len(possible_dots) == 4:
            break
    
    # Calculer les coordonnées du point manquant se trouvant à l'extrémité du segment de la liste possible_dots
    if len(possible_dots) == 4:
        if possible_dots[0][0] == possible_dots[1][0]:
            missing_one = (possible_dots[0][0], possible_dots[0][1] + 1)
        else:
            missing_one = (possible_dots[0][0] + 1, possible_dots[0][1])
        return (possible_dots + [missing_one], "diagonal" + ("1" if m == 1 else "2"))
    return None


def sound(type):
    pygame.mixer.Channel(1).set_volume(0.2)
    pygame.mixer.Channel(1).play(pygame.mixer.Sound(f"{PATH}\{type}.mp3"))
    

## --------------- Programme principal --------------- ##
# Variables globales qui permettent le fonctionnement du programme
first_extrem = None
second_extrem = None
# Application du curseur de la souris
pygame.mouse.set_cursor(*pygame.cursors.broken_x)
# Dessin des points de départ
draw_beginning_dots()

# Mode de jeu, 1: IA, 2: Joueur
PLAY_MODE = input("Mode de jeu (1: AI, 2: Player): ")
while PLAY_MODE not in ["1", "2"]:
    PLAY_MODE = input("Mode de jeu (1: AI, 2: Player): ")

# Programme qui s'exécute si l'IA est activée
if PLAY_MODE == "1":
    deep = 580 # Profondeur de recherche (pour l'instant, c'est inutile)
    deep_step = 0 # Profondeur actuelle
    possible = True # Si il est possible de continuer à dessiner
    while deep_step < deep and possible:
        dots = calc_dots(dots_placed, segments)
        # On récupère les segments possibles
        seqs = dots[0] + dots[1]
        possible_seqs = []
        for seq, dir in seqs:
            data = can_be_drawn(seq[0], seq[1])
            if data and not segment_already_placed((data[2], data[1])):
                possible_seqs.append(data)

        # Si il n'y a plus de segments possibles, alors on arrête
        if len(possible_seqs) == 0:
            possible = False
            break

        # On choisit un segment au hasard et on le dessine
        to_draw = random.choice(possible_seqs)
        if to_draw[0] and to_draw[0] != "None":
            missing = to_draw[0]
            dots_placed.append(missing)
        segments.append((to_draw[2], to_draw[1]))

        # On incrémente la profondeur
        deep_step += 1


## --------------- Création de la fenêtre et de la grille --------------- ##
# Création de la fenêtre
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
draw_screen(screen)
pygame.mixer.Channel(0).set_volume(0.5)
pygame.mixer.Channel(0).play(pygame.mixer.Sound(PATH + "\Sweden.mp3"), -1)

# La boucle principale
loop = True
while loop:
    # On parcourt la liste des événements reçus
    for event in pygame.event.get():
        # On quitte le programme si l'utilisateur ferme la fenêtre ou appuie sur la touche Echap
        if event.type == QUIT or event.type == KEYDOWN and event.key == K_ESCAPE:
            end()
            break
        # Si l'utilisateur clique sur la souris
        if event.type == MOUSEBUTTONDOWN:
            # Si la première extrémité du segment à tracer n'est pas définie
            if first_extrem is None:
                nearest_intersect = closest_intersect(event)
                first_extrem = nearest_intersect
                sound("Place")
                pygame.mouse.set_cursor(*pygame.cursors.diamond)
            # Si la première extrémité est définie mais pas la deuxième
            elif second_extrem is None:
                nearest_intersect = closest_intersect(event)
                second_extrem = nearest_intersect
            # Si les deux extrémités sont placées, on trace le segment si les conditions sont remplies
            if first_extrem is not None and second_extrem is not None:
                # On vérifie que le segment est valide
                valid = valid_segment(first_extrem, second_extrem)
                if valid:
                    # On trace le segment si il peut être tracé
                    data = can_be_drawn(first_extrem, second_extrem)
                    if data and not segment_already_placed((data[2], data[1])):
                        # On ajoute le point qui manque à la liste des points placés si il en manque un
                        if data[0] and data[0] != "None":
                            missing = data[0]
                            dots_placed.append(missing)
                        seq = data[1]
                        # On ajoute le segment à la liste des segments tracés et on le dessine
                        segments.append((data[2], seq))
                        # On met à jour l'écran
                        draw_screen(screen)
                        sound("Success")
                    else:
                        sound("Fail")
                else:
                    sound("Fail")
                        
                # On réinitialise les extrémités
                first_extrem, second_extrem = None, None
                pygame.mouse.set_cursor(*pygame.cursors.broken_x)