"""
create_sample_pdfs.py — Generates 3 sample cloud security policy PDFs for demo purposes.
Run this ONCE before ingesting: python create_sample_pdfs.py
"""

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from pathlib import Path

OUTPUT_DIR = Path("data/policies")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()

def build_pdf(filename: str, title: str, sections: list[dict]):
    path = OUTPUT_DIR / filename
    doc = SimpleDocTemplate(
        str(path),
        pagesize=LETTER,
        leftMargin=1*inch, rightMargin=1*inch,
        topMargin=1*inch, bottomMargin=1*inch
    )

    title_style = ParagraphStyle(
        "TitleStyle", parent=styles["Title"],
        fontSize=20, textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=14, alignment=TA_CENTER
    )
    h1_style = ParagraphStyle(
        "H1Style", parent=styles["Heading1"],
        fontSize=14, textColor=colors.HexColor("#16213e"),
        spaceBefore=14, spaceAfter=6
    )
    h2_style = ParagraphStyle(
        "H2Style", parent=styles["Heading2"],
        fontSize=12, textColor=colors.HexColor("#0f3460"),
        spaceBefore=10, spaceAfter=4
    )
    body_style = ParagraphStyle(
        "BodyStyle", parent=styles["BodyText"],
        fontSize=10, leading=14, spaceAfter=6, alignment=TA_LEFT
    )

    story = []
    story.append(Paragraph(title, title_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#0f3460")))
    story.append(Spacer(1, 0.2*inch))

    for section in sections:
        story.append(Paragraph(section["heading"], h1_style))
        for sub in section.get("subsections", []):
            story.append(Paragraph(sub["title"], h2_style))
            story.append(Paragraph(sub["body"], body_style))
        story.append(Spacer(1, 0.1*inch))

    doc.build(story)
    print(f"  [OK] Created: {path}")


# -- Document 1: NIST Cybersecurity Framework ----------------------------------
nist_sections = [
    {
        "heading": "1. Introduction",
        "subsections": [
            {
                "title": "1.1 Purpose",
                "body": (
                    "This document summarizes the NIST Cybersecurity Framework (CSF) Version 1.1 as adopted "
                    "by our organization. The Framework provides a policy framework of computer security guidance "
                    "for how private sector organizations in the United States can assess and improve their ability "
                    "to prevent, detect, and respond to cyber attacks. The Framework is organized around five core "
                    "functions: Identify, Protect, Detect, Respond, and Recover."
                )
            },
            {
                "title": "1.2 Scope",
                "body": (
                    "This policy applies to all employees, contractors, and third-party vendors with access to "
                    "organizational information systems, including cloud-hosted infrastructure on AWS, Azure, and GCP. "
                    "All cloud workloads classified as Confidential or higher must comply with the controls outlined "
                    "in this document. Exemptions require written approval from the Chief Information Security Officer (CISO)."
                )
            }
        ]
    },
    {
        "heading": "2. IDENTIFY (ID)",
        "subsections": [
            {
                "title": "2.1 Asset Management (ID.AM)",
                "body": (
                    "All cloud assets — including virtual machines, databases, storage buckets, serverless functions, "
                    "and network components — must be catalogued in the organization's Configuration Management Database (CMDB) "
                    "within 24 hours of provisioning. Assets must be tagged with: Owner, Environment (prod/staging/dev), "
                    "Data Classification, and Cost Center. Untagged assets are subject to automated suspension after 72 hours. "
                    "Monthly audits of the CMDB are required and must be reviewed by the Cloud Security team."
                )
            },
            {
                "title": "2.2 Risk Assessment (ID.RA)",
                "body": (
                    "A formal risk assessment must be conducted for all new cloud deployments before go-live, "
                    "and at minimum annually for existing workloads. Risk assessments must evaluate: threat likelihood, "
                    "potential impact, existing control effectiveness, and residual risk. All High and Critical risks "
                    "must have a documented remediation plan with an owner and target date. Risk acceptance must be "
                    "approved in writing by the system owner and the CISO."
                )
            },
            {
                "title": "2.3 Governance (ID.GV)",
                "body": (
                    "Cybersecurity roles and responsibilities are defined in the RACI matrix maintained by the Security "
                    "Governance team. The Cloud Security Policy is reviewed and updated annually or following a material "
                    "change in risk posture (e.g., major cloud migration, acquisition, or significant incident). "
                    "Compliance with this policy is assessed quarterly via automated scanning tools and annually via "
                    "third-party audit."
                )
            }
        ]
    },
    {
        "heading": "3. PROTECT (PR)",
        "subsections": [
            {
                "title": "3.1 Identity and Access Management (PR.AC)",
                "body": (
                    "Multi-Factor Authentication (MFA) is mandatory for all cloud console access, API key usage for "
                    "production environments, privileged accounts (e.g., root, admin), and remote access via VPN. "
                    "Principle of Least Privilege (PoLP) must be enforced: IAM roles and policies must grant only the "
                    "minimum permissions required. IAM policies must be reviewed quarterly. Shared credentials are "
                    "strictly prohibited. Service accounts must use short-lived tokens (max 1-hour TTL) via instance "
                    "metadata or Workload Identity Federation."
                )
            },
            {
                "title": "3.2 Data Security (PR.DS)",
                "body": (
                    "All data classified as Confidential or Restricted must be encrypted at rest using AES-256 and "
                    "in transit using TLS 1.2 or higher. Encryption keys must be managed through a dedicated Key "
                    "Management Service (AWS KMS, Azure Key Vault, or GCP Cloud KMS). Key rotation must occur at "
                    "least annually. Storage buckets/blobs containing sensitive data must have public access blocked "
                    "by policy and verified monthly. Data Loss Prevention (DLP) scanning must be enabled on all "
                    "production storage containing PII or payment data."
                )
            },
            {
                "title": "3.3 Protective Technology (PR.PT)",
                "body": (
                    "Web Application Firewalls (WAF) are required for all public-facing web applications. "
                    "Network segmentation must be enforced using VPCs/VNets with security groups and NACLs "
                    "following a deny-by-default approach. DDoS protection must be enabled for all production "
                    "workloads. Vulnerability scanning of cloud images and running workloads must occur at least weekly. "
                    "Critical and High vulnerabilities must be remediated within 15 days. Medium within 45 days."
                )
            }
        ]
    },
    {
        "heading": "4. DETECT (DE)",
        "subsections": [
            {
                "title": "4.1 Security Continuous Monitoring (DE.CM)",
                "body": (
                    "CloudTrail (AWS), Activity Log (Azure), or Cloud Audit Logs (GCP) must be enabled in ALL regions "
                    "and accounts, with logs retained for a minimum of 365 days. SIEM integration is required for "
                    "all production environments. Alerts must be configured for: root account usage, IAM policy changes, "
                    "S3 bucket ACL changes, security group modifications, and failed login attempts exceeding 5 in 10 minutes. "
                    "Threat detection services (AWS GuardDuty, Azure Defender, GCP Security Command Center) must be "
                    "enabled across all accounts."
                )
            },
            {
                "title": "4.2 Detection Processes (DE.DP)",
                "body": (
                    "Detection rules must be reviewed and tuned quarterly to minimize false positives. All detection "
                    "alerts classified as High or Critical severity must be acknowledged within 15 minutes and triaged "
                    "within 1 hour. The Security Operations Center (SOC) operates 24/7 and is the primary recipient "
                    "of all security alerts. Detection capability effectiveness is measured via monthly red team exercises "
                    "and purple team tabletop simulations."
                )
            }
        ]
    },
    {
        "heading": "5. RESPOND (RS) & RECOVER (RC)",
        "subsections": [
            {
                "title": "5.1 Incident Response (RS.RP)",
                "body": (
                    "The organization maintains a Cloud Incident Response Playbook covering the following incident types: "
                    "credential compromise, data exfiltration, ransomware, misconfiguration exposure, and DDoS. "
                    "All security incidents must be reported to the SOC within 1 hour of detection. Severity 1 incidents "
                    "require executive notification within 2 hours. The incident response lifecycle includes: Preparation, "
                    "Detection, Analysis, Containment, Eradication, Recovery, and Post-Incident Review. A post-incident "
                    "review must be completed within 5 business days for all Severity 1 and 2 incidents."
                )
            },
            {
                "title": "5.2 Recovery Planning (RC.RP)",
                "body": (
                    "Recovery Time Objectives (RTO) and Recovery Point Objectives (RPO) must be defined for all "
                    "production cloud workloads. Tier 1 (Critical): RTO 1hr, RPO 15min. Tier 2 (High): RTO 4hr, RPO 1hr. "
                    "Backups must be tested quarterly using automated restore testing pipelines. Backup data must be "
                    "stored in a separate cloud account or region from the primary workload. Immutable backup storage "
                    "must be used for all Tier 1 systems."
                )
            }
        ]
    }
]

# -- Document 2: AWS Security Best Practices -----------------------------------
aws_sections = [
    {
        "heading": "1. AWS Account Structure & Governance",
        "subsections": [
            {
                "title": "1.1 AWS Organizations & Control Tower",
                "body": (
                    "All AWS accounts must be managed under the organization's AWS Organizations structure via AWS "
                    "Control Tower. No standalone AWS accounts are permitted. AWS accounts must be provisioned via the "
                    "Account Vending Machine (AVM) process managed by the Cloud Platform team. Service Control Policies "
                    "(SCPs) are applied at the Organizational Unit (OU) level and cannot be overridden by individual "
                    "account policies. The following SCPs are applied organization-wide: deny-root-access, "
                    "deny-s3-public-access, require-mfa-for-iam-actions, deny-regions outside approved list."
                )
            },
            {
                "title": "1.2 AWS Root Account Security",
                "body": (
                    "The AWS root account must NEVER be used for day-to-day operations. Root access is restricted to "
                    "initial account setup, AWS Support plan changes, and specific billing tasks. The root account "
                    "email must be a group email (e.g., aws-root@company.com) monitored by the Security team. "
                    "Root account hardware MFA must be enabled within 24 hours of account creation. The root "
                    "account access keys must be deleted. Root account activity triggers an immediate P1 security alert."
                )
            }
        ]
    },
    {
        "heading": "2. Identity and Access Management (IAM)",
        "subsections": [
            {
                "title": "2.1 IAM Users vs. Roles",
                "body": (
                    "IAM Users should be avoided for production workloads. Applications and services must use IAM Roles "
                    "with instance profiles or OIDC-based federation. Human access to AWS must be federated through the "
                    "corporate Identity Provider (IdP) using AWS IAM Identity Center (SSO). IAM Users are permitted only "
                    "for break-glass emergency scenarios and must have time-limited credentials that are rotated "
                    "automatically. All IAM access keys older than 90 days must be automatically disabled."
                )
            },
            {
                "title": "2.2 IAM Policy Standards",
                "body": (
                    "IAM policies must follow least privilege principles. Wildcard (*) actions are prohibited in "
                    "production IAM policies except for explicitly approved read-only services. All IAM policies must "
                    "have a Condition block restricting access by source VPC, source IP, or MFA status where applicable. "
                    "AWS Managed Policies must be reviewed for over-permissiveness before attachment. "
                    "Custom IAM policies must be reviewed by the Cloud Security team before deployment to production. "
                    "IAM Access Analyzer must be enabled in each account to detect external access."
                )
            },
            {
                "title": "2.3 Secrets Management",
                "body": (
                    "All secrets (API keys, database passwords, certificates) must be stored in AWS Secrets Manager "
                    "or AWS Parameter Store (SecureString). Hard-coded credentials in source code, configuration files, "
                    "or environment variables (in plaintext) are strictly prohibited. Automated secret scanning must "
                    "be integrated into all CI/CD pipelines using tools such as TruffleHog or AWS CodeGuru. "
                    "Secret rotation must be enabled, with a maximum rotation interval of 90 days for all Tier 1 secrets."
                )
            }
        ]
    },
    {
        "heading": "3. Network Security",
        "subsections": [
            {
                "title": "3.1 VPC Architecture",
                "body": (
                    "All production workloads must reside in a dedicated VPC with private subnets for compute and data "
                    "tiers. Public subnets are restricted to NAT Gateways, Application Load Balancers, and Bastion Hosts. "
                    "Direct internet access from private subnets is prohibited. VPC Flow Logs must be enabled for all "
                    "VPCs and retained for 90 days minimum. Transit Gateway is the approved mechanism for cross-VPC "
                    "connectivity. VPC peering must be reviewed and approved by the Network Security team."
                )
            },
            {
                "title": "3.2 Security Groups & NACLs",
                "body": (
                    "Security groups must follow a deny-by-default approach. Inbound rules permitting 0.0.0.0/0 "
                    "are prohibited except for ports 80 and 443 on public-facing load balancers. SSH (port 22) and "
                    "RDP (port 3389) must NEVER be open to the internet (0.0.0.0/0). All bastion host access must use "
                    "AWS Systems Manager Session Manager instead of direct SSH/RDP where possible. "
                    "Security group changes in production require change management approval and are audited via "
                    "CloudTrail with real-time alerting."
                )
            }
        ]
    },
    {
        "heading": "4. Data Protection on AWS",
        "subsections": [
            {
                "title": "4.1 S3 Security",
                "body": (
                    "All S3 buckets must have: Public Access Block enabled at account and bucket level, "
                    "Server-Side Encryption enabled (SSE-S3 minimum, SSE-KMS for sensitive data), "
                    "S3 Versioning enabled for buckets containing critical data, "
                    "S3 Access Logging enabled for audit trail, "
                    "Bucket policies that deny s3:PutObject without encryption headers. "
                    "S3 Cross-Region Replication is required for Tier 1 data buckets. "
                    "Lifecycle policies must be configured to transition data to lower-cost tiers and enforce "
                    "retention policies."
                )
            },
            {
                "title": "4.2 RDS & Database Security",
                "body": (
                    "RDS instances must be deployed in private subnets only. Public accessibility must be disabled. "
                    "Encryption at rest must be enabled using AWS KMS. Automated backups must be retained for minimum "
                    "7 days for non-production and 35 days for production. Multi-AZ deployment is required for all "
                    "Tier 1 production databases. RDS IAM authentication must be used instead of static database "
                    "passwords where supported. Performance Insights and Enhanced Monitoring must be enabled. "
                    "Database audit logs must be sent to CloudWatch and retained for 12 months."
                )
            }
        ]
    },
    {
        "heading": "5. Logging, Monitoring & Incident Response",
        "subsections": [
            {
                "title": "5.1 AWS CloudTrail",
                "body": (
                    "AWS CloudTrail must be enabled in ALL regions for ALL accounts, including management events, "
                    "data events for S3 and Lambda, and Insights events. CloudTrail logs must be centralized to a "
                    "dedicated Security logging account with Object Lock enabled (immutable, WORM compliance). "
                    "CloudTrail S3 bucket must have public access blocked, versioning enabled, and MFA delete enabled. "
                    "Log integrity validation must be enabled. CloudTrail logs must be ingested into the SIEM within "
                    "5 minutes of generation."
                )
            },
            {
                "title": "5.2 AWS GuardDuty & Security Hub",
                "body": (
                    "Amazon GuardDuty must be enabled in all regions and accounts. GuardDuty findings of HIGH or "
                    "CRITICAL severity trigger automated remediation workflows (quarantine IAM role, snapshot EBS, "
                    "isolate instance). AWS Security Hub must be enabled with the following standards active: "
                    "AWS Foundational Security Best Practices, CIS AWS Foundations Benchmark v1.4, "
                    "and PCI DSS (for applicable accounts). Security Hub findings must feed into the SIEM and ticketing "
                    "system. A Security Hub score below 80% triggers an executive escalation workflow."
                )
            }
        ]
    }
]

# -- Document 3: SOC 2 Type II Overview ---------------------------------------
soc2_sections = [
    {
        "heading": "1. SOC 2 Program Overview",
        "subsections": [
            {
                "title": "1.1 What is SOC 2?",
                "body": (
                    "SOC 2 (Service Organization Control 2) is an auditing framework developed by the American "
                    "Institute of CPAs (AICPA). It defines criteria for managing customer data based on five "
                    "Trust Services Criteria (TSC): Security, Availability, Processing Integrity, Confidentiality, "
                    "and Privacy. Our organization undergoes an annual SOC 2 Type II audit, which assesses whether "
                    "our controls were operating effectively over a 12-month period. The audit is conducted by an "
                    "independent third-party CPA firm. The SOC 2 Type II report is available to customers and "
                    "prospects under NDA upon request."
                )
            },
            {
                "title": "1.2 Scope of the SOC 2 Audit",
                "body": (
                    "The SOC 2 audit scope covers all cloud infrastructure, software, and processes involved in "
                    "delivering the organization's production SaaS platform. In-scope systems include: production "
                    "AWS accounts (us-east-1, eu-west-1), Kubernetes orchestration layer, CI/CD pipelines, "
                    "application databases, customer data storage systems, and supporting security tooling. "
                    "Out of scope: development and staging environments, internal-only tools, and third-party "
                    "sub-processors who maintain their own SOC 2 compliance."
                )
            }
        ]
    },
    {
        "heading": "2. Security (CC6 - Common Criteria)",
        "subsections": [
            {
                "title": "2.1 Logical and Physical Access Controls (CC6.1 - CC6.3)",
                "body": (
                    "CC6.1: The organization restricts logical access to in-scope systems using Role-Based Access Control "
                    "(RBAC). All access requires unique user identification and MFA. Privileged access is granted via "
                    "just-in-time provisioning with manager approval and automatic expiration after 8 hours. "
                    "CC6.2: Access is provisioned through an approved ITSM workflow. Quarterly access reviews are "
                    "performed by system owners. Terminated employee access is revoked within 4 hours via automated "
                    "HR system integration. CC6.3: All production access is logged and monitored. Anomalous access "
                    "patterns trigger automated alerts to the Security Operations team."
                )
            },
            {
                "title": "2.2 Encryption Standards (CC6.7)",
                "body": (
                    "CC6.7: The organization uses AES-256 for data at rest and TLS 1.2+ for data in transit across "
                    "all in-scope systems. Encryption keys are managed through AWS KMS with HSM-backed key storage. "
                    "Key rotation is automated on an annual schedule. Certificate lifecycle management uses AWS "
                    "Certificate Manager with automatic renewal. All internal service-to-service communication "
                    "uses mutual TLS (mTLS) within the service mesh. Clear-text transmission of sensitive data "
                    "is technically enforced to be impossible through network policy controls."
                )
            }
        ]
    },
    {
        "heading": "3. Availability (A1)",
        "subsections": [
            {
                "title": "3.1 Availability Commitments (A1.1 - A1.3)",
                "body": (
                    "A1.1: The organization commits to 99.9% monthly uptime SLA for production systems. "
                    "Availability metrics are tracked in real-time via a public status page (status.company.com). "
                    "A1.2: Business Continuity and Disaster Recovery (BCDR) plans are maintained for all Tier 1 "
                    "systems with defined RTOs and RPOs. DR tests are conducted semi-annually with documented results. "
                    "A1.3: Environmental protections for cloud data centers are provided by AWS under the Shared "
                    "Responsibility Model. AWS SOC 2 and ISO 27001 reports are reviewed annually as part of "
                    "third-party vendor management."
                )
            }
        ]
    },
    {
        "heading": "4. Confidentiality (C1)",
        "subsections": [
            {
                "title": "4.1 Data Classification (C1.1 - C1.2)",
                "body": (
                    "C1.1: All customer data is classified as Confidential by default. The Data Classification Policy "
                    "defines four tiers: Public, Internal, Confidential, and Restricted. Data handling requirements "
                    "are enforced based on classification. C1.2: Confidential data is protected by technical controls "
                    "including encryption, access controls, and DLP policies. Customer data is logically isolated "
                    "per tenant using separate database schemas and encryption keys. Data is retained per the "
                    "contractual retention schedule and securely deleted (cryptographic erasure) upon termination "
                    "of service within 30 days."
                )
            }
        ]
    },
    {
        "heading": "5. Change Management & Vendor Management",
        "subsections": [
            {
                "title": "5.1 Change Management (CC8.1)",
                "body": (
                    "CC8.1: All production changes must follow the Change Management Policy. Changes are categorized as: "
                    "Standard (pre-approved, low-risk, automated), Normal (requires change advisory board review), "
                    "or Emergency (expedited review, post-change authorization). All changes must be tested in staging "
                    "before production deployment. Infrastructure changes must be implemented via Infrastructure-as-Code "
                    "(Terraform) with pull request review by at least one senior engineer. Hotfixes require dual approval. "
                    "All change records are retained for 3 years for audit purposes."
                )
            },
            {
                "title": "5.2 Vendor Risk Management (CC9.2)",
                "body": (
                    "CC9.2: All sub-processors with access to customer data must be reviewed and approved by the "
                    "Security and Privacy teams before onboarding. Vendors are assessed annually using the "
                    "organization's Third-Party Risk Management (TPRM) questionnaire. Vendors must provide their "
                    "current SOC 2 Type II report, ISO 27001 certificate, or equivalent evidence of security "
                    "controls. Data Processing Agreements (DPAs) must be signed before any data sharing. "
                    "Vendor access is granted using minimum necessary permissions and monitored via CASB tooling."
                )
            }
        ]
    }
]


if __name__ == "__main__":
    print("--- Generating sample policy PDFs...")
    build_pdf("sample_nist_csf.pdf", "NIST Cybersecurity Framework — Organizational Policy", nist_sections)
    build_pdf("sample_aws_security.pdf", "AWS Cloud Security Best Practices Policy", aws_sections)
    build_pdf("sample_soc2_overview.pdf", "SOC 2 Type II Compliance Overview", soc2_sections)
    print("\n[SUCCESS] All sample PDFs created in data/policies/")
    print("Next step: Run 'python ingest.py' to index them.")
