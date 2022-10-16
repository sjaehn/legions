import random


class Map:
    def __init__(self, size, min_value, max_value):
        self.width, self.height = size
        random.seed()

        track = None
        while track is None:
            # Generate a start point
            self.start = (random.randint(0, size[0] - 1), random.randint(0, size[1] - 1))

            # Generate a track
            track = self.generate_track([self.start])

        print("Start: ", self.start)
        print("Track: ", track)

        # Generate value map
        values = self.generate_values(min_value, max_value)
        print("Values: ", values)

        # Sort value map
        chain_start = values[2]
        values.remove(chain_start)
        chain = self.generate_chain([(1, 1)], [chain_start])
        print("Values: ", values)
        print("Chain start: ", chain_start)
        print("Chain: ", chain)

        # Build map
        self.map = None

        if (track is not None) and (chain is not None):
            self.map = [[(0, 0)] * size[0] for i in range(size[1])]
            for i in range(len(track)):
                x, y = track[i]
                self.map[x][y] = chain[i]

    def generate_track(self, track):
        if len(track) == self.width * self.height:
            return track

        x, y = track[-1]
        neighbors = []
        if (x > 0) and (x - 1, y) not in track:
            neighbors.append((x - 1, y))
        if (x < self.width - 1) and (x + 1, y) not in track:
            neighbors.append((x + 1, y))
        if (y > 0) and (x, y - 1) not in track:
            neighbors.append((x, y - 1))
        if (y < self.height - 1) and (x, y + 1) not in track:
            neighbors.append((x, y + 1))

        random.shuffle(neighbors)

        for n in neighbors:
            nt = track.copy()
            nt.append(n)
            new_track = self.generate_track(nt)

            if new_track is not None:
                return new_track

        return None

    def generate_chain(self, in_values, out_values):
        if len(out_values) == self.width * self.height:
            return out_values

        v = sum(x[0] * x[1] for x in out_values)

        iv = in_values.copy()
        ol = len(out_values)
        for i in range(ol):
            item = (i + 1, ol + 1)
            iv.append(item)

        iv.sort(key=lambda x: x[0] * x[1])

        ins = []
        for i in iv:
            if i[0] * i[1] < v:
                ins.append(i)
            else:
                break
        random.shuffle(ins)

        for i in ins:
            iv.remove(i)
            ov = out_values.copy()
            ov.append(i)

            new_values = self.generate_chain(iv, ov)

            if new_values is not None:
                return new_values

        return None

    def generate_values(self, min_factor, max_factor):
        v_list = []

        for i in range(min_factor, max_factor + 1):
            for j in range(min_factor, i + 1):
                v_list.append((i, j))

        v_list.sort(key=lambda x: x[0] * x[1])
        return v_list

