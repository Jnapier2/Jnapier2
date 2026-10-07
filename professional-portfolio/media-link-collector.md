# Media Link Collector

**Keep useful media references together without downloading the media.**

Media Link Collector turns a starting page into a reviewable list of discovered video, audio, image, playlist, and embedded-player links. A local browser interface lets someone narrow the scope, filter results, and export selected references to TXT or CSV.

It is useful when cataloging media on a site you own or have permission to inspect. Each reference retains its source page, title, type, and discovery evidence, so the result can be reviewed before another tool uses it.

## Design choices worth inspecting

- **Scope stays explicit.** Page-only, folder, and same-site choices keep discovery bounded. Collection follows discovered links rather than inventing addresses or claiming full-site coverage.
- **References keep their context.** Deduplication reduces repeated entries while source and discovery evidence explain where a result came from.
- **Export follows the review.** Filters and row selection let a person decide which references to keep. TXT contains URLs; CSV adds supporting context.
- **Progress can be resumed.** Saved continuation supports returning to an interrupted collection, while visible activity distinguishes completed work from incomplete coverage.
- **Collection respects access limits.** The tool observes robots rules and server backoff. It does not use logins, browser cookies, or access-control bypasses.

## Inspect a real output example

Open the [synthetic CSV export](evidence/media-link-collector-sample.csv) and [TXT export](evidence/media-link-collector-sample.txt). They come from a retained local fixture run, with loopback host addresses replaced for sharing. They demonstrate exported references, not playable media or successful crawling of those example addresses.

The fixture includes a media reference with a query string. Preserving that query illustrates why deduplication must not silently discard information needed to identify a resource. Actual signed links may be sensitive and should remain private.

## Availability and evidence

This is a documentation-only case study of the retained `0.1.0` Windows candidate. Application source and the runnable package remain private; no public application download is offered here.

An October 7, 2026 review checked the retained artifact and its synthetic output. Earlier local launcher and browser checks remain dated qualification evidence. Broad website compatibility, media playback, physical-device coverage and exhaustive collection are not established. JavaScript-only or authenticated media can be absent; this tool collects references and does not download or validate remote media.

The project demonstrates bounded discovery, evidence-preserving cataloging, resumable workflows, and deliberate export controls. No adoption, speed improvement, time-savings or completeness outcomes are claimed.

[Program index](README.md) · [GitHub profile](../README.md)

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
