import cProfile
import pstats
#import pyximport; pyximport.install(pyimport=True)
from app_ai import App

import random; random.seed(20)

app = App(tetrimino_limit=200)
cProfile.run("app.run()", "profileresults")
profile = pstats.Stats("profileresults")
profile.strip_dirs().sort_stats("time").print_stats()
