dt=$(date)

if [ $# == 0 ] ; then
	echo ERROR : add param
	exit 0
fi

year=${dt:0:4}
month=${dt:6:2}
day=${dt:10:2}

if [ -f sample.md ] && [ $# == 1 ] ; then
	cp sample.md $year-$month-$day-boj-$1.md
fi

if [ $# == 2 ] ; then
	code $year-$month-$day-boj-$1.md
fi
