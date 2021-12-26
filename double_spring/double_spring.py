from manimlib.imports import *

class Wall(Line):
    CONFIG = {
        "tick_spacing": 0.5,
        "tick_length": 0.25,
        "tick_style": {
            "stroke_width": 1,
            "stroke_color": WHITE,
        },
        "side": "right",
    }

    def __init__(self, height, **kwargs):
        Line.__init__(self, ORIGIN, height * UP, **kwargs)
        self.height = height
        self.ticks = self.get_ticks()
        self.add(self.ticks)

    def get_ticks(self):
        if self.side == "right":
            tick_side = DR
        elif self.side == "left":
            tick_side = DL
        n_lines = int(self.height / self.tick_spacing)
        lines = VGroup(*[
            Line(ORIGIN, self.tick_length * UR).shift(n * self.tick_spacing * UP)
            for n in range(n_lines)
        ])
        lines.set_style(**self.tick_style)
        lines.move_to(self, tick_side)
        return lines

class Mass(Dot):
    def __init__(self, position=0):
        Dot.__init__(self, position, radius=0.2)
        self.acceleration = 0
        self.velocity = 0
        self.position = position

        def update_mass(self, dt):
            self.velocity += self.acceleration * dt
            self.position += self.velocity * dt
            self.move_to(np.array([self.position, 0, 0]))

        self.add_updater(update_mass)
        
    def set_acceleration(self, a):
        self.acceleration = a

class Spring(ParametricFunction):
    CONFIG ={
        "height": 0.5,
        "spacing": 0.2,
        "spring_radius": 0.15,
    }

    def __init__(self, start_obj, end_obj, **kwargs):
        t_max = 6.5
        r = 0.12#self.spring_radius
        s = (2 - r)/(t_max)
        ParametricFunction.__init__(self,
            lambda t : op.add(
                r*(np.sin(TAU*t)*DOWN+np.cos(TAU*t)*RIGHT),
                s*((t_max-t))*RIGHT,
            ),
            t_min = 0, t_max = t_max,
            color = WHITE,
            stroke_width = 2,
        )

        def update_spring(self):
            self.connect_between_points(start_obj.get_right(), end_obj.get_left())

        self.add_updater(update_spring)

    def connect_between_points(self, start, end):
        self.move_to((start + end ) /2)
        self.rotate(Line(start, end).get_angle())
        self.stretch(Line(start, end).get_length()/Line(self.get_left(), self.get_right()).get_length(), 0)

class DoubleSpring(Scene):
    CONFIG = {
        "m": 1,
        "k": 50,
        "x1": 1,
        "x2": 0.2,

        "wall_height": 5,
        "wall_buff": 2,
    }

    def construct(self):
        left_wall = Wall(height=self.wall_height).to_edge(LEFT, buff=self.wall_buff).shift(self.wall_height/2 * DOWN)
        right_wall = Wall(height=self.wall_height, side="left").to_edge(RIGHT, buff=self.wall_buff).shift(self.wall_height/2 * DOWN)

        left_eq_point = left_wall.get_right()[0] / 3
        right_eq_point = right_wall.get_left()[0] / 3

        left_mass = Mass(left_eq_point + self.x1)
        right_mass = Mass(right_eq_point + self.x2)

        left_spring = Spring(left_wall, left_mass)
        middle_spring = Spring(left_mass, right_mass)
        right_spring = Spring(right_mass, right_wall)

        km = self.k / self.m

        def left_mass_updater(self):
            self.set_acceleration(km*((right_mass.get_x()-right_eq_point) - 2*(left_mass.get_x()-left_eq_point)))

        def right_mass_updater(self):
            self.set_acceleration(km*((left_mass.get_x()-left_eq_point) - 2*(right_mass.get_x()-right_eq_point)))

        left_mass.add_updater(left_mass_updater)
        right_mass.add_updater(right_mass_updater)

        self.add(left_wall, right_wall, left_mass, right_mass, left_spring, middle_spring, right_spring)
        self.wait(20)


        
