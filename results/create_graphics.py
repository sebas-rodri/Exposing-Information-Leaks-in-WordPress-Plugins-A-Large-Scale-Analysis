import duckdb
import matplotlib.pyplot as plt
import pandas as pd
import sys

if len(sys.argv) != 2:
    print("Usage: python create_graphics.py <path_to_duckdb>")
    sys.exit(1)
    
con = duckdb.connect(sys.argv[1])

#Static Analysis
#Count Plugins that were handled successfully
#Range num downloaded from max to min also avg
#Count Semgrep findings per rule
#Count Errors in run

#For semgrep category what was the plugin inside with max, min downloads and what is the avg
#Find name of logfile -> Try to categorize, here get lines in parse out part containing log, then just get top 5 names, and try to build categorizes e.g error, debug etc


#Dynamic Analysis
#Total of AJAX ROUTES called / Total of REST called
#Comparison to unique Endpoints or AJAX action
#Describe Wp-CLI
#Describe Test cases
#Plot from sorted max to low x unique rest called, y active installations
#Plot x unique AJAX, y active installations
#What about the zips?
#Count function_hooks, interesting hooks apart