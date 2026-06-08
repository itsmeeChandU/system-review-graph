# Linux Kernel System Review Atlas

This example stress-tests System Review Graph on a very large public repository.

Source used:

- Repository: https://github.com/torvalds/linux
- Commit: `2d3090a8aeb596a26935db0955d46c9a5db5c6ce`
- Commit date: `2026-06-08 07:58:32 -0700`

Method:

- A blobless git clone was used to read the real tracked path tree.
- A path-only mirror with empty files was generated for scanning.
- Source blobs were not copied into this repository.
- The atlas was generated with top-level Linux directories as child maps.

Open first:

```text
reports/system_review_graph.md
```

Then drill into child maps under:

```text
subsystems/<subsystem>/system_review_manifest.json
subsystems/<subsystem>/reports/system_review_graph.md
```

Quick source-surface review:

- The root atlas found 24 child maps including `arch`, `block`, `crypto`, `drivers`, `fs`, `include`, `init`, `io_uring`, `kernel`, `lib`, `mm`, `net`, `rust`, `scripts`, `security`, `tools`, and `virt`.
- Most child maps are C/C++ surfaces, with Rust also detected in `drivers`, `lib`, `mm`, `rust`, `samples`, `scripts`, and `tools`.
- `Documentation`, `scripts`, and `tools` show mixed source/support surfaces that should be reviewed differently from runtime kernel subsystems.
- The useful next refinement would map real Linux workflows such as boot/init, syscall path, memory allocation, networking packet flow, filesystem IO, driver model/probing, security hooks, and Rust integration gates.

Known boundary:

This is an inferred source-tree atlas, not an official Linux architecture audit.
It does not inspect file contents, build configurations, tests, maintainership,
or runtime behavior. Use it as a navigation and review-routing artifact.
