from game import Game

BOARD_SIZE = (10, 20)

WEIGHTS = [-200, 1000, -3000, -10]

def sleep_forever():
    while True: pass
    
class App(Game):
    def __init__(self, *, board_size=BOARD_SIZE, tetrimino_limit=-1, weights=WEIGHTS):
        super().__init__(*board_size)
        self.tetrimino_limit = tetrimino_limit
        self.weights = WEIGHTS

    def run(self):
        done = False
        while not done:
            #New falling tetrimino
            if self.ftetrimino is None:
                status = self.handle_new_falling_tetrimino()
                if status == "game_over":
                    self.game_over()
                    break
                try:
                    self.ai_compute_outcomes(self.weights)
                except ValueError:
                    self.game_over()
                    break
                #Moving & Rotating
                self.ai_move()

            #Gravity
            status = self.handle_gravity()
            if status == "game_over":
                self.game_over()
                break
            
            #Check for full lines
            if self.just_placed_tetrimino:
                self.check_for_full()
                self.just_placed_tetrimino = False
                if self.dropped_tetriminos == self.tetrimino_limit:
                    #print("Reached tetrimino limit: ", self.tetrimino_limit)
                    self.game_over()
                    break

    def game_over(self):
        pass
        #print("Game over")
        #print("Score: {0}".format(self.score))
        #print("Board:")
        #self.board.pprint()
        #print("Mask:")
        #for row in self.board.mask:
        #    print([0 if elem else 1 for elem in row])



if __name__ == "__main__":
    app = App()
    app.run()
    #scores = []
    #tries = 1
    #for i in range(tries):
    #    print("Try", i)
    #    app = App()
    #    app.run()
    #    scores.append(app.score)
    #print("Average:", sum(scores) / len(scores))
