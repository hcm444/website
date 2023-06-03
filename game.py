import pygame
import random
import geopandas as gpd
import sqlite3
import threading
import time
BOIDS = 20
SPEED = 0.0003
callsigns = ['CAW', 'CRO', 'BRD', 'CRW']
icao24_chars = '0123456789ABCDEF'
origin_countries = ['Crowistan', 'Cawcasia', 'Crowville', 'Republic of Crow','Crowatia','Democratic Republic of the Crowgo']
shapefile_path = "static/gadm41_UKR_shp/gadm41_UKR_0.shp"
gdf = gpd.read_file(shapefile_path)
bounds = gdf.total_bounds
pygame.init()
screen_width = 500
screen_height = 500
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Boids Algorithm")
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
boids = []
for i in range(BOIDS):
    boid = {
        "position": [random.randint(0, screen_width), random.randint(0, screen_height)],
        "velocity": [random.uniform(-1, 1), random.uniform(-1, 1)],
        "size": 5,
        'callsign': random.choice(callsigns) + str(random.randint(10, 99)),
        'icao24': ''.join(random.choices(icao24_chars, k=6)),
        'origin_country': random.choice(origin_countries)
    }
    boids.append(boid)


def align_boids(boid, boids):
    # get average velocity of nearby boids
    nearby_boids = [b for b in boids if b != boid and distance(boid["position"], b["position"]) < 50]
    if nearby_boids:
        avg_velocity = [sum(b["velocity"][i] for b in nearby_boids) / len(nearby_boids) for i in range(2)]
        # adjust velocity towards average velocity
        boid["velocity"] = normalize(
            [boid["velocity"][i] + (avg_velocity[i] - boid["velocity"][i]) / 8 for i in range(2)])


def keep_boids_on_screen(boid, screen):
    # keep boids within screen boundaries
    if boid["position"][0] < 0 or boid["position"][0] > screen.get_width():
        boid["velocity"][0] = -boid["velocity"][0]
    if boid["position"][1] < 0 or boid["position"][1] > screen.get_height():
        boid["velocity"][1] = -boid["velocity"][1]

def save_to_database(boid):
    conn = sqlite3.connect('databases/db.sqlite3')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS flights (icao24 text, callsign text, origin_country text, time_position real, 
 last_contact real, longitude real, latitude real, geo_altitude real, on_ground int, velocity real, true_track real, 
 vertical_rate real, sensors real, baro_altitude real, timestamp int)''')

    # Get the data to insert
    icao24 = str(boid.get('icao24'))
    callsign = str(boid.get('callsign'))
    origin_country = str(boid.get('origin_country'))
    time_position = 0
    last_contact = 0
    longitude = bounds[0] + round((bounds[2] - bounds[0]) * (boid["position"][0] / screen_width),4)
    latitude = bounds[1] + round((bounds[3] - bounds[1]) * (boid["position"][1] / screen_height),4)
    geo_altitude = 69.69
    on_ground = 0
    velocity = 69.69
    true_track = 69.69
    vertical_rate = 0
    sensors = 0
    baro_altitude = 0

    formatted_time = int(time.time())
    timestamp = formatted_time

    # Insert the record into the database with NULL values for new columns
    c.execute("INSERT INTO flights (icao24, callsign, origin_country, time_position,last_contact, longitude, latitude, geo_altitude, on_ground, velocity, true_track, vertical_rate, sensors, baro_altitude, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
              (icao24, callsign, origin_country, time_position,last_contact, longitude, latitude, geo_altitude, on_ground, velocity, true_track, vertical_rate, sensors, baro_altitude, timestamp))

    # Delete records older than 12 hours
    twelve_hours_ago = time.time() - (12 * 60 * 60)
    c.execute("DELETE FROM flights WHERE timestamp < ?", (twelve_hours_ago,))

    conn.commit()
    conn.close()




def save_boid_data(boids):
    while True:
        for boid in boids:
            save_to_database(boid)

        time.sleep(120)  # Wait for 2 minutes after all boids have been saved

# Create a thread for saving boid data
save_thread = threading.Thread(target=save_boid_data, args=(boids,))

save_thread.daemon = True
save_thread.start()


def avoid_boids(boid, boids):
    # get average position of nearby boids
    nearby_boids = [b for b in boids if b != boid and distance(boid["position"], b["position"]) < 25]
    if nearby_boids:
        avg_position = [sum(b["position"][i] for b in nearby_boids) / len(nearby_boids) for i in range(2)]
        # adjust velocity away from average position
        boid["velocity"] = normalize(
            [boid["velocity"][i] + (boid["position"][i] - avg_position[i]) / 8 for i in range(2)])


def move_boids(boid):
    boid["position"][0] += boid["velocity"][0] * SPEED
    boid["position"][1] += boid["velocity"][1] * SPEED
    boid["velocity"] = normalize(boid["velocity"])
    if boid["position"][0] > screen_width:
        boid["position"][0] = screen_width
        boid["velocity"][0] *= -1
    elif boid["position"][0] < 0:
        boid["position"][0] = 0
        boid["velocity"][0] *= -1
    if boid["position"][1] > screen_height:
        boid["position"][1] = screen_height
        boid["velocity"][1] *= -1
    elif boid["position"][1] < 0:
        boid["position"][1] = 0
        boid["velocity"][1] *= -1


def distance(p, q):
    return ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** 0.5


def normalize(v):
    norm = (v[0] ** 2 + v[1] ** 2) ** 0.25
    return [v[0] / norm, v[1] / norm]


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    for boid in boids:
        align_boids(boid, boids)
        avoid_boids(boid, boids)
        move_boids(boid)
        keep_boids_on_screen(boid, screen)
    screen.fill(BLACK)
    for boid in boids:
        pygame.draw.circle(screen, WHITE, [int(boid["position"][0]), int(boid["position"][1])], boid["size"])
    boid_positions = []
    for i in range(len(boids)):
        # Scale the x,y position of the boid to the range of the shapefile bounds
        x = bounds[0] + (bounds[2] - bounds[0]) * (boids[i]["position"][0] / screen_width)
        y = bounds[1] + (bounds[3] - bounds[1]) * (boids[i]["position"][1] / screen_height)
        boid_positions.append((y, x))  # lat, lon order
    for i in range(len(boids)):
        pygame.draw.circle(screen, WHITE, [int(boids[i]["position"][0]), int(boids[i]["position"][1])],
                           boids[i]["size"])
        font = pygame.font.SysFont(None, 18)
        text = font.render(f"{boid_positions[i][0]:.3f}, {boid_positions[i][1]:.3f}", True, WHITE)
        screen.blit(text, (boids[i]["position"][0] + 10, boids[i]["position"][1] + 10))
    pygame.display.update()
pygame.quit()