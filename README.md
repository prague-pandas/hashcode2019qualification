# Hash Code 2019 Online Qualification Round Solution

Problem: Photo slideshow

Team: Prague Pandas

## Links

* [Hash Code](https://codingcompetitions.withgoogle.com/hashcode/)
    * [2019 Online Qualification Scoreboard](https://codingcompetitions.withgoogle.com/hashcode/archive/2019)
* [Data set statistics](https://docs.google.com/spreadsheets/d/161ImQXt0-blghp4Appp8IgB1KC6MDHxHVQnIvxETcVg/edit?usp=sharing)

## Description

The solver solves the problem in two phases:

1. Pair the vertical photos to form slides.
2. Order the slides.

When pairing the vertical photos, the solver repeatedly takes
an arbitrary photo and searches for another photo to maximize
the size of the union of their tag sets.
When searching for the match, we only consider a constant-sized sample
of the photo population.

When ordering the slides, the solver greedily extends the slideshow.
It starts by taking an arbitrary slide and then repeatedly searches
for the next slide that maximizes the transition score.
When searching for the next slide, we only consider a constant-sized
sample of the slide population.

## Final score

* A: 2
* B: 109626
* C: 1517
* D: 375409
* E: 313967
* Total: 800521

[Rank: 582 of 6671](https://codingcompetitions.withgoogle.com/hashcode/archive/2019)
