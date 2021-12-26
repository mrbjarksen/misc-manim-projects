from manimlib.imports import *
from manimlib.constants import GREY_BROWN

class Block(Square):
    CONFIG = {
        "mass": 1,
        "velocity": 1,
        "fill_opacity": 1,
        "stroke_width": 0,
        "label_text": "m",
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        Square.__init__(self, side_length=1+np.log10(self.mass), **kwargs)
        self.label = TexMobject(self.label_text).set_width(0.5*self.side_length).set_color(BLACK)
        self.add(self.label)


class Trissa(VMobject):
    CONFIG = {
        "inner_radius": 0.1,
        "outer_radius": 0.3,
    }

    def __init__(self, position, corner, **kwargs):
        VMobject.__init__(self, **kwargs)
        wheel = AnnularSector(angle=TAU, **kwargs).move_to(position)
        connector = Line(corner, position)
        connector.scale(1 - (self.outer_radius / connector.get_length()), about_point=corner)
        self.add(connector, wheel)


class TrissuRope(VMobject):
    CONFIG = {
        "color": GREY_BROWN,
        "stroke_width": 10,
        "acceleration": 0,
        "velocity": 0,
    } 

    def __init__(self, start, end, arc_radius, **kwargs):
        digest_config(self, kwargs)
        VMobject.__init__(self, **kwargs)
        corner = start[1] * UP + end[0] * RIGHT
        self.horz_part = Line(start, corner - (arc_radius*RIGHT), **kwargs)
        self.vert_part = Line(corner - (arc_radius*UP), end, **kwargs)
        self.connector = ArcBetweenPoints(
            self.horz_part.get_end(), 
            self.vert_part.get_start(), 
            angle=-PI/2,
            **kwargs
        )
        self.add(self.horz_part, self.connector, self.vert_part)
        self.set_stroke(self.color, 10)
        self.add_updater(self.__class__.update_positions)

    def update_positions(self, dt):
        self.velocity += self.acceleration * dt
        dx = self.velocity * dt
        self.horz_part.put_start_and_end_on(
            self.horz_part.get_start() + dx * RIGHT,
            self.horz_part.get_end()
        )
        self.vert_part.put_start_and_end_on(
            self.vert_part.get_start(),
            self.vert_part.get_end() + dx * DOWN
        )

    def get_start(self):
        return self.horz_part.get_start()

    def get_end(self):
        return self.vert_part.get_end()

    def set_acceleration(self, a):
        self.acceleration = a


class TrissuSystem(VMobject):
    CONFIG = {
        "block1_config": {
            "mass": 5,
            "label_text": "m_1",
            "position": 5*LEFT + 1*UP,
        },
        "block2_config": {
            "mass": 3,
            "label_text": "m_2",
            "position": 4.5*RIGHT + DOWN,
        },
        "trissa_config": {
            "inner_radius": 0.1,
            "outer_radius": 0.3,
        },
        "table_config": {
            "width": 16,
            "height": 10,
            "space_from_block2": 0.5
        },
        "acceleration": 0,
        "gravity": 9.82,
        "friction": 0.25
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        VMobject.__init__(self, **kwargs)
        self.block1 = Block(**self.block1_config)
        self.block1.move_to(self.block1.position, aligned_edge=DR)
        self.block2 = Block(**self.block2_config)
        self.block2.move_to(self.block2.position, aligned_edge=LEFT)

        trissa_radius = self.trissa_config["outer_radius"]
        trissa_center = (self.block1.get_y()-trissa_radius) * UP + (self.block2.get_x()-trissa_radius) * RIGHT
        self.table_corner = self.block1.get_y(DOWN) * UP + (self.block2.get_x(LEFT) - self.table_config["space_from_block2"]) * RIGHT

        trissa = Trissa(trissa_center, self.table_corner, **self.trissa_config)
        self.rope = TrissuRope(
            self.block1.get_center(),
            self.block2.get_center(),
            trissa_radius,
            **kwargs
        )
        self.rope.set_acceleration(self.get_acceleration())

        table = Rectangle(**self.table_config).move_to(self.table_corner, aligned_edge=UR)

        self.block1.add_updater(lambda b: b.move_to(self.rope.get_start()))
        self.block2.add_updater(lambda b: b.move_to(self.rope.get_end()))

        self.add(self.rope, self.block1, self.block2, table, trissa)

    def get_acceleration(self):
        m1, m2, g, mu = self.block1.mass, self.block2.mass, self.gravity, self.friction
        return (m2 - mu*m1)*g/(m1 + m2)

    def get_distance_travelled(self):
        return self.block1.get_corner(DR)[0] - self.block1.position[0]

    def has_hit_end(self, buff=0.1):
        return self.get_distance_travelled() >= self.table_corner[0] - self.block1.position[0] - buff


class LodIHengsli(Scene):
    def construct(self):
        self.system = TrissuSystem()
        self.legend = self.get_legend(self.system)
        self.add(self.system, self.legend)
        self.wait_until(self.system.has_hit_end)

    def get_legend(self, system):
        legend = VGroup()
        m1_label = TexMobject(system.block1.label_text, "=", "\\SI{%s}{kg}" % system.block1.mass)
        m2_label = TexMobject(system.block2.label_text, "=", "\\SI{%s}{kg}" % system.block2.mass)
        v_tex = TexMobject("v = ")
        v_num = DecimalNumber(0, unit="\\si{m/s}").add_updater(lambda v: v.set_value(system.rope.velocity))
        v_label = VGroup(v_tex, v_num).arrange()
        s_tex = TexMobject("s = ")
        s_num = DecimalNumber(0, unit="\\si{m}").add_updater(lambda s: s.set_value(system.get_distance_travelled()))
        s_label = VGroup(s_tex, s_num).arrange()
        col = VGroup(m1_label, m2_label, v_label, s_label).arrange(DOWN, aligned_edge=LEFT)
        legend.add(col)
        legend.scale(0.8)
        legend.move_to((system.block1.get_y(DOWN) - 0.5) * UP + (FRAME_X_RADIUS - 0.5) * LEFT, aligned_edge=UL)
        return legend