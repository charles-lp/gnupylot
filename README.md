# gnupylot
A basic Matplotlib-like Python wrapper for gnuplot

## Requirements
- gnuplot

## Features

- Call gnuplot directly from your Python script
- Plot list and arrays without external files
- Matplotlib-like syntax

## Examples

Using standard gnuplot syntax:
```python
with Figure() as fig:
    fig.replot = True
    fig.set("grid")
    fig.set("key outside top horizontal")
    fig.plot("sin(x) dashtype 0")
    fig.plot([0,1], [0,0.5], "w lines linecolor 'red'")
    fig.show()
```

Using Matplotlib-like syntax:
```python
with Figure() as fig:
    fig.replot = True
    fig.set("grid")
    fig.set("key outside top horizontal")
    fig.plot("sin(x)", dashtype=0)
    fig.plot(x=[0,1], y=[0,0.5], w="lines", linecolor="'red'")
    fig.show()
```

Plot multiple figures at once:
```python
with Figure() as fig1, Figure() as fig2:
    fig1.plot("x**2")

    fig2.set("hidden3d")
    fig2.set("isosamples 50")
    fig2.splot("sin(x)*cos(y)")

    show(fig1, fig2)
```

## Known issues
- Depending on the windowing system, gnuplot windows may remain displayed even after the gnuplot process is terminated and have to be closed manually.