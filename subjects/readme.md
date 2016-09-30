# Subjects

The initial list of subjects is located at `java-projects.txt`. The file is curated list of java
projects used for analyzing pull requests in Github taken from
[gousiosg/pullreqs](https://github.com/gousiosg/pullreqs/blob/master/projects/java-projects.txt).

A python script to filter this list according to different criteria was also created. Details are
provided below.

## Dependencies

* Python 3.4+
* [Virtualenv](https://virtualenv.pypa.io/)

## Usage

```sh
make run
```

## Currently implemented passes

Current filtering passes include:

1. Checking if there is a `pom.xml` file at the root. Limiting our search for the top-level
`pom.xml` to the repository root helps streamline our future analyses.
1. Running `mvn test` in the project's master branch HEAD and ensuring the process has a return code
of `0`.

## Passes to be implemented

* Collecting a non-empty hit-spectrum matrix by running Crowbar/GZoltar instrumentation (e.g. using
[this maven plugin](https://github.com/aperez/aes-maven-plugin)).

## Github session token

Github's API might rate-limit the amount of anonymous requests you are allowed to make. To
circumvent that, you can [request an API
token](https://help.github.com/articles/creating-an-access-token-for-command-line-use/) and export
it to your environment:

```sh
export GITHUB_TOKEN=<token>
```
