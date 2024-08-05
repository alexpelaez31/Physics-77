"""Make sure the functions are called in the right order!!!"""

import numpy as np

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
    restitution = 1.0

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

def ball_collision(ball1, ball2):
    ball1, ball2 = ball_collision_pos_correction(ball1, ball2)
    ball1, ball2 = ball_collision_vel_correction(ball1, ball2)

    return ball1, ball2

baller1 = np.array([[0.,0],[1,0],[20,0],[1,0]])
baller2 = np.array([[1.,1],[-1,0],[20,0],[1,0]])

print(ball_collision(baller1, baller2))

