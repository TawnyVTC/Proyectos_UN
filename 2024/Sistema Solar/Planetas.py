import pygame
import math
import random

pygame.init()

WIDTH, HEIGHT = 1200, 650
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)
LIGHT_GREY = (192, 192, 192)

FONT = pygame.font.SysFont("Arial", 16)

class CuerpoCeleste:
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    SCALE = 100 / AU  # 1AU = 100 pixels
    TIEMPO = 3600 * 24  # 1 day

    def __init__(self, x, y, radio, color, masa, nombre="", es_asteroide=False):
        self.x = x
        self.y = y
        self.radio = radio
        self.color = color
        self.masa = masa
        self.nombre = nombre
        self.es_asteroide = es_asteroide

        self.orbit = []
        self.sol = False
        self.distancia_a_sol = 0

        self.x_vel = 0
        self.y_vel = 0

    def draw(self, win):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        # Dibujar la órbita solo si no es un asteroide
        if not self.es_asteroide and len(self.orbit) > 2:
            puntos = []
            for point in self.orbit:
                x, y = point
                x = x * self.SCALE + WIDTH / 2
                y = y * self.SCALE + HEIGHT / 2
                puntos.append((x, y))
            pygame.draw.lines(win, self.color, False, puntos, 2)

        # Dibujar el cuerpo celeste
        pygame.draw.circle(win, self.color, (x, y), self.radio)

        # Mostrar nombre solo si no es un asteroide
        if not self.es_asteroide and self.nombre:
            nombre_text = FONT.render(self.nombre, 1, WHITE)
            win.blit(nombre_text, (x - nombre_text.get_width() / 2, y - self.radio - 20))

    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        if other.sol:
            self.distancia_a_sol = distance

        force = self.G * self.masa * other.masa / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def posicion(self, planets):
        total_fx = total_fy = 0
        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.masa * self.TIEMPO
        self.y_vel += total_fy / self.masa * self.TIEMPO

        self.x += self.x_vel * self.TIEMPO
        self.y += self.y_vel * self.TIEMPO
        self.orbit.append((self.x, self.y))


def crear_cinturon_asteroides(num_asteroides, distancia_inicial, distancia_final, sol):
    asteroides = []
    for _ in range(num_asteroides):
        distancia = random.uniform(distancia_inicial, distancia_final)
        angulo = random.uniform(0, 2 * math.pi)
        x = math.cos(angulo) * distancia
        y = math.sin(angulo) * distancia
        radio = random.randint(2, 4)
        masa = random.uniform(1e15, 1e17)
        asteroide = CuerpoCeleste(x, y, radio, LIGHT_GREY, masa, es_asteroide=True)
        velocidad_orbital = math.sqrt(CuerpoCeleste.G * sol.masa / distancia)
        asteroide.x_vel = -velocidad_orbital * math.sin(angulo)
        asteroide.y_vel = velocidad_orbital * math.cos(angulo)
        asteroides.append(asteroide)
    return asteroides


def main():
    run = True
    clock = pygame.time.Clock()

    sol = CuerpoCeleste(0, 0, 15, YELLOW, 1.98892 * 10**30, "Sol")
    sol.sol = True

    tierra = CuerpoCeleste(-1 * CuerpoCeleste.AU, 0, 16, BLUE, 5.9742 * 10**24, "Tierra")
    tierra.y_vel = 29.783 * 1000

    marte = CuerpoCeleste(-1.524 * CuerpoCeleste.AU, 0, 12, RED, 6.39 * 10**23, "Marte")
    marte.y_vel = 24.077 * 1000

    mercurio = CuerpoCeleste(0.387 * CuerpoCeleste.AU, 0, 8, DARK_GREY, 3.30 * 10**23, "Mercurio")
    mercurio.y_vel = -47.4 * 1000

    venus = CuerpoCeleste(0.723 * CuerpoCeleste.AU, 0, 14, WHITE, 4.8685 * 10**24, "Venus")
    venus.y_vel = -35.02 * 1000

    jupiter = CuerpoCeleste(5.2 * CuerpoCeleste.AU, 0, 24, (255, 165, 0), 1.898 * 10**27, "Júpiter")
    jupiter.y_vel = 13.07 * 1000  # Velocidad orbital de Júpiter en m/s

    # Crear cinturón de asteroides fuera de Marte (1.6 AU - 2.8 AU)
    asteroides = crear_cinturon_asteroides(200, 2.1 * CuerpoCeleste.AU, 3.3 * CuerpoCeleste.AU, sol)

    planetas = [sol, tierra, marte, mercurio, venus, jupiter] + asteroides

    while run:
        clock.tick(60)
        WIN.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for planeta in planetas:
            planeta.posicion(planetas)
            planeta.draw(WIN)

        pygame.display.update()

    pygame.quit()


main()
