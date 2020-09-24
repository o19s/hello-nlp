PYTHONPATH=`pwd` \
eval $(egrep -v '^#' elasticsearch.conf | xargs) \
pytest -W ignore tests/units --cov-report xml:cov.xml --cov .