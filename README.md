pdf2pub
=======

An Inkscape extension to format plots exported from MATLAB for publication.


Usage
=====

The workflow for which this plugin was created is as follows:

1. Generate plot in MATLAB

2. Use [export_fig](https://github.com/ojwoodford/export_fig) to save to pdf. For instance,
~~~matlab
export_fig -pdf -q101 -append figures.pdf
~~~

3. Import the pdf (e.g., `figures.pdf`) in Inkscape

4. Ungroup pdf completely. You should use `ctrl+shift+g` several times instead of [deep_ungroup](http://luther.ceplovi.cz/git/inkscape-ungroup-deep.git), which relies mostly on SVG transforms instead of evaluating the actual `x,y` of the elements. For now, this plugin has no support for `transform`.

5. Run `pub2pdf`


Options
=======

The plugin comes with two default formats:

* `full` yields a figure with a width of approximately `244 pt`, i.e., the usual column width of a two column paper (e.g., in the standard IEEE style)
* `half` yields a figure with a width of approximately `130 pt`, so that you can put two plots side-by-side (again considering the IEEE style)
* `custom` allows you to choose your own formatting settings in the **Custom** tab. The settings are pretty much self-explanatory.

`full` and `half` will modify your plot color to the `Chamon` palette. It is inspired in Brewer's Set1 palette (see [RColorBrewer](http://cran.r-project.org/web/packages/RColorBrewer/index.html)) but modified so that it prints better in grayscale. In `custom` you can choose between `Keep original`, `Chamon`, `Brewer's Set1`, and `Brewer's Dark2`.
