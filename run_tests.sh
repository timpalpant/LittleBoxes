DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHONPATH=${DIR}/lib-python py.test -vvv ${DIR}/lib-python
