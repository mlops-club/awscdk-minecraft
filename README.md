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

Alternatively, without brew:
```
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to <DEST IN YOUR PATH>
```

where `DEST IN YOUR PATH` refers to a directory that is present in your `$PATH` environment variable. For example, you might have in your `~/.bashrc` the line `PATH=~/bin:$PATH` to look for programs in `~/bin` first, which would be the "DEST" supplied above.

You also need `node` to run `pre-commit`, which you can install with `brew install nvm` and `nvm install 18`.


### How do I add code?

We use pull requests. Create new branches based on `trunk` for experimentation, then open a PR for it.
You don't have to wait until you want to merge code to open a PR. For this project, the main purpose of doing PRs
is to share knowledge and get early feedback on your ideas.

Passing the `pre-commit` checks isn't a huge deal. They are mostly for your own benefit to prevent you
committing things to the repo that you don't want. You can always override `pre-commit` by running

```bash
git commit -m "I really want to commit this large file" --no-verify
```

> 📌 Note: you may want to use a different email/username for this repository than
> you typically use on your development machine. You can set your git settings locally
> like so:

```bash
git config --local user.email my-personal-email@gmail.com
git config --local user.user my-github-username
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
