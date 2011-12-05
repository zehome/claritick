# -*- coding: utf-8 -*-

from qbuilder.representations.matplotlib.base import MatplotlibBaseRepresentation as BaseRepresentation
from qbuilder.representations.matplotlib.base import TimedeltaFormatter, TimedeltaLocator
import matplotlib.pyplot as plt

class MatplotlibScatter(BaseRepresentation):
    def represent(self):
        data = self.qbuilder.all_data()
        Z = list(set([D[2:] for D in data]))
        C = []
        for i in range(len(Z)):
            C.append(self.colors.next())
        fig = plt.figure()
        lines = fig.add_subplot(111)
        # TODO : user should be able to choose this or we should
        # automatically decide depending on the range of the data
        logarithmic = True
        if logarithmic:
            lines.set_yscale('log', basey = 60)
        for i, z in enumerate(Z):
            X = [D[1] for D in data if D[2:] == z]
            Y = [self.makefloatfromstuff(D[0]) for D in data if D[2:] == z]
            lines.scatter(X,Y,c=C[i],s=3,linewidth=0,label=" ".join(z))
        lines.legend( )
        if self.title:
            lines.set_title(self.title)
        fig.autofmt_xdate()
        lines.yaxis.set_major_formatter(TimedeltaFormatter())
        plt.show(block=True,open_plot=False)
