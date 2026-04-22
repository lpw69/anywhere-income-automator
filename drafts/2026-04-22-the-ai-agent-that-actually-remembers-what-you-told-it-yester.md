# The AI agent that actually remembers what you told it yesterday

**Date:** 2026-04-22
**Source:** https://youtube.com/watch?v=Qn2c_U-cWQs

---

I've been watching the personal AI agent space with growing frustration.

OpenClaw promised to be our always-on digital assistant. The reality? Constantly restarting, burning through tokens with zero visibility, and asking me the same questions I answered yesterday.

Then Imran (a technical creator I follow) shared his setup using Hermes Agent, and the difference is stark.

**The three problems it actually solves:**

First, built-in memory. Every completed task gets written to memory automatically. The agent genuinely learns your workflows over time rather than starting fresh each session.

Second, it uses a standard SQLite database. This means it can search through every previous interaction to find what it needs. Forgot to save an API key properly? It'll dig through the logs and retrieve it.

Third, stability. Imran mentioned he hadn't restarted it in over a week. Compare that to hourly restarts with OpenClaw.

**The cost difference is significant**

By switching to Hermes with Open Router (which lets you choose from dozens of models including some free ones), Imran dropped from roughly $130 every five days down to about $10 for the same period.

That's a 90% reduction while maintaining the same output.

The clever bit: once you have a recurring task working, you can have Hermes write the actual code for it. Then you're not spending tokens on that task ever again. Standard software engineering principle (don't repeat yourself) applied to AI agents.

**What comes pre-installed**

Over 40 built-in tools covering browser automation, web search, scheduled jobs, even image generation. On Mac, it arrives with Apple Notes, Reminders, Find My, and iMessage integrations already configured.

No hunting through skills hubs trying to figure out which MCP servers you need.

---

[AD BREAK]

---

**The security question**

Valid concern when you're giving an AI agent access to your system.

Hermes can audit its own security setup. Ask it whether your configuration is secure and it will check for exposed keys, plain text secrets, and firewall issues.

For the properly cautious: it runs inside Docker containers for isolation, or on Modal as a serverless service. You're not forced to run it directly on your machine if that makes you uncomfortable.

**Running it on your phone**

This caught my attention. Imran demonstrated Hermes running on an Android device via Termux. Same installation script, same capabilities, accessible through Telegram.

The practical application: your personal AI agent travels with you, maintaining all the memory and workflows you've built up.

**Installation is one command**

For Mac, Linux, or Windows Subsystem for Linux, it's a single line from the Hermes documentation. Mac users might need Xcode developer tools first (xcode-select --install), but that's the only prerequisite.

The model selection happens through a simple 'hermes model' command where you can see exact pricing per million tokens before committing to anything.

I'm not saying this is the final answer to personal AI agents. Three weeks of stability in this space genuinely counts as a long track record, which tells you everything about how fast things are moving.

But if you've been burned by OpenClaw's instability or token costs, this is worth an afternoon of experimentation.

Source: Greg Isenberg's interview with Imran, "Hermes Agent: The New OpenClaw?" on YouTube.

Lewis

---

*Copy into Beehiiv to review and publish.*
