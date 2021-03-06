"""
Defines the AST nodes and structure for a SPEC formula.

TODO:
- Do we need a DAG representation for specs instead of a tree?
  TODO: add memoization
  - NOTE: since we are using tuples in python and the inner elements
    are not object, apart string, the formula representation is already
    ok.
- add walkers (e.g. explore the DAG of the formula)
"""
import sys


# SYMBOLS
TRUE          =  0
FALSE         =  1
ID            =  2
INT           =  3
FLOAT         =  4
PARAM_LIST    =  5
NIL           =  6
CALL_ENTRY    =  7
AND_OP        =  8
OR_OP         =  9
NOT_OP        = 10
SEQ_OP        = 11
STAR_OP       = 12
SPEC_SYMB     = 13
ENABLE_OP     = 14
DISABLE_OP    = 15
SPEC_LIST     = 16
DONTCARE      = 17
STRING        = 18
CI            = 19
CB            = 20
NULL          = 21
CALL_EXIT     = 22
ALIASES       = 23
ALIASES_LIST  = 24
NAMED_REGEXP  = 25
REGEXP_INST   = 26

inv_map = { 0 : "TRUE",
            1 : "FALSE",
            2 : "ID",
            3 : "INT",
            4 : "FLOAT",
            5 : "PARAM_LIST",
            6 : "NIL",
            7 : "CALL_ENTRY",
            8 : "AND_OP",
            9 : "OR_OP",
            10 : "NOT_OP",
            11 : "SEQ_OP",
            12 : "STAR_OP",
            13 : "SPEC_SYMB",
            14 : "ENABLE_OP",
            15 : "DISABLE_OP",
            16 : "SPEC_LIST",
            17 : "DONTCARE",
            18 : "STRING",
            19 : "CI",
            20 : "CB",
            21 : "NULL",
            22 : "CALL_EXIT",
            23 : "ALIASES",
            24 : "ALIASES_LIST",
            25 : "REGEXP",
            26 : "REGEXP_INST"}

################################################################################
# Node creation
################################################################################

def create_node(node_type, children):
    l = []
    l.append(node_type)
    for c in children: l.append(c)
    return tuple(l)

def new_nil(): return (NIL,)
def new_dontcare(): return (DONTCARE,)
def new_float(float_num): return (FLOAT, float_num)
def new_int(int_num): return (INT, int_num)
def new_id(id_string): return (ID, id_string)
def new_string(string_value): return (STRING, string_value)
def new_false(): return (FALSE,)
def new_true(): return (TRUE,)
def new_null(): return (NULL,)

def new_param(param_name, param_type, tails):
    return (PARAM_LIST, param_name, param_type, tails)

def new_ci(): return (CI,)
def new_cb(): return (CB,)

def new_call_entry(call_type, receiver, method_name, params):
    return (CALL_ENTRY, call_type, receiver, method_name, params)

def new_call_exit(assignee, call_type, receiver, method_name, params):
    # assignee at the end: so the rest is like the entry
    return (CALL_EXIT, call_type, receiver, method_name, params, assignee)

def new_named_regexp_inst(name, bound_vars):
    return (REGEXP_INST, name, bound_vars)

def new_and(p1,p2): return (AND_OP, p1, p2)
def new_or(p1,p2): return (OR_OP, p1, p2)
def new_not(p1): return (NOT_OP, p1)

def new_seq(p1,p2): return (SEQ_OP, p1, p2)
def new_star(p1): return (STAR_OP, p1)

def new_alias(alias_elem, tails):
    return (ALIASES_LIST, alias_elem, tails)

def new_enable_spec(regexp, atom, aliases):
    return (SPEC_SYMB, (ENABLE_OP, regexp, atom), aliases)

def new_disable_spec(regexp, atom, aliases):
    return (SPEC_SYMB, (DISABLE_OP, regexp, atom), aliases)

def new_named_regexp(name, bound_vars, regexp):
    return (NAMED_REGEXP, name, bound_vars, regexp)

def new_spec_list(spec, rest):
    return (SPEC_LIST, spec, rest)


################################################################################
# Access node
################################################################################

def get_node_type(node): return node[0]

const_nodes = (TRUE,FALSE,STRING,INT,FLOAT,NULL)
leaf_nodes = (TRUE,FALSE,STRING,INT,FLOAT,NULL,NIL,DONTCARE,ID)
logic_nodes = (AND_OP, OR_OP,NOT_OP)
regexp_nodes = (SEQ_OP,STAR_OP)
spec_nodes = (SPEC_SYMB,ENABLE_OP,DISABLE_OP)


def get_id_val(node): return node[1]

def get_call_assignee(node):
    assert CALL_EXIT == get_node_type(node)
    assert node[5] is not None
    return node[5]

def get_call_type(node):
    assert (CALL_ENTRY == get_node_type(node) or
            CALL_EXIT == get_node_type(node))
    assert node[1] is not None
    return node[1]

def get_call_receiver(node):
    assert (CALL_ENTRY == get_node_type(node) or
            CALL_EXIT == get_node_type(node))
    assert node[2] is not None
    return node[2]

def get_call_method(node):
    assert (CALL_ENTRY == get_node_type(node) or
            CALL_EXIT == get_node_type(node))
    assert node[3] is not None
    return node[3]

def get_call_params(node):
    assert (CALL_ENTRY == get_node_type(node) or
            CALL_EXIT == get_node_type(node))
    assert node[4] is not None
    return node[4]

# TODO: check where it is used
def get_call_signature(node):
    assert (CALL_ENTRY == get_node_type(node) or
            CALL_EXIT == get_node_type(node))
    method_name = get_call_method(node)

    param_types = []
    app_node = get_call_params(node)

    while (NIL != get_node_type(app_node)):
        ptype = get_param_type(app_node)
        assert ID == get_node_type(ptype) or NIL == get_node_type(ptype)

        if (ID == get_node_type(ptype)):
            param_types.append(get_id_val(ptype))
        else:
            param_types.append("NIL")
        app_node = get_param_tail(app_node)

    method_signature = new_id("%s(%s)" % (get_id_val(method_name),
                                          ",".join(param_types)))

    return method_signature


def get_regexp_node(node):
    assert SPEC_SYMB == get_node_type(node)
    assert node[1] is not None
    assert get_node_type(node[1]) in [ENABLE_OP, DISABLE_OP]

    regexpnode = (node[1])[1]
    assert regexpnode is not None
    return regexpnode

def get_spec_rhs(node):
    assert SPEC_SYMB == get_node_type(node)
    assert node[1] is not None
    assert get_node_type(node[1]) in [ENABLE_OP, DISABLE_OP]

    rhs = (node[1])[2]
    assert rhs is not None
    return rhs

def get_spec_aliases(node):
    assert SPEC_SYMB == get_node_type(node)
    assert node[2] is not None
    return node[2]

def is_spec_enable(node):
    assert SPEC_SYMB == get_node_type(node)
    assert node[1] is not None
    return get_node_type(node[1]) == ENABLE_OP

def is_spec_disable(node):
    assert SPEC_SYMB == get_node_type(node)
    assert node[1] is not None
    return get_node_type(node[1]) == DISABLE_OP

def get_param_name(node):
    assert PARAM_LIST == get_node_type(node)
    assert 4 == len(node)
    return node[1]

def get_param_type(node):
    assert PARAM_LIST == get_node_type(node)
    assert 4 == len(node)
    return node[2]

def get_param_tail(node):
    assert PARAM_LIST == get_node_type(node)
    assert 4 == len(node)
    return node[3]

def get_alias_old(node):
    assert ALIASES_LIST == get_node_type(node)
    assert 3 == len(node)
    (old, new) = node[1]
    return old

def get_alias_new(node):
    assert ALIASES_LIST == get_node_type(node)
    assert 3 == len(node)
    (old, new) = node[1]
    return new

def get_alias_tail(node):
    assert ALIASES_LIST == get_node_type(node)
    assert 3 == len(node)
    return node[2]


def get_named_regexp_id(node):
    assert NAMED_REGEXP == get_node_type(node)
    assert 4 == len(node)
    return node[1]

def get_named_regexp_vars(node):
    assert NAMED_REGEXP == get_node_type(node)
    assert 4 == len(node)
    return node[2]

def get_named_regexp_regexp(node):
    assert NAMED_REGEXP == get_node_type(node)
    assert 4 == len(node)
    return node[3]

def new_named_regexp_inst_name(node):
    assert REGEXP_INST == get_node_type(node)
    assert 3 == len(node)
    return node[1]

def new_named_regexp_inst_vars(node):
    assert REGEXP_INST == get_node_type(node)
    assert 3 == len(node)
    return node[2]

def new_named_regexp(name, bound_vars, regexp):
    return (NAMED_REGEXP, name, bound_vars, regexp)


################################################################################
# End - Node creation
################################################################################


def get_call_nodes(ast_node):
    def _get_call_nodes_rec(ast_node, call_set):
        node_type = get_node_type(ast_node)

        if (node_type in leaf_nodes):
            return call_set
        elif (node_type == SPEC_LIST or
              node_type == AND_OP or
              node_type == OR_OP or
              node_type == SEQ_OP or
              node_type == ENABLE_OP or
              node_type == DISABLE_OP):
            return _get_call_nodes_rec(ast_node[1],
                                       _get_call_nodes_rec(ast_node[2], call_set))
        elif (node_type == SPEC_SYMB):
            return _get_call_nodes_rec(ast_node[1], call_set)
        elif (node_type == NOT_OP or
              node_type == STAR_OP):
            return _get_call_nodes_rec(ast_node[1], call_set)
        elif (node_type == CALL_ENTRY or
              node_type == CALL_EXIT):
            call_set.add(ast_node)
            return call_set

    return _get_call_nodes_rec(ast_node, set())


def subs_alias(node, subs_map):
    node_type = get_node_type(node)

    if (node_type == TRUE): return node
    elif (node_type == FALSE): return node
    elif (node_type == NULL): return node
    elif (node_type == DONTCARE): return node
    elif (node_type == CI): return node
    elif (node_type == CB): return node
    elif (node_type == ID):
        # Perform the substitution
        if (node in subs_map):
            return subs_map[node]
        else:
            return node
    elif (node_type == INT or
          node_type == FLOAT or node_type == STRING):
        return node
    elif (node_type == PARAM_LIST):
        return node
    elif (node_type == CALL_ENTRY or
          node_type == CALL_EXIT):
        call_type = get_call_type(node)
        receiver = get_call_receiver(node)


        # now method name is void method
        mn = get_id_val(get_call_method(node))
        mn_splitted = mn.split(" ")
        if (len(mn_splitted) == 2):
            new = subs_alias(new_id(mn_splitted[1]), subs_map)
            method_name = new_id(mn_splitted[0] + " " +
                                 get_id_val(new))
        else:
            method_name = subs_alias(method_name, subs_map)

        params = get_call_params(node)

        if (CALL_EXIT == node_type):
            assignee = get_call_assignee(node)
            return new_call_exit(assignee, call_type, receiver, method_name, params)
        else:
            return new_call_entry(call_type, receiver, method_name, params)

    elif (node_type == AND_OP):
        return new_and(subs_alias(node[1], subs_map),
                       subs_alias(node[2], subs_map))
    elif (node_type == OR_OP):
        return new_or(subs_alias(node[1], subs_map),
                      subs_alias(node[2], subs_map))
    elif (node_type == NOT_OP):
        return new_not(subs_alias(node[1], subs_map))
    elif (node_type == SEQ_OP):
        return new_seq(subs_alias(node[1], subs_map),
                       subs_alias(node[2], subs_map))
    elif (node_type == STAR_OP):
        return new_star(subs_alias(node[1], subs_map))
    elif (node_type == SPEC_SYMB):
        regexp = subs_alias(get_regexp_node(node), subs_map)
        spec_rhs = subs_alias(get_spec_rhs(node), subs_map)

        if (is_spec_enable(node)):
            return new_enable_spec(regexp, spec_rhs, new_nil())
        else:
            return new_disable_spec(regexp, spec_rhs, new_nil())
    elif (node_type == SPEC_LIST):
        return new_spec_list(subs_alias(node[1], subs_map),
                             subs_alias(node[2], subs_map))
    else:
        raise UnexpectedSymbol(node)

def get_expr_vars(node):
    # Get the variables contained in the spec

    def get_expr_vars_rec(node, used_vars):

        node_type = get_node_type(node)

        if (node_type == TRUE): return node
        elif (node_type == FALSE): return node
        elif (node_type == NULL): return node
        elif (node_type == DONTCARE): return node
        elif (node_type == CI): return node
        elif (node_type == CB): return node
        elif (node_type == ID):
            used_vars.add(node)
        elif (node_type == INT or
              node_type == FLOAT or node_type == STRING):
            return node
        elif (node_type == PARAM_LIST):
            get_expr_vars_rec(get_param_name(node), used_vars)
            return node
        elif (node_type == CALL_ENTRY or
              node_type == CALL_EXIT):
            receiver = get_call_receiver(node)
            if (new_nil() != receiver):
                get_expr_vars_rec(receiver, used_vars)

            params = get_call_params(node)
            if (new_nil() != params):
                get_expr_vars_rec(params, used_vars)

            if (CALL_EXIT == node_type):
                assignee = get_call_assignee(node)
                if (new_nil() != assignee):
                    get_expr_vars_rec(assignee, used_vars)
        elif (node_type == REGEXP_INST):
            name = new_named_regexp_inst_name(node)
            vars_list = new_named_regexp_inst_vars(node)

            for v in vars_list:
                get_expr_vars_rec(v, used_vars)

        elif (node_type == AND_OP or
              node_type == OR_OP or
              node_type == SEQ_OP or
              node_type == SPEC_LIST):
            get_expr_vars_rec(node[1], used_vars)
            get_expr_vars_rec(node[2], used_vars)

        elif (node_type == NOT_OP or
              node_type == STAR_OP):
            get_expr_vars_rec(node[1], used_vars)

        elif (node_type == SPEC_SYMB):
            get_expr_vars_rec(get_regexp_node(node), used_vars)
            get_expr_vars_rec(get_spec_rhs(node), used_vars)
        else:
            raise UnexpectedSymbol(node)

    used_vars = set()
    get_expr_vars_rec(node, used_vars)
    return used_vars


def subs_named_regexp_rec(node, named_regexp_map, bound_vars, subs_map):
    """
    bound_vars: (prev_expr_vars, current_vars)
      - prev_expr_vars: variables defined in the  previous expressions
      - current_vars: variables defined in the current expression
    subs_map: maps from ids to values to substitue.
    """
    node_type = get_node_type(node)

    if (node_type == TRUE): return node
    elif (node_type == FALSE): return node
    elif (node_type == NULL): return node
    elif (node_type == DONTCARE): return node
    elif (node_type == CI): return node
    elif (node_type == CB): return node
    elif (node_type == ID):
        (prev_expr_var, myvar) = bound_vars
        assert prev_expr_var is not None
        assert type(prev_expr_var) == set
        assert myvar is not None
        assert type(myvar) == set

        if (node in subs_map):
            return subs_map[node]
        elif (node in prev_expr_var):
            # Avoid capture of variables
            tmp_id = len(bound_vars)
            new_var = new_id("tmp_%d" % tmp_id)
            while new_var in prev_expr_var:
                tmp_id = tmp_id + 1
                new_var = new_id("tmp_%d" % tmp_id)
            myvar.add(new_var)
            return new_var
        else:
            return node
    elif (node_type == INT or
          node_type == FLOAT or node_type == STRING):
        return node
    elif (node_type == PARAM_LIST):
        param = subs_named_regexp_rec(get_param_name(node),
                                      named_regexp_map,
                                      bound_vars,
                                      subs_map)
        tail = get_param_tail(node)
        if (new_nil() != tail):
            tail = subs_named_regexp_rec(tail,
                                         named_regexp_map,
                                         bound_vars,
                                         subs_map)
        return new_param(param, get_param_type(node), tail)

    elif (node_type == CALL_ENTRY or
          node_type == CALL_EXIT):
        call_type = get_call_type(node)
        method_name = get_call_method(node)
        receiver = get_call_receiver(node)
        if (new_nil() != receiver):
            receiver = subs_named_regexp_rec(receiver,
                                             named_regexp_map,
                                             bound_vars,
                                             subs_map)
        params = get_call_params(node)
        if (new_nil() != params):
            params = subs_named_regexp_rec(params,
                                           named_regexp_map,
                                           bound_vars,
                                           subs_map)
        if (CALL_EXIT == node_type):
            assignee = get_call_assignee(node)
            if (new_nil() != assignee):
                assignee = subs_named_regexp_rec(assignee,
                                                 named_regexp_map,
                                                 bound_vars,
                                                 subs_map)

            return new_call_exit(assignee, call_type, receiver, method_name, params)
        else:
            return new_call_entry(call_type, receiver, method_name, params)

    elif (node_type == REGEXP_INST):
        # Recursively call the substitution on the
        # regexp template.
        name = new_named_regexp_inst_name(node)
        vars_list = new_named_regexp_inst_vars(node)

        key = (name, len(vars_list))
        if (key not in named_regexp_map):
            raise Exception("REGEXP alias %s(%s) not declared in the spec!" %
                            (name, [get_id_val(v) for v in vars_list]))
        named_regexp = named_regexp_map[key]
        formal_list = get_named_regexp_vars(named_regexp)
        assert(len(vars_list) == len(vars_list))

        new_subs_map = {}
        for a,f in zip(vars_list, formal_list):
            if a in subs_map:
                new_subs_map[f] = subs_map[a]
            else:
                new_subs_map[f] = a

        regexp_template = get_named_regexp_regexp(named_regexp)
        sub_var = get_expr_vars(regexp_template)
        (prev_expr_var, myvar) = bound_vars
        assert prev_expr_var is not None
        assert myvar is not None

        new_prev = set(prev_expr_var)
        assert new_prev is not None
        new_prev.update(myvar)
        assert new_prev is not None
        assert sub_var is not None
        new_bound_vars = (new_prev, sub_var)

        res = subs_named_regexp_rec(regexp_template,
                                    named_regexp_map,
                                    new_bound_vars,
                                    new_subs_map)
        return res

    elif (node_type == AND_OP):
        return new_and(subs_named_regexp_rec(node[1], named_regexp_map,
                                             bound_vars, subs_map),
                       subs_named_regexp_rec(node[2], named_regexp_map,
                                             bound_vars, subs_map))
    elif (node_type == OR_OP):
        return new_or(subs_named_regexp_rec(node[1], named_regexp_map,
                                            bound_vars, subs_map),
                      subs_named_regexp_rec(node[2], named_regexp_map,
                                            bound_vars, subs_map))
    elif (node_type == NOT_OP):
        return new_not(subs_named_regexp_rec(node[1], named_regexp_map,
                                             bound_vars, subs_map))
    elif (node_type == SEQ_OP):
        return new_seq(subs_named_regexp_rec(node[1], named_regexp_map,
                                             bound_vars, subs_map),
                       subs_named_regexp_rec(node[2], named_regexp_map,
                                             bound_vars, subs_map))
    elif (node_type == STAR_OP):
        return new_star(subs_named_regexp_rec(node[1], named_regexp_map,
                                              bound_vars, subs_map))
    elif (node_type == SPEC_SYMB):
        regexp = subs_named_regexp_rec(get_regexp_node(node), named_regexp_map,
                                       bound_vars, subs_map)
        spec_rhs = subs_named_regexp_rec(get_spec_rhs(node), named_regexp_map,
                                         bound_vars, subs_map)
        aliases = get_spec_aliases(node)

        if (is_spec_enable(node)):
            return new_enable_spec(regexp, spec_rhs, aliases)
        else:
            return new_disable_spec(regexp, spec_rhs, aliases)
    elif (node_type == SPEC_LIST):
        return new_spec_list(subs_named_regexp_rec(node[1], named_regexp_map,
                                                   bound_vars, subs_map),
                             subs_named_regexp_rec(node[2], named_regexp_map,
                                                   bound_vars, subs_map))
    else:
        raise UnexpectedSymbol(node)

def subs_named_regexp(node, named_regexp_map):
    exprvar = get_expr_vars(node)
    return subs_named_regexp_rec(node, named_regexp_map,
                                 (set(), exprvar), {})

def pretty_print(ast_node, out_stream=sys.stdout, sep=""):

    def pretty_print_aux(out_stream, node, sep):
        def my_print(out_stream, string):
            out_stream.write(string)

        node_type = get_node_type(node)
        if (node_type == TRUE): my_print(out_stream, "TRUE")
        elif (node_type == FALSE): my_print(out_stream, "FALSE")
        elif (node_type == NULL): my_print(out_stream, "NULL")
        elif (node_type == DONTCARE): my_print(out_stream, "#")
        elif (node_type == CI): my_print(out_stream, "CI")
        elif (node_type == CB): my_print(out_stream, "CB")
        elif (node_type == ID or node_type == INT or node_type == FLOAT or node_type == STRING):
            my_print(out_stream, "%s%s" % (sep, str(node[1])))
        elif (node_type == PARAM_LIST):
            pretty_print_aux(out_stream,
                             get_param_name(node), "")
            if (None != get_param_type(node) and
                NIL != get_node_type(get_param_type(node))):
                my_print(out_stream, " : ")
                pretty_print_aux(out_stream,
                                 get_param_type(node),"")
            if (get_node_type(get_param_tail(node)) != NIL):
                my_print(out_stream, ",")
                pretty_print_aux(out_stream,get_param_tail(node),"")
        elif (node_type == CALL_ENTRY or
              node_type == CALL_EXIT):

            if (node_type == CALL_EXIT):
                assignee = get_call_assignee(node)
                if (get_node_type(assignee) != NIL):
                    pretty_print_aux(out_stream, assignee,"")
                    my_print(out_stream, " = ")

            call_type = get_call_type(node)
            my_print(out_stream, "[")
            pretty_print_aux(out_stream, call_type, "")
            my_print(out_stream, "] ")

            entry_type = "ENTRY" if node_type == CALL_ENTRY else "EXIT"
            my_print(out_stream, "[%s] " % entry_type)

            receiver = get_call_receiver(node)
            if (get_node_type(receiver) != NIL):
                my_print(out_stream, "[")
                pretty_print_aux(out_stream,receiver,"") # receiver
                my_print(out_stream, "] ")

            pretty_print_aux(out_stream,
                             get_call_method(node),"")

            my_print(out_stream, "(")

            param_list = get_call_params(node)
            if (get_node_type(param_list) != NIL):
                pretty_print_aux(out_stream, param_list, "") # params

            my_print(out_stream, ")")

        elif (node_type == REGEXP_INST):
            name = new_named_regexp_inst_name(node)
            vars_list = new_named_regexp_inst_vars(node)

            pretty_print_aux(out_stream,name,"")
            my_print(out_stream, "(")
            first = True
            for v in vars_list:
                if first:
                    first = False
                else:
                    my_print(out_stream, ",")
                pretty_print_aux(out_stream,v,"")
            my_print(out_stream, ")")

        elif (node_type == AND_OP):
            my_print(out_stream, "(")
            pretty_print_aux(out_stream,node[1],"")
            my_print(out_stream, " & ")
            pretty_print_aux(out_stream,node[2],"")
            my_print(out_stream, ")")
        elif (node_type == OR_OP):
            my_print(out_stream, "(")
            pretty_print_aux(out_stream,node[1],"")
            my_print(out_stream, " | ")
            pretty_print_aux(out_stream,node[2],"")
            my_print(out_stream, ")")
        elif (node_type == NOT_OP):
            my_print(out_stream, "! (")
            pretty_print_aux(out_stream,node[1],"")
            my_print(out_stream, ")")
        elif (node_type == SEQ_OP):
            my_print(out_stream, "(")
            pretty_print_aux(out_stream,node[1],"")
            assert (get_node_type(node[2]) != NIL)
            # my_print(out_stream, "); (")
            my_print(out_stream, "; ")
            pretty_print_aux(out_stream,node[2],"")
            my_print(out_stream, ")")
        elif (node_type == STAR_OP):
            my_print(out_stream, "((")
            pretty_print_aux(out_stream,node[1],"")
            my_print(out_stream, ")[*])")
        elif (node_type == SPEC_SYMB):
            my_print(out_stream, "SPEC ")
            pretty_print_aux(out_stream ,node[1], "")

            # Print Aliases
            aliases = get_spec_aliases(node)
            if (NIL != get_node_type(aliases)):
                my_print(out_stream, " ALIASES ")
                pretty_print_aux(out_stream, aliases, "")

        elif (node_type == ALIASES_LIST):
            old = get_alias_old(node)
            new = get_alias_new(node)
            pretty_print_aux(out_stream, old, "")
            my_print(out_stream, " = [")

            first = True
            for n in new:
                if not first:
                    my_print(out_stream, ",")
                first = False
                pretty_print_aux(out_stream, n, "")

            my_print(out_stream, "]")

            alias_tail = get_alias_tail(node)
            if (get_node_type(alias_tail) != NIL):
                my_print(out_stream, ",")
                pretty_print_aux(out_stream, alias_tail,"")

        elif (node_type == ENABLE_OP or
              node_type == DISABLE_OP):

            pretty_print_aux(out_stream ,node[1], "")

            if (node_type == ENABLE_OP):
                my_print(out_stream, " |+ ")
            elif (node_type == DISABLE_OP):
                my_print(out_stream, " |- ")
            else:
                raise Exception("Unknown type of spec")

            pretty_print_aux(out_stream,node[2],"")

        elif (node_type == NAMED_REGEXP):
            my_print(out_stream, "REGEXP ")

            rid = get_named_regexp_id(node)
            rvars = get_named_regexp_vars(node)
            rregexp = get_named_regexp_regexp(node)

            pretty_print_aux(out_stream , rid, "")
            my_print(out_stream, "(")
            first = True
            for v in rvars:
                if first:
                    first = False
                else:
                    my_print(out_stream, ",")
                pretty_print_aux(out_stream , v, "")
            my_print(out_stream, ") = [")
            pretty_print_aux(out_stream , rregexp, "")
            my_print(out_stream, "]")
        elif (node_type == SPEC_LIST):
            pretty_print_aux(out_stream,node[1],"")
            if (get_node_type(node[2]) != NIL):
                my_print(out_stream, "; ")
                pretty_print_aux(out_stream,node[2],"")
        else:
            raise UnexpectedSymbol(node)

    pretty_print_aux(out_stream, ast_node, sep)


# Simplification functions for regexp


def simplify_not(lhs):
    """ Syntactic simplification rules for the complement of regexp
    1. ! (! regexp) => regexp
    2. ! False => True[*]
    3. ! True[*] => False

    """
    true_star = new_star(new_true())

    if (get_node_type(lhs) == NOT_OP): return lhs[1]
    if (get_node_type(lhs) == FALSE): return true_star
    if (lhs == true_star): return new_false()

    return new_not(lhs)

def simplify_and(lhs, rhs):
    """ Syntactic simplification rules for the intersection
    1. regexp & regexp => regexp
    2. regex & FALSE => FALSE
    3. a & TRUE => a
    4. regexp & TRUE[*] => regexp
    5. regexp & ! regexp => FALSE
    """
    true_star = new_star(new_true())

    # 1.
    if (lhs == rhs): return lhs
    # 2.
    if (get_node_type(lhs) == FALSE or get_node_type(rhs) == FALSE):
        return new_false()
    # 3.
    f_3 = lambda lhs,rhs : get_node_type(lhs) == TRUE and get_node_type(rhs) in [CALL_ENTRY, CALL_EXIT]
    if (f_3(lhs,rhs)): return rhs
    if (f_3(rhs,lhs)): return lhs
    # 4.
    if (rhs == true_star): return lhs
    if (lhs == true_star): return rhs
    # 5.
    f_5 = lambda lhs,rhs : get_node_type(rhs) == NOT_OP and lhs == rhs[1]
    if (f_5(lhs,rhs)): return new_false()
    if (f_5(rhs,lhs)): return new_false()

    return new_and(lhs,rhs)

def simplify_or(lhs, rhs):
    """ Syntactic simplification rules for the intersection
    1. regexp | regexp => regexp
    2. regexp | FALSE => regexp
    3. a | TRUE => TRUE
    4. regexp | TRUE[*] => TRUE[*]
    5. regexp | ! regexp => TRUE[*]
    """
    true_star = new_star(new_true())

    # 1.
    if (lhs == rhs): return lhs
    # 2.
    f_2 = lambda lhs,rhs : get_node_type(lhs) == FALSE
    if (f_2(lhs,rhs)): return rhs
    if (f_2(rhs,lhs)): return lhs
    # 3.
    f_3 = lambda lhs,rhs : get_node_type(lhs) == TRUE and get_node_type(rhs) in [CALL_ENTRY, CALL_EXIT]
    if (f_3(lhs,rhs)): return new_true()
    if (f_3(rhs,lhs)): return new_true()
    # 4. regexp & TRUE[*] => regexp
    if (lhs == true_star or rhs == true_star): return true_star
    # 5.
    f_5 = lambda lhs,rhs : get_node_type(rhs) == NOT_OP and lhs == rhs[1]
    if (f_5(lhs,rhs)): return true_star
    if (f_5(rhs,lhs)): return true_star

    return new_or(lhs,rhs)

def simplify_seq(lhs, rhs):
    """ Syntactic simplification rules for the concatenation
    1. FALSE; regexp => FALSE
    2. regexp[*]; regexp[*] => regexp[*]
    """

    # 1.
    if (get_node_type(lhs) == FALSE or get_node_type(rhs) == FALSE):
        return new_false()
    # 2.
    if (lhs == rhs and
        get_node_type(lhs) == STAR_OP and
        get_node_type(rhs) == STAR_OP):
        return lhs

    return new_seq(lhs,rhs)

def simplify_star(lhs):
    """ Syntactic simplification rules for the kleene star
    1. (regexp[*])[*]
    """

    # 1.
    if (get_node_type(lhs) == STAR_OP): return lhs[1]

    return new_star(lhs)



class UnexpectedSymbol(Exception):
    def __init__(self, node):
        self.node = node
        node_type = get_node_type(node)
        message = "Unexpected symbol %s" % inv_map[node_type]

        super(Exception, self).__init__(message)


