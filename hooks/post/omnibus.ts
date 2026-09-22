// Oh My Pi entry point. Claude Code ignores this file (it reads hooks.json);
// omp discovers hooks/post/*.ts under a plugin root and loads it as an
// extension. Together they give the plugin one mirror script for two harnesses.
import type { ExtensionAPI } from "@oh-my-pi/pi-coding-agent";
import { spawnSync } from "node:child_process";
import { resolve } from "node:path";

const PLUGIN_ROOT = resolve(import.meta.dir, "..", "..");
const MDLOG = resolve(PLUGIN_ROOT, "scripts", "mdlog.py");

export default function omnibus(pi: ExtensionAPI): void {
  // Every skill runs scripts as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/..."`.
  // Claude Code sets the variable; omp's bash tool inherits it from here.
  process.env.CLAUDE_PLUGIN_ROOT = PLUGIN_ROOT;

  // Equivalent of the Claude Code `Stop` hook: mirror the turn into the note.
  pi.on("session_stop", async (event, ctx) => {
    const payload = JSON.stringify({
      session_id: event.session_id,
      cwd: ctx.cwd,
      messages: event.messages,
    });
    const run = spawnSync("python3", [MDLOG], {
      input: payload,
      cwd: ctx.cwd,
      encoding: "utf8",
      timeout: 30_000,
    });
    const failure = run.error?.message ?? (run.status === 0 ? "" : run.stderr.trim());
    if (failure && ctx.hasUI) {
      ctx.ui.notify(`omnibus mirror failed: ${failure}`, "warning");
    }
  });
}
