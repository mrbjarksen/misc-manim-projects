from manimlib.imports import *

class Block(Rectangle):
    CONFIG = {
        "mass": 1,
        "velocity": 1,
        "fill_opacity": 1,
        "stroke_width": 0,
        "label_text": "m",
        "acceleration": 0,
        "velocity": 0,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        height = 1+np.log10(self.mass)
        Rectangle.__init__(self, height=height, width=1.61*height, **kwargs)
        self.label = TexMobject(self.label_text).set_width(0.5*self.height).set_color(BLACK)
        self.add(self.label)

    def set_acceleration(self, a):
        self.acceleration = a
        self.add_updater(self.__class__.update_block)
    
    def update_block(self, dt):
        self.velocity += self.acceleration * dt
        self.shift(self.velocity * dt * RIGHT)


class Spring(ParametricFunction):
    CONFIG ={
        "unstretched_length": 2,
        "stretch_about": LEFT,
        "stiffness": 100,
        "dampening": 0.5,
        "mass": 0.1,
        "acceleration": 0,
        "velocity": 0,
        "displacement": 0,
    }

    def __init__(self, **kwargs):
        t_max = 8.5
        r = 0.1
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
        self.stretch_to_fit_width(self.unstretched_length + self.displacement, about_edge=self.stretch_about)

    def release(self):
        self.add_updater(self.__class__.update_spring)

    def update_spring(self, dt):
        self.acceleration = (-self.stiffness * self.displacement - self.dampening * self.velocity) / self.mass
        self.velocity += self.acceleration * dt
        self.displacement += self.velocity * dt
        self.stretch_to_fit_width(self.unstretched_length + self.displacement, about_edge=self.stretch_about)

    def set_displacement(self, displacement):
        self.displacement = displacement
        self.stretch_to_fit_width(self.unstretched_length + self.displacement, about_edge=self.stretch_about)


class SpringEnergy(Scene):
    CONFIG = {
        "compress_by": 1,
        "friction": 0.2,
        "distance_to_gate": 10,
        "spring_length": 2,
    }

    def construct(self):
        wall = Line(5*LEFT + 2*DOWN, 5*LEFT + 4*UP)
        floor = Line(5*LEFT + 2*DOWN, 8*RIGHT + 2*DOWN)
        block = Block().move_to(wall.get_start() + (self.spring_length + 0.5)*RIGHT, aligned_edge=DL)
        spring = Spring(unstretched_length=self.spring_length).move_to(wall.get_start() + (block.height/2)*UP, aligned_edge=LEFT)
        hand = SVGMobject(
            "/Users/bjarkibharksen/Documents/manim/projects/springenergy/hand.svg",
            stroke_width=0.1
        ).scale(0.5).rotate(PI/2).next_to(block, buff=0)
        gate = Circle(color=WHITE).stretch_to_fit_width(0.1).stretch_to_fit_height(2*block.height)
        gate.move_to(min(5, self.distance_to_gate + spring.get_right()[0])*RIGHT + 2.02*DOWN, aligned_edge=DOWN)

        distance_brace = BraceLabel(
            Line(
                spring.get_right()[0]*RIGHT + floor.get_y()*UP,
                gate.get_center()[0]*RIGHT + floor.get_y()*UP
            ),
            "\\SI{%s}{m}" % self.distance_to_gate,
            buff=0.08
        )
        distance_brace.brace.stretch_to_fit_height(0.15)
        distance_brace.label.scale(0.75).shift(0.2*UP)

        compression_brace = Brace(
            Line(
                spring.get_right()[0]*RIGHT + floor.get_y()*UP,
                (spring.get_right()[0] - self.compress_by)*RIGHT + floor.get_y()*UP
            ),
            buff=0.08
        )
        compression_brace.stretch_to_fit_height(0.15)

        self.add(wall, floor, spring, block, distance_brace)
        self.add_foreground_mobject(gate)
        self.wait(2)

        self.play(FadeInFrom(hand, 0.2*UP))

        def spring_compressor(spr):
            spr.set_displacement(min(0, block.get_left()[0]-spr.get_end()[0]-spr.unstretched_length))

        def brace_expander(brace):
            brace.stretch_to_fit_width(max(0.01, -spring.displacement), about_edge=RIGHT)

        spring.add_updater(spring_compressor)
        self.add(compression_brace)
        compression_brace.add_updater(brace_expander)

        self.wait(0.5)
        self.play(ApplyMethod(VGroup(block, hand).shift, (self.compress_by+0.5)*LEFT), run_time=3)
        spring.remove_updater(spring_compressor)
        compression_brace.remove_updater(brace_expander)

        force_tex = TexMobject("F = \\SI{%s}{N}" % (0.5 * spring.stiffness * self.compress_by**2))
        force_tex.scale(0.75).next_to(block.get_corner(UL), UP, aligned_edge=LEFT)
        compression_tex = TexMobject("\\SI{%s}{m}" % self.compress_by)
        compression_tex.scale(0.75).move_to(compression_brace.get_x()*RIGHT + distance_brace.label.get_y()*UP)
        self.wait(1)
        self.play(
            FadeInFrom(force_tex, 0.2*DOWN),
            FadeInFrom(compression_tex, 0.2*UP),
            run_time=1.5
        )
        self.wait(2)

        spring.mass += block.mass
        dampening = spring.dampening
        spring.dampening = 0

        def block_mover_from_spring(b):
            b.move_to(spring.get_start(), aligned_edge=LEFT)
        
        def block_released():
            return spring.displacement >= 0

        def block_stopped():
            return block.velocity <= 0

        def block_passed_gate():
            return block.get_right()[0] >= gate.get_x()

        self.remove(hand)
        spring.release()
        block.add_updater(block_mover_from_spring)
        self.wait_until(block_released)
        block.remove_updater(block_mover_from_spring)
        block.velocity = math.sqrt(spring.stiffness/block.mass) * self.compress_by
        block.set_acceleration(-self.friction * block.mass * 9.82)
        spring.mass -= block.mass
        spring.dampening = dampening
        self.wait_until(block_passed_gate, max_time=5)

        v_tex = TexMobject(
            "v = \\SI{%s}{m/s}" 
            % round(math.sqrt(
                    spring.stiffness/block.mass * self.compress_by**2 - 2*self.friction*9.82*(self.compress_by+self.distance_to_gate)
                ), 2)
        ).scale(0.75).next_to(gate, LEFT).set_y(force_tex.get_y())
        self.play(FadeInFrom(v_tex, 0.5*RIGHT), run_time=1.5)

        self.wait_until(block_stopped, max_time=3)