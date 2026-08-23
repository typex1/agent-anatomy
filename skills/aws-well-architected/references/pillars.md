# The six Well-Architected pillars — review questions

## Operational Excellence
- How are changes deployed and rolled back?
- Are failures observable (logs, metrics, traces, alarms)?

## Security
- Least-privilege IAM? Any wildcard actions or resources?
- Data encrypted in transit and at rest? Secrets in a manager, not code?

## Reliability
- What happens when a single AZ, instance, or dependency fails?
- Are retries bounded with backoff? Is there a DLQ for async work?

## Performance Efficiency
- Is the compute/storage choice matched to the access pattern?
- Any synchronous chains that should be async?

## Cost Optimization
- What is the idle cost? Anything running 24/7 that has bursty usage?
- Right-sized instances? Savings Plans / Spot where tolerable?

## Sustainability
- Can workloads run in fewer, better-utilized instances?
- Is data lifecycle policy deleting what nobody reads?
