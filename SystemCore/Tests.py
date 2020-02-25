import traceback
def aaa():
    trace = []
    stack = traceback.extract_stack()[:-3]  # -3, чтобы убрать функцию логирования,  эту и "traceback"
    for s in stack:
        trace.append(s.name + ' -> ' + s.line)
    return trace