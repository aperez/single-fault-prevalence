# Repository Miner

This folder will contain the source for our repository miner.

## Execution flow

We label `T` as the set of tests of a particular commit and `T+1` as the set of tests of its
successor.

- Iterate through every commit in the main branch ordered by most recent (within some bound):
    - If there is no `T+1` test suite available, run `mvn test`.
        - If tests are successful, save the *compiled tests* as `T+1`.
    - If there exists a `T+1` test suite, run it against the current codebase:
        - If tests fail, label the current commit as **buggy**.
            - However, if there are compilation failures or runtime errors, do nothing.
        - Afterwards, run test suite `T`:
            - If successful, `T+1`=`T`.

## Information to store
For each **buggy** commit, we will store:
- All the information yielded by `git show`, which includes:
  - Commit message
  - Author
  - Date
  - Parent commit
  - Delta as a unified diff
- Hit-spectra matrix (with per-test coverage information and test outcomes).

## Caveats of current approach
Rewriting the git history, such as doing [commit squashing](https://github.com/blog/2141-squash-your-commits) may influence our single/multiple fault
analysis.
