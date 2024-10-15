---
tags:
  - Event Driven Architecture
---

# Event-Driven Architecture

## Concepts


* [Interview questions from Event Driven Architecture](https://newsletter.systemdesigncodex.com/p/3-interview-questions-on-event-driven)
{% if summarized_content == 'true' %}
Three event-driven patterns are discussed in relation to system design interviews: Competing Consumer Pattern, Retry Messages Pattern, and Async Request Response Pattern. These patterns help handle asynchronous messages, retries, and request-response communication using message queues, ensuring efficient processing and error handling across multiple instances.
{% endif %}
{% if pdf == 'true' %}
??? note "Checkout the PDF"
      ![PDF](pdf/3-interview-questions-on-event-driven.pdf){ type=application/pdf style='min-height:100vh;width:100%' }
 {% endif %}

* [testurl](https://medium.com/@mkremer_75412/why-postgres-rds-didnt-work-for-us-and-why-it-won-t-work-for-you-if-you-re-implementing-a-big-6c4fff5a8644)
{% if summarized_content == 'true' %}
A startup's attempt to measure marketing effectiveness via statistical attribution modeling led to scalability issues with AWS RDS managed PostgreSQL due to EBS throughput opacity. They migrated to Aurora but faced similar performance and cost challenges, ultimately opting for a custom EC2 setup that significantly improved speed and reduced costs by $8K/month.
{% endif %}
{% if pdf == 'true' %}
??? note "Checkout the PDF"
      ![PDF](pdf/why-postgres-rds-didnt-work-for-us-and-why-it-won-t-work-for-you-if-you-re-implementing-a-big-6c4fff5a8644.pdf){ type=application/pdf style='min-height:100vh;width:100%' }
 {% endif %}

