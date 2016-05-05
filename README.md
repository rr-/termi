`termi`
-------

Images in your terminal, using ANSI and Unicode. Inspired by
[`shellpic`](https://github.com/larsjsol/shellpic).

#### Examples

Running `termi kurisu.png` in a terminal that supports 256 colors will result
in this:

> ![](https://cloud.githubusercontent.com/assets/1045476/15031404/ac06fbb8-1258-11e6-916d-c4e08d43952c.png)

If you're using one of [true color capable
terminals](https://gist.github.com/XVilka/8346728), you can also run `termi
kurisu.png --depth=24`:

> ![](https://cloud.githubusercontent.com/assets/1045476/15031403/ac0590f2-1258-11e6-8bca-1efc721fe880.png)

It works in dark terminals, too:

> ![](https://cloud.githubusercontent.com/assets/1045476/15031402/ac03215a-1258-11e6-8d31-4146eecde2b5.png)

You can also use custom palettes if you want.

You can even use it to display GIF animations:

> ![](https://cloud.githubusercontent.com/assets/1045476/15032039/cf9036e4-125d-11e6-8b7d-87538d57e68d.gif)

#### Installing

- `sudo python3 setup.py install`, or
- `yaourt -S termi-git` in Arch Linux.

#### Differences to [`shellpic`](https://github.com/larsjsol/shellpic)

- Quantization: while `shellpic` just maps the pixel color to keycodes on the
  fly, `termi` tries to do better and quantizes the images to target palette
  as a separate step. This allows techniques such as dithering, which enhance
  visual quality. (This matters only for non-true-color output.)
- Customizable palette: this can matter a lot; `shellpic` doesn't let you pass
  your own color palette, `termi` does. With some effort, this enables you to
  improve color matching no matter what terminal you're on.
- Smoother animations: animations do not produce ghost frame between the loops.
- Outright glitches: for some reason, `shellpic` renders a ghost line on my
  terminal on the right edge of the output.

To show most of problems mentioned above, here's what 256-color output from
`shellpic` looks on my URxvt:

>![20160505_004112_zqe](https://cloud.githubusercontent.com/assets/1045476/15031582/16c7ea9c-125a-11e6-9a0d-da6bc961c890.png)

I decided to roll my own solution for reasons mentioned above, but also because
it's fun!
