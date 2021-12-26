from manimlib.imports import *

class FallingWire(Scene):
    def construct(self):
        B = lambda y: np.exp(y)
        l, m, R, g = 1, 1, 1, 9.82
        wire = Square(side_length=l)
        wire.y, wire.v, wire.a = 0, 0, 0
        def update_wire(w, dt):
            w.a = g - (l**2)/(m*R) * (B(w.y+l) - B(w.y))**2 * w.v
            w.v += w.a * dt
            w.y += w.v * dt
            w.move_to(w.y*DOWN, aligned_edge=UP)
        wire.add_updater(update_wire)
        self.add(wire)
        self.wait(10)