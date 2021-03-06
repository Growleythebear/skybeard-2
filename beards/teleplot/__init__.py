#show spacecats test plugin
# Adapted from work by LanceMaverick
import telepot
import telepot.aio
from skybeard.beards import BeardChatHandler
from skybeard.predicates import regex_predicate
from skybeard.decorators import onerror
from skybeard.utils import get_args
from . import TelePlot
import re
import os
import sympy as sp
from numpy import linspace
from math import *


def format_msg(msg):
    text = msg['text']
    return ' '.join(get_args(text)).title()


class TelePlotSB(BeardChatHandler):
    __userhelp__ = """
    Makes plots with the /teleplot command. e.g:
    From two arrays: /teleplot [x1,x2,..,xN] [y1,y2,..,yN]
    From an expression: /teleplot (x**2+2*x+3)
    Additional options: -xaxis "label", -yaxis "label"
    Currently only index, add, subtract, divide, multiply 
    available for equation notation."
     """

    __commands__ = [
        ("teleplot", "makePlot", "make a plot." ),
    ]

    @onerror
    async def makePlot(self, msg):
        in_string = msg['text'].replace('/teleplot ', '')
        arrays = re.findall(r'(\[[\-\d\,\.\s]+\])+', in_string)
        eq_parser = TelePlot.eqn_parser
        options = re.findall(r'\-(\w+)\s\"([\w\d\/\s\.\-\'\)\(\,]+)', in_string)

        print("options: ")
        print(options)
        plotter = TelePlot.TelePlot()
        plotter.parseOpts(options)

        if len(arrays) < 1:
            opts2perform = TelePlot.checkandParse(in_string)
            if len(opts2perform) == 0:
                eqn = re.findall(r'(\([\w\(\)\d\s\-\+\*\/]+\))', in_string)
                eqn = eqn[0]
                for i in plotter.x:
                    equation = eqn.replace('x', '{}'.format(i)).replace('(', '').replace(')', '')
                    print(equation)
                    j = sp.simplify(equation)
                    plotter.y.append(j)
            else:
                strings_for_y = []
                for i in plotter.x:
                    res = re.findall(r'\(([\w\*\d\+\/\-\.\,]+)\)', in_string)[0]
                    final_string = res[0]
                    for key in opts2perform:
                        inside = opts2perform[key][1].replace('x', '{}'.format(i))
                        inside = sp.simplify(inside)
                        operation = eq_parser[key](inside)
                        final_string = final_string.replace('x'.format(opts2perform[key][0], opts2perform[key][1]), '{}'.format(operation))
                        print(final_string)
                    strings_for_y.append(final_string)
                for y in strings_for_y:
                    j = sp.simplify(y)
                    plotter.y.append(j)

        else:
            print("Arrays: ")
            assert len(arrays) == 2, "Error: Insufficient Number of Arrays Given."
            X = re.findall(r'([\d\.\-]+)', arrays[0])
            Y = re.findall(r'([\d\.\-]+)', arrays[1])
            print(X, Y)
        file_name = plotter.savePlot()
        await self.sender.sendPhoto(('temp.png', open('{}'.format(file_name), 'rb')))
        os.remove('{}'.format(file_name))
