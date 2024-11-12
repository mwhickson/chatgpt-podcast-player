# ChatGPT TUI Podcast Player

## Overview

I sat down with ChatGPT to see how far we would get in generating a TUI-based Podcast Player.

To my moderate suprise, I got something functional.

Some things went amazingly well.

Other things went less well, but not inherently bad.

## Screenshots

![Main Screen using Textualize](main-screen.png)

![Screen after searching for a podcast and selecting one to see its episodes](after-search-podcast-with-episodes.png)

![The episode information and player screen -- simple, ugly, but working](episode-info-with-player.png)

## Reflection

Overall, I was impressed by the session I had with ChatGPT in the production of the Podcast Player.

It's quite clear that, although a basic working application was generated, I would not want to release or support that application.

Using ChatGPT in an even more granular mode to generate boilerplate might be more viable, but existing code generation solutions (typically directly template driven) already fulfill that need in a more predictable, and usually a significantly higher quality, manner.

So, ultimately, no real surprises. Things ended up playing out mostly as expected. It's an impressive technology, but not without frustrating drawbacks.

Here are some additional thoughts I had related to the experiment:

- ChatGPT is... chatty. I ignored all the explanatory text, unless I needed to figure out what ChatGPT was trying to do. I referenced the actual code more frequently. I'm not sure this is a good default behaviour when triggering code generation mode.
- ChatGPT is ready to try an solve things in the first go. This was not the experience I was after and had to request a more iterative approach.
- Hallucination, or just plain incorrect implementations, made some code hard to get successfully generated.
- ChatGPT, despite its desire to jump in feet first, often chooses an implementation that it later "realizes" is missing (often obvious, and desirable) quality improvements
- The more likely there is to be training data (re: programming language, libraries, application functionality/features, etc.), the more likely ChatGPT will produce output able to achieve the desired outcome.
- ChatGPT can be guided to a solution. Suggesting the `Screen` component resulted in going from a repeatedly broken modal window solution being re-implemented successfully.
- ChatGPT cannot always be guided to a solution. Sometimes the generated code bounces from one bad implementation to another. It was easier to reduce the complexity of the desired outcome to force a difference approach during code generation.
- The longer the session goes on, the more ChatGPT needed to be reminded of the whole app. The code produced also grew much shorter in length, and was provided without context.
- User interface generation seems capable of ensuring the requested components are present; however, there is no immediately apparent attempt at achieving a pleasing design.
- Application development using ChatGPT is quicker in some respects, and might be good for prototyping; however, refining the code would almost certainly require manual modification for holistic clarity and to flesh out more complex features.

## Licence

Public Domain I guess. 

I'm certainly not claiming any copyright on this.
