#!/bin/bash

# Run this script to create the 5 suggested good first issues

gh issue create \
  --title "Good first issue: improve README quickstart" \
  --body "The quick start in the README can be further improved for clarity. Help new users get up and running faster by verifying the steps and proposing improvements." \
  --label "good first issue"

gh issue create \
  --title "Good first issue: add screenshot/GIF demo" \
  --body "A picture is worth a thousand words. We need an animated GIF or a compelling screenshot showing the system-review-graph in action in the README." \
  --label "good first issue"

gh issue create \
  --title "Example request: generate SRG for Django" \
  --body "Django is a widely used Python framework. It would be great to have an example System Review Graph generated for Django to showcase how it handles large MVC-like frameworks." \
  --label "enhancement"

gh issue create \
  --title "Example request: generate SRG for Kubernetes" \
  --body "Kubernetes is a massive Go codebase. Running the system-review-graph in atlas mode on Kubernetes would be a great stress test and a valuable example for the community." \
  --label "enhancement"

gh issue create \
  --title "Docs: compare SRG vs call graph vs dependency graph" \
  --body "Add a documentation page or section that clearly compares System Review Graph against traditional call graphs and dependency graphs, highlighting the different use cases." \
  --label "documentation"

echo "Issues created successfully!"