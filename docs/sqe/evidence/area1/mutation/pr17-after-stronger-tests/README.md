# PR #17 mutation result after stronger tests

The full mutmut 3.8.1 run on the revised PR #17 tree completed with **296
killed, 3 survived, 299 total, 0 unresolved (99.00%)**. The complete source
hashes, mutant IDs and diffs are in [`results.json`](results.json); the raw
console output and environment are preserved alongside it.

The three survivors are E-8, S-69 and S-123. Each is equivalent under the
current Django model defaults or query behavior. E-10 is absent from the
survivor list because the added manager/admin requester assertion kills it.

The full team suite also passed **82 tests and 144 subtests**. This is a local
measurement on the revised branch. PR #17's previous hosted result remains
295/299 until this commit is pushed and GitHub Actions runs on the new head.
