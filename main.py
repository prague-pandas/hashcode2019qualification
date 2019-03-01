#!/usr/bin/env python3

import argparse
import io
import itertools
import random

salt_bits = 32


class Photo:
    def __init__(self, i, line):
        self.i = i
        words = line.split()
        assert (words[0] in ['H', 'V'])
        self.vertical = words[0] == 'V'
        self.tags = set(words[2:])
        self.salt = random.getrandbits(salt_bits)

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
        self.salt = random.getrandbits(salt_bits)

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

    def solve(self, sample_size_slides, sample_size_vertical_photos):
        slides = set()
        vertical_photos = set()
        for photo in self.photos:
            if not photo.vertical:
                slides.add(Slide([photo]))
            else:
                vertical_photos.add(photo)
        while len(vertical_photos) >= 2:
            if len(vertical_photos) % 1000 == 0:
                print(f'Vertical photos remaining: {len(vertical_photos)}')
            photo = vertical_photos.pop()
            assert photo.vertical
            best_score = 0
            best_other = None
            sample = itertools.islice(vertical_photos, sample_size_vertical_photos)
            # sample = random.sample(vertical_photos, min(len(vertical_photos), sample_size_vertical_photos))
            for other in sample:
                other_score = len(photo.tags | other.tags)
                if other_score > best_score or best_other is None:
                    best_score = other_score
                    best_other = other
            slides.add(Slide([photo, best_other]))
            vertical_photos.remove(best_other)
        cur = slides.pop()
        slideshow = [cur]
        score_acc = 0
        while len(slides) > 0:
            if len(slides) % 1000 == 0:
                print(f'Slides remaining: {len(slides)}')
            best_score = 0
            best_slide = None
            sample = itertools.islice(slides, sample_size_slides)
            # sample = random.sample(slides, min(len(slides), sample_size_slides))
            # TODO: Stop sampling as soon as we have reached a good score.
            for slide in sample:
                interest = cur.interest(slide)
                if interest > best_score or best_slide is None:
                    best_score = interest
                    best_slide = slide
            assert (best_slide is not None)
            slideshow.append(best_slide)
            cur = best_slide
            slides.remove(best_slide)
            score_acc = score_acc + best_score
        # TODO: Improve slideshow by hillclimbing.
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
    # random.seed(0)

    parser = argparse.ArgumentParser()
    parser.add_argument('instance', nargs='+', type=argparse.FileType('r', encoding='utf_8'), help='input data set')
    parser.add_argument('-s', type=int, default=256, help='sample size for slideshow ordering')
    parser.add_argument('-v', type=int, default=256, help='sample size for vertical photo pairing')
    namespace = parser.parse_args()

    while True:
        for infile in namespace.instance:
            print(f'Input file: {infile.name}')
            infile.seek(0)
            instance = Instance(infile)

            solution = instance.solve(namespace.s, namespace.v)
            print(f'Solution score: {solution.score}')

            with open(f'{instance.name}.{solution.score}.out', 'w') as outfile:
                solution.write(outfile)


if __name__ == '__main__':
    main()
