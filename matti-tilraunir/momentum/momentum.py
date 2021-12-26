from manimlib.imports import *

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


class CollidingBlocks(VGroup):
    CONFIG = {
        "block1_config": {
            "mass": 3.5,
            "velocity": 1,
            "label_text": "m_1",
        },
        "block2_config": {
            "mass": 1,
            "velocity": -0.5,
            "label_text": "m_2",
        },
        "coefficient_of_restitution": 0.75,
    }

    def __init__(self, **kwargs):
        VGroup.__init__(self, **kwargs)
        self.block1 = Block(**self.block1_config)
        self.block1.move_to(-7*RIGHT + 2*DOWN, DR)
        self.block2 = Block(**self.block2_config)
        self.block2.move_to((self.block2.velocity/self.block1.velocity)*(-7)*RIGHT + 2*DOWN, DL)
        self.add(self.block1, self.block2)
        self.collided = False
        self.add_updater(self.__class__.update_positions)

    def update_positions(self, dt):
        m1, m2 = self.block1.mass, self.block2.mass
        v1, v2 = self.block1.velocity, self.block2.velocity
        x1, x2 = self.block1.get_edge_center(RIGHT)[0], self.block2.get_edge_center(LEFT)[0]
        C_R = self.coefficient_of_restitution

        self.block1.shift(v1*dt*RIGHT)
        self.block2.shift(v2*dt*RIGHT)

        if x1 >= x2-0.01 and not self.collided:
            self.block1.velocity = (m1*v1 + m2*v2 + m2*C_R*(v2-v1))/(m1 + m2)
            self.block2.velocity = (m1*v1 + m2*v2 + m1*C_R*(v1-v2))/(m1 + m2)
            self.collided = True


class ConservationOfMomentum(Scene):
    def construct(self):
        self.blocks = CollidingBlocks()
        self.floor = Line(10*LEFT+2*DOWN, 10*RIGHT+2*DOWN)
        self.legend = self.get_legend(self.blocks)
        self.add(self.blocks, self.floor, self.legend)
        def collided():
            return self.blocks.collided
        self.wait_until(collided)
        self.add_u_to_legend(self.blocks)
        self.wait(10)

    def get_legend(self, blocks):
        legend = VGroup()
        m1_label = TexMobject(blocks.block1.label_text, "=", "\\SI{%s}{kg}" % blocks.block1.mass)
        m2_label = TexMobject(blocks.block2.label_text, "=", "\\SI{%s}{kg}" % blocks.block2.mass)
        v1_label = TexMobject("v_1", "=", "\\SI{%s}{m/s}" % blocks.block1.velocity)
        v2_label = TexMobject("v_2", "=", "\\SI{%s}{m/s}" % blocks.block2.velocity)
        # C_R_label = TexMobject("C_R", "=", "\\num{%s}" % blocks.coefficient_of_restitution)
        left_col = VGroup(m1_label, m2_label).arrange(DOWN, aligned_edge=LEFT)
        right_col = VGroup(v1_label, v2_label).arrange(DOWN, aligned_edge=LEFT)
        right_col.next_to(left_col, aligned_edge=UP, buff=LARGE_BUFF)
        legend.add(left_col, right_col)
        legend.scale(0.8)
        legend.to_corner(UL)
        return legend

    def add_u_to_legend(self, blocks):
        to_col = VGroup(TexMobject("\\to"), TexMobject("\\to"))
        to_col.scale(0.8).arrange(DOWN, aligned_edge=LEFT).next_to(self.legend, buff=0.7)
        u1_label = TexMobject("u_1", "=", "\\SI{%s}{m/s}" % round(blocks.block1.velocity, 2))
        u2_label = TexMobject("u_2", "=", "\\SI{%s}{m/s}" % round(blocks.block2.velocity, 2))
        u_col = VGroup(u1_label, u2_label)
        u_col.scale(0.8).arrange(DOWN, aligned_edge=LEFT).next_to(to_col, buff=0.7)
        self.legend.add(to_col, u_col)
        self.play(AnimationGroup(
            FadeInFrom(to_col, 0.3*LEFT), FadeInFrom(u_col, 0.2*LEFT),
            lag_ratio=0.05
        ))
