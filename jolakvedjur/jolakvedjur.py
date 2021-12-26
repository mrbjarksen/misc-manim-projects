from fourier import FourierFromSVG
from manimlib.imports import *

class Gjafabref(Scene):
    def construct(self):
        congrats = TextMobject("Congratulations!")
        congrats.scale(1.5).set_color(YELLOW).to_edge(UP, buff=LARGE_BUFF)
        yay = TextMobject("You have won a lifetime supply of \\textit{Manim} videos \\\\ for personal, commercial or educational use!")
        redemption = TextMobject("To redeem your reward, speak to your \\\\ local \\textit{Manim} manufacturer.")
        redemption.next_to(yay, DOWN)
        VGroup(yay, redemption).center()

        self.play(FadeInFromDown(congrats))
        self.wait()
        self.play(Write(yay))
        self.wait(0.5)
        self.play(Write(redemption))
        self.wait()


class Heart(FourierFromSVG):
    CONFIG = {
        "n_vectors": 100,
        "n_cycles": 2,
        "file_name": "heart",
        "drawn_path_color": RED,
        "drawn_path_stroke_width": 10,
    }