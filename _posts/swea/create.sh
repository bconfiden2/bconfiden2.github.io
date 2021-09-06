dt=$(date '+%Y%m%d')

if [ $# == 0 ] ; then
	echo ERROR : add param
	exit 0
fi

year=${dt:0:4}
month=${dt:4:2}
day=${dt:6:2}

if [ -f sample.md ] && [ $# -ge 1 ] ; then
	cp sample.md $year-$month-$day-swea-$1.md
fi

if [ $# == 2 ] ; then
	code $year-$month-$day-swea-$1.md
fi
