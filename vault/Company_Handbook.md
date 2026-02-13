# Company Handbook

## Brand Voice

- **Tone:** Professional yet approachable
- **Language:** Clear, concise, jargon-free
- **Style:** Active voice preferred
- **Sign-off:** "Best regards" for emails

## Standard Operating Procedures

### Email Handling
1. All incoming emails are triaged automatically
2. Urgent/critical emails are flagged for immediate attention
3. Draft replies are generated and queued for approval
4. No email is sent without human approval

### Social Media
1. Content is generated based on topics and brand guidelines
2. All posts require human approval before publishing
3. Engagement metrics are tracked weekly

### Financial Operations
1. Transactions are automatically categorized
2. Anomalies trigger immediate alerts
3. All payments and invoices require approval
4. Monthly reconciliation reports are generated

### Calendar Management
1. Meeting requests are extracted from emails
2. Availability is checked before proposing times
3. All event creation requires approval

## Emergency Procedures

To halt all operations immediately:
1. Create a file called `EMERGENCY_STOP.md` in the vault root
2. The orchestrator will stop at the next iteration
3. All pending actions will be preserved for review

## Approval Process

1. Items needing approval appear in `Needs_Approval/`
2. Review the item's action plan and parameters
3. **Approve**: Move the file to `Approved/`
4. **Reject**: Move the file to `Rejected/`
5. The orchestrator will process approved items on the next cycle
