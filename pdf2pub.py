#!/usr/bin/env python

from lxml import etree
import sys

import inkex
from simplestyle import *
from simpletransform import *
from simplepath import *


def stop(msg = "Error!"):
    inkex.errormsg(msg)
    sys.exit(0)


class ChamonEffect(inkex.Effect):
    """
    Chamon Inkscape extension.
    """
    def __init__(self):
        """Constructor"""
        # Calls base class constructor
        inkex.Effect.__init__(self)

        self.OptionParser.add_option('--tabs', action = 'store',
            type = 'string', dest = 'tabs', default = 'full',
            help = 'Tabs')
        self.OptionParser.add_option('--format', action = 'store',
            type = 'string', dest = 'format', default = 'full',
            help = 'Format')
        self.OptionParser.add_option('--width', action = 'store',
            type = 'string', dest = 'width', default = '260px',
            help = 'Plot width')
        self.OptionParser.add_option('--font_family', action = 'store',
            type = 'string', dest = 'font_family', default = 'Arial',
            help = 'Font')
        self.OptionParser.add_option('--ticks_size', action = 'store',
            type = 'string', dest = 'ticks_size', default = '10px',
            help = 'Ticks font size')
        self.OptionParser.add_option('--labels_size', action = 'store',
            type = 'string', dest = 'labels_size', default = '8px',
            help = 'Labels font size')
        self.OptionParser.add_option('--line_width', action = 'store',
            type = 'string', dest = 'line_width', default = '1.6px',
            help = 'Line width')
        self.OptionParser.add_option('--color_pal', action = 'store',
            type = 'string', dest = 'color_pal', default = 'chamon_pal',
            help = 'Color palette')


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
                           '#ffab26', '#ffff33']}

        # Retrieve user options
        form = self.options.format
        if form == 'full':
            width = 260
            font_family = 'Arial'
            ticks_size = 8
            labels_size = 10
            line_width = 1.6
            color_pal = color_palettes['chamon_pal']
        elif form == 'half':
            width = 130
            font_family = 'Arial'
            ticks_size = 7
            labels_size = 9
            line_width = 1.2
            color_pal = color_palettes['chamon_pal']
        elif form == 'custom':
            width = inkex.unittouu(self.options.width)
            font_family = self.options.font_family
            ticks_size = inkex.unittouu(self.options.ticks_size)
            labels_size = inkex.unittouu(self.options.labels_size)
            line_width = inkex.unittouu(self.options.line_width)
            color_pal = color_palettes[self.options.color_pal]
        else:
            stop('Error! This format "%s" is unknown...' % form)

        # Get root node
        root_node = self.document.getroot()

        # 1. Clean up #########################################################
        # 1a. Remove white elements, ...
        for element in root_node.iter(inkex.addNS('path', 'svg')):
            style = parseStyle(element.get('style'))
            if (style.get('fill') == '#ffffff'
                    or style.get('stroke') == '#ffffff'):
                element.getparent().remove(element)

        # ... unused layers, ...
        for element in root_node.iter(inkex.addNS('g', 'svg')):
            if len(element) == 0:
                element.getparent().remove(element)

        # ... and clip paths
        for element in root_node.iter(inkex.addNS('clipPath', 'svg')):
            element.getparent().remove(element)

        # 2. Get plot elements ################################################
        # 2a. Grid
        xgrid = []
        ygrid = []

        for element in root_node.xpath('//svg:path[@style]', namespaces=inkex.NSS):
            if parseStyle(element.get('style')).get('stroke-dasharray') != 'none':
                path = parsePath(element.get('d'))
                # Eliminate zero length elements
                if path[0][1] != path[1][1]:
                    if path[0][1][0] == path[1][1][0]:
                        # Vertical path
                        xgrid.append(element)

                    elif path[0][1][1] == path[1][1][1]:
                        # Horizontal path
                        ygrid.append(element)

                    else:
                        stop('Error! There appears to be an'
                             'oblique path in your grid')

        # 2b. Plot area bounding box
        bbox = {}

        # Left-right borders
        x_min = float('inf')
        x_max = float('-inf')

        for element in xgrid:
            path = parsePath(element.get('d'))
            if x_min > path[0][1][0]:
                x_min = path[0][1][0]
                bbox['left'] = {'node': element,
                                'coord': [{'x': path[0][1][0], 'y': path[0][1][1]},
                                          {'x': path[1][1][0], 'y': path[1][1][1]}]}

            if x_max < path[0][1][0]:
                x_max = path[0][1][0]
                bbox['right'] = {'node': element,
                                 'coord': [{'x': path[0][1][0], 'y': path[0][1][1]},
                                           {'x': path[1][1][0], 'y': path[1][1][1]}]}

        # Top-bottom borders
        y_min = float('inf')
        y_max = float('-inf')

        for element in ygrid:
            path = parsePath(element.get('d'))
            if y_min > path[0][1][1]:
                y_min = path[0][1][1]
                bbox['top'] = {'node': element,
                               'coord': [{'x': path[0][1][0], 'y': path[0][1][1]},
                                         {'x': path[1][1][0], 'y': path[1][1][1]}]}

            if y_max < path[0][1][1]:
                y_max = path[0][1][1]
                bbox['bottom'] = {'node': element,
                                  'coord': [{'x': path[0][1][0], 'y': path[0][1][1]},
                                            {'x': path[1][1][0], 'y': path[1][1][1]}]}

        # 2c. Labels
        title = None
        xlabel = None
        ylabel = None

        x_min = float('inf')
        y_max = float('-inf')

        for element in root_node.iter(inkex.addNS('text', 'svg')):
            mat = parseTransform(element.get('transform','scale(1,1)'))
            xt = inkex.unittouu(element.get('x'))
            yt = inkex.unittouu(element.get('y'))
            x = mat[0][0]*xt + mat[0][1]*yt + mat[0][2]
            y = mat[1][0]*xt + mat[1][1]*yt + mat[1][2]

            if y < bbox['top']['coord'][0]['y']:
                # Text element above plot area is the plot title
                title = element

            if y > bbox['bottom']['coord'][0]['y'] and y_max < y:
                # Lowest text element (largest y) below plot area is the x-axis label
                y_max = y
                xlabel = element

            if x < bbox['left']['coord'][0]['x'] and x_min > x:
                # Most left text element (smallest x) to the left of plot area
                # is the y-axis label
                x_min = x
                ylabel = element

        # Remove plot title
        if title != None:
            title.getparent().remove(title)
            del title

        # 2d. Ticks
        xticks = []
        yticks = []
        cornerticks = []

        # Compile list of IDs to ignore (xlabel and ylabel, if they exist)
        labels_id = []
        if xlabel != None:
            labels_id.append(xlabel.get('id'))
        if ylabel != None:
            labels_id.append(ylabel.get('id'))

        for element in root_node.xpath('//svg:text', namespaces=inkex.NSS):
            if element.get('id') not in labels_id:
                x = inkex.unittouu(element.get('x'))
                y = inkex.unittouu(element.get('y'))

                if x > bbox['left']['coord'][0]['x'] and y > bbox['bottom']['coord'][0]['y']:
                    # xticks
                    xticks.append(element)

                elif x < bbox['left']['coord'][0]['x'] and y < bbox['bottom']['coord'][0]['y']:
                    # yticks
                    yticks.append(element)

                else:
                    # corner ticks
                    cornerticks.append(element)

        # Decide corner ticks
        if len(cornerticks) != 0 and len(cornerticks) != 2:
            stop('Error! You should have 2 corner ticks, you only have %s.'
                    % len(cornerticks))
        else:
            # Lowest tick (largest y) is xtick
            if inkex.unittouu(cornerticks[0].get('y')) > inkex.unittouu(cornerticks[1].get('y')):
                xticks.append(cornerticks[0])
                yticks.append(cornerticks[1])
            else:
                xticks.append(cornerticks[1])
                yticks.append(cornerticks[0])

        del cornerticks


        # 3. Resize figure ####################################################
        # 3a. Group all
        group = etree.SubElement(root_node, inkex.addNS('g', 'svg'))
        group.attrib['id'] = 'gChamon'

        for element in [el for el in root_node.iter()
                        if el.tag in [inkex.addNS('path', 'svg'),
                                      inkex.addNS('text', 'svg')]]:
            group.append(element)

        # 3b. Rescale
        # Estimate plot area size
        box_width = bbox['right']['coord'][0]['x'] - bbox['left']['coord'][0]['x']
        box_height = bbox['bottom']['coord'][0]['y'] - bbox['top']['coord'][0]['y']

        # Evaluate scaling factor given desired width
        scaling = width / box_width

        # Scale plot
        applyTransformToNode(parseTransform('scale(%s,%s)' % (scaling, scaling)), group)

        # 4. Fix text #########################################################
        # Compute font sizes
        ticks_size_str = str(ticks_size / scaling) + 'px'
        labels_size_str = str(labels_size / scaling) + 'px'

        # Format all text
        for element in root_node.xpath('//svg:tspan', namespaces=inkex.NSS):
            # 4a. Remove manual kern
            element.set('x', element.get('x').split(' ')[0])
            element.set('y', element.get('y').split(' ')[0])

            # 4b. Change font and add styling
            style = parseStyle(element.get('style'))
            style['font-family'] = font_family
            style['-inkscape-font-specification'] = font_family
            style['font-style'] = 'normal'
            style['font-stretch'] = 'normal'
            style['line-height'] = '125%'

            # Modify element style
            element.set('style', formatStyle(style))
            element.getparent().set('style', formatStyle(style))

        # 4c. Format ticks
        for element in xticks:
            style = parseStyle(element[0].get('style'))

            # Format
            style['font-size'] = ticks_size_str
            style['text-align'] = 'center'
            style['text-anchor'] = 'middle'

            # Modify element style
            element.set('style', formatStyle(style))
            element[0].set('style', formatStyle(style))

        for element in yticks:
            style = parseStyle(element[0].get('style'))

            # Format
            style['font-size'] = ticks_size_str
            style['text-align'] = 'right'
            style['text-anchor'] = 'end'

            # Modify element style
            element.set('style', formatStyle(style))
            element[0].set('style', formatStyle(style))

        # 4d. Format labels
        if xlabel != None:
            style = parseStyle(xlabel[0].get('style'))
            style['font-size'] = labels_size_str
            style['text-align'] = 'center'
            style['text-anchor'] = 'middle'
            xlabel.set('style', formatStyle(style))
            xlabel[0].set('style', formatStyle(style))

        if ylabel != None:
            style = parseStyle(ylabel[0].get('style'))
            style['font-size'] = labels_size_str
            style['text-align'] = 'center'
            style['text-anchor'] = 'middle'
            ylabel.set('style', formatStyle(style))
            ylabel[0].set('style', formatStyle(style))

        # 5. Reposition texts (align, place) ##################################
        # 5a. Align labels
        if xlabel != None:
            y = bbox['bottom']['coord'][0]['y'] + (ticks_size + 1.1*labels_size)/scaling
            x1 = bbox['bottom']['coord'][0]['x']
            x2 = bbox['bottom']['coord'][1]['x']
            xlabel.set('x', str(min(x1,x2) + abs(x1-x2)/2))
            xlabel.set('y', str(y))

        if ylabel != None:
            x = bbox['left']['coord'][0]['x'] - (2.5*ticks_size)/scaling
            y1 = bbox['left']['coord'][0]['y']
            y2 = bbox['left']['coord'][1]['y']
            ylabel.set('y', str(x))
            ylabel.set('x', str(-(min(y1,y2) + abs(y1-y2)/2)))

        # 5b. Align xticks
        y = bbox['bottom']['coord'][0]['y'] + (ticks_size + 1)/scaling

        for t in xticks:
            xt = inkex.unittouu(t.get('x'))
            x = float('inf')

            for g in xgrid:
                xg = parsePath(g.get('d'))[0][1][0]
                if abs(xg-xt) < abs(x-xt):
                    x = xg

            t.set('x', str(x))
            t[0].set('x', str(x))
            t.set('y', str(y))
            t[0].set('y', str(y))

        # 5c. Align yticks
        x = bbox['left']['coord'][0]['x'] - 3/scaling

        for t in yticks:
            yt = inkex.unittouu(t.get('y'))
            y = float('inf')

            for g in ygrid:
                yg = parsePath(g.get('d'))[0][1][1]
                if abs(yg-yt) < abs(y-yt):
                    y = yg

            t.set('x', str(x))
            t[0].set('x', str(x))
            t.set('y', str(y + ticks_size/2 - 0.4))
            t[0].set('y', str(y + ticks_size/2 - 0.4))

        # 6. Adjust plot traces (color, width) ################################
        # Get curves
        curves = {}

        for path in root_node.xpath('//svg:path', namespaces=inkex.NSS):
            style = parseStyle(path.get('style'))
            if style['stroke'] != '#000000':
                if style['stroke'] in curves.keys():
                    curves[style['stroke']].append(path)
                else:
                    curves[style['stroke']] = [path]

        # Format curves
        color_idx = 0
        for color in curves.keys():
            for path in curves[color]:
                style = parseStyle(path.get('style'))

                # 5a. Alter thickness of plot traces
                style['stroke-width'] = str(line_width/scaling) + 'px'

                # 5b. Alter colors of plot traces
                style['stroke'] = color_pal[color_idx]

                path.set('style', formatStyle(style))

            color_idx = (color_idx + 1) % len(color_pal)


        # 6. Additional fixups (grids) ########################################


if __name__ == '__main__':
    e = ChamonEffect()
    e.affect()
