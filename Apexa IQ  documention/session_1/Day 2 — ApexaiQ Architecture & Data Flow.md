# Day 2 — ApexaiQ Architecture & Data Flow

A closer look at how ApexaiQ actually works under the hood — how data makes its way from a customer's network into the ApexaiQ dashboard, and how it gets enriched and displayed along the way.

[ApexaiQ Flow of Data](../../assets/apexaiq-data-flow.jpeg)

## The 9-Step Data Flow

| # | Component | What It Does |
|---|---|---|
| 1 | **Security Tools** (in Your Network) | The tools you're already running — EDR, IAM, vulnerability scanners, and the like — sitting inside your own network |
| 2 | **ApexaiQ Collector** | A lightweight piece deployed inside your network, behind your firewall, that talks directly to those security tools |
| — | **Accelerator** (blue arrow, 1→2) | Pulls data *out of* your security tools and *into* the Collector |
| — | **Integration** (green arrow, 2→1) | Sends data and actions back *out* to your security tools (triggering a remediation, for example) |
| 3 | **Raw Feed → Pre Feed Rules** | The Collector pushes a raw data feed out through the firewall; automatic rules clean it up and normalize it before it ever reaches the dashboard |
| 4 | **ApexaiQ Dashboard (SaaS) → Post Feed Rules** | The core cloud platform processes the incoming data, then automatic rules route the resulting "Processed Feed" onward |
| 5, 6, 7 | **Devices, Users, Software** | The processed feed gets sorted into these three buckets — the actual inventory categories |
| 8 | **Enrich Rules / Your Input** | You can manually layer in extra context here — ownership, criticality, business details — that enriches the Devices records |
| 9 | **Integration** (label) | Loops back to the bidirectional relationship happening at steps 1–2 |

## Key Takeaway: Refining the "Agentless" Claim

Yesterday's research (Day 1) framed ApexaiQ as fully agentless, implying zero footprint anywhere at all. This diagram fills in an important detail:

- **"Agentless" is still accurate in the sense that matters most** — there's no agent sitting on every individual endpoint, no software installed on each laptop, server, or device. That part checks out.
- **That said, there is one lightweight Collector per customer network**, living behind the firewall, that talks to existing security tools and relays their data out to the SaaS dashboard.
