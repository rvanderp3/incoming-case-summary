# Overview

Performs a query of case data and builds a simple HTML report.  Internal systems are queried and host the report.  Their urls are not included in the code or README.  The `clusterUid` and `caseNo` are critical variables that are expanded in the URL.

~~~
export HYDRA_PASSWORD=
export HYDRA_USERNAME=
export HYDRA_PASSWORD=
export TELEMETRY_URL=https://site.com/&var-_id={clusterUid}
export CASE_URL=https://site.com/support/cases/#/case/{caseNo}
~~~

To run the tool export the variables above and run:

~~~
./build_report.py
~~~