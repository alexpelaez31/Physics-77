"""You need pygame installed in order to run this program!!!"""

import numpy as np
import pygame

pygame.init()

WIDTH, HEIGHT = 1000, 500
BALL_RADIUS = 20
POCKET_RADIUS = 40
RESTITUTION = 1.0
window = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# rows are balls (0 = cue, 1 = 1,...), columns are properties of balls (x velocity, y velocity, xpos, ypos)
ball0 = np.array([[250., 250.], [0., 0.], [20., 0.], [BALL_RADIUS, 0.]])
ball1 = np.array([[750., 250.], [0., 0.], [20., 0.], [BALL_RADIUS, 0.]])
ball2 = np.array([[750.+BALL_RADIUS*np.sqrt(2), 250.-BALL_RADIUS*np.sqrt(2)], [0., 0.], [20., 0.], [BALL_RADIUS, 0.]])
ball3 = np.array([[750.+BALL_RADIUS*np.sqrt(2), 250.+BALL_RADIUS*np.sqrt(2)], [0., 0.], [20., 0.], [BALL_RADIUS, 0.]])
ball4 = np.array([[750.+(2*BALL_RADIUS*np.sqrt(2)), 250.-(2*BALL_RADIUS*np.sqrt(2))], [0., 0.], [20., 0.], [BALL_RADIUS, 0.]])
ball5 = np.array([[750.+(2*BALL_RADIUS*np.sqrt(2)), 250.], [0., 0.], [20., 0.], [BALL_RADIUS, 0.]])
ball6 = np.array([[750.+(2*BALL_RADIUS*np.sqrt(2)), 250.+(2*BALL_RADIUS*np.sqrt(2))], [0., 0.], [20., 0.], [BALL_RADIUS, 0.]])

balls = np.array([ball0, ball1, ball2, ball3, ball4, ball5, ball6])

def add_vectors(v1, v2):
    return v1 + v2

def sub_vectors(v1, v2):
    return v1 - v2

def scale_vector(v1, c):
    return v1*c

def dot_prod(v1, v2):
    return np.sum(v1*v2)

# this function only works for 2-dimensional vectors
def magnitude(v1):
    return np.sqrt((v1[0])**2 + (v1[1])**2)

# this function calls another function
def norm_vector(v1):
    return v1 / magnitude(v1)

# this function makes a norm vector pointing FROM pos1 TO pos2
# pos1 and pos2 are assumed to be position vectors like [x, y]
# it also uses a previously defined function
def center_to_center_norm_vector(pos1, pos2):
    return norm_vector(pos2 - pos1)

# this function should only activate if there IS a collision
# ball1 and ball2 arrays with shape (4,2) and elts as FLOATS, NOT INTEGERS
# uses many previously defined functions
def ball_collision_pos_correction(ball1, ball2):

    # norm vector between two centers pointing FROM ball1 TO ball2
    normalized_direction_vector = center_to_center_norm_vector(ball1[0], ball2[0])
    #print(normalized_direction_vector)

    distance = magnitude(ball1[0] - ball2[0])                              # distance between centers of balls
    #print(distance)

    correction_amount = (ball1[3,0] + ball2[3,0] - distance) / 2           # (rad1 + rad2 - distance) / 2
    #print(correction_amount)

    correction_vector = normalized_direction_vector * correction_amount    # add this to each ball's position vector
    #print(correction_vector)
    #print(magnitude(correction_vector))

    ball1[0] = add_vectors(ball1[0], -correction_vector)   # new, corrected pos of ball1
    ball2[0] = add_vectors(ball2[0], correction_vector)   # new, corrected pos of ball2

    return ball1, ball2

# this function should only activate if there IS a collision
# ball1 and ball2 arrays with shape (4,2) and elts as FLOATS, NOT INTEGERS
# uses many previously defined functions
def ball_collision_vel_correction(ball1, ball2):

    # this section will allow us to calculate velocities/collisions in one dimension instead of two
    dir = center_to_center_norm_vector(ball1[0], ball2[0])   # this is the same as the previous function (dif name tho)
    v1 = dot_prod(ball1[1], dir)                             # find the velocity along dir of ball1
    v2 = dot_prod(ball2[1], dir)                             # find the velocity along dir of ball2

    m1 = np.array(ball1[2,0])
    m2 = np.array(ball2[2,0])

    # this controls the elasticity of each collision
    restitution = RESTITUTION

    # these 1-d formulas, from TenMinutePhysics, can be derived via the cons of momentum and kinetic energy eqs
    newv1 = np.array(((m1 * v1) + (m2 * v2) - (m2 * (v1 - v2) * restitution)) / (m1 + m2))
    newv2 = np.array(((m1 * v1) + (m2 * v2) - (m1 * (v2 - v1) * restitution)) / (m1 + m2))

    # apply changes to velocities
    ball1[1] += dir * (newv1 - v1)
    ball2[1] += dir * (newv2 - v2)

    # this serves to make velocities 0 if they are less than .001
    # the number should be changed depending on the size of our values, but is reasonable assuming radius = 1
    ball1[abs(ball1) < 1.0e-3] = 0.0
    ball2[abs(ball2) < 1.0e-3] = 0.0

    return ball1, ball2

# this function applies a position and velocity correction to each ball
def ball_collision(ball1, ball2):
    ball1, ball2 = ball_collision_pos_correction(ball1, ball2)
    ball1, ball2 = ball_collision_vel_correction(ball1, ball2)

# if a ball hits a horizontal wall, the y velocity flips
def horizontal_wall(ball):
    ball[1, 1] = -0.95 * ball[1, 1]

# if a ball hits a vertical wall, the x velocity flips
def vertical_wall(ball):
    ball[1, 0] = -0.95 * ball[1, 0]

# this function checks to see if two balls are colliding by determing the distance between their centers
def collision_check(n, m):
    if magnitude(n[0] - m[0]) < 2 * BALL_RADIUS:
        return True

# this function checks for collisions between a ball and a vertical wall (side of the screen)
def vertical_wall_check(ball):
    if ball[0, 0] >= WIDTH - BALL_RADIUS:
        wall = 1  # Right wall
    elif ball[0, 0] <= BALL_RADIUS:
        wall = -1  # Left wall
    else:
        wall = 0

    if wall == 1 and ball[1, 0] > 0:
        return True
    elif wall == -1 and ball[1, 0] < 0:
        return True
    else:
        return False

# this function checks for collisions between a ball and a horizontal wall (top/bottom of the screen)
def horizontal_wall_check(ball):
    if ball[0, 1] >= HEIGHT - BALL_RADIUS:
        wall = 1  # Right wall
    elif ball[0, 1] <= BALL_RADIUS:
        wall = -1  # Left wall
    else:
        wall = 0

    if wall == 1 and ball[1, 1] > 0:
        return True
    elif wall == -1 and ball[1, 1] < 0:
        return True
    else:
        return False


def pocket_check(ball, pocket):
    if magnitude(ball[0]-pocket) <= POCKET_RADIUS:
        return True

# the run function will allow pygame to display and the pool simulation to run
def run():
    run = True
    clock = pygame.time.Clock()
    fps = 60 # frames per second
    dt = 1 / fps
    gamma = 0.5  # damping factor

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        window.fill((0, 100, 0)) # green for the pool table

        # this part allows us to move the cue ball with our mouse in the direction of our mouse
        # the greater the distance from the cue ball, the greater the velocity of the cue ball
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            distance = mouse_pos - balls[0][0]
            balls[0][1] = distance*5



        # Pockets
        pygame.draw.circle(window, "black", (.5 * POCKET_RADIUS, .5 * POCKET_RADIUS), POCKET_RADIUS)
        pygame.draw.circle(window, "black", (WIDTH - .5 * POCKET_RADIUS, .5 * POCKET_RADIUS), POCKET_RADIUS)
        pygame.draw.circle(window, "black", (.5 * POCKET_RADIUS, HEIGHT - .5 * POCKET_RADIUS), POCKET_RADIUS)
        pygame.draw.circle(window, "black", (WIDTH - .5 * POCKET_RADIUS, HEIGHT - .5 * POCKET_RADIUS), POCKET_RADIUS)

        # Balls
        #draw_ball(ball0, "white", BALL_RADIUS)
        pygame.draw.circle(window, "white",  (balls[0][0]), BALL_RADIUS)
        pygame.draw.circle(window, "yellow", (balls[1][0]), BALL_RADIUS)
        pygame.draw.circle(window, "blue",   (balls[2][0]), BALL_RADIUS)
        pygame.draw.circle(window, "red",    (balls[3][0]), BALL_RADIUS)
        pygame.draw.circle(window, "purple", (balls[4][0]), BALL_RADIUS)
        pygame.draw.circle(window, "orange", (balls[5][0]), BALL_RADIUS)
        pygame.draw.circle(window, "green",  (balls[6][0]), BALL_RADIUS)

        pocket_centers = np.array(
            [[.5 * POCKET_RADIUS, .5 * POCKET_RADIUS],
             [WIDTH - .5 * POCKET_RADIUS, .5 * POCKET_RADIUS],
             [.5 * POCKET_RADIUS, HEIGHT - .5 * POCKET_RADIUS],
             [WIDTH - .5 * POCKET_RADIUS, HEIGHT - .5 * POCKET_RADIUS]]
        )

        for ball in balls:
            #print(ball)
            ball[0, 0] = ball[0, 0] + (ball[1, 0] * dt)  # xf = x0 + vx*dt
            ball[0, 1] = ball[0, 1] + (ball[1, 1] * dt)  # yf = y0 + vy*dt
            ball[1, 0] = ball[1, 0] - (ball[1, 0] * gamma * dt)  # vf = v0 - gamma*v0*dt (x direction)
            ball[1, 1] = ball[1, 1] - (ball[1, 1] * gamma * dt)  # vf = v0 - gamma*v0*dt (y direction)

        # checks for collisions between balls and walls
        for ball_n in balls:
            for ball_m in balls:
                if ball_n[0, 0] != ball_m[0, 0] and collision_check(ball_n, ball_m):  # Collisions between balls
                    ball_collision(ball_n, ball_m)
                    #print('Collision between ', ball_n, ' and ', ball_m)
                if vertical_wall_check(ball_n):  # Collisions with vertical walls
                    vertical_wall(ball_n)
                    #print(ball_n, ' hit a wall.')
                if horizontal_wall_check(ball_n):
                    horizontal_wall(ball_n)
                    #print(ball_n, ' hit a wall.')
                for pocket in pocket_centers:
                    #print(pocket)
                    if pocket_check(ball_n, pocket):
                        #print(ball_n, ' hit a pocket.')
                        ball_n[0], ball_n[1] = ([HEIGHT, WIDTH]), ([0, 0]) # we teleport the balls away
                if magnitude(ball_n[1]) < 10:  # this stops the balls from moving once they get below a certain speed
                    ball_n[1] = ([0,0])

        clock.tick(fps)
        pygame.display.update()
    pygame.quit()

run()
