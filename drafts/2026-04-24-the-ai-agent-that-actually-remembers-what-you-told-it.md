# The AI agent that actually remembers what you told it

**Date:** 2026-04-24
**Source:** https://youtube.com/watch?v=Qn2c_U-cWQs

---

You know that feeling when you explain something to a tool for the fifteenth time?

Greg Isenberg just did a deep dive with Imran on Hermes Agent, an open-source alternative to OpenClaw that's gaining serious traction. The standout feature: it actually learns from your previous tasks.

Unlike OpenClaw, which requires constant hand-holding and gateway restarts, Hermes writes to its own memory after every successful task. It searches through logs to find previous solutions. It even recalls API keys you mentioned weeks ago but forgot to save properly.

Imran shared his real numbers: token costs dropped from around $130 every five days to roughly $10 over the same period. That's a 90% reduction while doing the same work.

The trick isn't just switching tools. It's the methodology shift.

Instead of running the agent repeatedly for the same recurring tasks, you have it write the code once. Daily digest? Write the scraper once, run it forever without burning tokens. Weekly reports? Same approach.

This is the "don't repeat yourself" principle from software engineering, applied to AI agents.

The installation is a single terminal command on Mac, Linux, or Windows Subsystem for Linux. It comes with 40+ built-in tools and pre-installed skills for Apple Notes, Reminders, iMessage, and Find My. No hunting through skills hubs required.

For the security-conscious: you can run Hermes inside a Docker container, isolated from your files. Or deploy it as a serverless service on Modal. Imran runs his on bare metal but routinely asks the agent to audit his own security setup, a meta-prompt that checks for exposed keys, plain text secrets, and firewall issues.

The model flexibility impressed me most. Through Open Router, you access Claude, GPT, Qwen, and whatever free models happen to be available that week. Nvidia's Neotron was running free during the recording. Qwen 3.6 Plus costs roughly one-tenth the input token price of Claude Sonnet.

--- [AD BREAK] ---

Imran demonstrated something that caught my attention: he's running Hermes on a Solana Seeker Android phone via Termux.

A personal AI agent in your pocket, connected to Telegram, learning your workflows, available anywhere.

This matters because the gap between expensive AI subscriptions and capable open-source alternatives is closing rapidly. Three weeks of stable daily use, in a space where tools become obsolete in days, suggests Hermes has staying power.

If you've bounced between Claude Projects, OpenClaw, and various agent setups without finding something that sticks, this might be worth the 20 minutes to install and configure.

The full walkthrough is in Greg's video if you want the step-by-step.

Speak soon,

Lewis

---

*Copy into Beehiiv to review and publish.*
