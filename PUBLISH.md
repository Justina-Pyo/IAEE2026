# Publish to your GitHub account

Create an empty repository in your own account (suggested name: `nairobi-baas-rider-costs`). Do not initialize it with a README because this directory already has one. You may start private and change visibility after checking the files. This package contains aggregate data only.

With GitHub Desktop, add this folder as a local repository and publish it to the chosen account.

Alternatively, after configuring Git and authenticating GitHub locally:

```bash
git init -b main
git add .
git commit -m "Add reproducible Nairobi rider cost analysis"
git remote add origin https://github.com/YOUR_ACCOUNT/nairobi-baas-rider-costs.git
git push -u origin main
```

Replace YOUR_ACCOUNT. Do not paste passwords or tokens into source files or chat. If this directory is already initialized, omit `git init`; inspect `git status` and `git remote -v` before adding a remote. A successful push is required before citing a repository URL in a submission. Avoid links that identify the author in the anonymous manuscript.
