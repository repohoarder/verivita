cp ../target/universal/trace-query-1.0-SNAPSHOT.zip .
unzip trace-query-1.0-SNAPSHOT.zip
docker build -t fixr_verivita_web_search .
rm -r trace-query-1.0-SNAPSHOT.zip
rm -r trace-query-1.0-SNAPSHOT

