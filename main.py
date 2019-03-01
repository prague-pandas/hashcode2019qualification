#!/usr/bin/env python3

import argparse
import io
import random
import time


class Photo:
    def __init__(self, i, line):
        self.i = i
        words = line.split()
        assert (words[0] in ['H', 'V'])
        self.vertical = words[0] == 'V'
        self.tags = set(words[2:])

    def __str__(self):
        return f'{self.i} {self.vertical} {self.tags}'


class Slide:
    def __init__(self, photos):
        assert (len(photos) == 1 or len(photos) == 2)
        assert (len(photos) != 1 or photos[0].vertical is False)
        assert (len(photos) != 2 or (photos[0].vertical is True and photos[1].vertical is True))
        self.photos = photos
        self.tags = photos[0].tags
        if len(photos) > 1:
            self.tags = self.tags | photos[1].tags

    def interest(self, other):
        worst = len(self.tags & other.tags)
        if worst == 0:
            return 0
        current = len(self.tags - other.tags)
        if current < worst:
            if current == 0:
                return 0
            worst = current
        return min(worst, len(other.tags - self.tags))


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
        slides = set()
        cache = None
        for photo in self.photos:
            if not photo.vertical:
                slides.add(Slide([photo]))
            else:
                if cache is None:
                    cache = photo
                else:
                    slides.add(Slide([cache, photo]))
                    cache = None
        cur = slides.pop()
        slideshow = [cur]
        score_acc = 0
        while len(slides) > 0:
            if len(slides) % 1000 == 0:
                print(len(slides))
            best_score = 0
            best_slide = None
            for slide in random.sample(slides, min(len(slides), 32)):
                interest = cur.interest(slide)
                if interest > best_score or best_slide is None:
                    best_score = interest
                    best_slide = slide
            assert (best_slide is not None)
            slideshow.append(best_slide)
            cur = best_slide
            slides.remove(best_slide)
            score_acc = score_acc + best_score
        solution = Solution(self, slideshow, score_acc)
        return solution


class Solution:
    def __init__(self, instance, slides=[], score=None):
        self.instance = instance
        self.slides = slides
        if score is None:
            self.score = self.calculate_score()
        else:
            assert (score == self.calculate_score())
            self.score = score

    def __str__(self):
        output = io.StringIO()
        self.write(output)
        return output.getvalue()

    def add_slide(self, slide):
        self.slides.append(slide)

    def calculate_score(self):
        res = 0
        prev = None
        for slide in self.slides:
            if prev is None:
                prev = slide
                continue
            res = res + prev.interest(slide)
            prev = slide
        return res

    def write(self, outfile):
        outfile.write(f'{len(self.slides)}\n')
        for slide in self.slides:
            ids = []
            for photo in slide.photos:
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
        # print(instance)

        solution = instance.solve()
        # print(solution)
        start = time.time()
        print(solution.score)
        print(str(time.time() - start))

        with open(f'{instance.name}.{solution.score}.out', 'w') as outfile:
            solution.write(outfile)


if __name__ == '__main__':
    main()
