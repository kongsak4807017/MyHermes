---
name: aris-smart-hospital
description: "ARIS adapted for Smart Hospital projects: clinical workflow analysis, compliance checking (HIPAA, Thai FDA), IoT integration, and patient monitoring system design."
category: research
---

# ARIS for Smart Hospital Projects

> **ARIS Adaptation**: Research methodology applied to healthcare IT systems
> **Compliance**: HIPAA, Thai FDA, ISO 27001, HIMSS

## Workflow Adaptation

### W1: Clinical Discovery
- `research-lit` → search for clinical papers on target condition
- `idea-creator` → generate system architecture ideas
- `novelty-check` → check against existing hospital systems
- `research-review` → clinical expert review simulation

### W1.5: Prototype Bridge
- `experiment-bridge` → build PoC with synthetic patient data
- `run-experiment` → test with de-identified datasets
- `monitor-experiment` → track clinical metrics (sensitivity, specificity)

### W2: Compliance Review Loop
- `auto-review-loop` → iterate on system design
- `paper-claim-audit` → verify clinical claims
- `citation-audit` → verify medical literature citations

### W3: System Documentation
- `paper-plan` → system design document outline
- `paper-write` → technical specification
- `paper-compile` → PDF for stakeholder review

### W4: Regulatory Rebuttal
- `rebuttal` → respond to regulatory feedback

### W5: Multi-Site Deployment
- `resubmit-pipeline` → adapt for different hospital networks

## Smart Hospital Specific Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `clinical_domain` | — | Cardiology, Oncology, Emergency, etc. |
| `data_source` | — | EHR, IoT sensors, wearables |
| `compliance_framework` | `HIPAA+ThaiFDA` | Regulatory requirements |
| `integration_target` | — | Existing HIS/LIS/RIS system |
| `patient_volume` | — | Expected daily patient load |

## Example

```
/project-pipeline "Smart Hospital ICU monitoring with AI early warning"
  — type: smart-hospital
  — clinical_domain: critical-care
  — compliance_framework: HIPAA,ThaiFDA
  — data_source: EHR,bedside_monitors
  — patient_volume: 500/day
```

## Outputs
- `SYSTEM_DESIGN.md` — architecture specification
- `COMPLIANCE_CHECKLIST.md` — regulatory requirements
- `CLINICAL_VALIDATION.md` — evidence summary
- `DEPLOYMENT_PLAN.md` — rollout strategy
