# User Guide - Renewable Energy DD Management Tool

## Table of Contents
1. [Getting Started](#getting-started)
2. [Creating a DD Project](#creating-a-dd-project)
3. [Uploading Documents](#uploading-documents)
4. [Managing the DD Checklist](#managing-the-dd-checklist)
5. [Using the Q&A System](#using-the-qa-system)
6. [Reviewing Extracted Information](#reviewing-extracted-information)
7. [Tracking Progress](#tracking-progress)
8. [Generating Reports](#generating-reports)
9. [Collaboration Features](#collaboration-features)
10. [Best Practices](#best-practices)

## Getting Started

### First-Time Login

1. Navigate to the application URL
2. Click **"Sign in with Google"**
3. Select your Google account
4. Grant the necessary permissions:
   - Access to Google Drive
   - Basic profile information
5. You'll be redirected to your dashboard

### Understanding User Roles

- **Admin**: Full access including user management and system settings
- **Reviewer**: Can view, upload, annotate, and export documents
- **Read-Only**: Can view documents and reports but cannot make changes

## Creating a DD Project

### Step 1: Create New Project

1. Click **"New Project"** on the dashboard
2. Fill in project details:
   - **Project Name**: e.g., "Solar Farm Alpha - 50MW"
   - **Technology Type**: Solar, Wind, Hydro, or Battery Storage
   - **Capacity (MW)**: Project capacity in megawatts
   - **Location**: Project location
   - **Expected COD**: Commercial operation date
   - **Description**: Brief project description

3. Click **"Create Project"**

### Step 2: Automatic Folder Structure

The system automatically creates a Google Drive folder structure:
```
DD-[Project Name]/
├── Legal/
│   ├── Contracts/
│   ├── Permits/
│   └── Compliance/
├── Technical/
│   ├── Equipment/
│   ├── Production Data/
│   └── Interconnection/
├── Financial/
│   ├── Models/
│   ├── Audits/
│   └── Tax/
├── Environmental/
│   ├── Assessments/
│   ├── Permits/
│   └── Reports/
└── Commercial/
    ├── PPAs/
    ├── Offtake/
    └── Market Analysis/
```

### Step 3: Share with Team

1. Click **"Share Project"**
2. Enter team member emails
3. Assign roles (Admin, Reviewer, Read-Only)
4. Click **"Send Invitations"**

## Uploading Documents

### Method 1: Direct Upload

1. Navigate to the **"Documents"** tab
2. Click **"Upload Documents"** or drag-and-drop files
3. Select appropriate category (Legal, Technical, Financial, etc.)
4. Add optional description
5. Click **"Upload"**

### Method 2: Google Drive Sync

1. Go to **"Settings"** → **"Drive Integration"**
2. Click **"Connect Google Drive"**
3. Select the project folder
4. Enable **"Auto-sync"** for automatic document detection

### Supported File Types

- **Documents**: PDF, DOCX, DOC, TXT
- **Spreadsheets**: XLSX, XLS, CSV
- **Images**: PNG, JPG (for scanned documents)

### Document Processing

After upload, the system automatically:
1. **Classifies** the document type (PPA, Interconnection Agreement, etc.)
2. **Extracts** key terms and data
3. **Indexes** content for Q&A search
4. **Identifies** potential red flags

Processing typically takes 30 seconds to 2 minutes depending on document size.

## Managing the DD Checklist

### Viewing the Checklist

1. Navigate to **"DD Checklist"** tab
2. View items organized by category:
   - Legal (20 items)
   - Technical (25 items)
   - Financial (15 items)
   - Environmental (15 items)
   - Commercial (10 items)

### Updating Item Status

1. Click on a checklist item
2. Update status:
   - **Not Started**: No action taken
   - **Pending**: Awaiting seller
   - **Received**: Document received
   - **Under Review**: Being reviewed
   - **Approved**: Complete and approved
   - **Rejected**: Issues identified
   - **Not Applicable**: Item not relevant

3. Link related documents
4. Add reviewer notes
5. Click **"Save"**

### Tracking Responsible Parties

Each item shows:
- **Seller Actions**: Items awaiting seller's response (highlighted in orange)
- **Buyer Actions**: Items requiring buyer's review (highlighted in blue)
- **Third Party**: Items requiring external input (highlighted in purple)

### Priority Levels

- **Critical**: Must be completed before closing
- **High**: Important for transaction
- **Medium**: Standard DD item
- **Low**: Nice to have

## Using the Q&A System

### Basic Questions

1. Navigate to **"Q&A"** tab
2. Type your question in natural language:
   - "What is the PPA price?"
   - "When does the land lease expire?"
   - "What is the interconnection queue position?"

3. Click **"Ask"** or press Enter

### Advanced Questions

**Compare Documents:**
```
Compare warranty terms across all equipment contracts
```

**Check Status:**
```
Are all environmental permits in place?
```

**Identify Risks:**
```
What are the key commercial risks in this transaction?
```

**Financial Analysis:**
```
What is the expected project IRR based on the financial model?
```

### Understanding Responses

Each response includes:
- **Answer**: Detailed response based on documents
- **Sources**: List of documents used (with relevance scores)
- **Confidence Score**: System's confidence in the answer
  - Green (≥80%): High confidence
  - Yellow (60-79%): Medium confidence
  - Red (<60%): Low confidence - verify manually

**Low Confidence Warning**: When confidence is low, always cross-reference with original documents.

### Example Q&A Interactions

**Q: What is the PPA price and how does it escalate?**

A: According to the Power Purchase Agreement (dated January 15, 2024), the energy price is $45.50 per MWh with an annual escalation rate of 2.5% beginning in Year 3. This pricing structure is competitive for utility-scale solar projects in California.

Key terms:
- Base price: $45.50/MWh
- Escalation: 2.5% annually starting Year 3
- No escalation in Years 1-2

*Sources: PPA_Agreement.pdf (Relevance: 92%)*
*Confidence: 89%*

## Reviewing Extracted Information

### PPA Terms

Navigate to **"Documents"** → Select PPA → **"Extracted Terms"**

View automatically extracted information:
- **Parties**: Seller and buyer names
- **Project Details**: Capacity, location, technology
- **Dates**: Effective date, COD, term duration
- **Pricing**: Energy price, escalation, capacity payments
- **Delivery**: Delivery point, obligations
- **RECs**: Whether RECs transfer to buyer
- **Performance**: Guarantees and liquidated damages

### Red Flags

System automatically identifies:
- Unfavorable pricing terms
- Short contract duration
- Excessive liquidated damages
- Unclear delivery obligations
- Missing critical terms

Review and address each red flag before closing.

### Validation

Always validate extracted information:
1. Click **"View Source"** to see original text
2. Verify accuracy
3. Mark as **"Verified"** or **"Needs Correction"**
4. Add notes if corrections needed

## Tracking Progress

### Dashboard Overview

The main dashboard shows:

**Overall Completion**
- Progress bar showing % complete
- Color-coded status (Red <50%, Yellow 50-69%, Blue 70-89%, Green ≥90%)

**Category Breakdown**
- Progress by category (Legal, Technical, Financial, etc.)
- Number of items completed vs. total

**Recent Activity**
- Latest document uploads
- Checklist updates
- Issues identified

**Critical Alerts**
- Missing critical documents
- Approaching deadlines
- High-priority issues

### Completion Metrics

Track key metrics:
- **Documents Reviewed**: 38/45
- **Checklist Completion**: 67.5%
- **Critical Issues**: 2
- **High Issues**: 5
- **Days to Closing**: 45

## Generating Reports

### Executive Summary

1. Navigate to **"Reports"** tab
2. Click **"Generate Executive Summary"**
3. Review generated summary:
   - Project overview
   - DD status
   - Key findings
   - Risks and red flags
   - Deal breakers (if any)
   - Recommended next steps

4. Click **"Export"** for PDF or Word format

### Detailed DD Report

1. Click **"Generate Full DD Report"**
2. Select sections to include:
   - ☑ Executive Summary
   - ☑ Checklist with Status
   - ☑ Document Inventory
   - ☑ Findings and Issues
   - ☑ Extracted Terms
   - ☑ Q&A History

3. Choose format (PDF or Excel)
4. Click **"Generate Report"**

### Custom Reports

Create custom reports:
1. Click **"Custom Report"**
2. Select:
   - Date range
   - Categories to include
   - Specific documents
   - Issue severity levels
3. Add custom notes
4. Generate and export

## Collaboration Features

### Comments and Annotations

1. Open any document
2. Click **"Annotate"**
3. Highlight text
4. Add comment
5. @mention team members
6. Click **"Post"**

Team members receive notifications of:
- @mentions
- Comments on their uploads
- Status changes on items they're tracking

### Activity Feed

View all project activity:
- Document uploads
- Status changes
- Comments
- Issues created/resolved
- Report generation

Filter by:
- Team member
- Category
- Date range
- Activity type

### Sharing and Permissions

**Share Specific Documents:**
1. Select document
2. Click **"Share"**
3. Enter email
4. Set permissions (View or Edit)
5. Add expiration date (optional)
6. Click **"Send"**

**Project-Level Sharing:**
Managed by admins in **"Settings"** → **"Team Members"**

## Best Practices

### Document Organization

1. **Use consistent naming**: `[DocType]_[Party]_[Date].pdf`
   - Example: `PPA_UtilityCorp_2024-01-15.pdf`

2. **Upload complete documents**: Don't split multi-part agreements

3. **Include amendments**: Upload all amendments with original agreements

4. **Version control**: When uploading updated versions, note changes

### Checklist Management

1. **Daily Updates**: Review and update checklist daily
2. **Link Documents**: Always link relevant documents to checklist items
3. **Add Context**: Include notes explaining status
4. **Flag Issues**: Immediately flag critical issues

### Q&A System

1. **Be Specific**: Ask focused questions for better answers
2. **Verify Low Confidence**: Always verify responses with confidence <70%
3. **Use Follow-ups**: Ask follow-up questions for clarification
4. **Review Sources**: Check source documents cited in responses

### Security

1. **Session Timeout**: System logs out after 15 minutes of inactivity
2. **Sensitive Data**: Be cautious with personally identifiable information
3. **Access Control**: Regularly review team member permissions
4. **Audit Trail**: All actions are logged for compliance

### Workflow Recommendations

**Week 1: Setup**
- Create project
- Upload initial document package
- Review and customize checklist
- Invite team members

**Week 2-3: Document Review**
- Complete document uploads
- Review extracted terms
- Update checklist status
- Address initial red flags

**Week 4: Deep Dive**
- Use Q&A for detailed analysis
- Compare terms across documents
- Generate preliminary reports
- Schedule site visit

**Week 5-6: Final Review**
- Complete remaining checklist items
- Resolve all critical issues
- Generate executive summary
- Prepare for closing

## Troubleshooting

### Document Not Processing

**Issue**: Document stuck in "Processing" status

**Solutions**:
1. Check file size (must be <100MB)
2. Verify file is not corrupted
3. Ensure file type is supported
4. Try re-uploading
5. Contact support if issue persists

### Q&A Not Finding Information

**Issue**: Q&A says "No information found"

**Causes**:
1. Documents not yet indexed (wait 2-3 minutes after upload)
2. Information not in uploaded documents
3. Question too vague

**Solutions**:
1. Verify document was uploaded and processed
2. Try rephrasing question
3. Specify document type to search

### Slow Performance

**Solutions**:
1. Clear browser cache
2. Close unused tabs
3. Check internet connection
4. Use Chrome or Firefox (recommended)
5. Contact support if consistently slow

## Getting Help

### In-App Help
- Click **"?"** icon in top right
- Access contextual help for each page
- View video tutorials

### Support Channels
- **Email**: support@your-domain.com
- **Live Chat**: Available 9 AM - 5 PM EST
- **Knowledge Base**: https://help.your-domain.com

### Training
- New user onboarding: Schedule at onboarding@your-domain.com
- Advanced training: Monthly webinars
- Custom training: Available for enterprise customers

## Keyboard Shortcuts

- `Ctrl/Cmd + K`: Quick search
- `Ctrl/Cmd + U`: Upload document
- `Ctrl/Cmd + N`: New project
- `Ctrl/Cmd + /`: Open Q&A
- `Ctrl/Cmd + E`: Export report
- `Esc`: Close modal

## Mobile App

iOS and Android apps available:
- View documents
- Update checklist
- Ask questions
- Receive notifications
- Review reports

Download:
- App Store: https://apps.apple.com/renewable-dd-tool
- Google Play: https://play.google.com/renewable-dd-tool

---

**Version**: 1.0.0
**Last Updated**: January 2024
**Feedback**: Send suggestions to product@your-domain.com
