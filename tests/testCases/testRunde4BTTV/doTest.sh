#!/bin/bash

F=runde-5.txt

rm -f $F

../../ttSchweizer.py >/dev/null
if [ ! -e "$F" ]
then
    echo "$F existiert nicht, sollte aber erstellt werden."
fi

if ! grep -q "D <> A" $F
then
    echo "Die Begegnung D <> A muss in $F vorhanden sein"
fi

if ! grep -q '\(H <> B\)\|\(B <> H\)' $F
then
    echo "Die Begegnung B <> H muss in $F vorhanden sein"
fi

rm $F
