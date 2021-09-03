Equate
=======

*Find an equation for a number*

# Usage

All three scripts can be used to find an equation for a given target. Edit the `target` value in the top of the script and run it:

    ./sample.py
    ./lookup.py
    ./iterate.py

# How it works

I've taken three different approaches: random sampling, equation lookup, and equation iteration. With each approach, I tried to find the equation for the golden ratio. The basic idea is that if evaluate an equation that comes much closer to the target value compared to the number of equations of this size, then we found a good candidate.

## Sampling

The first approach was to randomly sample equations. Initially this seemed easiest given how complex enumeration of equations can get. It builds the equation tree by recursively sampling sub-trees. This works reasonably well and finds an equation in a few minutes.

The challenge is balancing the probabilities for different tree types. The tree can easily grow very deep, missing many of the shallow solutions. This can be countered by adjusting the weights on picking certain sub-trees and adding a maximum depth. This leaves many hyper-parameters to optimize. This could be beneficial if we have additional information on the solution and use this as a bias, but for all practical purposes this seems out of reach.

One possible benefit of this approach is that it can explore more complex equations that would not be easily found through iteration. However, the likelihood of finding that complex equation quickly vanishes with the exponential (or perhaps even faster) growth in the number of possible equations.

## Lookup

The next approach was to store all possible equation values in a lookup table and grow this table by applying operands to it. The idea is that if different equations result in the same value, they would collide in the table and simply the storage. It does find the target value within a minute, which is faster than the sample approach.

In practice the number of collisions turns out very small. For very basic equations it collides about 80% of the time, but with the introduction of irrational and transcendental numbers this goes down to just 20%. In other words, with most of the operands applied the table grows. This results in an combinatoric growth of the table, which stalls around depth 4.

## Iterate

The last approach is to just iterate through all possible equations, breadth first. This initially seemed complex to build, but with Python's yield statement, it turned out to be the shortest implementation of all. And despite it doing a bunch of redundant calculations, it finds the target within a few seconds and provides a nice alternative cosine-based equation right before proposing the square-root one, with the added bonus of a cube root solution.

```
$ ./iterate
((1/2)*(1+sqrt(5))) = 1.618033988749895 (accuracy: 16)
((2+sqrt(5))^(1/3)) = 1.618033988749895 (accuracy: 16)
(cos(((1/5)*pi))*2) = 1.618033988749895 (accuracy: 16)
```

When run with `min_compression = 0` it also finds `log(5) = 1.6094379124341003` with an accuracy of 2.1. While not a valid solution, this is fairly accurate approximation for its size.

This approach also has fewest parameters, leaving just the constants and operands to be implemented. Most operands have additional contraints that weed out trivial equivalences. Additional constraints can be added to remove more complex multi-level equivalences.

Because it is all computation and no memory, this algorithm can search forever and could be nicely parallelized. With the current operands, every additional size is about a factor 10x equation evaluations. On a laptop I can get to a size of about 10 operands (and constants) within the hour.

# License

MIT
