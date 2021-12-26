from manimlib.imports import *

class Kefli(MovingCameraScene):
    def construct(self):
        circle = Circle(radius=1, color=WHITE)
        P = Dot(color=GRAY)
        P.next_to(circle, RIGHT, buff=0)
        rope = Line(color=GRAY)
        path = VMobject(color=RED)
        path.set_points_as_corners([P.get_center(), P.get_center()+UP*0.001])
        t_val = ValueTracker(0.01)

        m = 20.371
        curve = ParametricFunction(
            lambda t: np.array([
                    np.cos(t)+t*np.sin(t), 
                    np.sin(t)-t*np.cos(t), 
                    0
                ]),
            t_min=0,
            t_max=m,
            color=RED
        )
        
        self.add_foreground_mobjects(circle, P)
        self.add(rope)

        def update_rope(r):
            t = t_val.get_value()
            r.put_start_and_end_on(
                np.array([
                    np.cos(t), 
                    np.sin(t), 
                    0
                ]), 
                np.array([
                    np.cos(t)+t*np.sin(t), 
                    np.sin(t)-t*np.cos(t), 
                    0
                ])
            )

        def update_P(p):
            p.move_to(rope.get_end())
        
        rope.add_updater(update_rope)
        P.add_updater(update_P)
        self.play(
            ApplyMethod(t_val.set_value, m),
            AnimationGroup(
                ApplyMethod(self.camera_frame.set_width, 70)
            ),
            ShowCreation(curve),
            rate_func=linear,
            run_time=25,
        )