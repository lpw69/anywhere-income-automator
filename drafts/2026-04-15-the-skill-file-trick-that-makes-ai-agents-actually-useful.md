# The skill file trick that makes AI agents actually useful

**Date:** 2026-04-15
**Source:** https://youtube.com/watch?v=S_oN3vlzpMw

---

Most people are using AI agents wrong.

I spent an hour watching Ross from Greg Isenberg's podcast break down exactly how Claude Code and similar AI agents process information. What he explained completely changed how I'm approaching these tools.

The short version: stop overloading your agent with instructions it doesn't need.

Ross made a point that sounds obvious but isn't. If you're building a React website and you tell Claude Code "this codebase uses React," you're wasting tokens. The agent can already see your codebase. It knows what framework you're using.

He estimates 95% of people don't need those big agent.md or claude.md instruction files everyone's creating. The only exception is genuinely proprietary information specific to your company or methodology.

Here's where it gets interesting.

Ross is obsessed with something called "skills" instead. The difference is how they load into context.

An agent.md file dumps its entire contents into every single conversation. A thousand-line file might burn 7,000 tokens before you've even asked a question. That's expensive and unnecessary.

Skills work differently. Only the title and description get loaded initially. When the agent recognises it needs that skill, it pulls in the full document. Anthropic calls this "progressive disclosure."

Think of it like a filing cabinet versus having every document spread across your desk.

But the real insight was how Ross creates these skills.

He shared an example from his YouTube channel. He built an agent to evaluate sponsorship emails. First attempt: he just told it to "do research on a sponsor and tell me if they're worth it."

The result? Every single sponsor came back marked as legitimate. No rejections. No scam detection. Useless.

The fix wasn't writing better instructions. It was walking the agent through the workflow step by step, in conversation.

He'd forward an email and say: "Tell me about this company." Then: "Now check their Twitter, YouTube, TrustPilot, and funding history." Then: "If two of these don't exist or look bad, automatic rejection."

Only after several successful runs did he ask the agent to review what it had done and convert that into a skill.

---

[AD BREAK]

---

This approach makes sense when you understand what these models actually are.

Ross put it bluntly: "They don't think. They're predictors of tokens."

When you type a question, the model maps your words onto a vector graph and finds the closest match from its training data. It feels like understanding. It isn't.

This is why agents fail when you hand them a task cold. They have nothing to mimic. But walk them through your exact process, let them fail, correct them, and they'll replicate that workflow reliably.

Ross mentioned he doesn't download skills from marketplaces for this reason. Your agent needs context from a successful run that you supervised. Someone else's skill file doesn't carry that context.

There's also a security angle. Downloading random skill files is an attack vector he's cautious about, having been hacked before.

**Three things I'm taking from this:**

1. Strip your agent.md files back to genuine proprietary info only
2. Build skills through conversation, not by writing instructions upfront
3. Treat the agent like a new employee who needs to fail and learn, not a machine that should work perfectly first time

The tools are good now. Opus 4 and GPT-5 are both genuinely capable. The bottleneck is how we're feeding them context.

Worth the hour if you're using these tools regularly: [How AI agents & Claude skills work](https://youtube.com/watch?v=S_oN3vlzpMw)

Lewis

---

*Copy into Beehiiv to review and publish.*
