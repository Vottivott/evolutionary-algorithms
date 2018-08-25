from itertools import izip

import pygame, sys
import pygame.gfxdraw
from pygame.locals import *
import numpy as np
from ..evomath import *
# import pyglet.media

def tuple_add(a,b):
    return [v_a+v_b for v_a,v_b in zip(a,b)]

def tuple_scale(a,factor):
    return [v_a*factor for v_a in a]


def to_tuple(np_array):
    try:
        return [np.asscalar(n) for n in np_array]
    except TypeError:
        return np_array

class ScoreText:
    def __init__(self, hitPosition):
        self.position = np.copy(hitPosition)
        self.time_left = 90
        self.rise_rate = 1

    def update(self):
        self.position[1] -= self.rise_rate
        self.time_left -= 1
        if self.time_left <= 0:
            return False
        return True

# import pyglet
class WormGraphics:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        self.size = w, h = 1200, 500#1200, 500
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.view_offset = w/7#17.0
        self.enemy_view_offset = 6.0*w/7
        # self.sputter_sound = pyglet.media.StaticSource(pyglet.media.load('../sputter_sound.wav'))#pygame.mixer.Sound('beep.wav')
        # self.sound_player = pyglet.media.Player()
        # self.crash_sound = pyglet.media.StaticSource(pyglet.media.load('../crash_sound.wav'))#pyglet.media.load('crash_sound.wav')
        # self.shot_sound = pyglet.media.StaticSource(pyglet.media.load('../shot_sound.wav'))
        # self.enemy_hit_sound = pyglet.media.StaticSource(pyglet.media.load('../enemy_hit_sound.wav'))
        # self.enemy_sputter_sound = pyglet.media.StaticSource(pyglet.media.load('../enemy_sputter_sound.wav'))
        # self.enemy_dive_sound = pyglet.media.StaticSource(pyglet.media.load('../enemy_dive_sound.wav'))
        self.main_worm_smoke_color = (200, 0, 0)
        self.main_worm_color = (0, 60, 75)
        self.starve_color = (178, 30, 35)
        self.middle_color = (0, 60, 75)
        self.full_color = (0, 240, 255)
        self.enemy_smoke_color = (40, 40, 40)
        self.enemy_color = (30, 30, 30)
        w = 0.8
        self.sky_color = [255.0 * w + b * (1.0 - w) for b in self.middle_color]
        w = 0.3
        self.ground_color = [255.0 * w + b * (1.0 - w) for b in self.middle_color]
        self.who_to_follow = 'main' # True = main robot, number n = enemy with index n
        self.user_control = None
        self.keys = None
        # TEST
        # self.main_worm_color = self.enemy_color
        # self.main_worm_smoke_color = self.enemy_smoke_color
        # self.crash_sound = pyglet.resource.media('crash_sound.wav')#pygame.mixer.Sound('crash_sound.wav')
        # effect.play()
        self.show_enemy_radars = False
        self.show_enemy_object_radars = False
        self.show_worm_radars = False
        self.show_worm_object_radars = False
        self.player_box_timer = 0.0
        self.PLAYER_BOX_TIME = 60

        self.score = 0
        self.score_font = pygame.font.Font('../Steppes.ttf', 30)
        self.shot_score_font = pygame.font.Font('../Steppes.ttf', 50)
        self.shot_score_color = (255,255,255)#self.main_worm_color
        self.shot_score_surface = self.score_font.render('+1000', False, self.shot_score_color)
        self.shot_score_texts = []

        self.frame = 0



    def update(self, worm_simulation):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            #if event.type == KEYDOWN and event.key == K_KP_ENTER:


        self.screen.fill(self.sky_color)
        # self.screen.fill((208, 212, 224))
        # self.screen.fill((240, 245, 250))

        # s = pygame.Surface(self.size)  # the size of your rect
        # if trace:
        #     s.set_alpha(28)  # alpha level
        # s.fill((0, 0, 0))  # this fills the entire surface
        # self.screen.blit(s, (0, 0))  # (0,0) are the top-left coordinates


        #     pointlists = get_curve()
        #     color = min(np.random.normal(200, 30, 1), 255)

        self.draw_fish(worm_simulation.worm, worm_simulation)
        self.draw_ball(worm_simulation.worm.football, worm_simulation)
        self.draw_grips(worm_simulation)
        self.draw_stones(worm_simulation.level, worm_simulation)
        self.draw_bar_level(worm_simulation)
        self.draw_debug_bounces(worm_simulation.worm, worm_simulation)
        self.draw_kicks(worm_simulation)

        # self.draw_fish_radars(worm_simulation)
        # self.draw_fish_object_radars(worm_simulation)


        # self.draw_shots(worm_simulation)

        self.draw_score(worm_simulation)

        pygame.display.flip()

        #TEST
        #self.frame += 1
        #pygame.image.save(self.screen, "screenshots/screenshot" + str(self.frame) + ".jpeg")
        #/TEST

        self.clock.tick(60)

        self.keys = pygame.key.get_pressed()  # checking pressed keys
        return self.keys[pygame.K_SPACE], self.keys[pygame.K_KP_ENTER], (self.keys[pygame.K_LCTRL] or self.keys[pygame.K_RCTRL] or self.keys[pygame.K_DOWN])#, (keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL] or keys[pygame.K_DOWN]), keys[pygame.K_LEFT]


    def draw_fish_radars(self, worm_simulation):
        for f in worm_simulation.worm.fish:
        # f = worm_simulation.worm.fish[0]
            for radar in f.radar_system.radars:
                point, dist = radar.point, radar.dist
                if True:#(point,dist) == (None,None):
                    point,dist = radar.read(f.position, worm_simulation.level)
                if True:#dist < 1:
                    dist = 0.5 + dist/2 # for drawing only
                    color = (255, int(150+(255-150)*dist), int(dist*255))
                    pygame.draw.circle(self.screen, color, self.np_to_screen_coord(point, worm_simulation), 5)


    def draw_bar_level(self, worm_simulation):
        level = worm_simulation.level
        bar_width = worm_simulation.level.bar_width
        if self.who_to_follow == None:
            cx = 0.0
        else:
            if self.who_to_follow == 'main' or self.who_to_follow >= len(worm_simulation.enemy_instances):
                cx = worm_simulation.worm.get_x()
            else:
                cx = worm_simulation.enemy_instances[self.who_to_follow].enemy.get_x()
        start = cx - self.get_view_offset(worm_simulation)
        end = start + self.size[0]
        start /= bar_width
        end /= bar_width
        xoff = -bar_width * (start - int(start))
        start = min(len(level), max(0, start))
        end = min(len(level), max(0, end))
        start = int(start)
        end = int(end+2)
        ceiling_region = worm_simulation.level.ceiling[start:end]
        ground_region = worm_simulation.level.ground[start:end]



        ceiling_coords = [(bar_width * x + xoff, y) for x, y in enumerate(list(ceiling_region))]
        # ceiling_pointlist = [(this, next) for this, next in izip(ceiling_coords, ceiling_coords[1:])]
        ground_coords = [(bar_width * x + xoff, y) for x, y in enumerate(list(ground_region))]
        # ground_pointlist = [(this, next) for this, next in izip(ground_coords, ground_coords[1:])]
        c_cave = self.ground_color#(150,160,170)
        # for point in ceiling_pointlist:
        #     pygame.draw.lines(self.screen, (255, color, 0), False, point, 2)
        # for point in ground_pointlist:
        #     pygame.draw.lines(self.screen, (255, color, 0), False, point, 2)
        pygame.draw.polygon(self.screen, c_cave, [[0,0]]+[[0,self.size[1]]] + ceiling_coords + [[self.size[0],self.size[1]]]+[[self.size[0],0]])
        pygame.draw.polygon(self.screen, c_cave, [[0,self.size[1]]] + [[0,self.size[1]]] + ground_coords + [[self.size[0],self.size[1]]])

    def play_crash_sound(self):
        # self.sound_player.queue(self.crash_sound)
        self.crash_sound.play()

    def play_sputter_sound(self):
        self.sputter_sound.play()

    def play_enemy_sputter_sound(self):
        self.enemy_sputter_sound.play()

    def play_enemy_dive_sound(self):
        self.enemy_dive_sound.play()


    def play_shot_sound(self):
        self.shot_sound.play()

    def play_enemy_hit_sound(self):
        self.enemy_hit_sound.play()


    def draw_worm(self, worm, worm_simulation):
        # self.draw_muscles(worm_simulation)
        for b in worm.balls:
            self.draw_ball(b, worm_simulation)

    def draw_fish(self, worm, worm_simulation):
        # self.draw_muscles(worm_simulation)
        for f in worm.fish:
            self.draw_dynamic_fish(f, worm_simulation)
            # self.draw_one_fish(f, worm_simulation)

    def get_fish_color(self, energy, age):
        energy = float(np.clip(energy, 0.0, 1.0))
        age = float(np.clip(age, 0.0, 1.0))
        if energy < 0.5:
            color = [a * (1.0 - energy / 0.5) + b * energy / 0.5 for a, b in zip(self.starve_color, self.middle_color)]
        else:
            color = [a * (1.0 - (energy-0.5) / 0.5) + b * (energy-0.5) / 0.5 for a, b in zip(self.middle_color, self.full_color)]
        if age > 0.9:
            color = [a * (1.0 - (age-0.9)/0.1) for a in color]
        return color

    def draw_stones(self, level, worm_simulation):
        for stone in level.stones:
            self.draw_stone(stone, worm_simulation)

    def draw_stone(self, stone, worm_simulation):
        pos = self.np_to_screen_coord(stone.position, worm_simulation)
        c_cave = (150, 160, 170)
        pygame.draw.circle(self.screen, c_cave,#self.middle_color,
                           pos, int(stone.radius))

    def draw_one_fish(self, fish, worm_simulation):
        pos = self.np_to_screen_coord(fish.position, worm_simulation)
        pygame.draw.circle(self.screen, self.get_fish_color(fish.energy, fish.age),
                           pos, int(fish.radius))

    def draw_debug_bounces(self, worm, worm_simulation):
        for b in worm.balls:
            for debug_bounce in b.debug_bounces:
                self.draw_debug_bounce(debug_bounce, worm_simulation, b.gripping)
            if not b.gripping:
                b.debug_bounces = []

    def draw_debug_bounce(self, debug_bounce, worm_simulation, gripping):
        if gripping:
            color = self.main_worm_color
        else:
            return
            color = self.shot_score_color
        pos = self.np_to_screen_coord(debug_bounce.position, worm_simulation)
        pygame.draw.circle(self.screen, color,
                           pos, 4)#2)


    def draw_ball(self, ball, worm_simulation):
        pos = self.np_to_screen_coord(ball.position, worm_simulation)
        # pygame.draw.circle(self.screen, (0, 0, 0),
        #                    pos, int(ball.radius))
        # pygame.draw.circle(self.screen, (255, 255, 255),
        #                    pos, int(ball.radius/2))
        pygame.draw.circle(self.screen, (255, 255, 255),
                           pos, int(ball.radius))
        # pygame.gfxdraw.aacircle(self.screen, pos[0], pos[1],
        #                         int(ball.radius/4), (0, 0, 0))
        # pygame.gfxdraw.aacircle(self.screen, pos[0], pos[1],
        #                         int(ball.radius), (0, 0, 0))

    def draw_muscles(self, worm_simulation):
        for m in worm_simulation.worm.muscles:
            self.draw_muscle(m, worm_simulation)

    def draw_grips(self, worm_simulation):
        for m in worm_simulation.worm.muscles:
            self.draw_grip(m, worm_simulation)


    def draw_kicks(self, worm_simulation):
        for f in worm_simulation.worm.fish:
            if f.start_shoot_animation:
                if f.animation_shoot_timer == 0: # if new kick
                    f.animation_foot_dir = np.array([[0.0],[0.0]]) # reset foot position to center
                f.animation_shoot_timer = 11
                f.start_shoot_animation = False
            if f.animation_shoot_timer > 0:
                f.animation_shoot_timer -= 1
                target_dir = normalized(worm_simulation.worm.football.position - f.position) * 15.0
                acc = (target_dir - f.animation_foot_dir) * 0.2
                f.animation_foot_dir += acc
                t = 11.0 - f.animation_shoot_timer
                dist = max(0, 5.0*t - 0.7*t**2)# - 1.0*max(0, t-8.0)**2
                d = normalized(f.animation_foot_dir) * dist
                self.draw_dynamic_fish_part(f.position + d, worm_simulation, 5.0,
                                            self.get_fish_color(f.energy, f.age))



    def draw_grip(self, muscle, worm_simulation):
        a = muscle.b1.position
        b = muscle.b2.position
        delta = muscle.line_segment.delta
        length = np.linalg.norm(delta)
        dir = delta / length
        d = 8.0

        self.draw_dynamic_fish_part(a + dir * d, worm_simulation, 5.0, self.get_fish_color(muscle.b1.energy, muscle.b1.age))
        self.draw_dynamic_fish_part(b - dir * d, worm_simulation, 5.0, self.get_fish_color(muscle.b2.energy, muscle.b2.age))



    def draw_muscle(self, muscle, worm_simulation):
        a = muscle.b1.position
        delta = muscle.line_segment.delta
        length = np.linalg.norm(delta)

        flex = 1.3
        extend = 0.6
        extendedness = length / worm_simulation.worm.max_real_muscle_length
        frac = extend + (flex-extend) * (1.0 - extendedness)

        n = 10

        extra_base = 1.2 * (1.2 + frac)

        r = worm_simulation.worm.balls[0].radius * frac * 0.8
        for i in range(n):
            worm_frac = (i+0.5)/n
            p = a + delta * worm_frac
            extra = extra_base / (0.5 + abs(worm_frac-0.7))
            self.draw_muscle_part(p, worm_simulation, r + extra)

    def draw_muscle_part(self, position, worm_simulation, radius):
        pos = self.np_to_screen_coord(position, worm_simulation)
        pygame.draw.circle(self.screen, self.main_worm_color,
                           pos, int(radius))




    def draw_dynamic_fish(self, fish, worm_simulation):
        if fish.animation_velocity is None:
            fish.animation_velocity = np.array(fish.velocity)
        else:
            acc = (fish.velocity - fish.animation_velocity) * 0.2
            fish.animation_velocity += acc # make the animation smoother on bounces
        a = fish.position - fish.animation_velocity
        delta = fish.animation_velocity
        length = np.linalg.norm(delta)

        flex = 1.0
        extend = 0.6
        extendedness = length / 20.0
        frac = extend + (flex-extend) * (1.0 - extendedness)

        n = 10

        extra_base = 1.2 * (1.2 + frac)

        r = fish.radius * frac * 0.3
        for i in range(n):
            worm_frac = (i+0.5)/n
            p = a + delta * worm_frac
            extra = extra_base / (0.4 + abs(worm_frac-0.85)*abs(worm_frac-0.85))
            self.draw_dynamic_fish_part(p, worm_simulation, r + extra, self.get_fish_color(fish.energy, fish.age))

    def draw_dynamic_fish_part(self, position, worm_simulation, radius, color):
        pos = self.np_to_screen_coord(position, worm_simulation)
        pygame.draw.circle(self.screen, color,
                           pos, max(0, int(radius)))


    def draw_enemy(self, enemy, worm_simulation):
        if not enemy.exploded:
            pos = self.np_to_screen_coord(enemy.position, worm_simulation)
            pygame.draw.rect(self.screen, self.enemy_color, pygame.Rect(pos[0]-enemy.width/2.0, pos[1]-enemy.height/2.0, enemy.width, enemy.height))


    def draw_smoke(self, worm_simulation):
        for particle in worm_simulation.smoke.particles:
            self.draw_smoke_particle(particle, worm_simulation)
        for particle in worm_simulation.smoke.frozen_particles:
            self.draw_smoke_particle(particle, worm_simulation)

    def draw_enemy_smoke(self, worm_simulation, index):
        smoke = worm_simulation.enemy_instances[index].smoke
        for particle in smoke.particles:
            self.draw_smoke_particle(particle, worm_simulation)
        for particle in smoke.frozen_particles:
            self.draw_smoke_particle(particle, worm_simulation)

    def np_to_screen_coord(self, np_vector, worm_simulation):
        if self.who_to_follow is None:
            x = np_vector[0]
            y = np_vector[1]
            view_offset = 0.0
        else:
            if self.who_to_follow == 'main' or self.who_to_follow >= len(worm_simulation.enemy_instances): # follow main robot
                x = np_vector[0] - worm_simulation.worm.get_x()
                y = np_vector[1]
                view_offset = self.view_offset
            else:
                x = np_vector[0] - worm_simulation.enemy_instances[self.who_to_follow].enemy.get_x()
                y = np_vector[1]
                view_offset = self.enemy_view_offset
        return (view_offset + x, y)

    def get_view_offset(self, worm_simulation):
        if self.who_to_follow is None:
            return 0.0
        return self.view_offset if self.who_to_follow == 'main' or self.who_to_follow >= len(worm_simulation.enemy_instances) else self.enemy_view_offset

    def draw_smoke_particle(self, particle, worm_simulation):

        # x = particle.get_left() - worm_simulation.worm.get_x()
        # y = particle.get_top()
        s = pygame.Surface((particle.width, particle.height))  # the size of your rect
        s.set_alpha(int(particle.alpha * 255))
        s.fill(particle.color)
        # self.screen.blit(s, (self.view_offset + x, y))
        x,y = self.np_to_screen_coord(particle.position, worm_simulation)
        pos  = (x - particle.width/2, y - particle.height/2)
        self.screen.blit(s, pos)
        #pygame.draw.rect(self.screen, (255,180,0), pygame.Rect(self.view_offset + x, y, particle.width, particle.height))

    def draw_radars(self, worm_simulation):
        if not worm_simulation.worm.exploded:
            radar_systems = [worm_simulation.radar_system]
            for radar_system in radar_systems:
                for radar in radar_system.radars:
                    point, dist = radar.point, radar.dist
                    if True:#(point,dist) == (None,None):
                        point,dist = radar.read(worm_simulation.worm.position, worm_simulation.level)
                    if True:#dist < 1:
                        dist = 0.5 + dist/2 # for drawing only
                        color = (255, int(150+(255-150)*dist), int(dist*255))
                        pygame.draw.circle(self.screen, color, self.np_to_screen_coord(point, worm_simulation), 5)

    def draw_enemies_radars(self, worm_simulation):
        for ei in worm_simulation.get_living_enemy_instances():
            radar_system = worm_simulation.enemys_radar_system
            for radar in radar_system.radars:
                point, dist = radar.point, radar.dist
                if True:#(point,dist) == (None,None):
                    point,dist = radar.read(ei.enemy.position, worm_simulation.level)
                if True:#dist < 1:
                    dist = 0.5 + dist/2 # for drawing only
                    color = (255, int(150+(255-150)*dist), int(dist*255))
                    pygame.draw.circle(self.screen, color, self.np_to_screen_coord(point, worm_simulation), 5)

    def draw_object_radars(self, worm_simulation):
        if not worm_simulation.worm.exploded:
            self.draw_object_radar(worm_simulation.radar_system.enemy_radar, worm_simulation.worm.position, worm_simulation.get_living_enemy_instances(), (255,80,255), (255,255,255), worm_simulation)

    def draw_fish_object_radars(self, worm_simulation):
        for i,f in enumerate(worm_simulation.worm.fish):
            object_list = list(worm_simulation.worm.fish)
            del object_list[i]
            self.draw_fish_attr_radar(f.radar_system.fish_radar, f.position, object_list, (255,80,255), (255,255,255), worm_simulation)


    def draw_enemy_object_radars(self, worm_simulation):
        for i,ei in enumerate(worm_simulation.enemy_instances):
            enemy = ei.enemy
            if not enemy.exploded:
                self.draw_object_radar(worm_simulation.enemys_radar_system.shot_radar, enemy.position, worm_simulation.shots, (150,80,255), (255,255,255), worm_simulation)
                self.draw_object_radar(worm_simulation.enemys_radar_system.worm_radar, enemy.position,
                                       worm_simulation.get_living_worm_list(), (255, 80, 255), (255, 255, 255), worm_simulation)
                other_enemies = worm_simulation.get_living_enemy_instances(i)
                self.draw_object_radar(worm_simulation.enemys_radar_system.enemy_radar, enemy.position,
                                       other_enemies, (0, 255, 0), (255, 255, 255), worm_simulation)

    def draw_object_radar(self, radar, position, object_list, close_color, far_color, worm_simulation):
        dist_vec = radar.read_dist_vector(position, object_list, worm_simulation.level)
        c_close = np.array(close_color)
        c_far = np.array(far_color)
        c_diff = c_far - c_close
        for i in range(radar.number_of_neurons):
            if dist_vec[i] < 1.0:
                if radar.only_left_half:
                    angle = -(i + 0.5) * radar.angle_slice - np.pi / 2.0
                else:
                    angle = (i + 0.5) * radar.angle_slice - np.pi
                color = c_close + c_diff * dist_vec[i]
                self.draw_circle_at_angle(color, position, dist_vec[i] * 150, angle,
                                          worm_simulation)


    def draw_fish_attr_radar(self, radar, position, object_list, close_color, far_color, worm_simulation):
        dist_vec, attr_vectors = radar.read_dist_vector_and_attribute_vectors(position, object_list, worm_simulation.level)
        x_pos, x_neg, y_pos, y_neg = attr_vectors
        #print attr_vectors
        c_x_pos = np.array((0, 255, 0))
        c_x_neg = np.array((0, 0, 255))
        c_y_pos = np.array((255, 0, 0))
        c_y_neg = np.array((255, 255, 255))
        # c_close = np.array(close_color)
        # c_far = np.array(far_color)
        # c_diff = c_far - c_close
        for i in range(radar.number_of_neurons_per_vector):
            if dist_vec[i] < 1.0:
                if radar.only_left_half:
                    angle = -(i + 0.5) * radar.angle_slice - np.pi / 2.0
                else:
                    angle = (i + 0.5) * radar.angle_slice - np.pi
                color = np.clip(c_x_pos * x_pos[i] + c_x_neg * x_neg[i] + c_y_pos * y_pos[i] + c_y_neg * y_neg[i], 0, 255)
                # color = c_close + c_diff * dist_vec[i]
                self.draw_circle_at_angle(color, position, dist_vec[i] * 150, angle,
                                          worm_simulation)


    def draw_player_box(self, rect, worm_simulation):
        line_fraction = 0.4 # 1.0 = full bounding box ~0 = only a pixel at each corner
        margin = 4
        width = 3
        worm = worm_simulation.worm
        x = np.asscalar(rect.get_position()[0]) -1#-worm.width/4.0
        y = np.asscalar(rect.get_position()[1]) #-worm.width/4.0
        pos = np.array([[x], [y]])
        color = (255, 200, 0)
        radius = rect.width / 2.0 + margin
        line_length = line_fraction * radius
        cornerNW = np.array([[np.asscalar(pos[0]) - radius], [np.asscalar(pos[1]) - radius]])
        cornerNE = np.array([[np.asscalar(pos[0]) + radius], [np.asscalar(pos[1]) - radius]])
        cornerSE = np.array([[np.asscalar(pos[0]) + radius], [np.asscalar(pos[1]) + radius]])
        cornerSW = np.array([[np.asscalar(pos[0]) - radius], [np.asscalar(pos[1]) + radius]])
        lineRight =np.array([[line_length], [0.0]])
        lineDown = np.array([[0.0], [line_length]])
        lineLeft = np.array([[-line_length], [0.0]])
        lineUp =   np.array([[0.0], [-line_length]])
        #print self.np_to_screen_coord(cornerNW + lineDown, worm_simulation)
        pygame.draw.line(self.screen, color, self.np_to_screen_coord(cornerNW + lineDown, worm_simulation), self.np_to_screen_coord(cornerNW, worm_simulation), width)
        pygame.draw.line(self.screen, color, self.np_to_screen_coord(cornerNW + lineRight, worm_simulation), self.np_to_screen_coord(cornerNW, worm_simulation), width)
        pygame.draw.line(self.screen, color, self.np_to_screen_coord(cornerSW + lineUp, worm_simulation), self.np_to_screen_coord(cornerSW, worm_simulation), width)
        pygame.draw.line(self.screen, color, self.np_to_screen_coord(cornerSW + lineRight, worm_simulation), self.np_to_screen_coord(cornerSW, worm_simulation), width)
        pygame.draw.line(self.screen, color, self.np_to_screen_coord(cornerNE + lineDown, worm_simulation), self.np_to_screen_coord(cornerNE, worm_simulation), width)
        pygame.draw.line(self.screen, color, self.np_to_screen_coord(cornerNE + lineLeft, worm_simulation), self.np_to_screen_coord(cornerNE, worm_simulation), width)
        pygame.draw.line(self.screen, color, self.np_to_screen_coord(cornerSE + lineLeft, worm_simulation), self.np_to_screen_coord(cornerSE, worm_simulation), width)
        pygame.draw.line(self.screen, color, self.np_to_screen_coord(cornerSE + lineUp, worm_simulation), self.np_to_screen_coord(cornerSE, worm_simulation), width)



    def unit_dir_vector(self, angle):
        return np.array([[np.cos(angle)],[-np.sin(angle)]])

    def draw_circle_at_angle(self, color, position, dist, angle, worm_simulation):
        p = position + dist * self.unit_dir_vector(angle)
        pygame.draw.circle(self.screen, color, self.np_to_screen_coord(p, worm_simulation), 5)

    def draw_shots(self, worm_simulation):
        for shot in worm_simulation.shots:
            x,y  = self.np_to_screen_coord(shot.position, worm_simulation)
            x = x - shot.width / 2.0
            y = y - shot.height/ 2.0
            pygame.draw.rect(self.screen, (255, 180, 0),
                             pygame.Rect(x, y, shot.width, shot.height))

    def draw_score(self, worm_simulation):
        score_color = (255, 255, 255)
        text_surface = self.score_font.render('Score: %d' % int(worm_simulation.score), False, score_color)
        self.screen.blit(text_surface, (20, 20))

    def add_shot_score_text(self, hitPosition, worm_simulation):
        self.shot_score_texts.append(ScoreText(hitPosition))

    def update_shot_score_texts(self):
        for i,shot_score_text in enumerate(list(self.shot_score_texts)):
            if not shot_score_text.update():
                del self.shot_score_texts[i]


    def draw_shot_score_texts(self, worm_simulation):
        for shot_score_text in self.shot_score_texts:
            self.screen.blit(self.shot_score_surface, self.np_to_screen_coord(shot_score_text.position, worm_simulation))



