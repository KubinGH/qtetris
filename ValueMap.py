class ValueMap:
    def __init__(self, lower_bound, upper_bound, lower_accept, upper_accept):
        self.lower_bound, self.upper_bound = lower_bound, upper_bound
        self.lower_accept, self.upper_accept = lower_accept, upper_accept

        self.delta_bound = self.upper_bound - self.lower_bound
        self.delta_accept = self.upper_accept - self.lower_accept
        self.ratio = self.delta_bound / self.delta_accept

    def __repr__(self):
        return "ValueMap({0}, {1}, {2}, {3})".format(self.lower_bound, self.upper_bound,
                                                     self.lower_accept, self.upper_accept)

    def __getitem__(self, key):
        return self.lower_bound + ((key - self.lower_accept) * self.ratio)
    
    
if __name__ == "__main__":
    vmap1 = ValueMap(1, 3, 1, 100)
    for i in range(1, 101):
        print(vmap1[i])
