#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def write_file(relative_path: str, content: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def replace_once(relative_path: str, old: str, new: str) -> None:
    path = ROOT / relative_path
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{relative_path}: expected one occurrence, found {count}: {old[:100]!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def prepend_once(relative_path: str, entry: str) -> None:
    path = ROOT / relative_path
    text = path.read_text(encoding="utf-8")
    if entry not in text:
        path.write_text(entry + text, encoding="utf-8")

# Register the module as a built-in plugin in the HTTP transport.
replace_once(
    "transports/bifrost-http/server/plugins.go",
    '\t"github.com/maximhq/bifrost/core/schemas"\n\t"github.com/maximhq/bifrost/plugins/compat"\n',
    '\t"github.com/maximhq/bifrost/core/schemas"\n\t"github.com/maximhq/bifrost/plugins/agentcapabilityrouter"\n\t"github.com/maximhq/bifrost/plugins/compat"\n',
)
replace_once(
    "transports/bifrost-http/server/plugins.go",
    "\tcase routing.PluginName:\n",
    "\tcase agentcapabilityrouter.PluginName:\n"
    "\t\tcapabilityRouterConfig, err := MarshalPluginConfig[agentcapabilityrouter.Config](pluginConfig)\n"
    "\t\tif err != nil {\n"
    "\t\t\treturn nil, fmt.Errorf(\"failed to marshal agent capability router config: %w\", err)\n"
    "\t\t}\n"
    "\t\treturn agentcapabilityrouter.Init(capabilityRouterConfig)\n\n"
    "\tcase routing.PluginName:\n",
)
replace_once(
    "transports/bifrost-http/server/plugins.go",
    "\t// 5. Routing rules. Runs after governance so rules evaluate against a fully stamped\n",
    "\t// 5. Agent capability router (opt-in). Runs after governance has stamped the caller\n"
    "\t// scope and before routing rules evaluate the logical model lane.\n"
    "\tcapabilityRouterConfig := s.getPluginConfig(agentcapabilityrouter.PluginName)\n"
    "\tif capabilityRouterConfig != nil && capabilityRouterConfig.Enabled {\n"
    "\t\ts.registerPluginWithStatus(ctx, agentcapabilityrouter.PluginName, nil, capabilityRouterConfig.Config, false)\n"
    "\t} else {\n"
    "\t\ts.markPluginDisabled(agentcapabilityrouter.PluginName)\n"
    "\t}\n"
    "\ts.Config.SetPluginOrderInfo(agentcapabilityrouter.PluginName, builtinPlacement, schemas.Ptr(5))\n\n"
    "\t// 6. Routing rules. Runs after governance so rules evaluate against a fully stamped\n",
)
replace_once(
    "transports/bifrost-http/server/plugins.go",
    "\ts.Config.SetPluginOrderInfo(routing.PluginName, builtinPlacement, schemas.Ptr(5))\n",
    "\ts.Config.SetPluginOrderInfo(routing.PluginName, builtinPlacement, schemas.Ptr(6))\n",
)
for old, new in [
    ("\t// 6. OTEL (if configured in PluginConfigs)\n", "\t// 7. OTEL (if configured in PluginConfigs)\n"),
    ("\ts.Config.SetPluginOrderInfo(otel.PluginName, builtinPlacement, schemas.Ptr(6))\n", "\ts.Config.SetPluginOrderInfo(otel.PluginName, builtinPlacement, schemas.Ptr(7))\n"),
    ("\t// 7. Semantic Cache (if configured in PluginConfigs)\n", "\t// 8. Semantic Cache (if configured in PluginConfigs)\n"),
    ("\ts.Config.SetPluginOrderInfo(semanticcache.PluginName, builtinPlacement, schemas.Ptr(7))\n", "\ts.Config.SetPluginOrderInfo(semanticcache.PluginName, builtinPlacement, schemas.Ptr(8))\n"),
    ("\t// 8. Compat (if any compat feature is enabled in ClientConfig)\n", "\t// 9. Compat (if any compat feature is enabled in ClientConfig)\n"),
    ("\ts.Config.SetPluginOrderInfo(compat.PluginName, builtinPlacement, schemas.Ptr(8))\n", "\ts.Config.SetPluginOrderInfo(compat.PluginName, builtinPlacement, schemas.Ptr(9))\n"),
    ("\t// 9. Maxim (if configured in PluginConfigs)\n", "\t// 10. Maxim (if configured in PluginConfigs)\n"),
    ("\ts.Config.SetPluginOrderInfo(maxim.PluginName, builtinPlacement, schemas.Ptr(9))\n", "\ts.Config.SetPluginOrderInfo(maxim.PluginName, builtinPlacement, schemas.Ptr(10))\n"),
    ("\t// 10. ModelCatalogResolver (last routing layer", "\t// 11. ModelCatalogResolver (last routing layer"),
]:
    replace_once("transports/bifrost-http/server/plugins.go", old, new)

# Add the plugin to the canonical built-in registry.
replace_once(
    "transports/bifrost-http/lib/config.go",
    '\t"github.com/maximhq/bifrost/framework/vectorstore"\n\t"github.com/maximhq/bifrost/plugins/compat"\n',
    '\t"github.com/maximhq/bifrost/framework/vectorstore"\n\t"github.com/maximhq/bifrost/plugins/agentcapabilityrouter"\n\t"github.com/maximhq/bifrost/plugins/compat"\n',
)
replace_once(
    "transports/bifrost-http/lib/config.go",
    "\tgovernance.PluginName,\n\totel.PluginName,\n",
    "\tgovernance.PluginName,\n\tagentcapabilityrouter.PluginName,\n\totel.PluginName,\n",
)

# Wire the independent plugin module into the transports release graph. The
# module is local-only until its first upstream tag exists, so use a zero
# pseudo-version plus an explicit relative replacement. This also makes
# `cd transports && go mod tidy` deterministic outside workspace resolution.
replace_once(
    "transports/go.mod",
    "\tgithub.com/maximhq/bifrost/framework v1.6.0\n\tgithub.com/maximhq/bifrost/plugins/compat v0.2.0\n",
    "\tgithub.com/maximhq/bifrost/framework v1.6.0\n"
    "\tgithub.com/maximhq/bifrost/plugins/agentcapabilityrouter v0.0.0-00010101000000-000000000000\n"
    "\tgithub.com/maximhq/bifrost/plugins/compat v0.2.0\n",
)
transports_mod = ROOT / "transports/go.mod"
transports_mod_text = transports_mod.read_text(encoding="utf-8")
local_replace = "replace github.com/maximhq/bifrost/plugins/agentcapabilityrouter => ../plugins/agentcapabilityrouter"
if local_replace not in transports_mod_text:
    transports_mod.write_text(transports_mod_text.rstrip() + f"\n\n{local_replace}\n", encoding="utf-8")

# Keep dependency automation aware of the new Go module.
replace_once(
    ".github/dependabot.yml",
    "  - package-ecosystem: gomod\n    directory: /plugins/governance\n",
    "  - package-ecosystem: gomod\n"
    "    directory: /plugins/agentcapabilityrouter\n"
    "    schedule:\n"
    "      interval: daily\n"
    "    open-pull-requests-limit: 0\n\n"
    "  - package-ecosystem: gomod\n"
    "    directory: /plugins/governance\n",
)

# Document the native order and why capability classification precedes CEL routing.
old_routing_table = """| Order | Plugin | Role |
|-------|--------|------|
| 4 | governance | Routing rules (CEL) + VK-scoped weighted load balancing |
| Higher | adaptive-loadbalancer (Enterprise) | Performance-based provider selection across the model catalog |
| 9 (last) | model-catalog-resolver | **Final fallback** — fills in `req.Provider` from the model catalog for unprefixed models when no earlier plugin picked one |

The resolver runs last so CEL routing rules can match on `provider == \"\"` (the unresolved state) and earlier plugins always get the canonical bare model. After `PreRequestHook` returns, the core validates that `req.Provider` is non-empty — an unresolvable request returns a 400 with a clear error.
"""
new_routing_table = """| Order | Plugin | Role |
|-------|--------|------|
| 4 | governance | Resolves the Virtual Key and stamps its scope on the request context |
| 5 | agent-capability-router (when enabled) | Rewrites configured dynamic aliases to deterministic role/capability lanes |
| 6 | routing | Evaluates CEL rules, computes `complexity_tier` when referenced, then applies VK-scoped provider selection |
| Higher | adaptive-loadbalancer (Enterprise) | Performance-based provider selection across the model catalog |
| Last | model-catalog-resolver | **Final fallback** — fills in `req.Provider` from the model catalog for unprefixed models when no earlier plugin picked one |

The capability router runs before `routing` so CEL rules see the classified logical lane while retaining the original caller and Virtual Key scope. The resolver runs last so CEL routing rules can still match on `provider == \"\"` (the unresolved state). After `PreRequestHook` returns, the core validates that `req.Provider` is non-empty — an unresolvable request returns a 400 with a clear error.
"""
replace_once("docs/plugins/sequencing.mdx", old_routing_table, new_routing_table)

# Add the page to the existing plugin navigation without reformatting docs.json.
docs_nav = ROOT / "docs/docs.json"
docs_text = docs_nav.read_text(encoding="utf-8")
nav_page = '"plugins/agent-capability-router"'
if nav_page not in docs_text:
    pattern = re.compile(r'(?P<indent>\s*)"plugins/getting-started",\n')
    match = pattern.search(docs_text)
    if match is None:
        raise RuntimeError("docs/docs.json: plugin getting-started navigation entry not found")
    indent = match.group("indent")
    replacement = match.group(0) + f'{indent}{nav_page},\n'
    docs_text = docs_text[:match.start()] + replacement + docs_text[match.end():]
    docs_nav.write_text(docs_text, encoding="utf-8")

prepend_once(
    "transports/changelog.md",
    "[feat]: register the native agent capability router plugin [@codex-corp](https://github.com/codex-corp)\n",
)

print("Applied native agent capability router changes")
