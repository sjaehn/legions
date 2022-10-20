import math
import random


def generate_values(min_factor, max_factor):
    v_list = []

    for i in range(min_factor, max_factor + 1):
        for j in range(min_factor, i + 1):
            v_list.append((i, j))

    v_list.sort(key=lambda x: x[0] * x[1])
    return v_list


class Map:
    def __init__(self, size, min_value, max_value):
        self.width, self.height = size
        random.seed()

        print("Create map", self.width, "x", self.height)

        track = None
        while track is None:
            # Clear map
            self.map = [[(1, 1)] * size[0] for _ in range(size[1])]
            print("Init")

            # Seed barriers
            min_barriers = (self.width - 4) * (self.height - 4)
            max_barriers = (self.width - 2) * (self.height - 2)
            nr_barriers = random.randint(min_barriers, max_barriers)
            for i in range(nr_barriers):
                succeed = False
                x = 0
                y = 0

                while not succeed:
                    x = random.randint(1, self.width - 2)
                    y = random.randint(1, self.height - 2)

                    # Less likely: barriers on border
                    if random.randint(0, 4) == 0:
                        x = random.randint(0, self.width - 1)
                        y = random.randint(0, self.height - 1)

                    succeed = True
                    if ((x > 0) and (not self.contains_legion((x - 1, y)))) or \
                            ((x < self.width - 1) and (not self.contains_legion((x + 1, y)))) or \
                            ((y > 0) and (not self.contains_legion((x, y - 1)))) or \
                            ((y < self.height - 1) and (not self.contains_legion((x, y + 1)))):
                        succeed = False

                b_idx = random.randint(0, 3)
                self.map[x][y] = (b_idx, 0)
                print("Barrier:", x, y)

            # Generate a start point
            self.start = None
            while self.start is None or not self.contains_legion(self.start):
                self.start = (random.randint(0, size[0] - 1), random.randint(0, size[1] - 1))

            print("Start:", self.start)

            # Generate a track
            track = self.generate_track([self.start])

        print("Start: ", self.start)
        print("Track: ", track)

        # Generate value map
        values = generate_values(min_value, max_value)
        print("Values: ", values)

        # Sort value map
        sidx = random.randint(2, 2 + int(math.sqrt(len(values) - 1)))
        chain_start = values[sidx]
        values.remove(chain_start)
        chain = self.generate_chain2(values, [chain_start])
        print("Values: ", values)
        print("Chain start: ", chain_start)
        print("Chain: ", chain)

        # Build map
        if (track is not None) and (chain is not None):
            for i in range(len(track)):
                x, y = track[i]
                self.map[x][y] = chain[i]

        else:
            self.map = None

    def generate_track(self, track):
        if len(track) == self.count_legions():
            return track

        x, y = track[-1]
        neighbors = []
        if (x > 0) and ((x - 1, y) not in track) and self.contains_legion((x - 1, y)):
            neighbors.append((x - 1, y))
        if (x < self.width - 1) and ((x + 1, y) not in track) and self.contains_legion((x + 1, y)):
            neighbors.append((x + 1, y))
        if (y > 0) and ((x, y - 1) not in track) and self.contains_legion((x, y - 1)):
            neighbors.append((x, y - 1))
        if (y < self.height - 1) and ((x, y + 1) not in track) and self.contains_legion((x, y + 1)):
            neighbors.append((x, y + 1))

        random.shuffle(neighbors)

        for n in neighbors:
            nt = track.copy()
            nt.append(n)
            new_track = self.generate_track(nt)

            if new_track is not None:
                return new_track

        return None

    def generate_chain2(self, values, primer):
        chain = primer.copy()
        vals = values.copy()
        lvalue = values[-1]
        lscore = lvalue[0] * lvalue[1]
        pvalue = primer[0]
        pscore = pvalue[0] * pvalue[1]
        field_size = self.count_legions()

        # Count score of chain
        score = sum(x[0] * x[1] for x in chain)

        # Generate chain
        while len(chain) < field_size:
            # Score of the max allowed value
            f = 0.25 + (0.25 + 2.0 * len(chain) / field_size) * random.random()
            mscore = pscore + f * (len(chain) - 1) * (lscore - pscore) / (field_size - 1) - (score - pscore)

            if mscore >= score:
                mscore = score - 1.0

            # Index of the max allowed value
            midx = 0
            for vi in vals:
                si = vi[0] * vi[1]
                if si <= mscore:
                    midx += 1

                else:
                    break

            if midx > 0:
                midx = midx - 1

            idx = random.randint(0, midx)
            if random.randint(0, 9) == 0:
                idx = random.randint(int(0.8 * midx), midx)

            v = vals[idx]
            print(score, mscore, midx, v[0] * v[1])
            chain.append(v)
            score += v[0] * v[1]
            vals.remove(v)

        return chain

    def force_level(self, pos):
        """
        Calculates the force level of the legion in the field provided by pos.
        :param pos: position of the field
        :return: Force level of the legion in the field provided by pos. 0 if there's no legion there.
        """

        x, y = pos
        if self.map[x][y] is None:
            return 0
        else:
            return self.map[x][y][0] * self.map[x][y][1]

    def contains_legion(self, pos):
        """
        Checks if there is a legion o a field provided by pos.

        :param pos: position of the field to check
        :return: True if there is a legion o a field provided by pos. Otherwise False.
        """

        return self.force_level(pos) > 0

    def count_legions(self):
        """
        Counts the number of remaining other legions.
        :return: number of remaining other legions
        """

        if self.map is None:
            return 0

        count = 0
        for x in range(self.width):
            for y in range(self.height):
                if self.contains_legion((x, y)):
                    count += 1

        return count

    def is_empty(self):
        """
        Checks if there are any (other) legions on the map.

        :return: True if there are any (other) legions on the map. Otherwise False.
        """

        return self.count_legions() <= 1

    def has_neighbors(self, pos):
        """
        Checks if there are legions next to the field pos.

        :param pos: position
        :return: True if there are legions next to the field pos. Otherwise False.
        """

        x, y = pos
        if (x >= 1) and (self.contains_legion((x - 1, y))) and (self.force_level((x - 1, y)) > 0):
            return True
        if (x < self.width - 1) and (self.contains_legion((x + 1, y))) and (
                self.force_level((x + 1, y)) > 0):
            return True
        if (y >= 1) and (self.contains_legion((x, y - 1))) and (self.force_level((x, y - 1)) > 0):
            return True
        if (y < self.height - 1) and (self.contains_legion((x, y + 1))) and (
                self.force_level((x, y + 1)) > 0):
            return True
        return False
