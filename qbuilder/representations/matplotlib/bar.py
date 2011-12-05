# -*- coding: utf-8 -*-

from qbuilder.representations.matplotlib.base import MatplotlibBaseRepresentation as BaseRepresentation
from numpy import arange
import matplotlib.pyplot as plt

class MatplotlibBar(BaseRepresentation):
    def round_decade(self, nbr, symb):
        if symb == "<":
            while nbr % 10 != 0:
                nbr -= 1
            return nbr
        elif symb == ">":
            while nbr % 10 != 0:
                nbr += 1
            return nbr
        return 0

    def fillkeyname(self, data, poskey):
        keyname = []
        for elm in data:
            if keyname == []:
                keyname.append(elm[poskey])
            if elm[poskey] not in keyname:
                keyname.append(elm[poskey])
        return keyname

    def fillstuffname(self, data, posname):
        stuffname = []
        for elm in data:
            if stuffname == []:
                stuffname.append(elm[posname])
            if elm[posname] not in stuffname:
                stuffname.append(elm[posname])
        return stuffname

    def fillvalues(self, data, stuffname, posname, posvalue):
        values = []
        index = 0
        valmax = data[0][posvalue]
        valmin = data[0][posvalue]
        while index < len(stuffname):
            tmp = []
            current_key = stuffname[index]
            index2 = 0
            while index2 < len(data):
                if data[index2][posname] == current_key:
                    tmp.append(data[index2][posvalue])
                    if data[index2][posvalue] > valmax:
                        valmax = data[index2][posvalue]
                    if data[index2][posvalue] < valmin:
                        valmin = data[index2][posvalue]
                index2 += 1
            values.append(tmp)
            index += 1
        return values, valmax, valmin

    def colorslegend(self, idbar):
        colorsleg = []
        for elm in idbar:
            colorsleg.append(elm[0])
        return colorsleg

    def represent(self):
        data = self.qbuilder.all_data()
        keyname = self.fillkeyname(data, poskey = 2)
        stuffname = self.fillstuffname(data, posname = 1)
        values, valmax, valmin = self.fillvalues(data, stuffname, posname = 1, posvalue = 0)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        width = 0.25
        N = len(keyname)
        ind = arange(N)
        index = 0
        space = 0
        space_between_each_column = 0.05
        idbar = []
        while index < len(stuffname):
            idbar.append(ax.bar(ind + space, values[index], width - space_between_each_column, color = self.colors[index]))
            index += 1
            space += width
        mymin = (self.round_decade(valmin, "<")) / 2
        mymax = (self.round_decade(valmax, ">")) * 2
        grad = self.round_decade((mymin + mymax) / 5, ">")
        ax.set_ylabel("Quantite de produit")
        if self.title:
            ax.set_title(self.title)
        ax.set_xticks(ind + width)
        ax.set_xticklabels(keyname)
        ax.set_yticks(arange(mymin, mymax, grad))
        ax.legend(self.colorslegend(idbar), stuffname)
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.text(rect.get_x() + rect.get_width() / 2., 1.05 * height, "%d" % int(height), ha= "center", va= "bottom")
        index = 0
        while index < len(stuffname):
            autolabel(idbar[index])
            index += 1
        plt.show(block=True, open_plot=False)
