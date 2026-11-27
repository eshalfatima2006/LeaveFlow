"""Generate an isolated, verbatim validate function for Sonar complexity comparison."""

import ast
from pathlib import Path
import textwrap


source = Path("backend/leave/serializers.py").read_text(encoding="utf-8")
tree = ast.parse(source)
serializer = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "LeaveRequestSerializer")
function = next(node for node in serializer.body if isinstance(node, ast.FunctionDef) and node.name == "validate")
snippet = textwrap.dedent("\n".join(source.splitlines()[function.lineno - 1:function.end_lineno])) + "\n"
output = Path("../LeaveFlow-sonar-critical")
output.mkdir(exist_ok=True)
(output / "validate.py").write_text(snippet, encoding="utf-8")
print(f"Extracted unchanged validate body to {output / 'validate.py'}")
