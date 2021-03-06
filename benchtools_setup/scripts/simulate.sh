#!/bin/sh

echo "COMMAND LINE: " "$@"
echo "BENCHTOOLS_PARAMS: $BENCHTOOLS_PARAMS"
echo "BENCHTOOLS_INSTANCE: $BENCHTOOLS_INSTANCE"

CB_PATH=${BENCHTOOLS_PARAMS%%;*}
str3=${BENCHTOOLS_PARAMS##*;}
temp=${BENCHTOOLS_PARAMS#$CB_PATH;}
SPECS=${temp#;$str3}

echo ${BENCHTOOLS_PARAMS}
echo ${CB_PATH}
echo ${SPECS}



echo "python ${CB_PATH}/cbverifier/driver.py -m simulate -z -t ${BENCHTOOLS_INSTANCE} -s ${SPECS}"
python "${CB_PATH}/cbverifier/driver.py" -m simulate -z -t ${BENCHTOOLS_INSTANCE} -s "${SPECS}"
