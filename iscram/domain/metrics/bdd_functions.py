import dd.cudd as _bdd


fmt_bdd = {"or": " | ", "and": " & "}


def build_sg_graph_dict(sg):
    """ Builds a dictionary of dependencies for each node, where each node can have either component
    or supplier dependents or both. If a node has no dependents of a certain type, the key is missing.
    A node with no dependents has an empty dictionary."""
    def type_tag(node):
        return list(filter(lambda t: t in ("component", "supplier"), sg.nodes[node].tags))[0]

    g = {n: {} for n in sg.nodes.keys()}
    for e in sg.edges:
        if "potential" not in e.tags:
            g[e.dst][type_tag(e.src)] = g[e.dst].get(type_tag(e.src), []) + [e.src]

    return g


def recursive_build_expr(sg, g, u, discovered):
    """ DFS to build the logical expression encoding system graph structure. """
    # The discovered list is useful for BDD variable ordering heuristic
    discovered.append(u)

    # Get expressions (if any) for component and supplier dependencies. Lists should be empty if not any relevant deps.
    comp_exprs = [recursive_build_expr(sg, g, c, discovered) for c in g[u].get("component", [])]
    sup_exprs = [recursive_build_expr(sg, g, s, discovered) for s in g[u].get("supplier", [])]

    # Combine current node with the non-empty dependency lists
    # The basic expression format is ( this_node | ( component_deps ) | ( supplier_deps ) )
    # component_deps should be joined by the component logic function specified in the sg
    # supplier_deps are joined by default by "and"
    # Some of the logic below is added only to produce cleaner formatting/parentheses.
    expr = u
    if len(comp_exprs) > 0:
        comp_expr = fmt_bdd[sg.nodes[u].logic["component"]].join(comp_exprs)
        if len(comp_exprs) > 1:
            comp_expr = "( {} )".format(comp_expr)
        expr = "{} | {}".format(expr, comp_expr)
    if len(sup_exprs) > 0:
        sup_expr = fmt_bdd[sg.nodes[u].logic.get("supplier", "and")].join(sup_exprs)
        if len(sup_exprs) > 1:
            sup_expr = "( {} )".format(sup_expr)
        expr = "{} | {}".format(expr, sup_expr)

    if expr == u:
        return expr
    else:
        return "( {} )".format(expr)


def prep_for_bdd(sg):
    g = build_sg_graph_dict(sg)
    discovered = []
    r_expr = recursive_build_expr(sg, g, "indicator", discovered)
    return r_expr, discovered


def build_bdd(sg):
    """ Main function to produce a BDD from a system graph. Returns the BDD and root node as a tuple."""
    r_expr, nodes_as_discovered = prep_for_bdd(sg)

    bdd = _bdd.BDD(memory_estimate=(int(2**30 * 0.3)))
    bdd.configure(reordering=True)
    bdd.declare(*nodes_as_discovered)
    r = bdd.add_expr(r_expr)
    bdd.reorder()

    return bdd, r


def bdd_prob(bdd, f, p, memo):
    """ Recursively evaluate the BDD probability at node f. Follows Shannon expansion as described by Rauzy.
     Note: The BDD here should not be one that has been converted to minimal-cutset-only form.
     To evaluate a minimal-cutset-only BDD a different algorithm is needed. """

    if f == bdd.false:
        return 0
    if f == bdd.true:
        return 1
    if (r := memo.get(("prob", str(f)), None)) is not None:
        return 1 - r if f.negated else r

    # f = ite(x, g, h)
    x, g, h = f.var, f.high, f.low
    r = p[x] * bdd_prob(bdd, g, p, memo) + (1-p[x]) * bdd_prob(bdd, h, p, memo)

    # The memo holds the non-negated probability of f. Negation is handled after retrieval from memo.
    memo[("prob", str(f))] = r

    return 1-r if f.negated else r


