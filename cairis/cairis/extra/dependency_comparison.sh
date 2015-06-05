#!/bin/bash
SCRIPT_DIR=$(cd "$( dirname "${BASH_SOURCE[0]}")" && pwd)

function check_snakefood {
	sfood_path=$(which sfood)
	check=$?
	echo $check
	sfood_flatten_path=$(which sfood-flatten)
	check=$(($?+$check))
	echo $check
}

function snakehood_test {	
	echo "Looking for dependencies..."
	CAIRIS_DIR="$(dirname "$SCRIPT_DIR")"
	sfood -fuqi ../cairisd.py | sfood-flatten | sed -e "s#"$CAIRIS_DIR"##g" | sort > $SCRIPT_DIR/dependencies.txt
	total_dep=$(sfood -fuqi ../cairis.py | sfood-flatten | sed -e "s#"$CAIRIS_DIR"##g" | wc -l)
	cur_dep=$(cat dependencies.txt | grep .py | wc -l)
	echo -e "Original dependency count: $total_dep\nCurrent dependency count: $cur_dep\n"
	echo "The list of CAIRIS-web dependencies can be found in $SCRIPT_DIR/dependencies.txt"
}

check_snakefood

if [ "$check" -eq "0" ]
then
	echo Snakehood found. Continuing...
	snakehood_test
else
	echo Snakehood is not installed. Please install snakehood by using 'apt-get install snakehood'
	exit 1
fi
