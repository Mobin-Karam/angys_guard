# AngysGuard repository rename and GitHub Projects runbook

## Canonical repository name

The selected repository slug is:

```text
Mobin-Karam/angysguard
```

The current repository remains `Mobin-Karam/laptop_guard_v3` until the GitHub repository Settings rename is executed. GitHub should then redirect old repository URLs, but documentation and clone commands should still be migrated to the canonical AngysGuard URL.

The repository rename does **not** automatically rename the installed Python package/module/CLI. `laptop-guard` and `laptop_guard` remain compatibility identifiers until a separately validated migration is released.

## Rename action

The repository owner performs the GitHub admin rename:

```text
Settings -> General -> Repository name -> angysguard -> Rename
```

After the rename:

1. verify `https://github.com/Mobin-Karam/angysguard`;
2. verify the old repository URL redirects;
3. update local remotes to the canonical URL;
4. verify Actions and repository-management bootstrap;
5. update canonical clone/docs/package URLs;
6. refresh Graphify and repository presentation;
7. complete the remaining acceptance criteria in issue #30.

A local clone can update its remote after the rename with:

```bash
git remote set-url origin https://github.com/Mobin-Karam/angysguard.git
```

## GitHub Project v2

Canonical project title:

```text
AngysGuard — Product, Platform & Architecture Delivery
```

The board is defined by:

- `docs/PROJECT_MANAGEMENT.md` — human planning contract;
- `.github/repository-management/project-v2.json` — machine-readable project blueprint;
- `.github/repository-management/issues.json` — canonical milestone/label assignment;
- `.github/repository-management/milestones.json` — delivery targets;
- issue #9 — project-level tracker.

The project contains current hardening, v11.2-v12.0, architecture evolution, v13 self-hosted/Linux app, v14 managed control, Windows/Android expansion, security, provider work, and platform requests.

## Project bootstrap

GitHub Projects v2 is user/organization scoped. The normal repository `GITHUB_TOKEN` is not sufficient for this board. GitHub CLI requires a token with the `project` scope.

Create a repository secret named:

```text
ANGYSGUARD_PROJECT_TOKEN
```

Do not commit or print the token.

Then run the manual workflow:

```text
Actions -> AngysGuard Project v2 Bootstrap -> Run workflow
```

The workflow runs `scripts/bootstrap_github_project.sh`, which:

- finds or creates the canonical AngysGuard Project;
- links it to the repository;
- creates Priority, Track, Area, Effort, Target and Blocked fields when missing;
- adds the roadmap issues defined in `project-v2.json`;
- sets Target from milestone groups;
- maps Priority/Track/Area/Blocked from issue labels;
- can be rerun to synchronize later changes.

The current GitHub CLI/API surface does not expose project-view creation in the same way as project/field/item operations. Configure the views described in `docs/PROJECT_MANAGEMENT.md` in the GitHub Projects UI after the project is created.

## Security

- never put a GitHub token in repository files, issues, logs, or bot messages;
- use a scoped token dedicated to project synchronization;
- keep repository/application runtime secrets separate from GitHub administration credentials;
- repository renaming must not change or expose AngysGuard device-secret storage.
