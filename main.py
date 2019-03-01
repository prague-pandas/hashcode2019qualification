#!/usr/bin/env python3

import argparse
import random
import io


class Photo:
    def __init__(self, i, line):
        self.i = i
        words = line.split()
        assert (words[0] in ['H', 'V'])
        self.vertical = words[0] == 'V'
        self.tags = words[2:]

    def __str__(self):
        return f'{self.i} {self.vertical} {self.tags}'


class Instance:
    def __init__(self, infile):
        self.name = infile.name
        N = int(next(infile))
        self.photos = []
        for i, line in zip(range(N), infile):
            self.photos.append(Photo(i, line))

    def __str__(self):
        return str(list(map(str, self.photos)))

    def solve(self):
        solution = Solution(self)
        cache = None
        for photo in self.photos:
            if not photo.vertical:
                solution.add_slide([photo])
            else:
                if cache is None:
                    cache = photo
                else:
                    solution.add_slide([cache, photo])
                    cache = None
        return solution


class Solution:
    def __init__(self, instance):
        self.instance = instance
        self.slides = []

    def __str__(self):
        output = io.StringIO()
        self.write(output)
        return output.getvalue()

    def add_slide(self, photos):
        assert (len(photos) == 1 or len(photos) == 2)
        assert (len(photos) != 1 or photos[0].vertical is False)
        assert (len(photos) != 2 or (photos[0].vertical is True and photos[1].vertical is True))
        self.slides.append(photos)

    def write(self, outfile):
        outfile.write(f'{len(self.slides)}\n')
        for slide in self.slides:
            ids = []
            for photo in slide:
                ids.append(photo.i)
            outfile.write(' '.join(map(str, ids)))
            outfile.write('\n')


def main():
    random.seed(0)

    parser = argparse.ArgumentParser()
    parser.add_argument('instance', nargs='+', type=argparse.FileType('r', encoding='utf_8'))
    namespace = parser.parse_args()

    for infile in namespace.instance:
        print(infile.name)
        instance = Instance(infile)
        #print(instance)

        solution = instance.solve()
        #print(solution)

        with open(f'{instance.name}.out', 'w') as outfile:
            solution.write(outfile)


if __name__ == '__main__':
    main()
