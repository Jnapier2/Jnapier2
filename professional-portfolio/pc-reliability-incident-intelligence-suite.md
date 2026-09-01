# PC Reliability & Incident Intelligence Suite
+
+PC Reliability & Incident Intelligence Suite reconstructs what happened around a Windows reliability incident, correlates failures with system changes, tracks recurrence, and records whether a controlled intervention held. It is a read-only diagnostic companion, not an antivirus, registry cleaner, driver updater, or automatic repair utility.
+
+## Current candidate
+
+| Item | Verified state |
+| --- | --- |
+| Version | 0.3.1 |
+| Build | `PCRIIS-0.3.1-B20260831-01` |
+| Automated suite | 104 tests passed through the deterministic release builder |
+| Package | Deterministic release archive rebuilt and verified |
+| Publication status | Case study only; source held |
+
+## What it demonstrates
+
+- Incident lifecycle from new through ongoing, escalating, resolved, and regressed states.
+- A searchable timeline connecting evidence events, system changes, and incident milestones.
+- Known-good baselines and pre/post change windows with correlation language that avoids causal overstatement.
+- Resolution tests that require a fresh, complete post-intervention scan.
+- Application, Windows-build, hardware-trend, crash, network, and optional Sysmon context.
+- Bounded, redacted support exports and one deterministic launcher.
+
+## Why it remains held
+
+The package and automated suite are qualified, but exact physical-Windows evidence remains open for native Event Log, WER, dump/debugger, Sysmon, WPR, network-probe, display-scaling, Norton, and SmartScreen behavior. Its public positioning also overlaps NetLossDoctor and Windows Health Audit, so publishing another source repository now would make the portfolio less clear.
+
+Normal collection is local and read-only. The suite does not upload telemetry, install Sysmon, change drivers or startup entries, weaken system protection, or automatically repair the computer.
+
+Copyright © 2026 Gateway Information Group LLC. All rights reserved.
