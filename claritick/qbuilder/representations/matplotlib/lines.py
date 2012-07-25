# -*- coding: utf-8 -*-

from qbuilder.representations.matplotlib.base import MatplotlibBaseRepresentation as BaseRepresentation

from pylab import *

class MatplotlibLines(BaseRepresentation):
    def represent(self):
        data = self.qbuilder.all_data()
        my_plots = []
        Z = set([D[2:] for D in data])
        for z in Z:
            X = [D[1] for D in data if D[2:] == z]
            Y = [self.makefloatfromstuff(D[0]) for D in data if D[2:] == z]
            my_plots.append(plot(X,Y))
        import pdb
        xlabel(data[0].keys()[0])
        ylabel(data[0].keys()[1])
        if self.title:
            title(self.title)
        f = gcf()
        f.legend(my_plots,Z)
        # Example of how to manage events:
        #def event_handler(*args, **kwargs):
        #    print "EVENT !",args, kwargs
        #f.canvas.mpl_connect('button_release_event', event_handler)
        #f.canvas.mpl_connect('button_press_event', event_handler)
        #f.canvas.mpl_connect('motion_notify_event', event_handler)
        #f.canvas.mpl_connect('key_press_event', event_handler)
        #f.canvas.mpl_connect('key_release_event', event_handler)

        # Example of a simple button
        #next_target_button = matplotlib.widgets.Button(axes([0.1, 0.05, 0.06, 0.04]), 'Next')
        #def next_target_callback(event):
        #    # Modify data
        #    self.modify_data()
        #    # Redraw
        #    f.canvas.draw()
        #    print "Next was called..."
        #next_target_button.on_clicked(next_target_callback)

        show(block=True,open_plot=False)
