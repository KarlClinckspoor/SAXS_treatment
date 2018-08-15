---
title: SAXS tools used in my PhD
author: Karl
---

# ESRF data treatment

Contains scripts regarding the treatment of data obtained from ESRF ID02. Also has scripts to work in tandem with `superSAXS`, a tool developed by Jan Skov Pedersen and Reginaldo Oliveira.

Please excuse the non-Pythonic code, it was my first real project.

* `Average_SAXS_kinetics.py`: Gathers all the data files in the folder, groups them and averages them.
* `Subtract_water.py`: Subtracts the intensities of the background, here thought of as water.
* `Find_time_between_runs.py`: Either calculates the spacing of each frame from the `ccdframes` command parameters or, starting with the initial parameters, extracts the datastamps of each experimental file and then calculates the spacing based on that.
* `converting_files.py`: Converts the experimental files from ESRF to a format compatible with the `superSAXS` program. Also can create a file compatible with the batch functionality of `superSAXS`.
* `converting_results.py`: `superSAXS` generates a results file that can be difficult/tedious to read or plot. This script converts it to a more palatable, but less human-readable, csv file
* `plot_everything.py`: plots and saves all the resulting files.

# WLM models

This folder contains a few scripts that model Kratky-Porod core-shell structures with the PRISM model for intermicellar interactions. It also has a tool to plot this data and vary the parameters interactively, and also can compare the model to real data, and adjust the parameters accordingly.