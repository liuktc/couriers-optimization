def max(sort: str):
    return (
        f"; {sort} max\n"
        f"(define-fun max ((a {sort}) (b {sort})) {sort} (ite (> a b) a b))\n"
    )