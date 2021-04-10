import dd.cudd as _bdd

from iscram.domain.model import SystemGraph

fmt_bdd = {"or": " | ", "and": " & "}


def node_expr(n, logic, c_deps, s_deps):
    expr = n

    if len(c_deps) > 0:
        expr += fmt_bdd["or"]
        c_deps_fmt = fmt_bdd[logic]
        c_deps_expr = c_deps_fmt.join(c_deps)
        expr += "( " + c_deps_expr + " )"

    if len(s_deps) > 0:
        expr += fmt_bdd["or"]
        s_deps_expr = fmt_bdd["and"].join(s_deps)
        expr += "( " + s_deps_expr + " )"

    return expr


def prep_for_bdd(sg: SystemGraph):

    ind_deps = [d.risk_src_id for d in sg.indicator.dependencies]
    exprs = [
        {"indicator": (fmt_bdd[sg.indicator.logic_function]).join(ind_deps) }
    ]

    components = set([c.identifier for c in sg.components])

    l = {}
    for c in sg.components:
        l[c.identifier] = c.logic_function

    for s in sg.suppliers:
        l[s.identifier] = "and"

    g = {}
    supplier_deps = {}

    for d in sg.security_dependencies:
        if d.risk_dst_id in components and not d.risk_src_id in components:
            adj = supplier_deps.get(d.risk_dst_id, [])
            adj.append(d.risk_src_id)
            supplier_deps[d.risk_dst_id] = adj
        else:
            adj = g.get(d.risk_dst_id, [])
            adj.append(d.risk_src_id)
            g[d.risk_dst_id] = adj

    queue = list(ind_deps)
    visited = set()

    while(queue):
        u = queue.pop(0)
        if u in visited: continue
        visited.add(u)
        deps = g.get(u, [])
        s_deps = supplier_deps.get(u, [])
        logic = l[u]
        exprs.append({
            u: node_expr(u, logic, deps, s_deps)
        })
        queue.extend(deps)
        queue.extend(s_deps)

    order = list([list(e.keys())[0] for e in exprs])
    order = {u: idx for idx, u in enumerate(order)}

    return exprs, order


def build_bdd(sg):
    exprs, order = prep_for_bdd(sg)

    bdd = _bdd.BDD(memory_estimate=(int(2**30 * 0.3)))
    bdd.configure(reordering=True)

    bdd.declare(*(["indicator"] + [c.identifier for c in sg.components] + [s.identifier for s in sg.suppliers]))

    r = bdd.add_expr(exprs[0]["indicator"])

    for d_raw in exprs[1:]:
        d = {key: bdd.add_expr(val) for key, val in d_raw.items()}
        r = bdd.let(d, r)

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


