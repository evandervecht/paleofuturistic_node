# Update an existing project with copier

Generated projects record their answers in `.copier-answers.yml`, which lets
copier re-apply the template when it evolves.

From inside a generated project with a clean working tree:

```sh
uvx copier update --trust
```

Copier re-renders the template with your recorded answers at the new template
version and three-way-merges the result with your local changes. Review the
diff, resolve any conflicts, then run the QA cycle before committing:

```sh
./workflow.cmd format
./workflow.cmd lint
./workflow.cmd test
```

To change an answer (for example switching `integrate_pages`), pass it
explicitly:

```sh
uvx copier update --trust --data integrate_pages=false
```
