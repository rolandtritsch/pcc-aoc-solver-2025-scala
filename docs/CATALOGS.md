# Agent Company Catalog Research

Research snapshot: September 19, 2026

## Executive summary

There is no single catalog that is broader, better maintained, well validated,
and demonstrably production-tested. The ecosystem is fragmented.

The strongest alternatives to [this catalog][paperclip-companies] are:

| Candidate | Contents | Strongest quality | Main weakness | Assessment |
| --- | ---: | --- | --- | --- |
| [Ever Works Organizations][ever-orgs] | 36 companies | Breadth and structural validation | One-maintainer, two-day content burst with little adoption | Best broad alternative |
| [stubbi/companies][stubbi-companies] | 4 companies | Curation, provenance, licensing, and CI | Small and inactive since May 2026 | Best quality-focused alternative |
| [Paperclip built-in teams][paperclip-teams] | 4 teams | Native compatibility and active maintenance | Teams rather than complete companies | Safest foundation |
| [companies.sh][companies-directory] | 18 indexed companies | Cross-repository discovery | Mostly reindexes this repository | Useful directory, not a replacement |
| [ClipMart][clipmart] | 60 advertised listings | Browsing experience | Unverified, opaque, and not currently downloadable | Not ready |
| [PaperclipOrg][paperclip-org] | 2 advertised paid companies | Packaged commercial offering | Closed artifacts and no independent validation | Insufficient evidence |

The practical strategy is to combine Paperclip's built-in teams with selectively
audited packages from Ever Works, `stubbi/companies`, this repository, and the
GitHub long tail. No source should be imported directly into a consequential
environment without an acceptance review.

## Scope and method

"Better" was assessed against:

- direct Paperclip or [Agent Companies][agent-companies] `agentcompanies/v1`
  compatibility;
- breadth and depth of reusable packages;
- recent maintenance and contributor diversity;
- schema, graph, build, and import validation;
- source provenance and licensing;
- public auditability and adoption signals;
- evidence that templates work, rather than merely parse.

The research inspected live GitHub repository metadata, recursive file trees,
commit and contributor histories, pull requests, GitHub Actions workflows,
catalog manifests, Paperclip's current CLI documentation, and the live content
served by catalog websites. GitHub code search reached its 100-result cap.

No candidate package was imported or executed. Paid artifacts were not
purchased. Structural validation and repository activity therefore do not prove
runtime quality or business outcomes.

## Baseline: paperclipai/companies

At the snapshot date, the upstream repository contains 16 companies, 447 agent
definitions, 56 teams, 523 skills, 2 projects, and 7 tasks. Every company has a
Paperclip sidecar.

Its strengths are breadth within the Paperclip ecosystem, direct importability,
source links, and a documented contribution format. Its maintenance signals are
weak:

- the last upstream content commit was March 23, 2026;
- 45 of its 46 commits came from one contributor;
- 9 pull requests remain open, mostly without review;
- only 1 pull request has ever been merged;
- there are no GitHub Actions workflows or checks on the current head;
- there are no branch rules or releases.

This makes the repository useful seed material, but not a reliably maintained
dependency.

## Best broad alternative: ever-works/orgs

[Ever Works Organizations][ever-orgs] is the only clearly larger open catalog
found during the research.

### Ever Works evidence

- 36 `agentcompanies/v1` company packages;
- 343 agents, 99 teams, and 256 skills;
- coverage across engineering, marketing, security, finance, research,
  education, media, commerce, recruiting, and other business functions;
- MIT license and explicit attribution fields;
- a generated machine-readable manifest;
- [CI validation][ever-actions] for structure, frontmatter, reporting and
  manager graphs, and manifest consistency;
- vendor-neutral packages, with Ever Works-specific data isolated in `.works`
  sidecars.

Paperclip documents importing a company package from a local path or GitHub
repository. Its importer should consume the base `agentcompanies/v1` package and
ignore the Ever Works sidecar. This was not verified with a live dry run.

### Ever Works reservations

- All 36 companies were added in nine commits between July 17 and July 19,
  2026.
- The repository has one contributor and only one internally authored pull
  request.
- At the snapshot date it had 2 stars, no forks, and no content updates since
  July 19.
- Only 4 company packages contain projects and only 9 tasks exist across the
  entire catalog.
- None of the packages contains a `.paperclip.yaml` sidecar.
- Validation establishes structural consistency, not task performance.
- There are no published runtime evaluations, usage figures, or user outcome
  reports.

Ever Works is better than this repository for breadth and repository hygiene,
but it is not proven to be better in operation.

## Best curated alternative: stubbi/companies

[stubbi/companies][stubbi-companies] has the strongest curation and provenance
discipline found, although it is much smaller.

### stubbi evidence

- 4 companies covering financial services, legal services, academic research,
  and an industrial research lab;
- 39 agents, 16 teams, and 219 skills;
- per-company licenses and attribution notices;
- external material pinned to upstream commit SHAs and checked for drift;
- explicit human-review boundaries for regulated domains;
- reproducible build, test, and validation targets;
- [CI][stubbi-actions] runs both `make test` and `make check` for each company;
- the README accurately discloses the single-maintainer curation model.

### stubbi reservations

- The last update was May 15, 2026.
- It is maintained by one person and had 3 stars and no forks at the snapshot
  date.
- The repository has no projects or seed tasks, so these are carefully
  constructed workforces rather than operational business packages.
- Its five pull requests were self-authored and merged without independent
  review.

This is the best source for templates to trust *after inspection*, especially in
finance, legal, and research domains. It is not a general replacement catalog.

## Safest native source: Paperclip's team catalog

The actively maintained [Paperclip repository][paperclip] now includes the
first-party `@paperclipai/teams-catalog`, separate from this company catalog.

It currently ships:

- Core Exec Team;
- Product Engineering;
- Product Design;
- Content Machine.

The generated manifest records file hashes, dependency resolution, trust level,
and compatibility status. The package is covered by catalog validators,
shipped-catalog tests, server tests, and installation tests. Paperclip exposes
read-only inspection and preview commands before installation:

```sh
npx paperclipai teams browse
npx paperclipai teams inspect <catalog-id>
npx paperclipai teams preview <catalog-id> --company-id <id>
npx paperclipai teams install <catalog-id> --company-id <id>
```

These are the highest-confidence building blocks found, but they are four small
teams rather than a diverse catalog of finished companies. See the current
[Paperclip CLI documentation][paperclip-cli] and [generated team manifest][paperclip-teams].

## Discovery layer: companies.sh

The [companies.sh directory][companies-directory] and its
[open-source CLI][companies-tool] can discover and install compatible packages
from arbitrary GitHub repository paths.

The live directory API indexed 18 companies at the snapshot date:

- 16 from `paperclipai/companies`;
- 1 from `iamfiscus/agent-companies`;
- 1 from `aronprins/paperclip-company-playbook`.

The directory did not expose license, verification, or freshness fields for
these entries. It is a useful discovery and installation layer, but adds only
two packages beyond this repository and is not itself a richer source.

## ClipMart does not yet pass verification

[ClipMart][clipmart] advertises 60 templates and initially appears to be the
strongest alternative. The evidence does not support treating it as an
installable catalog yet.

- The homepage claimed 60 available templates, while its served payload exposed
  46 listing records and only 43 distinct import URLs.
- Every exposed listing record was marked unverified.
- All 46 exposed records had blank source-repository URLs, zero stars, zero
  forks, and the same April 11, 2026 creation date.
- Cost and revenue estimates were presented without supporting evidence. For
  example, [Lead Gen Machine][clipmart-lead-gen] claimed estimated monthly
  revenue of USD 2,000 to USD 10,000.
- The advertised template download path returned HTTP 404 during the live
  check.
- The [open-source site repository][clipmart-source] had 12 commits, no license,
  no tests, and no Actions workflows. Its July commit only added a documentation
  link; the functional implementation work dated from March.
- The deployed site's newer static listing data was not backed by auditable
  company packages in the public source repository.

ClipMart should be reconsidered only after downloads, source provenance,
validation, and real usage evidence are available.

## PaperclipOrg has insufficient public evidence

[PaperclipOrg][paperclip-org] advertised two paid companies—SaaS Factory and
E-Commerce Empire—with a third planned. The downloadable artifacts, change
history, validation, licensing details, and user results were not publicly
auditable without purchase.

This may be a commercial product rather than a community catalog, but there is
not enough public evidence to rank it above open alternatives.

## The wider ecosystem is fragmented

GitHub code search for `agentcompanies/v1` in `COMPANY.md` reached the 100-result
cap:

- 100 results across 58 repositories;
- 48 repositories with only one matching package;
- 10 repositories with multiple matching packages;
- several apparent catalogs that were forks or copies of this repository;
- many application-specific configurations rather than reusable templates.

Notable fragments include:

- `learners-superpumped/paperclip-templates`: five marketing and content
  examples, but no license or CI;
- `L1l1thLY/AgentCompany`: three templates with CI, bundled into a separate
  platform project;
- `iamfiscus/agent-companies`: one detailed 20-agent engineering company;
- `aronprins/paperclip-company-playbook`: one practical package and operating
  guide;
- many one-off legal, accounting, SaaS, research, game studio, and development
  companies.

Two useful projects generate packages rather than cataloging them:

- [Yesterday AI's company wizard][company-wizard] builds companies from modular
  agent templates, but does not ship complete company packages and had been
  inactive since April 2026;
- [Grolea Paperclip Blueprints][paperclip-blueprints] was active in September
  2026 and generates schema-valid bundles from a Markdown brief, but supplies no
  ready-made catalog.

## Recommendation

Do not replace this repository with one alternative. Use a curated portfolio:

1. Start with Paperclip's built-in teams for the trusted organizational core.
2. Use Ever Works as a broad source of structures and ideas.
3. Use `stubbi/companies` for deeper specialist packages.
4. Treat this repository and one-off GitHub packages as raw material.
5. Avoid ClipMart packages until its artifacts and provenance become auditable.
6. Maintain reviewed copies of adopted packages rather than importing mutable
   upstream heads into production.

In short: Ever Works is better by breadth, `stubbi/companies` is better by
curation, and Paperclip's internal team catalog is better by compatibility. None
is yet a clearly superior, production-proven marketplace.

## Package acceptance gate

Before adopting a package:

1. Pin the source commit.
2. Establish the package and upstream licenses.
3. Review provenance and all vendored or referenced skills.
4. Inspect prompts, scripts, tool permissions, and network behavior.
5. Scan for secrets, prompt injection, exfiltration paths, and destructive
   instructions.
6. Validate the schema, reporting graph, identifiers, and referenced files.
7. Run a Paperclip import preview or dry run.
8. Import into an isolated test company with agents initially paused.
9. Run bounded tasks with explicit expected outputs and budgets.
10. Record evaluation results before promoting the package.

[agent-companies]: https://github.com/agentcompanies/agentcompanies
[clipmart]: https://www.clipmart.ai/
[clipmart-lead-gen]: https://www.clipmart.ai/templates/lead-gen-machine
[clipmart-source]: https://github.com/paperclipai/clipmart
[companies-directory]: https://companies.sh/
[companies-tool]: https://github.com/paperclipai/companies-tool
[company-wizard]: https://github.com/Yesterday-AI/paperclip-plugin-company-wizard
[ever-actions]: https://github.com/ever-works/orgs/actions
[ever-orgs]: https://github.com/ever-works/orgs
[paperclip]: https://github.com/paperclipai/paperclip
[paperclip-blueprints]: https://github.com/Grolea-HQ/paperclip-blueprints
[paperclip-cli]: https://github.com/paperclipai/paperclip/blob/master/doc/CLI.md
[paperclip-companies]: https://github.com/paperclipai/companies
[paperclip-org]: https://papercliporg.com/
[paperclip-teams]: https://github.com/paperclipai/paperclip/blob/master/packages/teams-catalog/generated/catalog.json
[stubbi-actions]: https://github.com/stubbi/companies/actions
[stubbi-companies]: https://github.com/stubbi/companies
