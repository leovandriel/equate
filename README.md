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

```
$ ./sample
(('pi', '^', ('-', 'pi')), '+', ('-', ((('pi', '+', '1'), '*', ('1', '+', '1')), '+', ('-', ('pi', '*', 'pi'))))) (18) at 2.4 digits: 1.6138447870330699
((('-', 'pi'), '+', (('-', ('-', '1')), '+', (('1', '+', '1'), '+', '1'))), '^', ('-', 'pi')) (15) at 2.6 digits: 1.6155047770238482
```

# Lookup

The second approach was to store all possible equation values in a lookup table and grow this table by applying operands to it. The idea is that if different equations result in the same value, they would collide in the table and simply the storage. It does find the target value within a minute, which is faster than the sample approach.

In practice the number of collisions turns out very small. For very basic equations it collides about 80% of the time, but with the introduction of irrational and transcendental numbers this goes down to just 20%. In other words, with most of the operands applied the table grows. This results in an exponential growth of the table, which stalls around depth 4.

```
$ ./lookup
looking for 1.618033988749895
iteration 0
found: (log 5) = 1.6094379124341003 accuracy: 2.1 compression: 0.1
iteration 1
found: (2 ^ (log 2)) = 1.6168066722416747 accuracy: 2.9 compression: -0.5
found: ((sqrt 2) * (log pi)) = 1.6188925298220267 accuracy: 3.1 compression: -1.0
found: ((2 ^ -7) + (log 5)) = 1.6172504124341003 accuracy: 3.1 compression: -1.1
found: ((log 5) + (5 ^ -3)) = 1.6174379124341003 accuracy: 3.2 compression: -1.2
found: ((log 8) ^ (sin 7)) = 1.617658080128246 accuracy: 3.4 compression: -1.1
```

# Iterate

The next approach is to iterate through all possible equations, breadth first. This initially seemed complex to build, but with Python's yield statement, it turned out to be the shortest implementation of all. And despite it doing a bunch of redundant calculations, it finds the target (golden ratio) within a few seconds and provides a nice alternative cosine-based equation right before proposing the commonly used square-root one, with the added bonus of a cube root solution. Note that `^/n` indicates the n-th root, i.e. the inverse of `^n`.

```
$ ./iterate
(cos((pi/5))*2) = 1.618033988749895 (diff: 16)
((1+(5^/2))/2) = 1.618033988749895 (diff: 16)
((2+(5^/2))^/3) = 1.618033988749895 (diff: 16)
```

This approach also has fewest parameters, leaving just the constants and operands to be implemented. Most operands have additional constraints that weed out trivial equivalences. Additional constraints can be added to remove more complex multi-level equivalences.

Because it is all computation and no memory, this algorithm can search forever and could be nicely parallelized. With the current operands, every additional size is about a factor 8x evaluations. On a laptop I can get to a size of about 10 operands (and constants) within 30 minutes.

# Collision

For larger equation size, the iterate script gives equations that have trivial equivalences, like `2+3` instead of `5`. These can be filtered out in the equation generator by adding additional conditions before yielding. The collision script helps with finding these equivalences by keeping a lookup of values and equations. The case of `2+3` was addressed by adding `if (value1 + value2) not in primitives`.

The most trivial ones have been removed. What is left are slightly less trivial cases like `3*(3^2)`. While these can be addressed as well, overall performance doesn't necessarily improve.

```
$ ./collision
size: 1 found: 0
size: 2 found: 0
collision: (2^2) = (1+3)
collision: (2*3) = (1+5)
collision: (3+5) = (2^3)
size: 3 found: 3
collision: cos((pi/3)) = (1/2)
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

# Benchmark

The benchmark script helps with keeping an eye on performance of the equation iterator. It lists growth of the equation count per size and time per iteration. Additionally every script can be profiled by uncommenting `#-m cProfile -s tottime` in the header.

```
$ ./benchmark
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

# Series

While iterate script helps find some interesting equations, like the relation between `cos(pi/5)` and `sqrt(5)`, running it on the bunch of well-known constants has not revealed any surprising equivalences. Perhaps we need to expand our horizons and look at infinite series. The series script adds support for infinite sums and products, as well as continued fractions. This is done by introducing two new variables: `N`, the index of recursion and `R` the value of the next recursion. The equation can then be evaluated in reverse, starting with R equal to 1 or 0.

For every equation that seems to converge, it runs the equation finder used in the iterate script. If it cannot find a closed form (irrational), it calls the [OEIS](https://oeis.org/) API to see if this number is known. Calls to the API are cached.

```
$ ./series
found oeis: (1/(N+R)) = 1.4331274267223117 conv:16 oeis:3
- Decimal representation of continued fraction 1, 2, 3, 4, 5, 6, 7, ...
- Decimal expansion of (684125+sqrt(635918528029))/1033802.
- Decimal expansion of (232405+sqrt(71216963807))/348378.
found oeis: ((1/R)+N) = 0.697774657964008 conv:16 oeis:3
- Decimal expansion of number with continued fraction expansion 0, 1, 2, 3, 4, 5, 6, ...
- Decimal expansion of the value of the continued fraction [1; 1, 2, 3, 4, 5, ...].
- Duplicate of A052119.
found oeis: (-(1/(N+R))) = 0.38821076556779577 conv:16 oeis:1
- Decimal expansion of J_0(2)/J_1(2) = 1 - 1/(2 - 1/(3 - 1/(4 - ...))).
found oeis: (-((1/R)+N)) = 2.5759203213682222 conv:16 oeis:1
- Decimal expansion of BesselJ(1,2)/BesselJ(0,2).
found equation: (1+(R/(1+N))) = e = 2.718281828459045 conv:16 diff:16 has: e,
found equation: (1+(R/(3+N))) = (((-2)+e)*2) = 1.4365636569180904 conv:16 diff:16 has: e,
```

It is able to find a continued fraction for e within second: `(1+(R/(1+N)))`. Pi might be a lot harder to find.

# License

MIT
