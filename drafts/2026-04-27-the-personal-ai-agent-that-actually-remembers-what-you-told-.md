# The personal AI agent that actually remembers what you told it

**Date:** 2026-04-27
**Source:** https://youtube.com/watch?v=Qn2c_U-cWQs

---

You know that moment when you explain something to a tool for the fifteenth time and wonder why you bothered?

Greg Isenberg just released a walkthrough of Hermes Agent with his friend Imran, and it tackles the exact frustration that made me give up on OpenClaw after three days.

The core problem with most AI agents right now is amnesia. You set them up, get them working, then come back tomorrow and start from scratch. Imran described restarting his OpenClaw gateway once an hour on bad days. He was spending more time maintaining the system than actually using it.

Hermes Agent works differently. It has built-in memory that writes to itself every time you complete a task successfully. Over time, it genuinely learns your workflows. It stores everything in a standard SQLite database, which means it can search through past interactions in real time.

Imran shared a detail that made me sit up. If you forget to save an API key to an environment variable but passed it to the agent at some point, Hermes can search through its logs and find it for you. That alone would have saved me hours of frustration last month.

The token visibility issue matters too. With OpenClaw, Imran was spending roughly $130 every five days with no clear understanding of why. After switching to Hermes with Open Router, he got that down to about $10 for the same period. Over 90% reduction.

The trick is building deterministic workflows. Instead of having the AI process the same task repeatedly, you get it to write the code once, then run that code going forward. No tokens burned on repetition.

---

[AD BREAK]

---

For anyone concerned about security, Imran mentioned something clever. You can ask Hermes to audit your own setup. It knows where your keys are stored and your configuration, so you can prompt it to check whether anything sensitive is exposed in plain text or if your firewall has gaps.

The installation is genuinely simple for Mac users. One terminal command handles it. Hermes comes with over 40 built-in tools covering browser control, web search, scheduled tasks, even image generation. If you are on a MacBook, Apple Notes, Reminders, iMessage, and Find My work out of the box without hunting for integrations.

You can also run it inside a Docker container for isolation, or deploy it on Modal as a serverless service if you want it off your machine entirely.

What caught my attention most was this. Imran mentioned he has been using Hermes for over three weeks, which he described as a long time in this space. That says something about how quickly the agent landscape is moving. Three weeks of consistent use without switching is apparently noteworthy.

The full walkthrough from Greg Isenberg covers everything from basic installation to running Hermes on an Android phone via Termux. Worth watching if you want the step-by-step.

Source: [Hermes Agent: The New OpenClaw?](https://youtube.com/watch?v=Qn2c_U-cWQs) by Greg Isenberg

Lewis

---

*Copy into Beehiiv to review and publish.*
