# Risk Scoring Methodology

## Overview

The Portfolio Health Agent uses a weighted algorithmic model to assess loan account risk on a 0-1 scale, where:
- **0** = No risk (perfect repayment history)
- **1** = Maximum risk (default/severe delinquency)

Risk scores are normalized to three categories:
- **LOW**: Score < 0.4
- **MEDIUM**: Score 0.4-0.7
- **HIGH**: Score ≥ 0.7

## Risk Factors

The model incorporates five key factors with weighted contributions:

### 1. Arrears Days (35% weight)

**Definition**: Number of days the account is past due

**Scoring:**
- 0 days = 0.0 (no risk)
- 180+ days = 1.0 (maximum risk)
- Linear interpolation between points

**Rationale**: The strongest predictor of default. Each day overdue increases default probability exponentially in microfinance contexts.

**Example:**
- 30 days overdue = 0.17 contribution
- 90 days overdue = 0.50 contribution
- 180 days overdue = 1.00 contribution

### 2. Repayment Rate (25% weight)

**Definition**: Historical on-time repayment percentage (0-1 scale)

**Calculation:**
```
Repayment Rate = Total Repaid / Total Expected Repayment
```

**Scoring:**
- 100% on-time = 0.0 (no risk, since we use 1 - rate)
- 50% on-time = 0.5 (moderate risk)
- 0% on-time = 1.0 (maximum risk)

**Rationale**: Demonstrates borrower's commitment to loan obligations. Past behavior predicts future behavior.

### 3. Account Age (15% weight)

**Definition**: Time since loan disbursement in months

**Scoring:**
```
< 6 months   = 0.8 (highest risk - new accounts)
6-12 months  = 0.5 (moderate risk)
> 12 months  = 0.2 (lower risk - established accounts)
```

**Rationale**: New borrowers are riskier due to:
- Unknown repayment behavior
- Seasonal business cycles not yet observed
- Selection bias (new accounts more likely to default)

### 4. Loan Amount Ratio (15% weight)

**Definition**: Outstanding principal / Original loan amount

**Calculation:**
```
Loan Ratio = (Principal Disbursed - Principal Repaid) / Principal Disbursed
```

**Scoring:**
- 0% outstanding (fully repaid) = 0.0 (no risk)
- 50% outstanding = 0.5 (moderate risk)
- 100% outstanding = 1.0 (maximum risk)

**Rationale**: 
- Higher outstanding = longer repayment window = more time to default
- Quick repayment demonstrates confidence
- Failing early indicates fundamental issues

### 5. Missed Payments (10% weight)

**Definition**: Aggregate count of payment defaults/missed dates

**Scoring:**
```
0 missed    = 0.0 (no risk)
1-5 missed  = Proportional (0.0-1.0)
5+ missed   = 1.0 (maximum risk)
```

**Rationale**: Frequency of defaults indicates pattern of non-commitment or financial stress.

## Composite Score Calculation

The final risk score is computed as a weighted sum:

```
Risk Score = (0.35 × Arrears) + 
             (0.25 × Repayment_Gap) + 
             (0.15 × Account_Age) + 
             (0.15 × Loan_Ratio) + 
             (0.10 × Missed_Payments)
```

Where each component is normalized to [0, 1].

**Bounds Check:**
```
Final Score = min(1.0, max(0.0, Raw_Score))
```

## Weight Justification

### Why 35% for Arrears?

Empirical research in microfinance shows:
- Current delinquency is the strongest default predictor
- 90+ day arrears = 80%+ probability of ultimate default
- Once accounts become delinquent, recovery rates drop dramatically

### Why 25% for Repayment Rate?

- Historical behavior explains 25-40% of default variance
- More predictive than demographic factors alone
- Captures both capacity and willingness to pay

### Why 15% for Account Age?

- New accounts have 3-5x default risk vs. established
- But stabilizes after 12 months
- Less important than current performance

### Why 15% for Loan Ratio?

- Proxy for loan burden and remaining exposure
- Newer loans more likely to default
- Works complementarily with account age

### Why 10% for Missed Payments?

- Pattern behavior (vs. isolated arrears event)
- Indicates chronic cash flow stress
- Less predictive than total arrears days

## Threshold Selection

### HIGH Risk (≥ 0.7)

**Accounts requiring immediate intervention:**
- ~15-20% of portfolios typically fall here
- ~70-80% eventual default rate if untreated
- Should trigger escalation to loan officer

**Typical profile:**
- Arrears ≥ 60 days, OR
- Repayment rate ≤ 30%, OR
- Multiple recent missed payments

### MEDIUM Risk (0.4-0.7)

**Accounts requiring monitoring:**
- ~20-30% of portfolios typically fall here
- ~20-40% default rate if untreated
- Should trigger follow-up communication

**Typical profile:**
- Arrears 15-60 days, AND/OR
- Repayment rate 30-80%, AND/OR
- Sporadic missed payments

### LOW Risk (< 0.4)

**Normal portfolio operations:**
- ~50-60% of portfolios typically fall here
- ~2-5% default rate
- Routine monitoring sufficient

**Typical profile:**
- Current or minimal arrears
- 80%+ on-time repayment
- No recent missed payments

## Validation & Calibration

### Testing Against Historical Data

1. **Discrimination Power**: Does the score separate defaulters from non-defaulters?
   - Target: ROC-AUC ≥ 0.75

2. **Calibration**: Does a score of 0.7 actually mean 70% default probability?
   - Compare actual default rates by score bucket

3. **Stability**: Does the score predict forward 3-6 months?
   - Track scores vs. actual outcomes

### Recalibration Schedule

- **Monthly**: Review score distribution and default rates
- **Quarterly**: Adjust weights if performance degrades
- **Annually**: Major review with stakeholder feedback

## Customization

### For Different Loan Types

**Agricultural loans** (seasonal):
- Increase account age weight (20%)
- Adjust arrears thresholds for seasonal harvests

**Microenterprises** (variable income):
- Increase repayment rate weight (30%)
- Longer observation period before high-risk classification

**Mortgages** (low default):
- Lower thresholds overall
- Emphasize collateral value (future enhancement)

### For Different Risk Appetites

**Conservative institutions:**
- Increase threshold to 0.6 for high-risk
- Add approval requirement for MEDIUM-risk actions

**Growth-oriented institutions:**
- Decrease threshold to 0.8 for high-risk
- Allow more autonomous escalations

## Future Enhancements

1. **Machine Learning**: Learn weights from historical data
2. **Behavioral Factors**: Include borrower communication patterns
3. **Collateral Adjustment**: Factor in collateral value/type
4. **External Data**: Incorporate credit bureau scores
5. **Dynamic Thresholds**: Adjust by portfolio composition
6. **Ensemble Models**: Combine algorithmic + ML predictions

## Limitations

1. **Data Quality**: Depends on accurate Mifos X data
2. **Bias**: May perpetuate historical lending biases
3. **Context**: Doesn't account for external shocks (economic, COVID)
4. **Timing**: Backward-looking (uses past repayment)
5. **Simplicity**: Doesn't capture complex relationships

## References

- Schreiner, M. (2004). "Credit Scoring for Microfinance" - Standard methodology
- Fitch, R. (2003). "Small Business Lending Risk" - Weighting recommendations
- Microfinance Risk Management Institute standards

## Questions?

For score recalibration or methodology questions:
1. Review recent decision logs
2. Compare predicted vs. actual outcomes
3. Consult with loan officers about field experience
4. Contact Mifos X community for benchmarks
