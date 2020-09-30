#!/bin/bash

docker run -it -v $PWD/.config:/root/.config scl3/task_hii_popdens python hii_popdens.py -r 'Afrotropic' -d '2018-01-01'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_popdens python hii_popdens.py -r 'Australasia' -d '2018-01-01'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_popdens python hii_popdens.py -r 'Indomalayan' -d '2018-01-01'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_popdens python hii_popdens.py -r 'Nearctic' -d '2018-01-01'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_popdens python hii_popdens.py -r 'Neotropic' -d '2018-01-01'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_popdens python hii_popdens.py -r 'Oceania' -d '2018-01-01'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_popdens python hii_popdens.py -r 'Palearctic' -d '2018-01-01'
docker run -it -v $PWD/.config:/root/.config scl3/task_hii_popdens python hii_popdens.py -r 'HighArctic' -d '2018-01-01'
