# Single Fault Prevalence

Code in this repository looks at several open-source Java project subjects, mines their repositories
to identify bug-fixes and classifies those fixes according to the amount of bugs they eliminate.

Our goal with this study is to confirm our hypothesis that the majority of software bugs are
detected and fixed *one-at-a-time*. If true, this fact will certainly impact the way fault
localization techniques are employed in practice.

More information about each particular component in the analysis is provided in each sub-folder's
`readme.md` file.

## Usage

To install the Java runtime instrumenter, run:
```sh
make install-instrumentation-plugin
```

Mine subject repositories:
```sh
make run-miner
```

After the miner completes, we can summarize the analysis by:
```sh
make read-db
```
