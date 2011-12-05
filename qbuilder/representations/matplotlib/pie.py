# -*- coding: utf-8 -*-

from qbuilder.representations.matplotlib.base import MatplotlibBaseRepresentation as BaseRepresentation
import matplotlib.pyplot as plt

class MatplotlibPie(BaseRepresentation):
    def represent(self):
        data = self.qbuilder.all_data()
        fig = plt.figure()
        ax = plt.axes([0.1, 0.1, 0.8, 0.8])
        line = fig.add_subplot(111)
        if self.title:
            plt.title(self.title)
        values = []
        for elm in data:
            values.append(elm[0]) # A rendre paramétrable
        labels = []
        for elm in data:
            labels.append(elm[1]) # A rendre paramétrable
        valmax = max(values)
        explodes = []
        for elm in values:
            if elm == valmax:
                explodes.append(0.1)
            else:
                explodes.append(0)
        def my_autopct(pct):
            total = sum(values)
            val = int(pct * total / 100.0)
            return "{p:.1f}% ({v:d})".format(p=pct, v=val)
        line.pie(values, explode = explodes, labels = labels, colors = self.colors, autopct = my_autopct, shadow = True)
        plt.show(block = True, open_plot = False)

