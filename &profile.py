import cProfile
import pstats
from app_ai import App

import random; random.seed(20)

app = App()
cProfile.run("app.run()", "profileresults")
profile = pstats.Stats("profileresults")
profile.sort_stats("time").strip_dirs().print_stats()
