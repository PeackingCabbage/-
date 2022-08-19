"""
作者：讨啄的白菜
日期：2022年08月13日
"""
import random
import cv2
import pygame
import pymunk
import pymunk.pygame_util
import math
from pymunk.vec2d import Vec2d
import numpy as np
from pymunk.autogeometry import march_soft


pygame.init()

WIDTH, HEIGHT = 1536, 800
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('坦克动荡')

mouse_joint = None
mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)

collision_types = {
    "tank": 1,
    "bullet": 2,
}

font = pygame.font.SysFont("Arial", 30)

bullets = []

red_win = 0
green_win = 0

class Bullet:
    def __init__(self, bullet_shape):
        self.bullet_shape = bullet_shape
        self.time = 500
    def update(self, space):
        self.time -= 1
        if self.time <= 0 and self.bullet_shape in space.shapes:
            space.remove(self.bullet_shape.body, self.bullet_shape)
            bullets.remove(self)


def calculate_distance(p1, p2):
    return math.sqrt((p2[1] - p1[1])**2 + (p2[0] - p1[0])**2)

def calculate_angle(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

def draw(space, window, draw_options, line):
    window.fill("white")
    if line:
        pygame.draw.line(window, "black", line[0], line[1], 3)
    space.debug_draw(draw_options)
    window.blit(
        font.render("red    : %d" % red_win, True, pygame.Color("red")),
        (1400, 10)
    )
    window.blit(
        font.render("green: %d" % green_win, True, pygame.Color("green")),
        (1400, 50)
    )
    # window.blit(pygame.transform.rotate(tank1_img, 90 - np.angle(tank1.rotation_vector[0] + 1j*tank1.rotation_vector[1], deg=True)), tank1.position - (12, 7))
    pygame.display.update()

def create_boundaries(space, width, height):
    rects = [
        [(width/2, height - 10), (width, 20)],
        [(width/2, 10), (width, 20)],
        [(10, height/2), (20, height)],
        [(width - 10, height/2), (20, height)],
    ]

    for pos, size in rects:
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = pos
        shape = pymunk.Poly.create_box(body, size)
        shape.elasticity = 0.4
        shape.friction = 1
        space.add(body, shape)

def create_structure(space, width, height):
    BROWN = (139, 69, 19, 100)
    rects = [
        [(600, height - 120), (40, 200), BROWN, 100],
        [(900, height - 120), (40, 200), BROWN, 100],
        [(750, height - 240), (340, 40), BROWN, 150],
    ]

    for pos, size, color, mass in rects:
        body = pymunk.Body()
        body.position = pos
        shape = pymunk.Poly.create_box(body, size, radius=2)
        shape.color = color
        shape.mass = mass
        shape.elasticity = 0.4
        space.add(body, shape)

def create_ball(space, radius, pos):
    body = pymunk.Body()
    body.position = pos
    shape = pymunk.Circle(body, radius)
    shape.density = 0.1
    shape.elasticity = 1
    shape.friction = 0
    shape.color = (255, 0, 0, 100)
    space.add(body, shape)
    return shape

def create_ret(space, pos, size, flag):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = pos
    if flag == 0:
        # body.position = pos + (4//2, size//2)
        shape = pymunk.Poly.create_box(body, (4, size), radius=1)  # 竖
    else:
        # body.position = pos + (size // 2, 4 // 2)
        shape = pymunk.Poly.create_box(body, (size, 4), radius=1)

    shape.elasticity = 1
    shape.density = 0.1
    shape.color = (77, 77, 77, 100)
    space.add(body, shape)
    return shape

def create_seg(space, pos, size, flag):
    body = pymunk.Body(body_type=pymunk.Body.STATIC)
    body.position = pos
    rad = 4
    if flag == 0:
        shape = pymunk.Segment(body, (0, 0), (0, size), radius=rad)
    else:
        shape = pymunk.Segment(body, (0, 0), (size, 0), radius=rad)

    shape.elasticity = 1
    shape.density = 0.1
    shape.color = (77, 77, 77, 100)
    space.add(body, shape)
    return shape

def create_map(space):
    image = cv2.imread("10x10.png", cv2.IMREAD_GRAYSCALE)
    image = cv2.resize(image, (image.shape[0]*2, image.shape[1]*2))
    map = image < 127
    # map_body = pymunk.Body()
    # space.add(map_body)
    def sample_func(point):
        x = int(point[0])
        y = int(point[1])
        return 1 if map[y][x] else 0

    pl_set = march_soft(pymunk.BB(0, 0, map.shape[0], map.shape[1]), map.shape[0], map.shape[1], .5, sample_func)
    for poly_line in pl_set:
        for i in range(len(poly_line) - 1):
            a = poly_line[i]
            b = poly_line[i + 1]
            segment = pymunk.Segment(space.static_body, a, b, 1)
            segment.density = 0.1
            space.add(segment)
    # for i in range(map.shape[0]):
    #     for j in range(map.shape[1]):
    #         if map[i][j]:
    #             create_ret(space, (j, i), (1, 1))
def create_map2(space):
    # create_ret(space, (0,0), 164, 0)
    for _ in range(500):
        pos = (random.randint(0, 30) * 50, random.randint(0, 20) * 50)
        size = random.randint(1, 1) * 50
        flag = random.choice((0, 1))
        create_seg(space, pos, size, flag)

def create_tank(space, color):
    tank_body = pymunk.Body()
    tank_body.position = (random.randint(100, 1400), random.randint(100, 800))

    # tank_shape = pymunk.Poly.create_box(tank_body, (20, 15))
    tank_shape = pymunk.Poly.create_box(tank_body, (28, 21))
    tank_shape.density = 0.1
    tank_shape.color = color
    tank_shape.collision_type = collision_types["tank"]

    tank_shape_2 = pymunk.Circle(tank_body, 7)
    tank_shape_2.density = 0.1
    tank_shape_2.collision_type = collision_types["tank"]
    tank_shape_2.color = (int(color[0] * 200 / 255), int(color[1] * 200 / 255), int(color[2] * 200 / 255), color[3])

    tank_shape_3 = pymunk.Segment(tank_body, (-5, 0), (20, 0), 2)
    tank_shape_3.density = 0.1
    tank_shape_3.collision_type = collision_types["tank"]
    tank_shape_3.color = (int(color[0] * 123 / 255), int(color[1] * 123 / 255), int(color[2] * 123 / 255), color[3])

    space.add(tank_shape, tank_shape_2, tank_shape_3, tank_body)
    return tank_body

def fire(space, tank):
    bullet_body = pymunk.Body()
    bullet_body.position = tank.position + tank.rotation_vector * 24
    bullet_shape = pymunk.Circle(bullet_body, 3)
    bullet_shape.density = 0.1
    bullet_shape.elasticity = 1
    bullet_shape.friction = 0
    bullet_shape.color = pygame.Color("black")
    bullet_shape.collision_type = collision_types["bullet"]

    bullet_body.velocity = (tank.rotation_vector) * 170
    space.add(bullet_body, bullet_shape)
    bullets.append(Bullet(bullet_shape))


def create_stick_figure(space):
    shapes = []
    bodies = []
    joints = []

    # head = pymunk.Body()
    # bodies.append(head)
    # head.position = (300, 500)
    # head_shape = pymunk.Circle(head, 20)
    # shapes.append(head_shape)

    torso = pymunk.Body()
    bodies.append(torso)
    torso.position = (300, 520)
    torso_shape = pymunk.Segment(torso, (0, 0), (0, 70), 5)
    torso_shape.color = (0, 0, 200, 100)
    tou_shape = pymunk.Circle(torso, 20, (0, -20))
    tou_shape.color = (200, 0, 0, 100)
    shapes.append(torso_shape)
    shapes.append(tou_shape)

    left_arm = pymunk.Body()
    bodies.append(left_arm)
    left_arm.position = (300, 520)
    left_arm_shape = pymunk.Segment(left_arm, (0, 0), (-25, 30), 5)
    left_arm_shape.color = (0, 0, 200, 100)
    shapes.append(left_arm_shape)

    left_arm_2 = pymunk.Body()  # 左下臂
    bodies.append(left_arm_2)
    left_arm_2.position = (275, 550)
    left_arm_2_shape = pymunk.Segment(left_arm_2, (0, 0), (-25, 30), 5)
    left_arm_2_shape.color = (200, 0, 0, 100)
    shapes.append(left_arm_2_shape)

    right_arm = pymunk.Body()
    bodies.append(right_arm)
    right_arm.position = (300, 520)
    right_arm_shape = pymunk.Segment(right_arm, (0, 0), (25, 30), 5)
    right_arm_shape.color = (0, 0, 200, 100)
    shapes.append(right_arm_shape)

    right_arm_2 = pymunk.Body()  # 右下臂
    bodies.append(right_arm_2)
    right_arm_2.position = (325, 550)
    right_arm_2_shape = pymunk.Segment(right_arm_2, (0, 0), (25, 30), 5)
    right_arm_2_shape.color = (200, 0, 0, 100)
    shapes.append(right_arm_2_shape)

    left_leg = pymunk.Body()
    bodies.append(left_leg)
    left_leg.position = (300, 590)
    left_leg_shape = pymunk.Segment(left_leg, (0, 0), (-25, 30), 6)
    left_leg_shape.color = (0, 0, 200, 100)
    shapes.append(left_leg_shape)

    left_leg_2 = pymunk.Body()
    bodies.append(left_leg_2)
    left_leg_2.position = (275, 620)
    left_leg_2_shape = pymunk.Segment(left_leg_2, (0, 0), (-25, 30), 6)
    left_leg_2_shape.color = (200, 0, 0, 100)
    shapes.append(left_leg_2_shape)

    right_leg = pymunk.Body()
    bodies.append(right_leg)
    right_leg.position = (300, 590)
    right_leg_shape = pymunk.Segment(right_leg, (0, 0), (25, 30), 6)
    right_leg_shape.color = (0, 0, 200, 100)
    shapes.append(right_leg_shape)

    right_leg_2 = pymunk.Body()
    bodies.append(right_leg_2)
    right_leg_2.position = (325, 620)
    right_leg_2_shape = pymunk.Segment(right_leg_2, (0, 0), (25, 30), 6)
    right_leg_2_shape.color = (200, 0, 0, 100)
    shapes.append(right_leg_2_shape)

    for shape in shapes:
        shape.friction = 1
        shape.mass = 3
        shape.elasticity = 0.5
        shape.filter = pymunk.ShapeFilter(group=1)

    # head_torso_joint = pymunk.PivotJoint(head, torso, (300, 500))
    # joints.append(head_torso_joint)

    torso_left_arm_joint = pymunk.PivotJoint(torso, left_arm, (300, 520))
    joints.append(torso_left_arm_joint)

    torso_right_arm_joint = pymunk.PivotJoint(torso, right_arm, (300, 520))
    joints.append(torso_right_arm_joint)

    left_arm_12_joint = pymunk.PivotJoint(left_arm, left_arm_2, (275, 550))
    joints.append(left_arm_12_joint)

    right_arm_12_joint = pymunk.PivotJoint(right_arm, right_arm_2, (325, 550))
    joints.append(right_arm_12_joint)

    torso_left_leg_joint = pymunk.PivotJoint(torso, left_leg, (300, 590))
    # torso_left_leg_RatchetJoint =  pymunk.RatchetJoint(left_leg, torso, 0, math.pi / 3)
    joints.append(torso_left_leg_joint)
    # joints.append(torso_left_leg_RatchetJoint)

    torso_right_leg_joint = pymunk.PivotJoint(torso, right_leg, (300, 590))
    # torso_right_leg_RatchetJoint = pymunk.RatchetJoint(right_leg, torso, 0, math.pi / 3)
    joints.append(torso_right_leg_joint)
    # joints.append(torso_right_leg_RatchetJoint)

    left_leg_12_joint = pymunk.PivotJoint(left_leg, left_leg_2, (275, 620))
    left_leg_12_joint_2 = pymunk.RatchetJoint(left_leg_2, left_leg, 0, -math.pi)
    joints.append(left_leg_12_joint)
    joints.append(left_leg_12_joint_2)
    left_leg_12_joint_3 = pymunk.DampedRotarySpring(left_leg, left_leg_2, -math.pi, 3000, 60)
    joints.append(left_leg_12_joint_3)


    right_leg_12_joint = pymunk.PivotJoint(right_leg, right_leg_2, (325, 620))
    right_leg_12_joint_2 = pymunk.RatchetJoint(right_leg_2, right_leg, 0, -math.pi)
    joints.append(right_leg_12_joint)
    joints.append(right_leg_12_joint_2)
    right_leg_12_joint_3 = pymunk.DampedRotarySpring(right_leg, right_leg_2, -math.pi, 3000, 60)
    joints.append(right_leg_12_joint_3)

    space.add(*bodies, *shapes, *joints)

    return torso

def create_swing_ball(space):
    rotation_center_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    rotation_center_body.position = (300, 300)

    body = pymunk.Body()
    body.position = (300, 300)
    line = pymunk.Segment(body, (0, 0), (255, 0), 5)
    circle = pymunk.Circle(body, 40, (255, 0))
    line.friction = 1
    circle.friction = 1
    line.mass = 8
    circle.mass = 30
    circle.elasticity = 0.95
    rotation_center_joint = pymunk.PinJoint(body, rotation_center_body, (0, 0), (0, 0))
    space.add(circle, line, body, rotation_center_joint)

def restart(space, tank1, tank2):
    is_end = 0
    try:
        space.remove(*tank1.shapes, *tank2.shapes, tank1, tank2)
    except:
        pass
    for s in space.shapes[:]:
        try:
            space.remove(s.body, s)
        except:
            continue
    t1 = create_tank(space, (255, 0, 0, 100))
    t2 = create_tank(space, (0, 255, 0, 100))
    create_map2(space)

    return t1, t2, is_end


def run(window, width, height):
    run = True
    clock = pygame.time.Clock()
    fps = 60
    dt = 1 / fps
    space = pymunk.Space()
    # space.gravity = (0, 0)

    # create_boundaries(space, width, height)
    # create_structure(space, width, height)
    # stick_figure = create_stick_figure(space)
    tank1 = create_tank(space, (255, 0, 0, 100))
    # print(tank1.shapes)
    tank2 = create_tank(space, (0, 255, 0, 100))
    # create_ball(space, 10, (50, 50))

    tank = {
        "speed": 100,
        "angular_velocity": 3
    }

    draw_options = pymunk.pygame_util.DrawOptions(window)

    translation = pymunk.Transform()
    scaling = 1

    pressed_pos = None
    ball = None

    cnt = 1
    remove_obj = set([])
    def remove_tank(arbiter, space, data):
        tank_shape = arbiter.shapes[0]
        print(tank_shape)
        space.remove(tank_shape)

    def remove_bullet(arbiter, space, data):
        bullet_shape = arbiter.shapes[1]
        tank_shape = arbiter.shapes[0]
        # space.remove(bullet_shape, bullet_shape.body)
        remove_obj.add(bullet_shape)
        if bullet_shape in bullets:
            bullets.remove(bullet_shape)
        remove_obj.add(tank_shape)

    h = space.add_collision_handler(collision_types["tank"], collision_types["bullet"])
    # h2 = space.add_collision_handler(collision_types["tank"], collision_types["bullet"])
    h.separate = remove_bullet
    # h2.separate = remove_bullet
    create_map2(space)
    is_end = 0

    while run:
        # print(tank2.shapes)
        line = None
        if cnt == 1:
            mouse_joint = None
            mouse_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
            cnt = 0
        if ball and pressed_pos:
            line = [pygame.mouse.get_pos(), pressed_pos]

        # stick_figure.apply_force_at_world_point((0, -27000), stick_figure.position + (0, -100))

        key = pygame.key.get_pressed()

        tank1.velocity = 0, 0
        tank1.angular_velocity = 0
        tank2.velocity = 0, 0
        tank2.angular_velocity = 0

        tank1_fire_available = False
        tank1_move_available = False
        tank1_rotate_available = False
        tank2_fire_available = False
        tank2_move_available = False
        tank2_rotate_available = False

        global red_win
        global green_win
        if len(tank2.shapes) == 0 and is_end == 0:
            red_win += 1
            is_end = 1
        if len(tank1.shapes) == 0 and is_end == 0:
            green_win += 1
            is_end = 1

        for item in tank1.shapes:
            if isinstance(item, pymunk.shapes.Poly):
                tank1_move_available = True
            elif isinstance(item, pymunk.shapes.Segment):
                tank1_fire_available = True
            elif isinstance(item, pymunk.shapes.Circle):
                tank1_rotate_available = True

        for item in tank2.shapes:
            if isinstance(item, pymunk.shapes.Poly):
                tank2_move_available = True
            elif isinstance(item, pymunk.shapes.Segment):
                tank2_fire_available = True
            elif isinstance(item, pymunk.shapes.Circle):
                tank2_rotate_available = True

        if key[pygame.K_UP] and tank1_move_available:
            tank1.velocity = tank1.rotation_vector * tank["speed"]
        if key[pygame.K_DOWN] and tank1_move_available:
            tank1.velocity = tank1.rotation_vector * -tank["speed"]

        if key[pygame.K_LEFT] and tank1_rotate_available:
            tank1.angular_velocity = -tank["angular_velocity"]
        if key[pygame.K_RIGHT] and tank1_rotate_available:
            tank1.angular_velocity = tank["angular_velocity"]

        if key[pygame.K_w] and tank2_move_available:
            tank2.velocity = tank2.rotation_vector * tank["speed"]
        if key[pygame.K_s] and tank2_move_available:
            tank2.velocity = tank2.rotation_vector * -tank["speed"]

        if key[pygame.K_a] and tank2_rotate_available:
            tank2.angular_velocity = -tank["angular_velocity"]
        if key[pygame.K_d] and tank2_rotate_available:
            tank2.angular_velocity = tank["angular_velocity"]

        # if key[pygame.K_KP_ENTER]:
        #     fire(space, tank1)
            # bullet.velocity = (tank1.rotation_vector) * 400
        for item in remove_obj.copy():
            if item in space.shapes:
                space.remove(item)
        remove_obj.clear()

        for b in bullets:
            b.update(space)

        left = int(key[pygame.K_KP_4])
        up = int(key[pygame.K_KP_8])
        down = int(key[pygame.K_KP_2])
        right = int(key[pygame.K_KP_6])
        zoom_in = int(key[pygame.K_x])
        zoom_out = int(key[pygame.K_z])

        zoom_speed = 0.1
        scaling *= 1 + (zoom_speed * zoom_in - zoom_speed * zoom_out)

        translate_speed = 10
        translation = translation.translated(
            translate_speed * left - translate_speed * right,
            translate_speed * up - translate_speed * down,
        )

        draw_options.transform = (
            pymunk.Transform.scaling(scaling)
            @ translation
        )

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if mouse_joint is not None:
                    space.remove(mouse_joint)
                    mouse_joint = None

                p = Vec2d(*event.pos)
                hit = space.point_query_nearest(p, 5, pymunk.ShapeFilter())
                if hit is not None and hit.shape.body.body_type == pymunk.Body.DYNAMIC:
                    shape = hit.shape
                    # Use the closest point on the surface if the click is outside
                    # of the shape.
                    if hit.distance > 0:
                        nearest = hit.point
                    else:
                        nearest = p
                    mouse_joint = pymunk.PivotJoint(
                        mouse_body, shape.body, (0, 0), shape.body.world_to_local(nearest)
                    )
                    mouse_joint.max_force = 50000
                    mouse_joint.error_bias = (1 - 0.15) ** 60
                    space.add(mouse_joint)

            elif event.type == pygame.MOUSEBUTTONUP:
                if mouse_joint is not None:
                    space.remove(mouse_joint)
                    mouse_joint = None
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                tank1, tank2, is_end = restart(space, tank1, tank2)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_KP_ENTER and tank1_fire_available:
                fire(space, tank1)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and tank2_fire_available:
                fire(space, tank2)
        # if key[pygame.K_KP_ENTER] and tank1_fire_available:
        #     fire(space, tank1)
        # if key[pygame.K_SPACE] and tank2_fire_available:
        #     fire(space, tank2)




        mouse_body.position = pygame.mouse.get_pos()


        draw(space, window, draw_options, line)
        space.step(dt)
        clock.tick(fps)

    pygame.quit()


if __name__ == "__main__":
    run(window, WIDTH, HEIGHT)

