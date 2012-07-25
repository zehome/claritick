import itertools

from qbuilder.representations.base.baserepr import BaseRepresentation
from qbuilder.lib import get_granularity

import matplotlib
matplotlib.use('module://mplh5canvas.backend_h5canvas')
from matplotlib.ticker import Locator, Formatter

class MatplotlibBaseRepresentation(BaseRepresentation):
    # itertools.cycle is infinite iterator, not len
    # colors = itertools.cycle(['b','g','r','c','m','y','k'])
    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']

class TimedeltaLocator(Locator):
    """
    Tries to place ticks at right places for timedeltas
    """
    MAJMIN = 5
    MAJMAX = 20
    MINMIN = 20
    MINMAX = 50
    def __init__(self, minor = False):
        self.mintickcount = self.MINMIN if minor else self.MAJMIN
        self.maxtickcount = self.MINMAX if minor else self.MAJMAX

    def __call__(self):
        """
        Returns the location of the ticks.
        Tries to keep between MAJMIN and MAJMAX ticks for major ticks
        and between MINMIN and MINMAX ticks for minor ticks
        """
        vmin, vmax = self.axis.get_view_interval()
        if vmax<vmin:
            vmin, vmax = vmax, vmin
        gran_name, gran_size, tick_count = get_granularity(vmax, self.mintickcount, self.maxtickcount, just_get_granularity = False, allow_non_sql_granularities = True)
        return range(int(vmin), int(vmax), int(gran_size))

class TimedeltaFormatter(Formatter):
    """
    Formats an integer to be display as a time
    """
    def __call__(self, x, pos=None):
        min = int(x / 60)
        sec = x % 60
        hr = int(min / 60)
        min = min % 60
        day = int(hr / 24)
        hr = hr % 24
        if hr == 12:
            hr = 0
            day = day + 0.5
        timedisplay = "%d:%2.2d:%2.2d" % (hr,min,sec) if hr or min or sec else ""
        daysdisplay = "%3.1fJ" % (day,) if day else ""
        return " ".join([daysdisplay, timedisplay])
