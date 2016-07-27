EigenFace Explorer
======

This repository contains the source code for EigenFace explorer - a web app that lets you create eigenface projections for an arbitrary headshot.

A couple things of note if you'd like to play around with this locally:
- Run hello.py to run the app
- Prior to running the app, you'll need to run eigenfaces.py. This is a script that pulls the source images and creates the pickle file of eigenfaces. The file is too large for git to handle normally.
- You'll need a bunch of python packages to run this locally. The main ones are sklearn, numpy, and pickle. Look at the import statements in hello.py, process_photos.py, and eigenfaces.py for a full list.
