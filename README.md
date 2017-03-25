pdf2pub
=======

An Inkscape extension to format plots exported from MATLAB for publication.

This was developed and tested on Inkscape 0.91 with MATLAB r2014b.


Installation
============

Simply copy `pdf2pub.inx` and `pdf2pub.py` to your Inkscape extention folder (something like `{inkscape}/share/extensions` or `.config/inkscape/extensions` if you're on Ubuntu) and restart Inkscape.


Usage
=====

The workflow for which this extension was created is as follows:

1. Generate plot in MATLAB.

2. Use [export_fig](https://github.com/ojwoodford/export_fig) to save to pdf. For instance,
~~~matlab
export_fig -pdf -q101 -append figures.pdf
~~~

3. Import the pdf (e.g., `figures.pdf`) into Inkscape.

4. Ungroup pdf completely. Hit `ctrl+shift+g` a few times.

5. Run `pub2pdf`.


Options
=======

The plugin comes with two default formats:

* `full` yields a figure with a width of approximately `244 pt`, i.e., the usual column width of a two column paper (e.g., in the standard IEEE style)
* `half` yields a figure with a width of approximately `130 pt`, so that you can put two plots side-by-side (again considering the IEEE style)

The `custom` option allows you to choose your own format in the **Custom** tab. The settings are pretty much self-explanatory.


TODO
====

This is still somewhat under development and still hasn't been tested enough. Some things that still need fixing:

* Handle scenarios in which the plot comes from some other software (or older MATLAB version)
* Include a lot of safety checking (right now, if things don't look as they should, the extension will simply fail)
