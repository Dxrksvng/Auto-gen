# Assignment 3 — Governed document platform

The official confidential assignment brief at `../assignment-brief/Forward Deployed AI-Eng Assignment 2026.pdf` is the source of truth. Do not publish it.

Assignment 3 evolves the successful Assignment 2 letter workflow into a shared platform for teams that have different templates, input data and business rules. The objective is a controlled reusable document-generation system, not a universal low-code product.

## Design rule

**Configurable at the edge; governed at the core.**

Keep the shared engine separate from versioned document-specific configuration. A Document Definition contains an input schema, mappings, bounded validation and business rules, an approved template, approval/output policy and versions.

“Free-Style” means supporting several approved document designs and input shapes. It never permits arbitrary Python, JavaScript, SQL, shell commands, external HTTP calls or unconstrained AI-generated customer wording.

## Evidence discipline

Separate assignment facts, observed AS2 facts, proposed design, production extensions and open questions. Do not invent Sunday infrastructure, roles, volumes, SLAs, retention requirements or business rules. Preserve the AS2 boundary: generated documents are for controlled review and release; customer delivery requires an agreed workflow.

## Scope

This assignment root is the working project. Its required answer must explicitly cover feasibility, architecture/operation, balanced trade-offs and a practical guide for Office/Google Workspace/email users. A full implementation is not required.
