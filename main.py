#!/usr/bin/env python3

import argparse
import io
import itertools
import random

import matplotlib.pyplot as plt
import time
from tqdm import tqdm

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
        vertical_slide_scores = []
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        with tqdm(total=len(vertical_photos), desc='Pairing vertical photos') as pbar:
            time_next = None
            while len(vertical_photos) >= 2:
                if time_next is None or time.time() >= time_next:
                    ax.clear()
                    ax.hist(vertical_slide_scores)
                    fig.canvas.draw()
                    time_next = time.time() + 1
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
                pbar.update(2)
                vertical_slide_scores.append(best_score)
        plt.close()
        slideshow = []
        score_acc = 0
        plt.ion()
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        slideshow_scores = []
        with tqdm(total=len(slides), desc='Ordering slides') as pbar:
            cur = slides.pop()
            slideshow.append(cur)
            pbar.update(1)
            time_next = None
            while len(slides) > 0:
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
                pbar.update(1)
                slideshow_scores.append(best_score)
                if time_next is None or time.time() >= time_next:
                    ax.clear()
                    ax.hist(slideshow_scores)
                    fig.canvas.draw()
                    time_next = time.time() + 1
        plt.close()
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

    def interests(self):
        for i in range(len(self.slides) - 1):
            yield self.slides[i].interest(self.slides[i+1])

    def slide_tag_counts(self):
        for slide in self.slides:
            yield len(slide.tags)

    def vertical_slides(self):
        for slide in self.slides:
            if len(slide.photos) >= 2:
                yield slide

    def vertical_slide_tag_counts(self):
        for slide in self.vertical_slides():
            yield len(slide.tags)

    def write(self, outfile):
        outfile.write(f'{len(self.slides)}\n')
        for slide in self.slides:
            ids = []
            for photo in slide.photos:
                ids.append(photo.i)
            outfile.write(' '.join(map(str, ids)))
            outfile.write('\n')

    @staticmethod
    def read(infile, instance):
        S = int(next(infile))
        slides = []
        for i, line in zip(range(S), infile):
            photos = [instance.photos[photo_id] for photo_id in map(int, line.split())]
            slides.append(Slide(photos))
        return Solution(instance, slides=slides)


def main():
    # random.seed(0)

    parser = argparse.ArgumentParser()
    parser.add_argument('instance', nargs='+', type=argparse.FileType('r', encoding='utf_8'), help='input data set')
    parser.add_argument('--solution', nargs='*', type=argparse.FileType('r', encoding='utf_8'), help='base solution')
    parser.add_argument('-s', type=int, default=256, help='sample size for slideshow ordering')
    parser.add_argument('-v', type=int, default=256, help='sample size for vertical photo pairing')
    parser.add_argument('--forever', type=bool, default=False, help='iterate forever?')
    namespace = parser.parse_args()

    while True:
        for infile, infile_solution in itertools.zip_longest(namespace.instance, namespace.solution):
            if infile is None:
                continue
            print(f'Input file: {infile.name}')
            infile.seek(0)
            instance = Instance(infile)

            if infile_solution is None:
                solution = instance.solve(namespace.s, namespace.v)
            else:
                infile_solution.seek(0)
                solution = Solution.read(infile_solution, instance)
            print(f'Solution score: {solution.score}')

            plt.ioff()
            plt.hist(list(solution.interests()))
            plt.show()
            plt.hist(list(solution.slide_tag_counts()))
            plt.show()
            plt.hist(list(solution.vertical_slide_tag_counts()))
            plt.show()

            with open(f'{instance.name}.{solution.score}.out', 'w') as outfile:
                solution.write(outfile)
        if not namespace.forever:
            break


if __name__ == '__main__':
    main()
