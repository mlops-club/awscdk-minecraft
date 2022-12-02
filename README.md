# 📣 Welcome to the December 2022 Minecraft Hackathon


## Contributing

The setup has only been tested for Linux and MacOS, not Windows :(.
If you're on windows, you'll have the best contributor experience using the Windows Subsystem for Linux 2 (WSL2).

### How do I run this project locally?

```
# install "just"; it's like "make", but less frustrating
brew install just

# install the project's python packages and pre-commit
just install
```

### How do I add code?

We use pull requests. Create new branches based on `trunk` for experimentation, then open a PR for it.
You don't have to wait until you want to merge code to open a PR. For this project, the main purpose of doing PRs
is to share knowledge and get early feedback on your ideas.

Passing the `pre-commit` checks isn't a huge deal. They are mostly for your own benefit to prevent you
committing things to the repo that you don't want. You can always override `pre-commit` by running

```bash
git commit -m "I really want to commit this large file" --no-verify
```

#### Notes on commits

Ask Eric or Ryan if you need any help with these.

DON'T COMMIT...

- credentials. Feel free to put them in a `.env` file, but make sure it's gitignored!
- large files (large CSV, ML model weights, C binaries, video, etc.)
  use git LFS rather than committing it directly.
- unformatted code

The pre-commit hooks setup for this repo when you ran `just install` will remind you
about these each time you commit :)
