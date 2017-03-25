#!/usr/bin/env python

from lxml import etree
from subprocess import Popen, PIPE
import sys, math, itertools

import inkex
from simplestyle import *
from simpletransform import *
from simplepath import *


# General presets
arrow_stroke_width = '0.8'
legend_line_length = 15
legend_entry_sep = 18 - 1.5
legend_font_size = 10   # pt!


def stop(msg="Error!"):
    inkex.errormsg(msg)
    sys.exit(0)


class pdf2pub(inkex.Effect):
    def __init__(self):
        """Constructor"""
        # Calls base class constructor
        inkex.Effect.__init__(self)

        # Define parser options
        # Selected tab (ignored)
        self.OptionParser.add_option('--tabs', action='store',
                                     type='string', dest='tabs',
                                     default='full', help='Tabs')

        # Plot format
        self.OptionParser.add_option('--format', action='store',
                                     type='string', dest='format',
                                     default='full', help='Format')
        # General setup
        self.OptionParser.add_option('--xticks', action='store',
                                     type='string', dest='xticks',
                                     default='', help='x-ticks')
        self.OptionParser.add_option('--yticks', action='store',
                                     type='string', dest='yticks',
                                     default='', help='y-ticks')
        self.OptionParser.add_option('--color_pal', action='store',
                                     type='string', dest='color_pal',
                                     default='original',
                                     help='Color palette')
        self.OptionParser.add_option('--bbox_color_find', action='store',
                                     type='string', dest='bbox_color_find',
                                     default='#262626', help='Bounding box original color')
        self.OptionParser.add_option('--bbox_color', action='store',
                                     type='string', dest='bbox_color',
                                     default='#262626', help='Bounding box color')
        self.OptionParser.add_option('--grid_color_find', action='store',
                                     type='string', dest='grid_color_find',
                                     default='#dfdfdf', help='Grid original color')
        self.OptionParser.add_option('--grid_color', action='store',
                                     type='string', dest='grid_color',
                                     default='#dfdfdf', help='Grid color')
        self.OptionParser.add_option('--elements_dict', action='store',
                                     type='string', dest='elements_dict',
                                     default='true', help='Legend and additional elements')

        # Custom options
        self.OptionParser.add_option('--width', action='store',
                                     type='string', dest='width',
                                     default='260px', help='Plot width')
        self.OptionParser.add_option('--height', action='store',
                                     type='string', dest='height',
                                     default='196px', help='Plot height')
        self.OptionParser.add_option('--font_family', action='store',
                                     type='string', dest='font_family',
                                     default='CMU Serif', help='Font')
        self.OptionParser.add_option('--font_color', action='store',
                                     type='string', dest='font_color',
                                     default='#262626', help='Font color')
        self.OptionParser.add_option('--ticks_size', action='store',
                                     type='string', dest='ticks_size',
                                     default='10px', help='Tick labels font size')
        self.OptionParser.add_option('--labels_size', action='store',
                                     type='string', dest='labels_size',
                                     default='8px', help='Axis labels font size')
        self.OptionParser.add_option('--plot_stroke_width', action='store',
                                     type='string', dest='plot_stroke_width',
                                     default='1.6px', help='Plot line width')
        self.OptionParser.add_option('--bbox_stroke_width', action='store',
                                     type='string', dest='bbox_stroke_width',
                                     default='0.4px', help='Bounding box/grid line width')


    def effect(self):
        """Effect behaviour"""
        # Color palettes
        color_palettes = {
            'brewer_set1': ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3',
                            '#ff7f00', '#ffff33', '#a65628', '#f781bf',
                            '#999999'],
            'brewer_dark2': ['#1b9e77', '#d95f02', '#7570b3', '#e7298a',
                             '#66a61e', '#e6ab02', '#a6761d', '#666666'],
            'chamon_pal': ['#3e89c8', '#e41a1c', '#5ed046', '#000000',
                           '#ffab26', '#ffff33'],
            'original': None}

        # Retrieve user options
        form = self.options.format
        if form == 'full':
            width = 260
            height = 196
            font_family = 'CMU Serif'
            font_color = '#262626'
            ticks_size = 8
            labels_size = 10
            plot_stroke_width = 1.2
            bbox_stroke_width = 0.4
            grid_stroke_width = 0.4
            color_pal = color_palettes[self.options.color_pal]
        elif form == 'half':
            width = 130
            height = 98
            font_family = 'CMU Serif'
            font_color = '#262626'
            ticks_size = 7
            labels_size = 9
            plot_stroke_width = 1.2
            bbox_stroke_width = 0.4
            grid_stroke_width = 0.4
            color_pal = color_palettes[self.options.color_pal]
        elif form == 'custom':
            width = self.unittouu(self.options.width)
            height = self.unittouu(self.options.height)
            font_family = self.options.font_family
            font_color = self.options.font_color
            ticks_size = self.unittouu(self.options.ticks_size)
            labels_size = self.unittouu(self.options.labels_size)
            plot_stroke_width = self.unittouu(self.options.plot_stroke_width)
            bbox_stroke_width = self.unittouu(self.options.bbox_stroke_width)
            grid_stroke_width = self.unittouu(self.options.bbox_stroke_width)
            color_pal = color_palettes[self.options.color_pal]
        else:
            stop('Error! This format "%s" is unknown...' % form)

        # Retrieve ticks values
        if self.options.xticks == '':
            xticks = None
        else:
            xticks = [tick.strip() for tick in self.options.xticks.split(',')]

        if self.options.yticks == '':
            yticks = None
        else:
            yticks = [tick.strip() for tick in self.options.yticks.split(',')]

        # Retrieve general presets
        bbox_stroke_color_find = self.options.bbox_color_find.lower()
        bbox_stroke_color = self.options.bbox_color.lower()
        grid_stroke_color_find = self.options.grid_color_find.lower()
        grid_stroke_color = self.options.grid_color.lower()
        if self.options.elements_dict == 'true':
            elements_dict = True
        else:
            elements_dict = False

        # Get root node
        root_node = self.document.getroot()

        # Get main layer node (most elements)
        nelements = 0
        main_layer = None
        for element in root_node.iter(inkex.addNS('g', 'svg')):
            if nelements < len(element):
                main_layer = element
        if main_layer is None:
            main_layer = root_node

        # Get position and size of all elements
        p = Popen('inkscape --query-all %s' % self.args[-1],
            shell=True, stdout=PIPE, stderr=PIPE)
        rc = p.wait()
        allpos = p.stdout.read()

        # Get largest id number
        last_id = re.match(r'[A-z]+(\d+)', allpos.splitlines()[-1].strip())
        last_id = int(last_id.group(1))

        # Get axes labels
        xlab_id = None
        xlab_pos = 0
        ylab_id = None
        ylab_pos = float('inf')
        for line in allpos.splitlines():
            data = re.match(r'^(tspan[\d-]+),(-?\d+.?\d*),(-?\d+.?\d*),\d+.?\d*,\d+.?\d*',
                line.strip())

            if data is not None:
                if xlab_pos <= float(data.group(3)):
                    xlab_pos = float(data.group(3))
                    xlab_id = data.group(1)

                if ylab_pos >= float(data.group(2)):
                    ylab_pos = float(data.group(2))
                    ylab_id = data.group(1)

        if (xlab_id is not None) and (ylab_id is not None):
            xlab_text = [element.text for element in
                root_node.xpath('//svg:tspan[@id="%s"]' % xlab_id, namespaces=inkex.NSS)]
            ylab_text = [element.text for element in
                root_node.xpath('//svg:tspan[@id="%s"]' % ylab_id, namespaces=inkex.NSS)]

        if (xlab_id is None) or (ylab_id is None) or (len(xlab_text) != 1) or (len(ylab_text) != 1):
            inkex.errormsg('WARNING: could not detect labels. '
                'Will proceed with placeholder.\n')
            xlab_text = 'X-AXIS LABEL'
            ylab_text = 'Y-AXIS LABEL'
        else:
            xlab_text = xlab_text[0]
            ylab_text = ylab_text[0]

        # 1. Clean up #########################################################
        # Keep list of removed elements
        deleted = []

        # 1a. Remove white elements, ...
        for element in root_node.iter(inkex.addNS('path', 'svg')):
            style = parseStyle(element.get('style'))
            obj_fill = style.get('fill')
            obj_stroke = style.get('stroke')
            if ((obj_fill == '#ffffff' and obj_stroke == 'none') or
                    (obj_fill == 'none' and obj_stroke == '#ffffff')):
                deleted.append(element.get('id'))
                element.getparent().remove(element)

        # ... unused layers, ...
        for element in root_node.iter(inkex.addNS('g', 'svg')):
            if len(element) == 0:
                deleted.append(element.get('id'))
                element.getparent().remove(element)

        # ... clip paths, ...
        for element in root_node.iter(inkex.addNS('clipPath', 'svg')):
            deleted.append(element.get('id'))
            element.getparent().remove(element)

        # ... and labels
        for element in root_node.iter(inkex.addNS('text', 'svg')):
            deleted.append(element.get('id'))
            element.getparent().remove(element)


        # 2. Resize image #####################################################
        ### 2a. Get plot area size
        # Get plot area NW and SE corner positions by matching any element that
        # is not <tspan> or <text>. We also ignore <svg> and <layer>, since they
        # bound the full image.
        plot_nw_x = float('inf')
        plot_nw_y = float('inf')
        plot_se_x = 0
        plot_se_y = 0
        for line in allpos.splitlines():
            data = re.match(r'^(?!svg)(?!layer)(?!tspan)(?!text)([-\w]+),(-?\d+.?\d*),(-?\d+.?\d*),(\d+.?\d*),(\d+.?\d*)',
                line.strip())

            if data and data.group(1) not in deleted:
                if plot_nw_x >= float(data.group(2)):
                    plot_nw_x = float(data.group(2))
                if plot_nw_y >= float(data.group(3)):
                    plot_nw_y = float(data.group(3))

                if plot_se_x <= float(data.group(2)) + float(data.group(4)):
                    plot_se_x = float(data.group(2)) + float(data.group(4))
                if plot_se_y <= float(data.group(3)) + float(data.group(5)):
                    plot_se_y = float(data.group(3)) + float(data.group(5))

        # Calculate plot area width and height
        plot_width = plot_se_x - plot_nw_x
        plot_height = plot_se_y - plot_nw_y

        ### 2b. Fit canvas to plot area
        # Get image bounding box NW and SE corner positions by matching any
        # element that is not <svg> or <layer>.
        nw_x = float('inf')
        nw_y = float('inf')
        se_x = 0
        se_y = 0
        for line in allpos.splitlines():
            data = re.match(r'^(?!svg)(?!layer)(?!tspan)(?!text)([-\w]+),(-?\d+.?\d*),(-?\d+.?\d*),(\d+.?\d*),(\d+.?\d*)',
                line.strip())

            if data and data.group(1) not in deleted:
                if nw_x >= float(data.group(2)):
                    nw_x = float(data.group(2))
                if nw_y >= float(data.group(3)):
                    nw_y = float(data.group(3))

                if se_x <= float(data.group(2)) + float(data.group(4)):
                    se_x = float(data.group(2)) + float(data.group(4))
                if se_y <= float(data.group(3)) + float(data.group(5)):
                    se_y = float(data.group(3)) + float(data.group(5))

        # Set viewbox size
        root_node.set('viewBox', '%d %d %.8f %.8f' %
            (nw_x, nw_y, se_x - nw_x, se_y - nw_y))

        ### 2c. Resize plot
        root_node.set('width', '%.8f' % (width/plot_width*(se_x - nw_x)))
        root_node.set('height', '%.8f' % (height/plot_height*(se_y - nw_y)))
        root_node.set('preserveAspectRatio', 'none')


        # 3. Get plot elements ################################################
        ### 3a. Get grid/plot elements
        # Look for paths with predefined bounding box/grid color.
        bbox = []
        grid = []

        for element in root_node.xpath('//svg:path[@style]',
                                       namespaces=inkex.NSS):
            stroke = parseStyle(element.get('style')).get('stroke').lower()
            if stroke == bbox_stroke_color_find:
                bbox.append(element)
            elif stroke == grid_stroke_color_find:
                grid.append(element)

        ### 3b. Get plot traces
        # Look for elements whose colors are not the bounding box/grid colors.
        # Get curves grouped by colors
        curves = {}

        for element in root_node.xpath('//svg:*[@style]', namespaces=inkex.NSS):
            if element.tag != inkex.addNS('text', 'svg'):
                style = parseStyle(element.get('style'))
                if style['stroke'] not in ['none', bbox_stroke_color_find, grid_stroke_color_find]:
                    if style['stroke'] in curves.keys():
                        curves[style['stroke']].append(element)
                    else:
                        curves[style['stroke']] = [element]
                elif style['fill'] not in ['none', bbox_stroke_color_find, grid_stroke_color_find]:
                    if style['fill'] in curves.keys():
                        curves[style['fill']].append(element)
                    else:
                        curves[style['fill']] = [element]


        # 4. Fix grid and plot boundaries #####################################
        ### 4a. Fix bounding box
        for element in bbox:
            style = parseStyle(element.get('style'))

            # Fix thickness and color
            style['stroke-width'] = str(bbox_stroke_width) + 'px'
            style['stroke'] = bbox_stroke_color

            element.set('style', formatStyle(style))

        ### 4b. Fix bounding box
        for element in grid:
            style = parseStyle(element.get('style'))

            # Fix thickness and color
            style['stroke-width'] = str(grid_stroke_width) + 'px'
            style['stroke'] = grid_stroke_color

            element.set('style', formatStyle(style))


        # 5. Fix plot traces ##################################################
        color_idx = 0
        for color in curves.keys():
            for element in curves[color]:
                style = parseStyle(element.get('style'))

                ### 5a. Fix thickness
                if style['fill'] == 'none':
                    style['stroke-width'] = str(plot_stroke_width) + 'px'

                ### 5b. Alter colors of plot traces
                if color_pal is not None:
                    style['stroke'] = color_pal[color_idx]

                    if style['fill'] != 'none':
                        style['fill'] = color_pal[color_idx]

                element.set('style', formatStyle(style))

            if color_pal is not None:
                color_idx = (color_idx + 1) % len(color_pal)


        # 6. Ticks and labels #################################################
        # Evaluate scaling to compensate for distorted aspect ratio
        scale_y = math.sqrt(float(width)/float(height)*plot_height/plot_width)
        scale_x = 1/scale_y

        # Evaluate font scaling to compensate for resizing
        scale_size = width/plot_width*scale_x

        ### 6a. Find bounding box left/bottom coordinates
        xaxis = 0
        yaxis = float('inf')
        for element in bbox:
            path = parsePath(element.get('d'))

            # Disconsider zero length elements
            if path[0][1] != path[1][1]:
                if yaxis >= min(path[0][1][0],path[1][1][0]):
                    yaxis = min(path[0][1][0],path[1][1][0])

                elif xaxis <= max(path[0][1][1], path[1][1][1]):
                    xaxis = max(path[0][1][1], path[1][1][1])

        ### 6b. Separate x and y grids
        xgrid = []
        ygrid = []
        for element in grid:
            path = parsePath(element.get('d'))
            # Disconsider zero length elements
            if path[0][1] != path[1][1]:
                if path[0][1][0] == path[1][1][0]:
                    # Vertical path
                    xgrid.append(path[0][1][0])
                elif path[0][1][1] == path[1][1][1]:
                    # Horizontal path
                    ygrid.append(path[0][1][1])
                else:
                    stop('Error! There appears to be an'
                         'oblique path in your grid')

        ### 6c. x-axis tick labels
        if xticks is None:
            xticks = ['X'] * len(xgrid)

        if len(xgrid) < len(xticks):
            inkex.errormsg('WARNING: Number of x-tick labels provided exceeds '
                            'the number of x-ticks found in the plot. '
                            'Ignoring extra values.\n')
        elif len(xgrid) > len(xticks):
            inkex.errormsg('WARNING: Number of x-tick labels provided is less '
                            'than the number of x-ticks found in the plot. '
                            'Filling up with placeholders.\n')
            xticks.extend(['X'] * (len(xgrid)-len(xticks)))

        # ([x-axis position] + [font height]) / scale_y +
        #   [distance from axis to tick (~5px)] / scale_size
        xtick_y = (xaxis + self.unittouu('%fpt' % ticks_size))/scale_y + 5/scale_size

        for (xtick,xticklabel) in zip(sorted(xgrid),xticks):
            # [position of tick along axis] / scale_x
            xtick_x = xtick/scale_x

            last_id = last_id + 1
            tspan = etree.Element("tspan", id = 'tspan%d' % last_id)
            tspan.text = xticklabel

            last_id = last_id + 1
            text = etree.Element("text",
                style = 'font-family:%s;fill:%s;font-size:%fpt;' % (font_family, font_color, ticks_size/scale_size) +
                        'font-weight:normal;fill-opacity:1;'
                        'text-align:center;text-anchor:middle;'
                        'fill-rule:nonzero;stroke:none;line-height:125%;'
                        'letter-spacing:0px;word-spacing:0px;font-stretch:normal;'
                        'font-variant:normal;writing-mode:lr-tb;',
                id = 'text%d' % last_id,
                transform = 'scale(%.8f,%.8f)' % (scale_x, scale_y),
                x = '%f' % (xtick_x),
                y = '%f' % (xtick_y))

            text.append(tspan)
            main_layer.append(text)

        ### 6d. y-axis tick labels
        if yticks is None:
            yticks = ['Y'] * len(ygrid)

        if len(ygrid) < len(yticks):
            inkex.errormsg('WARNING: Number of y-tick labels provided exceeds '
                            'the number of y-ticks found in the plot. '
                            'Ignoring extra values.\n')
        elif len(ygrid) > len(yticks):
            inkex.errormsg('WARNING: Number of y-tick labels provided is less '
                            'than the number of y-ticks found in the plot. '
                            'Filling up with placeholders.\n')
            yticks.extend(['Y'] * (len(ygrid)-len(yticks)))

        # [y-axis position] / scale_x +
        #   [distance from axis to tick (~4px)] / scale_size
        ytick_x = yaxis/scale_x - 4/scale_size

        for (ytick,yticklabel) in zip(sorted(ygrid, reverse=True),yticks):
            # ([position of tick along axis] + [font height]/2) / scale_y
            ytick_y = (ytick + self.unittouu('%fpt' % ticks_size)/2)/scale_y

            last_id = last_id + 1
            tspan = etree.Element("tspan", id = 'tspan%d' % last_id)
            tspan.text = yticklabel

            last_id = last_id + 1
            text = etree.Element("text",
                style = 'font-family:%s;fill:%s;font-size:%fpt;' % (font_family, font_color, ticks_size/scale_size) +
                        'font-weight:normal;fill-opacity:1;'
                        'text-align:end;text-anchor:end;'
                        'fill-rule:nonzero;stroke:none;line-height:125%;'
                        'letter-spacing:0px;word-spacing:0px;font-stretch:normal;'
                        'font-variant:normal;writing-mode:lr-tb;',
                id = 'text%d' % last_id,
                transform = 'scale(%.8f,%.8f)' % (scale_x, scale_y),
                x = '%f' % (ytick_x),
                y = '%f' % (ytick_y))

            text.append(tspan)
            main_layer.append(text)


        ### 6e. x-axis label
        # x-axis label
        # ([y-axis position] + [plot width]/2) / scale_x
        xlab_x = (yaxis + plot_width/2)/scale_x
        # [tick position] + [font height]/scale_x +
        #   [distance from tick to label (~6pt)]/scale_x
        xlab_y = xtick_y + self.unittouu('%fpt' % labels_size)/scale_y + 9/scale_size

        last_id = last_id + 1
        xlab = etree.Element("text",
            style = 'font-family:%s;fill:%s;font-size:%fpt;' % (font_family, font_color, ticks_size/scale_size) +
                    'font-weight:normal;fill-opacity:1;'
                    'text-align:center;text-anchor:middle;'
                    'fill-rule:nonzero;stroke:none;line-height:125%;'
                    'letter-spacing:0px;word-spacing:0px;font-stretch:normal;'
                    'font-variant:normal;writing-mode:lr-tb;',
            id = 'text%d' % last_id,
            transform = 'scale(%.8f,%.8f)' % (scale_x, scale_y),
            x = '%f' % (xlab_x),
            y = '%f' % (xlab_y))

        last_id = last_id + 1
        xlab_tspan = etree.Element("tspan", id = 'tspan%d' % last_id)
        xlab_tspan.text = xlab_text
        xlab.append(xlab_tspan)

        ### 6f. y-axis label
        # [tick position] + [# of characters in longest tick]*[width of each character (~4.21px @ 8pt)] +
        #   [distance between tick and label (~6pt)]
        ylab_x = ytick_x - max([len(el) for el in yticks])*4.3 - 15/scale_size
        # ([x-axis position] + [plot height]/2) / scale_y
        ylab_y = (xaxis - plot_height/2)/scale_y

        last_id = last_id + 1
        ylab = etree.Element("text",
            style = 'font-family:%s;fill:%s;font-size:%fpt;' % (font_family, font_color, ticks_size/scale_size) +
                    'font-weight:normal;fill-opacity:1;'
                    'text-align:center;text-anchor:middle;'
                    'fill-rule:nonzero;stroke:none;line-height:125%;'
                    'letter-spacing:0px;word-spacing:0px;font-stretch:normal;'
                    'font-variant:normal;writing-mode:lr-tb;',
            id = 'text%d' % last_id,
            transform = 'matrix(0,-%.8f,%.8f,0,0,0)' % (scale_y, scale_x),
            x = '%f' % (-ylab_y),
            y = '%f' % (ylab_x))
            # (x,y transformed due to label rotation in <transform>)

        last_id = last_id + 1
        ylab_tspan = etree.Element("tspan", id = 'tspan%d' % last_id)
        ylab_tspan.text = ylab_text
        ylab.append(ylab_tspan)

        main_layer.append(xlab)
        main_layer.append(ylab)


        # 7. Create elements dictionary #######################################
        if elements_dict:
            ### 7a. Arrow
            # Create marker definition (Arrow2Mend)
            last_id = last_id + 1
            marker_id = last_id
            marker = etree.Element('marker',
                orient = 'auto',
                refY = '0',
                refX = '0',
                id = 'marker%d' % (last_id),
                style = 'overflow:visible')

            # Create marker drawing (Arrow2Mend)
            last_id = last_id + 1
            marker_path = etree.Element('path',
                id = 'path%d' % (last_id),
                style = 'fill:%s;stroke:%s;fill-rule:evenodd;' % (bbox_stroke_color, bbox_stroke_color) +
                        'fill-opacity:1;stroke-width:0.625;stroke-linejoin:round;'
                        'stroke-opacity:1',
                d = 'M 8.7185878,4.0337352 -2.2072895,0.01601326 8.7185884,-4.0017078 '
                    'c -1.7454984,2.3720609 -1.7354408,5.6174519 -6e-7,8.035443 z',
                transform = 'scale(-0.6,-0.6)')

            # Include marker definition under defs node
            defs_node = root_node.xpath('//svg:defs', namespaces=inkex.NSS)[0]
            marker.append(marker_path)
            defs_node.append(marker)

            # Add example arrow next to plot
            last_id = last_id + 1
            marker_path = etree.Element('path',
                style = 'color:%s;solid-color:%s;' % (bbox_stroke_color, bbox_stroke_color) +
                        'stroke:%s;stroke-width:%s;' % (bbox_stroke_color, self.unittouu(arrow_stroke_width)/scale_size) +
                        'marker-end:url(#marker%d);' % marker_id +
                        'mix-blend-mode:normal;color-interpolation:sRGB;'
                        'isolation:auto;color-interpolation-filters:linearRGB;'
                        'fill-rule:nonzero;solid-opacity:1;fill:none;fill-opacity:1;'
                        'clip-rule:nonzero;display:inline;opacity:1;'
                        'stroke-linecap:square;stroke-linejoin:round;'
                        'stroke-miterlimit:10;stroke-dasharray:none;'
                        'stroke-dashoffset:0;stroke-opacity:1;'
                        'color-rendering:auto;image-rendering:auto;shape-rendering:auto;'
                        'text-rendering:auto;enable-background:accumulate;'
                        'overflow:visible;visibility:visible',
                d = 'M %f,%f h %f' % (400/(scale_size/scale_x), 200/(scale_size/scale_y), 15/(scale_size/scale_x)),
                id = 'path%d' % (last_id))

            main_layer.append(marker_path)

            ### 7b. Legend
            # [line length] / ([size scaling] / [x-axis scaling])
            legend_line_dx = legend_line_length/(scale_size/scale_x)
            # [x position] / ([size scaling] / [x-axis scaling])
            legend_line_x = 400/(scale_size/scale_x)
            # ([x position] + [line length] + [line-label separation]) /
            #   ([size scaling]): the [x-axis scaling] is already
            #   taken care of by the transform in the text node
            legend_text_x = (400 + legend_line_length + 5)/scale_size

            legend_entry = 0
            for original_color in curves.keys():
                # ([start position] + ([entry number] - 1)*[distance between legend entries]) /
                #   ([size scaling] / [y-axis scaling])
                legend_line_y = (220 + legend_entry*legend_entry_sep)/(scale_size/scale_y)
                # [legend line position] / [y-axis scaling] +
                #   ([font size]/3 - 1) / [size scaling]
                text_line_y = legend_line_y/scale_y + (self.unittouu('%fpt' % legend_font_size)/3 - 1)/scale_size

                if color_pal is not None:
                    legend_color = color_pal[legend_entry % len(color_pal)]
                else:
                    legend_color = original_color

                # Legend color line
                last_id = last_id + 1
                legend_path = etree.Element('path',
                    style = 'color:%s;solid-color:%s;' % (legend_color, legend_color) +
                            'stroke:%s;stroke-width:%s;' % (legend_color, self.unittouu('1.5')/scale_size) +
                            'clip-rule:nonzero;display:inline;'
                            'overflow:visible;visibility:visible;opacity:1;'
                            'isolation:auto;color-interpolation-filters:linearRGB;'
                            'mix-blend-mode:normal;color-interpolation:sRGB;'
                            'solid-opacity:1;fill:none;stroke-linecap:butt;'
                            'fill-opacity:1;fill-rule:nonzero;'
                            'stroke-linejoin:bevel;stroke-miterlimit:10;'
                            'stroke-dasharray:none;stroke-dashoffset:0;'
                            'stroke-opacity:1;color-rendering:auto;'
                            'image-rendering:auto;shape-rendering:auto;'
                            'text-rendering:auto;enable-background:accumulate',
                    d = 'M %f,%f h %f' % (legend_line_x, legend_line_y, legend_line_dx),
                    id = 'path%d' % (last_id))

                # Legend label
                last_id = last_id + 1
                legend_text = etree.Element("text",
                    style = 'font-family:%s;fill:%s;font-size:%fpt;' % (font_family, font_color, legend_font_size/scale_size) +
                            'font-weight:normal;fill-opacity:1;'
                            'text-align:start;text-anchor:start;'
                            'fill-rule:nonzero;stroke:none;line-height:125%;'
                            'letter-spacing:0px;word-spacing:0px;font-stretch:normal;'
                            'font-variant:normal;writing-mode:lr-tb;',
                    id = 'text%d' % last_id,
                    transform = 'scale(%.8f,%.8f)' % (scale_x, scale_y),
                    x = '%f' % (legend_text_x),
                    y = '%f' % (text_line_y))

                last_id = last_id + 1
                legend_tspan = etree.Element("tspan", id = 'tspan%d' % last_id)
                legend_tspan.text = 'Entry %d' % (legend_entry + 1)
                legend_text.append(legend_tspan)

                # Add elements to layer
                main_layer.append(legend_path)
                main_layer.append(legend_text)

                legend_entry = legend_entry + 1


if __name__ == '__main__':
    e = pdf2pub()
    e.affect()
