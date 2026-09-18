# Place Farmy on your Mac and publish it

The original snapshot was prepared in a remote workspace. On 2026-09-18 the project was verified at `/Users/Shared/projects/farmy`. The extracted files did not include Git history; any new local history starts from this extracted baseline. See [the workspace audit](implementation-plan.md).

## Local folder

The handover describes `farmy-project.zip` as containing a `farmy` directory with local Git history, but that history was absent from the inspected extraction. For a fresh transfer, inspect the archive contents before extracting. Move that directory to the requested `/users/shared/projects/farmy`. Standard macOS spelling is `/Users/Shared/projects/farmy`; on a case-sensitive filesystem these paths differ, so select the one you intend. Do not overwrite an existing directory.

For example, after extracting into Downloads and confirming the target does not exist:

```bash
mkdir -p /Users/Shared/projects
mv ~/Downloads/farmy /Users/Shared/projects/farmy
cd /Users/Shared/projects/farmy
python3 scripts/check_docs.py
git status
```

The handover reports an original automation-authored commit, but that commit was not present in the extraction. Check `git config user.name` and `git config user.email` before creating replacement history; do not claim it preserves the original commit.

## Public repository

Published on 2026-09-18 at [cgrbxl/farmy](https://github.com/cgrbxl/farmy), with `main` tracking `origin/main`. New history was initialised from the extracted files. The commands below are retained for fresh setup; do not rerun repository creation against the existing repository.

The connected GitHub account observed during preparation was `cgrbxl`. The following are user-executed instructions and do not imply the repository exists. If publishing under another account or organisation, replace the owner.

With GitHub CLI installed and authenticated:

```bash
gh auth login
gh repo create cgrbxl/farmy --public --source=. --remote=origin --push --description 'Farmer-controlled memory and a composable agricultural intelligence ecosystem'
```

If the repository name already exists, inspect it before proceeding; do not overwrite it or force-push. Alternatively create an empty public repository through GitHub's interface and follow its instructions to add the remote and push the existing main branch. Do not initialise a second README remotely.

## After publishing

Select licensing terms, configure private vulnerability reporting, and choose branch protection/review rules appropriate to contributors. These are future repository settings, not settings applied by this snapshot.

This is a documentation repository. Farmy installation commands will be added when working components and validated deployment packages exist.
