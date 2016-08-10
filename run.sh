DATE=`date +"%Y-%m-%d-%H:%M"`;

cat feedsRanked.txt | sort -n -r  |  cut -f2 -d" " | nice -15 python2.6 test6.py 2>&1 | tee "$DATE.txt";
cat "$DATE.txt" | mutt -s "zbozi - $DATE" nadvornik.jiri@gmail.com;

