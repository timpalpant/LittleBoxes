parallel -j 64 curl -O -L -b cookies.txt http://www.nytimes.com/svc/crosswords/v2/puzzle/daily-{}.puz ::: $(./dateloop.sh 2015-12-01 2015-12-13)
