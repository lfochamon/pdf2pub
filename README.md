pdf2pub
=======

An Inkscape extension to format plots for publication (primarily targeted at MATLAB).

Preparing figures for publication is time consuming, even more so if you use MATLAB graphical features to place legends, arrows, normalize colors, etc. This extension is part of a MATLAB+Inkscape workflow in which "raw" plots are imported into Inkscape to be fixed. A similar workflow can be used with other softwares, such as R.

Developed and tested on Inkscape 0.91 with MATLAB r2014b.


Installation
============

Simply copy `pdf2pub.inx` and `pdf2pub.py` to your Inkscape extention folder (something like `{inkscape}/share/extensions` or `.config/inkscape/extensions` if you're on Ubuntu) and restart Inkscape.


Usage
=====

The workflow for which this extension was created is as follows:

1. Plot figure in MATLAB. Do not include titles or legends, but do name your axes!

2. Use [export_fig](https://github.com/ojwoodford/export_fig) to save plot to pdf. For instance,
~~~matlab
set(gcf, 'Color', 'w')
export_fig -pdf -q101 -append figures.pdf
~~~

3. Import the pdf (e.g., `figures.pdf`) into Inkscape.

4. Ungroup object completely. Select plot and hit `ctrl+shift+g` a few times.

5. Run `pub2pdf`.


Options
=======

`pdf2pub` differentiates between grid lines, bounding box, and actual plot curves based on their `style` elements. You must provide enough arguments in the `Find bounding box style` and `Find grid style` to identity these elements. For newer MATLAB versions, the `stroke` (color) is enough. The best way is to select the element and hit `ctrl+shift+x` to check the XML node of that element.

`pdf2pub` comes with two default plot formats:

* `full` gives a figure with a width of approximately `244 pt`, which is the usual column width of a two column paper (e.g., in the standard IEEE style)
* `half` yields a figure with a width of approximately `125 pt`, so that you can squeeze two plots side-by-side (again considering the IEEE style)

These default format also make decisions as to plot line, grid, and bounding box styles. You can change these options using the `custom` option and filling in your preferences in the **Custom** tab. Settings are pretty much self-explanatory.


TODO
====

This is still somewhat under development and still hasn't been tested enough. Some things that still need fixing:

* Include some safety checks (right now, if things don't look as they should, the extension will simply fail)
* Fix aspect ratio of closed paths, circles, etc.
