"""Run mutmut with the two project-specific mutation operators.

Mutmut 3.8 exposes its built-in operator registry as a list rather than a
plugin entry point.  These operators are appended before mutmut's CLI is
loaded, so the normal mutmut reporting, test selection, caching, and result
export remain in use.  Mutmut currently requires Linux/WSL because its worker
model relies on fork; the CI job runs this command on Ubuntu.
"""

import libcst as cst
import libcst.matchers as m


def operator_overlap_boundary(node: cst.Call):
    """Change inclusive interval intersection to exclusive comparisons."""
    if not m.matches(node.func, m.Attribute(attr=m.Name("filter"))):
        return
    for argument in node.args:
        if argument.keyword and argument.keyword.value in {"start_date__lte", "end_date__gte"}:
            yield node.with_changes(
                args=[
                    item.with_changes(keyword=cst.Name(argument.keyword.value[:-1]))
                    if item is argument
                    else item
                    for item in node.args
                ]
            )


def operator_overlap_truth(node: cst.Call):
    """Invert the active-overlap existence predicate."""
    if m.matches(
        node,
        m.Call(func=m.Attribute(value=m.Name("overlap"), attr=m.Name("exists"))),
    ):
        yield cst.UnaryOperation(operator=cst.Not(), expression=node)


def main() -> None:
    from mutmut.mutation import mutators
    from mutmut.utils import format_utils

    original_get_mutant_name = format_utils.get_mutant_name

    def get_project_mutant_name(path, mutant_method_name):
        """Match file-derived names to Django's runtime ``leave`` package."""
        name = original_get_mutant_name(path, mutant_method_name)
        return name.removeprefix("backend.")

    format_utils.get_mutant_name = get_project_mutant_name

    mutators.mutation_operators.extend(
        [
            (cst.Call, operator_overlap_boundary),
            (cst.Call, operator_overlap_truth),
        ]
    )

    from mutmut.__main__ import cli

    cli()


if __name__ == "__main__":
    main()
