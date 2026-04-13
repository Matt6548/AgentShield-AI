# Product Shell User Guide

## What You See First

Open the local UI and look at these sections in order:

1. Reference Product Flow
2. Product Shell
3. Run History
4. Approval And Audit

## How To Use It

### 1. Start With The Real Workflow

Run a reference flow or one of the integration examples.

What this means in practice:

- a user or app asks for a status check
- SafeCore evaluates the request
- the connector path is either allowed or blocked
- audit evidence is written locally

### 2. Read The Product Shell Summary

The overview shows:

- total runs
- how many were ALLOW
- how many needed approval
- how many were DENY
- how many stayed blocked
- whether any audit integrity issue has appeared

## How To Read Run History

Run history is the fastest way to answer:

- what just happened
- why it was allowed or blocked
- whether approval is involved
- what the next user-facing step is

Use the decision filter if you want to focus on one class of outcomes.

## How To Read The Approval Queue

The approval queue shows flows that are still waiting on approval-oriented review.

What to look for:

- why the request is waiting
- what the operator should check
- what the next step is

Important:

- pending does not mean approved
- escalation does not authorize execution
- the shell shows visibility, not a full workflow engine

## How To Read The Audit Viewer

The audit viewer shows the recent local evidence trail.

You can see:

- timestamp
- run id
- action
- decision context
- audit integrity state
- local audit file path

## Plain-Language Statuses

### ALLOW

The request stayed inside the current safe boundary.

### NEEDS_APPROVAL

The request may be valid later, but it must stay blocked until explicit approval exists.

### DENY

The request crossed a dangerous boundary and must not proceed.

## Honest Limits

The shell is useful today, but it is still intentionally narrow.

It is not a production-ready platform.

It is:

- local
- dry-run-first
- RC/MVP
- a validated core with a usable shell

It is not:

- a cloud control plane
- a full approval portal
- an enterprise audit database
