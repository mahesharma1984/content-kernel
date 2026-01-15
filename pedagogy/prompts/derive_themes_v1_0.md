# Theme Derivation Prompt

You are analyzing a literary text based on its kernel data (computational narratology analysis).

## Input Data
- **Pattern Name:** {pattern_name}
- **Core Dynamic:** {core_dynamic}
- **Reader Effect:** {reader_effect}
- **Tone:** {tone}
- **Device Priorities:** {device_priorities}
- **Device Mediation Summary:** {device_mediation_summary}
- **Sample Devices:** {sample_devices}

## Task
Identify 3-4 major themes this text explores. Themes should:
1. Connect directly to the alignment pattern
2. Show what the text SAYS about a topic (not just the topic)
3. Be supported by devices from the device_priorities list
4. Use quotes from micro_devices only

## Output Format
Return ONLY valid JSON (no markdown, no preamble):

{
  "themes": [
    {
      "name": "Concise theme name (3-5 words)",
      "slug": "url-friendly-slug",
      "description": "What the text says about this theme (2-3 sentences, Grade 10-11 language)",
      "pattern_connection": "How the alignment pattern creates this theme (1-2 sentences)",
      "device_examples": [
        {
          "device_name": "Device from priorities list",
          "quote": "Exact quote from micro_devices[].anchor_phrase",
          "effect": "How this device creates the theme (1 sentence)"
        }
      ]
    }
  ]
}

## Constraints
- Themes must connect to {pattern_name}
- Use ONLY devices from device_priorities
- Quotes must be EXACT from micro_devices[].anchor_phrase
- Language level: Year 11 VCE students
- 2-3 device examples per theme
- Focus on how pattern creates theme, not general analysis

## Example Theme (for reference only)
{
  "name": "Cosmic Perspective vs Human Intimacy",
  "slug": "cosmic-perspective-human-intimacy",
  "description": "The text explores the tension between vast cosmic scale and intimate human experience. Astronauts simultaneously observe Earth from detached cosmic distance while experiencing deeply personal thoughts and emotions.",
  "pattern_connection": "The Cosmic Contemplation pattern's omniscient narration creates dual consciousness that holds both intimacy and distance simultaneously.",
  "device_examples": [
    {
      "device_name": "Juxtaposition",
      "quote": "A hand-span away beyond a skin of metal the universe unfolds",
      "effect": "Contrasts intimate human scale with cosmic immensity, creating meditative awareness of human position."
    }
  ]
}

