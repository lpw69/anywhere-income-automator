# The skill that separates good AI agents from useless ones

**Date:** 2026-04-15
**Source:** https://youtube.com/watch?v=S_oN3vlzpMw

---

Most people are using AI agents completely wrong.

They download someone else's prompt template, paste it in, and wonder why the output is rubbish. Then they blame the technology.

Ross Haleliuk (who builds AI agents professionally) shared something on Greg Isenberg's podcast that made me rethink how I approach this stuff entirely.

His take: the models are already good. Opus 4.6, GPT 5.4. They don't need you to tell them basic information they can already see in your codebase or context. What they need is something different.

They need to watch you work first.

Here's the mistake Ross sees constantly. Someone identifies a workflow they want to automate. Maybe it's researching potential sponsors, or qualifying leads, or processing invoices. And they immediately jump to writing instructions for the AI.

This almost never works well.

Ross uses his own sponsor research as an example. He forwards emails to an AI agent and asks it to evaluate whether the company is worth partnering with. First attempt? The agent said every single sponsor was legitimate. No rejections. No red flags. Just thumbs up across the board.

The problem wasn't the model. The problem was Ross hadn't shown it what a proper evaluation actually looks like.

So he changed his approach. Instead of writing instructions upfront, he walked through the workflow with the agent step by step. Check their Twitter. Check their TrustPilot. See if they've raised money. If two of these don't exist or look dodgy, automatic rejection.

Once they'd done several successful runs together, then he asked the AI to review what they'd done and create a skill file from it.

The difference is night and day.

This maps directly to how I think about building income systems. Whether you're setting up a matched betting tracker, a client qualification process, or a content research workflow, the same principle applies.

---

[AD BREAK]

---

The technical bit that matters here is understanding how "skills" differ from those agent.md files everyone obsesses over.

An agent.md file gets loaded into context every single conversation. If yours is 1,000 lines, that's roughly 7,000 tokens burned on every single run. Most people don't need this.

Skills work differently. Only the title and description sit in context. The full instructions only get pulled in when the agent recognises it needs them. Ross calls this "progressive disclosure."

It's more efficient. And more importantly, it means your agent only references specific workflows when they're actually relevant.

His 95% rule is useful here. You only need an agent.md file if you have proprietary information or methodology that genuinely must be referenced in every single conversation. Most people don't have that.

Three practical takeaways:

First, stop downloading other people's skills and prompt templates. Your agent needs context of what a successful run looks like for your specific situation. Someone else's template doesn't give it that.

Second, walk through your workflow manually with the AI before trying to automate it. Let it fail. Correct it. Show it what good looks like. Then ask it to create the skill.

Third, keep your persistent context minimal. The models are already trained on vast amounts of information. You don't need to explain that your codebase uses React when it can see the codebase directly.

The underlying principle here is one I keep coming back to. Systems beat willpower, but only when those systems are actually built on observed reality rather than theoretical instructions.

Whether you're building AI workflows or income streams, the same logic applies. Watch what actually works before you try to systematise it.

Speak Friday,
Lewis

---

*Copy into Beehiiv to review and publish.*
