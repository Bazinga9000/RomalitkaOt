import io


def line_to_symtable(line, symtable):
    return [symtable.index(i) for i in line]


def print_to_string(sg, hook_function=None):
    model = sg.solver.model()
    label_width = max(len(s.label) for s in sg.symbol_set.symbols.values())

    def print_function(p) -> str:
        cell = sg.grid[p]
        i = model.eval(cell).as_long()
        label = None
        if hook_function is not None:
            label = hook_function(p, i)
        if label is None:
            label = f"{sg.symbol_set.symbols[i].label:{label_width}}"
        return label

    out = io.StringIO()
    sg.lattice.print(print_function, " " * label_width, stream=out)
    return out.getvalue()
