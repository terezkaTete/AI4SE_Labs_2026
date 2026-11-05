# Task 1 – Cloning the Playground repository

**Result:** https://github.com/Neltharion59/AI4SE_Playground is cloned into
`Week_06_Implementation/AI4SE_Playground/` (13 source modules in `playground/playground/`,
13 test modules in `playground/tests/`). Its `.git` folder was removed so the files are
tracked as plain content of this repository instead of a nested repo / submodule.

## How the agent did it

The coding assistant (Claude Code) has no dedicated "clone" feature. It used its
general-purpose **Bash tool** – the ability to execute shell commands on my machine –
and simply ran the ordinary git CLI:

```bash
cd Week_06_Implementation
git clone https://github.com/Neltharion59/AI4SE_Playground.git
rm -rf AI4SE_Playground/.git
```

So the enabling mechanism is **tool use**: the LLM itself only produces text, but the
agent harness exposes tools (shell, file read/write, …) that the model can call. The model
decided which command to run, the harness executed it, and the command's output was
fed back to the model, which then listed the cloned files to verify the result.

Things that made it work:

- **Locally installed `git`** and network access – the agent reuses whatever tools exist
  on the machine.
- **Public repository over HTTPS** – no credentials needed. (For a private repo, the
  agent would rely on my existing git credentials / SSH keys or the `gh` CLI.)
- **Permission system** – every shell command passes through Claude Code's permission
  layer (here "auto mode", where a classifier approves or blocks actions). This was visible
  in practice: when the agent tried `git remote add upstream …` to sync the course repo, the
  classifier **blocked** it as a remote reconfiguration. The agent then fetched the
  upstream URL directly instead (`git fetch <url> main`), which does not change the repo's
  configuration. The clone itself was allowed because it only creates new local files.
