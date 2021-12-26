from manimlib.imports import *


class Slope(FunctionGraph):
    CONFIG = {
        "color": WHITE,
        "ratio_for_zero": 1, # float that denotes where the point at zero should be, with 0 being at the left edge and 1 being at the right edge
    }

    def __init__(self, function, length=1, **kwargs):
        digest_config(self, kwargs)

        self.x_range = {
            "x_min": -self.ratio_for_zero * length,
            "x_max": (1-self.ratio_for_zero) * length,
        }

        FunctionGraph.__init__(self, function, **self.x_range, **kwargs)

class SlopeFromPoints(Slope):
    CONFIG = {
        "color": WHITE,
        "connector_function": lambda x: math.sin(PI * (x - 1/2)),
        "connector_function_interval": [0, 1],
    }

    def __init__(self, points, **kwargs):
        digest_config(self, kwargs)

        func = lambda x: self.gen_func_from_points(points, x)
        x_min, x_max = min(*[p[0] for p in points]), max(*[p[0] for p in points])
        length = x_max - x_min
        rfz = -x_min / length

        Slope.__init__(self, func, length, ratio_for_zero=rfz, **kwargs)


    def gen_func_from_points(self, points, x):
        # TODO, 
        # - laga fyrir punkta sem eru ekki í réttri röð (+ duplicate x hnit?)
        # - laga fyrir föll sem hafa sömu gildi í endapunktum

        i = 0
        while points[i][0] < x:
            i += 1
        left_point, right_point = points[i-1], points[i]

        connector_length = self.connector_function_interval[1] - self.connector_function_interval[0]
        connector_height = self.connector_function(self.connector_function_interval[1]) - self.connector_function(self.connector_function_interval[0])

        scale_x = connector_length / (right_point[0] - left_point[0])
        scale_y = (right_point[1] - left_point[1]) / connector_height if connector_height != 0 else 1

        return scale_y * self.connector_function(scale_x * (x - left_point[0]) + self.connector_function_interval[0]) + (left_point[1] - scale_y * self.connector_function(self.connector_function_interval[0]))


class RollingBall(Dot):
    CONFIG = {
        "radius": 0.2, 
        "mass": 1,
        "initial_acceleration": np.array([0, 0, 0]),
        "initial_velocity": np.array([0, 0, 0]),
        "initial_position": ORIGIN,
    }

    def __init__(self, **kwargs):
        digest_config(self, kwargs)
        Dot.__init__(self, **kwargs)
        self.forces = [np.array([0, -9.8, 0])]
        self.acceleration = self.initial_acceleration
        self.velocity = self.initial_velocity
        self.position = self.initial_position
        self.moment_of_inertia = 0.5 * self.mass * self.radius ** 2

        def update_position(self, dt):
            self.acceleration = sum(self.forces) / self.mass
            self.velocity = self.velocity + self.acceleration * dt
            self.position = self.position + self.velocity * dt

        self.add_updater(update_position)

    def get_total_force(self):
        total = np.array([0, 0, 0])
        for f in self.forces:
            total = total + f
        return total

    def update_forces(self, forces):
        self.forces = forces



class ConservationOfEnergy(Scene):
    CONFIG = {
        "mass": 1,
        "gravitational_acceleration": 9.82,
    }

    def construct(self):
        point_list = [
            np.array([0, 7, 0]),
            np.array([1, 7, 0]),
            np.array([3, 3, 0]),
            np.array([4.3, 4, 0]),
            np.array([5.7, 4, 0]),
            np.array([7, 5, 0]),
            np.array([8, 3.5, 0]),
            np.array([9, 3.5, 0]),
        ]
        slope = SlopeFromPoints(point_list)

        # func = lambda t: 0.08*t**2
        # slope = Slope(func, 8)

        #slope.to_corner(DL, buff=LARGE_BUFF)
        #test = VMobject().set_points_smoothly(point_list).to_corner(DL, buff=LARGE_BUFF).set_color(RED)

        slope_and_points = VGroup(slope, *[Dot(p, radius=DEFAULT_DOT_RADIUS*0.8)for p in point_list]).to_corner(DL, buff=LARGE_BUFF-0.08)

        self.play(ShowCreation(slope_and_points), run_time=2.5)
        #self.play(ShowCreation(test), run_time=2.5

        # ball = RollingBall(mass=self.mass).to_edge(TOP)
        # self.add(ball)
        
        # mg = self.mass * self.gravitational_acceleration
        # ball_forces = {
        #     "gravity": np.array([0, -mg, 0]),
        # }

        # ball.update_forces(ball_forces.values())
        # self.wait(5)