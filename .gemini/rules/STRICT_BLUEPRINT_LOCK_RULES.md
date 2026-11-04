# STRICT AI BLUEPRINT LOCK RULE (৬টি মার্কডাউন ব্লুপ্রিন্ট লক)

> **MANDATORY DIRECTIVE FOR ALL AI AGENTS & CODING ASSISTANTS:**
> This rule is an absolute constraint for all AI agents working in this project. You must strictly obey this protocol at all times without exception.

---

## 1. The 6 Markdown Blueprint Lock Hierarchy (/docs ROOT)

Before making any proposal, executing any command, or writing code, the AI must align with the **6 Markdown Blueprint Lock Architecture**:

1. **`docs/PRD.md` (#01 Product Requirements Document):** Defines project scope, target devices, core features, and user requirements. Never add out-of-scope features.
2. **`docs/AppFlow.md` (#02 Application & User Flow):** Defines the exact deterministic execution pipeline. Never skip diagnostic or backup stages.
3. **`docs/UI_Spec.md` (#03 CLI & User Experience Specifications):** Defines user-facing CLI menus, progress counters, and verification tables.
4. **`docs/TRD.md` (#04 Technical Requirements Document):** Defines low-level Android subsystems (Cgroups, PowerKeeper, AppOps, Netpolicy, Doze).
5. **`docs/Schema.md` (#05 Data Schemas & App Dictionary):** Defines Tier 1 (Priority Communication), Tier 2 (Restricted Drainers), and Tier 3 (Protected Frameworks).
6. **`docs/Plan.md` (#06 Phased Execution & Safety Verification Plan):** Defines execution phases, safety guardrails, and CI validation protocols.

---

## 2. Strict Operational Boundaries (Zero-Mistake Protocol)

### A. Strict Scope Isolation (Zero Cross-Repo Contamination)
- **Rule:** This repository is `Noti-Fixer for Chinese Devices`.
- **Constraint:** NEVER introduce files, references, code, or documentation from any other project (e.g. Circle to Search, Mail Merge, etc.).
- **Enforcement:** If another project exists on the machine, keep it 100% separate. Treat this repository as a completely isolated open-source package.

### B. Device Actions vs Repository Commits
- **Rule:** Do NOT blindly push to Git on every single ad-hoc user query or test command.
- **Constraint:** Git commits must only be made for structured, tested, production-grade improvements to the tool/engine that benefit all users of the repository.
- **Enforcement:** Keep test scripts, intermediate logs, and scratch files local or in `.gitignore`. Never clutter the Git history with one-off device logs.

### C. Zero Destructive Commands (Hard Security Gate)
- **Rule:** Never suggest or execute root (`su`), bootloader unlocking, factory resetting, or package uninstallation.
- **Constraint:** All commands must pass `scripts/safety_guard.py`.
- **Enforcement:** If a command contains prohibited tokens (`uninstall`, `pm clear`, `wipe`, `format`, `rm -rf`), it must be aborted immediately.

### D. Always Backup Before Changes
- Every execution of `apply_notification_fix.py` MUST generate a reversible snapshot in `backups/backup_<device>_<timestamp>.json` before applying changes.

### E. Mandatory Empirical Verification
- Never claim success without live proof.
- Verify that Google FCM socket (`mtalk.google.com:5228`) is connected.
- Verify that Standby Buckets, AppOps, and Doze whitelists match the specifications in `docs/Schema.md`.
