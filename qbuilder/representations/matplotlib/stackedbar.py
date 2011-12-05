# -*- coding: utf-8 -*-

from qbuilder.representations.matplotlib.base import MatplotlibBaseRepresentation as BaseRepresentation
from numpy import arange
import matplotlib.pyplot as plt

class MatplotlibStackedBar(BaseRepresentation):
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

    def createstacked(self, values, index):
        if index == 0:
            return values[index]
        dataadded = []
        incre = 0
        while incre < len(values[index]):
            dataadded.append(values[index][incre] + values[index - 1][incre])
            incre += 1
        return dataadded

    def represent(self):
        data = self.qbuilder.all_data()
        keyname = self.fillkeyname(data, poskey = 2)
        stuffname = self.fillstuffname(data, posname = 1)
        values, valmax, valmin = self.fillvalues(data, stuffname, posname = 1, posvalue = 0)
        fig = plt.figure()
        md = fig.add_subplot(111)
        width = 0.25
        N = len(keyname)
        ind = arange(N)
        index = 0
        idbar = []
        while index < len(stuffname):
            if index == 0:
                idbar.append(md.bar(ind, values[index], width, color = self.colors[index]))
            else:
                idbar.append(md.bar(ind, values[index], width, color = self.colors[index], bottom = self.createstacked(values, index - 1)))
            index += 1
        mymin = (self.round_decade(valmin, "<")) / 2
        mymax = (self.round_decade(valmax, ">")) * len(stuffname)
        grad = self.round_decade((mymin + mymax) / 10, ">")
        md.set_ylabel("Quantite de produit") # A rendre parametrable
        if self.title:
            md.set_title(self.title)
        md.set_xticks(ind + width)
        md.set_xticklabels(keyname)
        md.set_yticks(arange(mymin, mymax + len(stuffname) * grad, grad))
        md.legend(self.colorslegend(idbar), stuffname)
        plt.show(block=True, open_plot=True)
