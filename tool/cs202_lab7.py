import os, sys, json, subprocess, re
from collections import defaultdict
from pycparser import c_parser, c_ast
from pycparser.c_generator import CGenerator

# ---------- Utilities ----------
def read_text(p): 
    return open(p, 'r', encoding='utf-8', errors='ignore').read()

def write_text(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f: f.write(s)

def strip_preprocessor(src):
    # Remove preprocessor directives
    no_preproc = "\n".join([ln for ln in src.splitlines() if not ln.lstrip().startswith("#")])
    # Remove // single-line comments
    no_preproc = re.sub(r'//.*', '', no_preproc)
    # Remove /* multi-line */ comments
    no_preproc = re.sub(r'/\*.*?\*/', '', no_preproc, flags=re.DOTALL)
    return no_preproc

# ---------- CFG ----------
class Block:
    def __init__(self, bid): self.id, self.lines = bid, []
class CFG:
    def __init__(self): 
        self.blocks, self.edges, self._next = {}, set(), 0
    def new_block(self):
        bid = f"B{self._next}"; self._next += 1
        self.blocks[bid] = Block(bid); return bid
    def add_edge(self, u, v): self.edges.add((u, v))

gen = CGenerator()

def stmt_text(node):
    try:
        txt = gen.visit(node)
        if not txt.endswith("}") and not txt.endswith(";"):
            txt += ";"
        return txt
    except Exception:
        return str(type(node).__name__) + ";"

def build_seq(cfg, stmts):
    entry = last = None
    cur = cfg.new_block()
    def flush():
        nonlocal entry, last, cur
        if entry is None: entry = cur
        last = cur
        cur = cfg.new_block()
        cfg.add_edge(last, cur)
        last = cur
    for s in stmts or []:
        if isinstance(s, (c_ast.If, c_ast.While, c_ast.For, c_ast.DoWhile, c_ast.Switch)):
            if cfg.blocks[cur].lines:
                if entry is None: entry = cur
                last = cur
            else:
                if entry is None: entry = cur
                last = cur
            if isinstance(s, c_ast.If):
                e, l = build_if(cfg, s)
            elif isinstance(s, c_ast.While):
                e, l = build_while(cfg, s)
            elif isinstance(s, c_ast.For):
                e, l = build_for(cfg, s)
            elif isinstance(s, c_ast.DoWhile):
                e, l = build_dowhile(cfg, s)
            else:
                e, l = build_switch_flat(cfg, s)
            cfg.add_edge(last, e)
            cur = l
            last = cur
        else:
            cfg.blocks[cur].lines.append(stmt_text(s))
    if entry is None:
        entry = cur
    return entry, cur

def build_if(cfg, node: c_ast.If):
    cond = cfg.new_block(); cfg.blocks[cond].lines.append(f"if({gen.visit(node.cond)})")
    t_entry, t_exit = build_seq(cfg, _as_list(node.iftrue))
    cfg.add_edge(cond, t_entry)
    if node.iffalse is not None:
        f_entry, f_exit = build_seq(cfg, _as_list(node.iffalse))
        cfg.add_edge(cond, f_entry)
        join = cfg.new_block()
        cfg.add_edge(t_exit, join); cfg.add_edge(f_exit, join)
        return cond, join
    else:
        join = cfg.new_block()
        cfg.add_edge(cond, join)
        cfg.add_edge(t_exit, join)
        return cond, join

def build_while(cfg, node: c_ast.While):
    cond = cfg.new_block(); cfg.blocks[cond].lines.append(f"while({gen.visit(node.cond)})")
    b_entry, b_exit = build_seq(cfg, _as_list(node.stmt))
    cfg.add_edge(cond, b_entry)
    cfg.add_edge(b_exit, cond)
    exitb = cfg.new_block()
    cfg.add_edge(cond, exitb)
    return cond, exitb

def build_for(cfg, node: c_ast.For):
    initb = cfg.new_block()
    if node.init is not None:
        for s in _as_list(node.init): cfg.blocks[initb].lines.append(stmt_text(s))
    condb = cfg.new_block(); cfg.blocks[condb].lines.append(f"for({gen.visit(node.cond) if node.cond else ''})")
    cfg.add_edge(initb, condb)
    b_entry, b_exit = build_seq(cfg, _as_list(node.stmt))
    cfg.add_edge(condb, b_entry)
    postb = cfg.new_block()
    if node.next is not None:
        for s in _as_list(node.next): cfg.blocks[postb].lines.append(stmt_text(s))
    cfg.add_edge(b_exit, postb)
    cfg.add_edge(postb, condb)
    exitb = cfg.new_block(); cfg.add_edge(condb, exitb)
    return initb, exitb

def build_dowhile(cfg, node: c_ast.DoWhile):
    body_entry, body_exit = build_seq(cfg, _as_list(node.stmt))
    condb = cfg.new_block(); cfg.blocks[condb].lines.append(f"do_while({gen.visit(node.cond)})")
    cfg.add_edge(body_exit, condb)
    cfg.add_edge(condb, body_entry)
    exitb = cfg.new_block(); cfg.add_edge(condb, exitb)
    return body_entry, exitb

def build_switch_flat(cfg, node: c_ast.Switch):
    h = cfg.new_block(); cfg.blocks[h].lines.append(f"switch({gen.visit(node.cond)})")
    body_entry, body_exit = build_seq(cfg, _as_list(node.stmt))
    cfg.add_edge(h, body_entry)
    exitb = cfg.new_block(); cfg.add_edge(body_exit, exitb)
    return h, exitb

def _as_list(x):
    if x is None: return []
    if isinstance(x, c_ast.Compound): return x.block_items or []
    return [x]

def build_cfg_from_source(src):
    parser = c_parser.CParser()
    cleaned = strip_preprocessor(src)
    ast = parser.parse(cleaned)
    cfg = CFG()
    funcs = [d for d in ast.ext if isinstance(d, c_ast.FuncDef)]
    mains = [f for f in funcs if getattr(getattr(f.decl, 'name', None), 'lower', lambda: '')() == 'main' or f.decl.name == 'main']
    targets = mains if mains else funcs
    entry = last = None
    for f in targets:
        e, l = build_seq(cfg, _as_list(f.body))
        if entry is None: entry = e
        if last is not None: cfg.add_edge(last, e)
        last = l
    if entry is None:
        entry = cfg.new_block()
    return cfg

# ---------- DOT ----------
def to_dot(cfg):
    out = ["digraph CFG {", '  node [shape=box, fontname="Consolas", fontsize=10];', "  rankdir=TB;"]
    for b, blk in cfg.blocks.items():
        escaped_lines = []
        for ln in blk.lines:
            safe = ln.replace('\\', '\\\\').replace('"', '\\"')
            escaped_lines.append(safe)
        lbl = "\\l".join(escaped_lines) + ("\\l" if escaped_lines else "")
        if not lbl:
            lbl = "(join/ε)"
        out.append(f'  "{b}" [label="{b}: {lbl}"];')
    for u, v in sorted(cfg.edges):
        out.append(f'  "{u}" -> "{v}";')
    out.append("}")
    return "\n".join(out)

def render_dot(dot_text, png_path):
    dot_path = png_path[:-4] + ".dot"
    write_text(dot_path, dot_text)
    try:
        subprocess.run(["dot", "-Tpng", dot_path, "-o", png_path], check=True)
        print(f"[SUCCESS] Rendered {png_path}")
    except Exception as e:
        print(f"[WARN] Graphviz render failed: {e}")

# ---------- Metrics ----------
def compute_metrics(cfg):
    N, E = len(cfg.blocks), len(cfg.edges)
    CC = E - N + 2
    return {"N": N, "E": E, "CC": CC}

# ---------- Reaching Definitions ----------
def extract_defs_in_block_lines(lines):
    defs = []
    for ln in lines:
        m = re.match(r'\s*(?:[A-Za-z_][\w\s\*]+)?\b([A-Za-z_]\w*)\s*(?:\[[^\]]+\])?\s*=\s*', ln)
        if m:
            defs.append(m.group(1))
    return defs

def collect_definitions(cfg):
    did = 0
    def_map, defs_in_block = {}, defaultdict(list)
    for b, blk in cfg.blocks.items():
        for var in extract_defs_in_block_lines(blk.lines):
            d = f"D{did}"; did += 1
            line_text = next((ln for ln in blk.lines if re.search(rf'\b{re.escape(var)}\b\s*=', ln)), (blk.lines[0] if blk.lines else ""))
            def_map[d] = (var, b, line_text)
            defs_in_block[b].append(d)
    return def_map, defs_in_block

def preds(cfg):
    pr = defaultdict(set)
    for u, v in cfg.edges: pr[v].add(u)
    for b in cfg.blocks: pr[b] = pr[b]
    return pr

def reaching_definitions(cfg, def_map, gen_sets):
    var_to_defs = defaultdict(set)
    for d, (v, b, ln) in def_map.items(): var_to_defs[v].add(d)
    blocks = list(cfg.blocks.keys())
    in_s = {b: set() for b in blocks}
    out_s = {b: set(gen_sets.get(b, set())) for b in blocks}
    kill = {}
    for b in blocks:
        g = gen_sets.get(b, set())
        k = set()
        for d in g:
            v = def_map[d][0]
            k |= (var_to_defs[v] - g)
        kill[b] = k
    pr = preds(cfg)
    changed = True
    iters = []
    while changed:
        snapshot = {'in': {b: sorted(in_s[b]) for b in blocks}, 'out': {b: sorted(out_s[b]) for b in blocks}}
        iters.append(snapshot)
        changed = False
        for b in blocks:
            new_in = set().union(*[out_s[p] for p in pr[b]]) if pr[b] else set()
            new_out = gen_sets.get(b, set()) | (new_in - kill[b])
            if new_in != in_s[b] or new_out != out_s[b]:
                in_s[b], out_s[b] = new_in, new_out
                changed = True
    return in_s, out_s, kill, iters, gen_sets

# ---------- Reporting ----------
def write_defs(prog_dir, name, def_map):
    lines = []
    for d, (v, b, ln) in sorted(def_map.items(), key=lambda x: int(x[0][1:])):
        lines.append(f"{d}: var={v}, block={b}, line={ln}")
    write_text(os.path.join(prog_dir, f"{name}_definitions.txt"), "\n".join(lines))

def write_gen_kill_csv(prog_dir, name, gen_sets, kill_sets):
    """Write separate gen/kill CSV: Basic-Block, gen[B], kill[B]"""
    rows = ["Basic-Block,gen[B],kill[B]"]
    blocks = sorted(set(gen_sets.keys()) | set(kill_sets.keys()))
    for b in blocks:
        g = " ".join(sorted(gen_sets.get(b, set())))
        k = " ".join(sorted(kill_sets.get(b, set())))
        rows.append(f"{b},{g},{k}")
    write_text(os.path.join(prog_dir, f"{name}_gen_kill.csv"), "\n".join(rows))

def write_rd_table(prog_dir, name, gen_sets, kill_sets, in_s, out_s):
    """Write unified reaching definitions table with gen/kill/in/out per block"""
    rows = ["Basic-Block,gen[B],kill[B],in[B],out[B]"]
    blocks = sorted(set(gen_sets.keys()) | set(in_s.keys()))
    for b in blocks:
        g = " ".join(sorted(gen_sets.get(b, set())))
        k = " ".join(sorted(kill_sets.get(b, set())))
        i = " ".join(sorted(in_s.get(b, set())))
        o = " ".join(sorted(out_s.get(b, set())))
        rows.append(f"{b},{g},{k},{i},{o}")
    write_text(os.path.join(prog_dir, f"{name}_reaching_definitions.csv"), "\n".join(rows))

def write_iters_csv(prog_dir, name, iters):
    """Write per-iteration CSV with Iteration, Basic-Block, in[B], out[B] only"""
    rows = ["Iteration,Basic-Block,in[B],out[B]"]
    all_blocks = set()
    for snap in iters:
        all_blocks.update(snap['in'].keys())
    all_blocks = sorted(all_blocks)
    
    for idx, snap in enumerate(iters):
        for b in all_blocks:
            i = " ".join(snap['in'].get(b, []))
            o = " ".join(snap['out'].get(b, []))
            rows.append(f"{idx},{b},{i},{o}")
    write_text(os.path.join(prog_dir, f"{name}_iterations.csv"), "\n".join(rows))

def run_on_file(c_path, out_dir):
    name = os.path.splitext(os.path.basename(c_path))[0]
    prog_dir = os.path.join(out_dir, name)
    os.makedirs(prog_dir, exist_ok=True)
    
    print(f"\n[PROCESSING] {name}")
    src = read_text(c_path)
    cfg = build_cfg_from_source(src)
    dot = to_dot(cfg)
    render_dot(dot, os.path.join(prog_dir, f"{name}_cfg.png"))
    write_text(os.path.join(prog_dir, f"{name}_cfg.dot"), dot)
    metrics = compute_metrics(cfg)
    def_map, defs_in_block = collect_definitions(cfg)
    gen_sets = {b: set(dids) for b, dids in defs_in_block.items()}
    in_s, out_s, kill_s, iters, gen_sets = reaching_definitions(cfg, def_map, gen_sets)
    write_defs(prog_dir, name, def_map)
    write_gen_kill_csv(prog_dir, name, gen_sets, kill_s)
    write_rd_table(prog_dir, name, gen_sets, kill_s, in_s, out_s)
    write_iters_csv(prog_dir, name, iters)
    print(f"[METRICS] N={metrics['N']} E={metrics['E']} CC={metrics['CC']}")
    print(f"[OUTPUTS] All files written to {prog_dir}/")
    return name, metrics

def write_consolidated_metrics(out_dir, results):
    """Write a single metrics table for all programs"""
    rows = ["Program No.,Program Name,No. of Nodes (N),No. of Edges (E),Cyclomatic Complexity (CC)"]
    for idx, (name, metrics) in enumerate(results, start=1):
        rows.append(f"{idx},{name},{metrics['N']},{metrics['E']},{metrics['CC']}")
    write_text(os.path.join(out_dir, "metrics_summary.csv"), "\n".join(rows))
    print(f"\n[SUMMARY] Wrote consolidated metrics to {out_dir}/metrics_summary.csv")

def main():
    if len(sys.argv) < 2:
        print("Usage: python tool\\cs202_lab7.py corpus\\program1.c [program2.c ...]")
        sys.exit(1)
    out_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "out"))
    results = []
    for p in sys.argv[1:]:
        name, metrics = run_on_file(p, out_dir)
        results.append((name, metrics))
    write_consolidated_metrics(out_dir, results)
    print("\n[DONE] All programs processed. Check out/ for organized folders.")

if __name__ == "__main__":
    main()
