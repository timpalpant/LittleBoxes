DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHONPATH=${DIR}/lib-python python benchmark_solvers.py data/nyt/daily-2016-01-*.puz $@
