# -*- coding: utf-8 -*-

from qbuilder.representations.base.baserepr import BaseRepresentation
import pprint

class TextRepresentation(BaseRepresentation):
    def represent(self):
        data = self.qbuilder.all_data()
        pp = pprint.PrettyPrinter(indent = 4)
        pp.pprint(data)
