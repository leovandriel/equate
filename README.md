Equate
======

*Find interesting equations*

# About

This is an attempt to explore the space of all equations to find an interesting one. Interesting is pretty loosely defined here, but basically means that there is some mathematical significance, beyond what is currently documented.

Much of this work is based on the basic idea that if the numeric evaluation of two equations are equal (or very close) then the equations are likely equal as well. This isn't always the case, especially as equations get more complex, but in general seems like a solid basis for search.

Following is the list of scripts in this repository. They require python3.

# Sample

The first approach was to randomly sample equations. Initially this seemed easiest given how complex enumeration of equations can get. It builds the equation tree by recursively sampling sub-trees. This works reasonably well and finds an equation in a few minutes.

The challenge is balancing the probabilities for different tree types. The tree can easily grow very deep, missing many of the shallow solutions. This can be countered by adjusting the weights on picking certain sub-trees and adding a maximum depth. This leaves many hyper-parameters to optimize. This could be beneficial if we have additional information on the solution and use this as a bias, but for all practical purposes this seems out of reach.

One possible benefit of this approach is that it can explore more complex equations that would not be easily found through iteration. However, the likelihood of finding that complex equation quickly vanishes with the exponential growth in the number of possible equations.

Usage: `./sample`

# Lookup

The second approach was to store all possible equation values in a lookup table and grow this table by applying operands to it. The idea is that if different equations result in the same value, they would collide in the table and simply the storage. It does find the target value within a minute, which is faster than the sample approach.

In practice the number of collisions turns out very small. For very basic equations it collides about 80% of the time, but with the introduction of irrational and transcendental numbers this goes down to just 20%. In other words, with most of the operands applied the table grows. This results in an exponential growth of the table, which stalls around depth 4.

Usage: `./lookup`

# Iterate

The next approach is to just iterate through all possible equations, breadth first. This initially seemed complex to build, but with Python's yield statement, it turned out to be the shortest implementation of all. And despite it doing a bunch of redundant calculations, it finds the target (golden ratio) within a few seconds and provides a nice alternative cosine-based equation right before proposing the commonly used square-root one, with the added bonus of a cube root solution. Note that `^/n` indicates the n-th root, i.e. the inverse of `^n`.

```
$ ./iterate
(cos((pi/5))*2) = 1.618033988749895 (diff: 16)
((1+(5^/2))/2) = 1.618033988749895 (diff: 16)
((2+(5^/2))^/3) = 1.618033988749895 (diff: 16)
```

This approach also has fewest parameters, leaving just the constants and operands to be implemented. Most operands have additional constraints that weed out trivial equivalences. Additional constraints can be added to remove more complex multi-level equivalences.

Because it is all computation and no memory, this algorithm can search forever and could be nicely parallelized. With the current operands, every additional size is about a factor 8x evaluations. On a laptop I can get to a size of about 10 operands (and constants) within 30 minutes.

Usage: `./iterate`

# Collision

For larger equation size, the iterate script gives equations that have trivial equivalences, like `2+3` instead of `5`. These can be filtered out in the equation generator by adding additional conditions before yielding. The collision script helps with finding these equivalences by keeping a lookup of values and equations. The case of `2+3` was addressed by adding `if (value1 + value2) not in primitives`.

The most trivial ones have been removed. What is left are slightly less trivial cases like `3*(3^2)`. While these can be addressed as well, overall performance doesn't necessarily improve.

```
size: 1 found: 0
size: 2 found: 0
collision: (2^2) = (1+3)
collision: (2*3) = (1+5)
collision: (3+5) = (2^3)
size: 3 found: 3
collision: cos((pi/3)) = (1/2)
collision: tan((pi/3)) = (3^/2)
collision: ((-1)+5) = (1+3)
collision: ((-2)+1) = (-1)
collision: (log(2)*2) = log((1+3))
collision: ((-3)+1) = (-2)
collision: ((-3)+2) = (-1)
collision: ((-5)+1) = (-(1+3))
collision: ((-5)+2) = (-3)
collision: ((-5)+3) = (-2)
size: 4 found: 10
```

Usage: `./collision`

# Benchmark

This script helps with keeping an eye on performance of the equation iterator. It lists growth of the equation count per size and time per iteration. Additionally every script can be profiled by uncommenting `#-m cProfile -s tottime` in the header.

```
size: 1 growth: 6.0x avg: 6.0 nanos: 2333 count: 0.0M
size: 2 growth: 2.17x avg: 3.61 nanos: 2000 count: 0.0M
size: 3 growth: 9.23x avg: 4.93 nanos: 1008 count: 0.0M
size: 4 growth: 4.76x avg: 4.89 nanos: 1121 count: 0.0M
size: 5 growth: 8.33x avg: 5.44 nanos: 999 count: 0.0M
size: 6 growth: 6.56x avg: 5.61 nanos: 1045 count: 0.03M
size: 7 growth: 7.95x avg: 5.9 nanos: 1076 count: 0.25M
size: 8 growth: 7.44x avg: 6.07 nanos: 1135 count: 1.85M
size: 9 growth: 7.98x avg: 6.26 nanos: 1127 count: 14.72M
```

Usage: `./benchmark`

# Series

The iterate script helps find some interesting equations, like the relation between `cos(pi/5)` and `sqrt(5)`, but nothing new. Running it on the bunch of well-known constants has not revealed any surprising equivalences. Perhaps we need to expand our horizons and look at infinite series. This script add support for infinite sums and products, but also continued fractions. This is done by introducing two new primitives: `N`, the index of recursion and `R` the value of the next recursion. The equation can then be evaluated in reverse, starting with R equal to 1 or 0.

For every equation that seems to converge, it runs the equation finder used in the iterate script. If it cannot find a closed form, it calls the [OEIS](https://oeis.org/) API to see if this number is known. Calls to the API are cached.

```
found oeis: (1/(N+R)) = 1.4331274267223117 conv:16 oeis:3
  Decimal representation of continued fraction 1, 2, 3, 4, 5, 6, 7, ...
  Decimal expansion of (684125+sqrt(635918528029))/1033802.
  Decimal expansion of (232405+sqrt(71216963807))/348378.
found nothing: (2/(N+R)) = 1.7756355884645123 conv:16
found nothing: (3/(N+R)) = 2.0639145845357936 conv:16
found nothing: (5/(N+R)) = 2.542411658195814 conv:16
found oeis: ((1/R)+N) = 0.697774657964008 conv:16 oeis:3
  Decimal expansion of number with continued fraction expansion 0, 1, 2, 3, 4, 5, 6, ...
  Decimal expansion of the value of the continued fraction [1; 1, 2, 3, 4, 5, ...].
  Duplicate of A052119.
found nothing: ((2/R)+N) = 1.1263572396234227 conv:16
found nothing: ((3/R)+N) = 1.4535485249622122 conv:16
found nothing: ((5/R)+N) = 1.9666366710842487 conv:16
found equation: ((N+R)/3) = (1/(1+3)) = 0.25 conv:16 diff:16
found equation: ((N+R)/5) = (1/(1+(3*5))) = 0.0625 conv:16 diff:16
found equation: ((R/3)+N) = (1/((1/3)+1)) = 0.75 conv:16 diff:16
found equation: ((R/5)+N) = (1/((1/5)+3)) = 0.3125 conv:16 diff:16
```

Usage: `./series`

# License

MIT
