# ISO 9001:2015 - Clause 10.2: Nonconformity and Corrective Action

## Purpose
To react to nonconformities, take action to control and correct them, deal with consequences, evaluate the need for action to eliminate root causes, implement corrective actions, and review their effectiveness.

## 10.2.1 Nonconformity Response

### Types of Nonconformities

**Product/Service Nonconformities:**
- Does not meet specifications
- Customer requirements not fulfilled
- Design or development errors
- Manufacturing defects
- Service delivery failures

**Process Nonconformities:**
- Process not followed as documented
- Critical parameters out of control
- Equipment malfunction
- Resource inadequacy
- Training deficiencies

**System Nonconformities:**
- QMS requirements not met
- ISO 9001 requirements not addressed
- Procedure not effective
- Documentation missing or incorrect
- Audit findings

### Immediate Response Actions

**When Nonconformity Occurs:**

**1. React to the Nonconformity**
- Stop production/service if necessary
- Contain the nonconformity immediately
- Segregate nonconforming product/output
- Prevent unintended use or delivery
- Alert relevant personnel
- Document the occurrence

**2. Take Action to Control and Correct**

**Containment:**
- Isolate affected product/service
- Tag or mark clearly as nonconforming
- Secure in designated hold area
- Prevent mixing with conforming items
- Implement interim controls

**Correction:**
- Identify immediate fix needed
- Repair, rework, or adjust
- Re-inspect after correction
- Verify acceptability
- Obtain approval for release

**3. Deal with the Consequences**

**Customer Impact:**
- Assess if customer already received nonconforming product
- Notify customer if required
- Determine disposition (return, rework at customer site, concession)
- Expedite replacement if needed
- Compensate for inconvenience if appropriate

**Internal Impact:**
- Assess impact on schedule
- Reallocate resources as needed
- Update production/service plans
- Communicate delays

**Regulatory/Legal Impact:**
- Determine reporting requirements
- Notify regulatory bodies if required
- Document for compliance records
- Implement recall if necessary

## Nonconformity Documentation

### Nonconformance Report (NCR)

**NCR Number:** {{ncr_number}} (Unique identifier)

**Information Captured:**

**Identification:**
- Date and time of discovery
- Discovered by (name and department)
- Location of occurrence
- Product/service identification
- Quantity affected

**Description:**
- Nature of nonconformity
- Requirements not met (specification, standard, customer requirement)
- Evidence (photos, measurements, test results)
- Severity/criticality assessment

**Containment Actions:**
- Immediate actions taken
- Quantity contained/segregated
- Interim controls implemented
- Personnel notified

**Impact Assessment:**
- Customer impact (yes/no, details)
- Production impact
- Cost implications
- Regulatory implications

## 10.2.2 Root Cause Analysis and Corrective Action

### Evaluation of Need for Action

**Criteria to Eliminate Root Cause:**
- Severity of nonconformity (critical, major, minor)
- Frequency or recurrence potential
- Customer impact significance
- Cost implications
- Regulatory considerations
- Organizational risk

**Decision:**
- Proceed with root cause analysis and corrective action
- Monitor for recurrence before deeper investigation
- Accept as isolated incident with no further action

### Root Cause Analysis Methods

**5 Whys Technique:**
```
Nonconformity: Product failed leak test
Why 1: O-ring seal leaked
Why 2: O-ring not seated properly
Why 3: Assembly fixture worn
Why 4: Fixture maintenance overdue
Why 5: Maintenance schedule not followed
Root Cause: Preventive maintenance system inadequate
```

**Fishbone (Ishikawa) Diagram:**
Categories analyzed:
- **Man**: Operator training, awareness, fatigue
- **Machine**: Equipment condition, calibration, capability
- **Material**: Supplier quality, incoming inspection, storage
- **Method**: Procedure adequacy, work instructions, complexity
- **Measurement**: Test accuracy, calibration, interpretation
- **Environment**: Temperature, humidity, lighting, cleanliness

**Fault Tree Analysis:**
- Systematic deductive analysis
- Works backward from nonconformity
- Identifies contributing factors
- Quantifies probabilities

**8D Problem Solving:**
- D0: Prepare and plan
- D1: Establish the team
- D2: Describe the problem
- D3: Develop interim containment
- D4: Determine root cause
- D5: Choose permanent corrective actions
- D6: Implement and validate corrective actions
- D7: Prevent recurrence
- D8: Recognize team and effort

### Determining Corrective Actions

**Corrective Action vs. Correction:**
- **Correction**: Fixes the specific nonconformity (immediate)
- **Corrective Action**: Eliminates the root cause (systemic)

**Potential Corrective Actions:**

**Process Changes:**
- Revise procedures or work instructions
- Add process controls or checks
- Implement automation or poka-yoke
- Change process parameters
- Add in-process inspections

**Training and Competence:**
- Provide additional training
- Increase supervision
- Verify understanding
- Refresher training programs
- Competency assessment

**Design Changes:**
- Redesign product/service
- Improve specifications
- Enhance robustness
- Simplify design
- Design for manufacturability

**Resource Changes:**
- Upgrade equipment
- Improve tooling or fixtures
- Enhance calibration program
- Add staffing resources
- Improve facilities or environment

**Supplier Management:**
- Improve supplier qualification
- Enhance incoming inspection
- Develop supplier capability
- Change suppliers
- Improve supplier communication

**System Improvements:**
- Update QMS procedures
- Improve documentation
- Enhance communication
- Strengthen management review
- Improve internal audits

### Corrective Action Planning

**Action Plan Development:**

**For Each Corrective Action:**
- Specific action to be taken (What?)
- Responsible person (Who?)
- Target completion date (When?)
- Resources required (How much?)
- Success criteria (How measured?)
- Risk of implementation

**Example Corrective Action Plan:**

| Action | Responsible | Due Date | Resources | Success Criteria |
|--------|-------------|----------|-----------|------------------|
| Revise assembly procedure to emphasize fixture inspection | Quality Engineer | {{date_1_month}} | 8 hours | Procedure updated and approved |
| Train all assemblers on revised procedure | Production Supervisor | {{date_6_weeks}} | 4 hours + trainer | 100% attendance, competency verified |
| Implement daily fixture inspection checklist | Production Lead | {{date_1_month}} | Create checklist | Checklist in use, 100% completion |
| Add fixture inspection to preventive maintenance schedule | Maintenance Manager | {{date_1_month}} | Update system | Monthly inspections scheduled |
| Audit effectiveness of actions | Quality Manager | {{date_3_months}} | 4 hours | Zero recurrence of this issue |

## 10.2.3 Implementation of Corrective Actions

### Execution

**Implementation Steps:**
1. Obtain necessary approvals (management, customer, regulatory)
2. Communicate changes to affected personnel
3. Provide training on new/changed requirements
4. Update documentation (procedures, work instructions, forms)
5. Implement changes in a controlled manner
6. Monitor initial implementation closely
7. Document evidence of implementation

**Change Control Integration:**
- Corrective actions triggering design changes follow change control process
- Impact assessment conducted
- Validation performed as necessary
- Customer notification if contractually required

**Communication:**
- Inform all stakeholders of changes
- Explain reasons for corrective actions
- Gain buy-in and commitment
- Provide forums for questions and feedback

## 10.2.4 Effectiveness Review

### Verification of Corrective Action Effectiveness

**Timing:**
- Initial check: Shortly after implementation ({% if company_size == "Small" %}2-4 weeks{% else %}1-2 weeks{% endif %})
- Follow-up verification: After sufficient time/volume ({% if company_size == "Small" %}3 months{% else %}1-3 months{% endif %})
- Final effectiveness review: Long-term monitoring (6-12 months)

**Methods to Verify Effectiveness:**

**Direct Monitoring:**
- Monitor for recurrence of original nonconformity
- Track related metrics and KPIs
- Review inspection and test results
- Analyze process data
- Observe operations

**Indirect Indicators:**
- Customer complaint trends
- Internal audit findings
- Management review discussions
- Employee feedback
- Cost of quality metrics

**Effectiveness Criteria:**
- Zero recurrence of same nonconformity
- Improved process capability or performance
- Reduced defect rates
- Increased customer satisfaction
- Reduced costs

**Outcomes:**

**Effective:**
- Corrective action achieved intended result
- Root cause eliminated
- Nonconformity has not recurred
- Performance improved
- Close the NCR

**Not Effective:**
- Nonconformity recurred
- Root cause not fully addressed
- Performance not improved
- Further analysis required
- Revise corrective action and re-implement

## 10.2.5 Update Risks and Opportunities

### Integration with Risk Management

**Review and Update:**
- Nonconformities may reveal new risks not previously identified
- Effectiveness of risk mitigation actions evaluated
- Opportunities for improvement identified
- Risk register updated with lessons learned

**Process:**
- Review nonconformity context
- Assess if related to identified risk
- Determine if new risk identified
- Update risk assessment accordingly
- Communicate changes to planning process

## 10.2.6 Changes to QMS

### QMS Updates Required

**When Corrective Actions Necessitate QMS Changes:**
- Procedures or work instructions revised
- Forms or records updated
- Training materials modified
- Organizational responsibilities changed
- Resources reallocated
- Processes redesigned

**Change Implementation:**
- Changes managed through document control system
- Affected personnel notified and trained
- Changes verified effective
- QMS documentation maintained current
- Management informed of significant changes

## Corrective Action Management

### Corrective Action Register

**Information Tracked:**
- NCR number and date
- Nonconformity description
- Root cause identified
- Corrective actions planned
- Responsible persons
- Due dates and status
- Effectiveness verification results
- Closure date

### Reporting and Metrics

**Monthly Corrective Action Report:**
- Open corrective actions (by age)
- Overdue actions highlighted
- New corrective actions opened
- Corrective actions closed
- Effectiveness verification pending
- Repeat issues identified

**Analysis:**
- Trends in nonconformity types
- Root cause distribution (Pareto)
- Effectiveness rates
- Time to resolution
- Cost of nonconformities
- Sources of nonconformities (internal vs. external)

### Management Review Input

Corrective action data provided to management review:
- Summary of significant nonconformities
- Corrective action effectiveness
- Trends and recurring issues
- Systemic QMS weaknesses identified
- Improvement opportunities
- Resource needs

## Responsibilities

**Nonconformity Originator:**
- Identify and document nonconformity
- Initiate NCR
- Implement immediate containment

**Process Owner:**
- Lead root cause analysis
- Develop corrective action plan
- Implement corrective actions
- Monitor effectiveness

**Quality Manager:**
- Review all NCRs and corrective actions
- Provide technical assistance
- Verify root cause analysis adequacy
- Approve corrective action plans
- Verify effectiveness
- Report to management
- Identify systemic issues

**Top Management:**
- Review significant nonconformities
- Approve major corrective actions
- Provide resources
- Hold process owners accountable
- Drive continuous improvement culture

## Training and Awareness

**Personnel Trained On:**
- How to identify nonconformities
- NCR process and documentation
- Root cause analysis techniques
- Corrective action development
- Problem-solving methodologies
- Importance of preventing recurrence

---
**Document Control**
- Version: 1.0
- Last Updated: {{generation_date}}
- Next Review: {{next_review_date}}
- Owner: Quality Manager
- Approved by: Top Management
