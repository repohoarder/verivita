# callback-verification
Dynamic verification using callbacks.


# External Dependencies
- PySMT
- TraceRunner
- Google protobuf 3.0

*WARNING* we require protobuf version 3.0


# Installation

1. You need to install PySMT with z3 (follow the instruction at https://github.com/pysmt/pysmt)

2. Compile the protobuffer interface (from the root directory of the project). You need the TraceRunner repository for this.
```
protoc -I=<TraceRunner-repo>/TraceRunnerRuntimeInstrumentation/tracerunnerinstrumentation/src/main/proto/edu/colorado/plv/tracerunner_runtime_instrumentation --python_out=./cbverifier/traces <TraceRunner-repo>/TraceRunnerRuntimeInstrumentation/tracerunnerinstrumentation/src/main/proto/edu/colorado/plv/tracerunner_runtime_instrumentation/tracemsg.proto
```

3. add the cbverifier path to the PYTHONPATH environment variable



# Usage

## Verify a trace:
```python cbverifier/driver.py -t <trace-file> -s <spec-files> -k <bmc-bound>```

Example:
```
python cbverifier/driver.py -f json -t cbverifier/test/examples/trace1.json -s cbverifier/test/examples/spec1.spec -k 2
```

`<spec-files>` is a colon separated list of paths to specification files.

Note: the `-f json` flag can be used if the trace is in json format. For binary format traces (the default generated by trace runner) no flags are needed.

Note: the verifier tool has different parameters, like the `-k` bound. Use `-h` to get an help screen that explain them.


## Check the input files (traces and specs) and print them as output
```python cbverifier/driver.py -m check-files -t <trace-file> -s <spec-files>```


## Print the list of grounded specifications
```python cbverifier/driver.py -m show-ground-specs -t <trace-file> -s <spec-files>```

## Simulate a trace

The following command simulate the trace and applies the constraints
described by the set of specifications. This step can be used to
validate a set of specifications againts a concrete trace of execution.
```
python driver.py  -t <trace-file> -s <spec-files> -m simulate
```

The command allows to simulate a trace specified by an arbitrary order
of top-level callbacks with the paramter `-w`.

For example, consider the trace:

```
TRACE:
[0] [CB] void com.ianhanniballake.contractiontimer.ContractionTimerApplication.<init>() (612b562) 
  [1] [CI] void android.app.Application.<init>() (612b562) 
[4] [CB] void com.ianhanniballake.contractiontimer.ContractionTimerApplication.attachBaseContext(android.content.Context) (612b562,6a2a16b) 
  [5] [CI] void android.content.ContextWrapper.attachBaseContext(android.content.Context) (612b562,6a2a16b) 
[8] [CB] java.lang.String com.ianhanniballake.contractiontimer.ContractionTimerApplication.getPackageName() (612b562) 
  [9] [CI] java.lang.String android.content.ContextWrapper.getPackageName() (612b562) 
[12] [CB] java.lang.ClassLoader com.ianhanniballake.contractiontimer.ContractionTimerApplication.getClassLoader() (612b562) 
  [13] [CI] java.lang.ClassLoader android.content.ContextWrapper.getClassLoader() (612b562) 
[16] [CB] com.ianhanniballake.contractiontimer.provider.ContractionProvider.<clinit> (NULL) 
  [17] [CI] void android.content.UriMatcher.<init>(int) (f426055,-1) 
  [19] [CI] void android.content.UriMatcher.addURI(java.lang.String,java.lang.String,int) (f426055,com.ianhanniballake.contractiontimer,contractions,1) 
  [21] [CI] void android.content.UriMatcher.addURI(java.lang.String,java.lang.String,int) (f426055,com.ianhanniballake.contractiontimer,contractions/#,2) 
[24] [CB] void com.ianhanniballake.contractiontimer.provider.ContractionProvider.<init>() (ca6f21a) 
```

With the command:
```
python driver.py  -t <trace-file> -s <spec-files> -m simulate -w 8:0
```
we test if the trace
```
[8] [CB] java.lang.String com.ianhanniballake.contractiontimer.ContractionTimerApplication.getPackageName() (612b562) 
  [9] [CI] java.lang.String
  android.content.ContextWrapper.getPackageName() (612b562) 
[0] [CB] void com.ianhanniballake.contractiontimer.ContractionTimerApplication.<init>() (612b562) 
  [1] [CI] void android.app.Application.<init>() (612b562) 
```
can be simulated according to the set of specifications.


## Run unit tests:
```nosetests```



# Current limitations - to be solved

- DONTCARE are still not handled by the grounding

- bitmask: add the bitmask to the encoding
