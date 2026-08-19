# Day 1 — ApexaiQ Research

Research into what ApexaiQ does, IT Asset Management, the competitive landscape, agentless architecture, cybersecurity fundamentals, and key industry terminology.

---

## 1. What Does ApexaiQ Do? What Industry Problem Does It Solve?

| Aspect | Details |
|---|---|
| What it is | Agentless, continuous IT asset assurance platform (SaaS) |
| Founded / HQ | 2021 — Milford, Massachusetts, USA |
| Core output | **ApexaiQ Score** (60–160) — one number for IT health, security & compliance |
| Who it serves | Financial services, healthcare, insurance, MSPs, mid-market & enterprise IT |
| Key capabilities | Asset discovery • risk scoring • compliance monitoring • EOL/EOS tracking • remediation prioritization • M&A due diligence • dashboards & integrations |
| Industry problem it solves | Fragmented tools, shadow IT, and outdated assets create blind spots — ApexaiQ unifies them into one prioritized risk view |
| Why it's different | Agentless deployment • one quantified score • business-impact-based prioritization • native MSP multi-tenancy |

---

## 2. What Is IT Asset Management (ITAM), and Why Do Companies Need It?

**ITAM** is the practice of tracking every hardware, software, and cloud asset an organization owns, from purchase to retirement.

**The Asset Lifecycle:**

| Stage | What Happens |
|---|---|
| 1. Planning | Forecast needs and set budget before buying |
| 2. Procurement | Purchase, lease, and record licensing terms |
| 3. Deployment | Install, configure, tag with owner/location |
| 4. Usage & Maintenance | Monitor, patch, track warranty/support |
| 5. Upgrade / Replacement | Refresh assets as they age or lose support |
| 6. Retirement & Disposal | Securely wipe and dispose of the asset |

**Why companies need asset management software:**

| Benefit | Why It Matters |
|---|---|
| Cost Control | Cuts duplicate purchases & unused licenses |
| Security | Surfaces outdated/unauthorized assets before attackers find them |
| Compliance | Keeps audit-ready records (HIPAA, ISO 27001, GDPR, PCI-DSS) |
| Efficiency | One source of truth instead of manual spreadsheets |
| Planning | Lifecycle data drives budgeting & refresh cycles |



---

## 3. Competitors of ApexaiQ

**Company snapshot:**

| Competitor | Primary Focus | Deployment Time | Pricing Model | Best For |
|---|---|---|---|---|
| ServiceNow | Enterprise ITSM + ITAM | 3–6 months | Quote-based, enterprise (high) | Large enterprises already on ServiceNow |
| Lansweeper | Network discovery & inventory | 1–2 weeks | Per-asset subscription (mid) | Mid-sized IT teams needing fast on-prem discovery |
| ManageEngine | Mid-market ITAM (AssetExplorer) | 2–6 weeks | Affordable tiered pricing (low) | Budget-conscious mid-market |
| Device42 | CMDB & dependency mapping | 4–12 weeks | $30K+/year at scale (high) | Data-center-heavy infrastructure teams |
| Flexera | Software license compliance (SAM) | 4–12 weeks | Quote-based, enterprise (high) | Enterprises facing complex vendor audits |
| **ApexaiQ** | Agentless continuous asset assurance | Days–weeks | SaaS subscription (competitive) | MSPs & orgs needing fast, unified risk visibility |

**Strengths, weaknesses & difference from ApexaiQ:**

| Competitor | Key Strength | Key Weakness | Difference from ApexaiQ |
|---|---|---|---|
| ServiceNow | Deep lifecycle & workflow integration; huge ecosystem | Expensive, complex, slow to deploy | ApexaiQ is lighter, agentless, purpose-built — no lengthy ITSM configuration |
| Lansweeper | Fast, accurate agentless network discovery | Weak cloud discovery; no risk scoring or SLA tracking | ApexaiQ adds compliance, obsolescence & prioritized remediation on top |
| ManageEngine | Affordable, easy to adopt | Limited security/compliance depth | ApexaiQ focuses on continuous security risk, not just bookkeeping |
| Device42 | Deep infrastructure & dependency mapping | Costly at scale; limited business context | ApexaiQ turns inventory into a quantified, board-level risk score |
| Flexera | Best-in-class software license normalization | Licensing-centric; not risk-scoring focused | Complementary — licensing vs. security risk |

**Case studies:**

| Competitor | Real-World Example |
|---|---|
| ServiceNow | A global bank adds the ITAM module to its existing ServiceNow ITSM, but needs months of configuration before seeing full asset-risk context. |
| Lansweeper | A mid-sized manufacturer gets an accurate inventory, but still manually cross-references vulnerability data in spreadsheets. |
| ManageEngine | A regional healthcare provider tracks laptops/licenses on a limited budget, but needs a separate tool for HIPAA risk assessment. |
| Device42 | A data-center-heavy enterprise maps dependencies before a migration, then layers a risk platform on top for compliance reporting. |
| Flexera | A global enterprise defends an Oracle licensing audit using Flexera, while tracking security posture separately. |



---

## 4. Why Is ApexaiQ an Agentless Platform?

**Agent-based vs. agentless:**

| Dimension | Agent-Based | Agentless |
|---|---|---|
| Installation | Software on every device | Nothing installed on devices |
| Deployment Speed | Slow — device by device | Fast — via APIs/protocols |
| Performance Impact | Uses local CPU/memory | No impact on the device |
| Maintenance | Update agents fleet-wide | Maintained centrally by vendor |
| Coverage | Devices without agent are invisible | Sees unmanaged & IoT/OT devices too |

**Why ApexaiQ chose agentless:**

| Reason | Benefit |
|---|---|
| Speed | Onboards a new environment in days, not months |
| Coverage | Covers legacy, IoT, and OT devices that reject agents |
| Low risk | One less piece of software to secure or conflict with existing tools |
| MSP scale | Economical to run across dozens of client tenants at once |

---

## 5. Cybersecurity Findings

**CIA Triad:**

| Principle | Meaning |
|---|---|
| Confidentiality | Only authorized users can access data (encryption, access control) |
| Integrity | Data stays accurate & unaltered (hashing, digital signatures) |
| Availability | Systems stay accessible when needed (redundancy, DDoS protection) |

**Common threats:**

| Threat | Description | Common Solution |
|---|---|---|
| Malware / Ransomware | Damages, steals, or encrypts data for ransom | Antivirus, EDR, backups, patching |
| Phishing | Tricks users into giving up credentials | Training, email filtering, MFA |
| Zero-Day Exploits | Attacks a flaw before a patch exists | Threat monitoring, rapid patching |
| DDoS | Floods a system to make it unavailable | Traffic filtering, load balancing |
| Insider Threats | Legitimate access misused | Least privilege, monitoring |

**Key frameworks:**

| Framework | What It Does |
|---|---|
| SIEM | Collects & correlates logs/events in real time for detection |
| SOAR | Automates response workflows across security tools |
| NIST CSF | Identify → Protect → Detect → Respond → Recover |
| MITRE ATT&CK | Knowledge base of real-world attacker tactics |


---

## 6. Key Concepts

| Concept | What It Means | Relation to ApexaiQ |
|---|---|---|
| ApexaiQ Score | 60–160 score of IT health, security & compliance | ApexaiQ's flagship risk metric |
| IT Asset Management | Tracking assets across their full lifecycle | The discipline ApexaiQ automates |
| Vulnerabilities | Weaknesses attackers can exploit | Continuously identified & scored (sourced from NVD + CWE) |
| Obsolescence | Assets becoming outdated/unsupported | Tracked as a risk factor |
| Compliance | Meeting laws/standards for data protection | Mapped automatically to HIPAA, ISO 27001, etc. |
| Maintenance | Keeping assets updated & functional | Tracked as a score input |
| End of Life / Support / Maintenance | Vendor stops selling / supporting / patching a product | Combined into one obsolescence signal |
| Asset Hygiene | Keeping assets secure, updated & configured | What the ApexaiQ Score effectively measures |
| Crown Jewel Assets | Most business-critical assets | Flagged for top remediation priority |
| Inventory | Complete, current list of all assets | The foundational data layer of the platform |
| NVD | US database of known vulnerabilities (CVEs), maintained by NIST | Ingested to enrich vulnerability data with CVSS scores |
| Patch Management | Deploying updates that fix vulnerabilities | Patch status feeds risk prioritization |
| Data Breaches | Unauthorized access to sensitive data | Reduced by closing visibility gaps |
| MSP | Third party managing a client's IT remotely | Supported via multi-tenant dashboard |
| Device Types | Classes of hardware/endpoints (servers, IoT, OT...) | Categorized to apply the right risk logic |
| True SaaS | Fully hosted, multi-tenant, browser-delivered app | ApexaiQ itself is True SaaS |
| Inbound / Outbound Integration | Data flowing in from, or out to, other systems | Pulls from AD/NVD; pushes to SIEM/ITSM/GRC |
| Compliance Standards (CISA, CISO, HIPAA, ISO 27001) | Agencies, roles & standards setting the security bar | Mapped for reporting; aligns with CISA-flagged CVEs |
| Perimeter | Traditional network boundary (firewalls, VPNs) | Covers perimeter & cloud-based assets alike |
| ROI / KPI | Return on investment / measurable performance metrics | Delivers fast ROI; surfaces KPIs like MTTR |
| Auto-remediation | Automatically fixing issues without manual work | Triggers automated fixes from risk findings |
| Network Protocols | Rules for data transmission (SNMP, SSH, HTTPS) | Used for agentless discovery |
| Due Diligence | Assessing risk before a business decision | Used for fast M&A IT risk assessment |
| SOAR | Automates & orchestrates security response | Can trigger workflows from ApexaiQ findings |
| Role of ITAM in Zero Trust | "Never trust, always verify" needs accurate asset data | Supplies the asset data access decisions rely on |
| CAASM | Unified view of all known & unknown cyber assets | ApexaiQ operates in this category |

