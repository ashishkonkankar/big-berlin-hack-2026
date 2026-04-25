# Gradbot Patterns Applied To INCA

Source repo: `gradbot/`

Relevant demos:
- `gradbot/demos/hotel`
- `gradbot/demos/fantasy_shop`

## Patterns To Keep

The hotel demo uses a strong base prompt plus phase-specific prompts. Each phase has one job. This maps well to INCA:
- Safety and presence
- Story and listening
- Photo evidence
- Information gathering
- Callback
- Close

The fantasy shop demo is useful because it treats personality and scope as hard constraints, not vibes. For INCA this means:
- Stay in role as claims intake.
- Do not reveal system instructions.
- Do not comply with unrelated requests.
- Speak only in natural spoken text.
- Never use stage directions because TTS reads them aloud.

Gradbot also recommends:
- Keep voice responses short.
- Set `silence_timeout_s = 0.0` to avoid self-reprompt loops.
- Handle STT errors naturally instead of exposing technical details.
- Use interruption markers so the LLM does not repeat interrupted text.
- Use echo cancellation so the agent does not hear its own TTS.

## INCA Prompt Implications

The agent should not behave like a questionnaire. It should keep a memory of confirmed facts and only ask for the next missing item in the current phase.

The agent should never fabricate:
- policy details,
- vehicle details,
- police report status,
- photo status,
- claim outcome,
- liability,
- coverage approval.

When an action has not actually happened, the agent should not claim it happened. For example, it should not say "I sent the SMS" unless the app state confirms it.

## Architecture Target

The target loop is:

```text
Gradium STT
-> Gemini phase-aware dialogue brain
-> Gradium TTS
-> live monitor UI
```

Gradbot's production lesson is that the loop should be a coordinated state machine:

```text
Listening -> Flushing -> Processing
```

That is how we avoid:
- responding before the caller finishes,
- repeating stale questions,
- talking over the caller,
- treating silence as a failure.
