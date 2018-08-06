CREATE DATABASE trace_query;
\c trace_query
CREATE TABLE method(
	method_id SERIAL PRIMARY KEY,
	signature VARCHAR(1024) NOT NULL,
	first_framework_override VARCHAR(1024),
	/*application_class VARCHAR(1024), excluding so messages merge between traces*/
	is_callback BOOLEAN,
	is_callin BOOLEAN
);
CREATE TABLE method_param(
	param_id SERIAL PRIMARY KEY,
	method_id integer NOT NULL,
	param_position integer NOT NULL, /* 0 for return value 1 for reciever rest for params*/
	CONSTRAINT method_param_method_id_fkey FOREIGN KEY (method_id) 
		REFERENCES method (method_id) MATCH SIMPLE
);
CREATE TABLE traces(
	trace_id SERIAL PRIMARY KEY,
	app_name VARCHAR,
	trace_name VARCHAR,
	git_repo VARCHAR,
	trace_runner_version integer,
	trace_data_path VARCHAR /* link to data, append to $DATAROOT */
);
CREATE TABLE aggrigate_edge(
	start_method_param integer NOT NULL,
	end_method_param integer NOT NULL,
	PRIMARY KEY (start_method_param, end_method_param),
	trace_count integer NOT NULL,
	app_count integer NOT NULL,
	FOREIGN KEY (start_method_param) REFERENCES method_param (param_id),
	FOREIGN KEY (end_method_param) REFERENCES method_param (param_id)
);
CREATE TABLE trace_edge(
	edge_id SERIAL PRIMARY KEY,
	start_method_param integer NOT NULL,
	end_method_param integer NOT NULL,
	trace_id integer NOT NULL,
	FOREIGN KEY (trace_id) REFERENCES traces (trace_id),
	FOREIGN KEY (start_method_param) REFERENCES method_param (param_id),
	FOREIGN KEY (end_method_param) REFERENCES method_param (param_id)
);
