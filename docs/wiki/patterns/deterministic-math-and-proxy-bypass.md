# Pattern: Deterministic Math Generation & Local-Proxy Bypass

## Summary
Two robustness patterns adopted in Home Kumon: (1) generate math problems by computation,
not by prompting an LLM; (2) force local (localhost) network calls to bypass a corporate
proxy. Related: [[home-kumon-architecture]], [[home-kumon-app]].

## When to use
- **Deterministic math:** whenever an answer key must be provably correct and the LLM adds
  risk without benefit (arithmetic, anything computable). The model is great for reading/logic
  prose but unreliable and slow for arithmetic, and a wrong key would mark a correct child
  wrong.
- **Local-proxy bypass:** whenever an app on a managed/corporate machine must reach a service
  on `localhost` while a system proxy (PAC) routes all other traffic through an inspecting
  proxy (e.g. iboss → `127.0.0.1:8009`).

## Example
**Deterministic math** (`app/content.py`): math problems are produced by `_math_starter()`
(computes the prompt and the exact answer, including `quotient_remainder` like `57R14`).
`generate_batch()` routes `subject == "math"` to this computed path (source `"computed"`);
reading/logic use LM Studio with a starter-bank fallback.

**Proxy bypass** (`app/lmstudio.py`): the LM Studio client uses a `requests.Session` with
`trust_env = False`, so `HTTP(S)_PROXY` is ignored and the local `localhost:1234` call goes
DIRECT. The launchers also export `NO_PROXY=localhost,127.0.0.1,::1`. For `pip` behind the
proxy, `run.sh`/`run.bat` accept `PIP_PROXY` and auto-add `--trusted-host` flags (SSL
inspection re-signs certs, which pip would otherwise reject):
`PIP_PROXY=http://127.0.0.1:8009 ./run.sh`.

## Anti-patterns
- ❌ Asking the LLM to produce math problems *and* their answer keys, then trusting them.
- ❌ Hardcoding a proxy in app code (use `trust_env`/`NO_PROXY` so behavior follows the env).
- ❌ Pointing LM Studio at the machine's hostname/LAN IP — the PAC only bypasses
  `localhost`/`127.0.0.1`, so a non-local address would be proxied and fail.
- ❌ Globally disabling TLS verification to fix pip — scope it to PyPI hosts via
  `--trusted-host` only.
