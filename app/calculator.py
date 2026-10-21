"""A small, safe calculator tool for the agent.

We never call eval() on model output. Instead we parse the expression into an
AST and only allow plain arithmetic on numbers.
"""
import ast
import operator

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}
MAX_EXPONENT = 100


def safe_eval(expression: str) -> float:
    """Evaluate an arithmetic expression like '17 * (3 + 2) ** 2'.

    Raises ValueError for anything that isn't plain arithmetic.
    """
    expression = expression.strip().replace("^", "**").replace("×", "*").replace("÷", "/")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as e:
        raise ValueError(f"Not a valid expression: {expression!r}") from e
    return _eval(tree.body)


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        left, right = _eval(node.left), _eval(node.right)
        if isinstance(node.op, ast.Pow) and abs(right) > MAX_EXPONENT:
            raise ValueError("Exponent too large")
        return _OPS[type(node.op)](left, right)
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    raise ValueError("Only numbers and + - * / // % ** are allowed")
