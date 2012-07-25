#!/usr/bin/env python
#-*- coding: utf-8 -*-
"""
Lancement du Query Builder
"""

# Hack to be able to launch the qbuilder from its own folder
import sys
sys.path.append("..")
####

from qbuilder.main import main
from optparse import OptionParser
import logging

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("--loadjson", dest="jsonfile",
                      help="Load query instructions from JSON file", metavar="FILE")
    parser.add_option("--sql",
                      action="store_true", dest="build_query", default=False,
                      help="Generate and print the SQL query")
    parser.add_option("--get_data",
                      action="store_true", dest="get_data", default=False,
                      help="Generate the SQL and print the resulting data")
    parser.add_option("-v", "--verbose", default = 0,
                      action="count", dest="verbosity",
                      help="Add many -v to increment verbosity (from critical messages only (default) to debug (4 -v))"
                      )
    parser.add_option("-f", "--folder", default = 'sample',
                      dest="modelsfolder",
                      help="Folder that describes your database (models and configuration - see sample)"
                      )
    parser.add_option("-d", "--database", default ='auto:auto@bingo:5432/qbuilder',
                      dest="databaseurl",
                      help="The right part of the database Url. [username:password@host:port/database]")
    parser.add_option("-s", "--statistics",
                      dest="statistics", default=False,
                      help="[A TRADUIRE]: Affiche: Median/Max/Min/Variance/Ecart-type/: Accepte les percentiles")
    parser.add_option("-r", "--representation",
                      dest="representation", default='TextRepresentation',
                      help="Choose how you want to display the result")
    (options, args) = parser.parse_args()

    # Prepare a basic logger
    # We take the logging level from the verbosity option
    # if the verbosity is not in the dictionnary, that means it's higher
    # than DEBUG and should be DEBUG
    logging.basicConfig(level = {0:logging.CRITICAL, 1:logging.ERROR, 2:logging.WARNING, 3:logging.INFO}.get(options.verbosity, logging.DEBUG))
    main(options, logging.getLogger("querybuilder"), *args)
