import argparse
import re


def emit_regexps(name_prefix, base_types, methodmap):
    regexp_list = []
    for method in methodmap:
        r_start =  "REGEXP " + name_prefix + method[1] + "(f) = [("

        or_clauses = []
        for base_type in base_types:
            or_clauses.append("[" + method[0] + "] [ENTRY] [f] " + method[2] + " " + base_type + "." + method[3])

        regexp = r_start + "\n    " + "\n    |\n    ".join(or_clauses) + "\n)]"
        regexp_list.append(regexp)
    print "//Auto generated by fragment-alias-gen.py do not edit\n" + ";\n".join(regexp_list)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Combine possible method names with types in subexpressions (REGEXP)')
    parser.add_argument('--base_types', type=str,
                        help="List of all the possible types of objects implementing method",required=True)
    parser.add_argument('--methods', type=str,
                        help="methods to alias, [cb/ci];[human readable name];[signature]")
    parser.add_argument('--name_prefix', type=str,
                        help="prefix to append to method names")

    args = parser.parse_args()

    methodmap = []

    sigmatch = re.compile(".*\(.*\)$")

    with open(args.methods,'r') as callbacks_file:
        for line in callbacks_file:
            split_line = line.strip().split(";")
            event_type = split_line[0]
            if event_type not in {"CB","CI"}:
                raise Exception("Line must be declared callback or callin")
            alias = split_line[1]
            if len(alias.split(" ")) != 1:
                raise Exception("remove space from name")

            return_type = split_line[2]


            methodsignature = split_line[3]
            if sigmatch.match(methodsignature) is None:
                raise Exception("bad signature: " + methodsignature)
            methodmap.append((event_type,alias, return_type,methodsignature))

    fragment_types = []
    with open(args.base_types,'r') as fragment_types_file:
        for line in fragment_types_file:
            fragment_types.append(line.strip())
    emit_regexps(args.name_prefix, fragment_types, methodmap)