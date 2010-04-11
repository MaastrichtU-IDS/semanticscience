#!/bin/sh

# Edit the following to match your local environment;  the syntax
# for calling this shell script should be:  mopac.sh input output.
# Depending on which version of mopac you have, you may need to remove
# the "<" and ">" symbols below, or make other changes.  For example,
# some versions of mopac expect the input file to be "FOR005" and the
# output to be "FOR006"; some versions require the input file to end in 
# ".DAT", etc., etc.

ln mopac.in FOR005
"$ACHOME/exe/mopac"
mv FOR006 mopac.out
rm -f FOR0??
