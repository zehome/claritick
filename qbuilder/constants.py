import os
import itertools

QB_STYPE_MAX, QB_STYPE_MIN, QB_STYPE_AVG, QB_STYPE_MED, QB_STYPE_VAR, QB_STYPE_STD, QB_STYPE_CNT, QB_STYPE_CRP = [str(i) for i in range(8)]
QB_STYPE_NAMES = {
    QB_STYPE_MAX : u"Maximum",
    QB_STYPE_MIN : u"Minimum",
    QB_STYPE_AVG : u"Average",
    QB_STYPE_MED : u"Median",
    QB_STYPE_VAR : u"Variance",
    QB_STYPE_STD : u"Standard deviation",
    QB_STYPE_CNT : u"Element count",
    QB_STYPE_CRP : u"Element count after removing those over percentile",
    }
QB_FRISE_COLORS = itertools.cycle(['GoldenRod', 'Tan', 'DodgerBlue', 'OliveDrab', 'Crimson', 'FireBrick', 'DarkViolet', 'Green', 'Chocolate', '#808080',])
