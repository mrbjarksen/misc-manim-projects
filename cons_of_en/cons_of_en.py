from manimlib.imports import *

class FallBall(Dot):
    CONFIG = {
        "mass": 1,
        "radius": 0.2,
        "acceleration": 9.82 * DOWN,
        "velocity": ORIGIN,
    }

    def start_move(self):
        self.add_updater(self.__class__.make_ball_fall)

    def make_ball_fall(self, dt):
        self.velocity += self.acceleration * dt
        ds = self.velocity * dt
        self.shift(ds)



class ConservationOfEnergy(Scene):
    CONFIG = {
        "g": 9.82,
        "y_at_zero": -2,
        "total_energy_color": GREEN,
        "kinetic_energy_color": RED,
        "potential_energy_color": BLUE,
    }

    def construct(self):
        ball = FallBall(2*UR, acceleration=self.g*DOWN)

        K_tex = TexMobject("K", "=")
        K_tex[0].set_color(self.kinetic_energy_color)
        K_val = ValueTracker().add_updater(lambda k: k.set_value(1/2 * ball.mass * get_norm(ball.velocity)**2))
        K_num = DecimalNumber(unit="N").add_updater(lambda k: k.set_value(K_val.get_value()))
        K = VGroup(K_tex, K_num).arrange()

        U_tex = TexMobject("U", "=")
        U_tex[0].set_color(self.potential_energy_color)
        U_val = ValueTracker().add_updater(lambda u: u.set_value(ball.mass * self.g * (ball.get_y() - self.y_at_zero)))
        U_num = DecimalNumber(unit="N").add_updater(lambda u: u.set_value(U_val.get_value()))
        U = VGroup(U_tex, U_num).arrange()

        E_tex = TexMobject("E", "=")
        E_tex[0].set_color(self.total_energy_color)
        E_val = ValueTracker().add_updater(lambda e: e.set_value(K_val.get_value() + U_val.get_value()))
        E_num = DecimalNumber(unit="N").add_updater(lambda e: e.set_value(E_val.get_value()))
        E = VGroup(E_tex, E_num).arrange()

        energies = VGroup(K, U, E).arrange(DOWN).to_corner(UL, buff=0.8)

        self.add(ball, energies)
        self.wait(2)
        
        ball.start_move()

        self.wait(10)