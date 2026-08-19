# AI CINEMATIC VIDEO PROMPTING — MASTER WORKFLOW V3
## OmniFlash-focused practical rulebook

## PURPOSE

Convert rough story ideas into clean cinematic AI video prompts while preserving the user's intended story and giving the video engine enough information to produce accurate character placement movement emotion continuity and camera language.

Core philosophy:

> Give the engine freedom where it can reason reliably and explicit control where ambiguity can break the shot.

This version consolidates the earlier workflow rules with observed OmniFlash behavior and the latest tested prompting discoveries.

---

# 1. WORKFLOW OVERVIEW

ROUGH STORY
→ identify intended events
→ define protagonist and players
→ define assets
→ define environment
→ define visual style
→ identify important spatial relationships
→ divide into cinematic story beats
→ determine which beats need spatial/camera enforcement
→ refine each beat
→ validate punctuation and dialogue
→ output lightweight standalone video prompt

Do not rewrite the user's story merely to make it cinematic.

Creative development is allowed when the user has not yet defined necessary characters assets environments or other production elements. Clearly distinguish established information from proposed ideas.

---

# 2. STORY FOUNDATION

When starting a new story establish when relevant:

## Protagonist
- identity
- age when relevant
- appearance
- height
- physique
- hair
- clothing
- personality
- motivation
- abilities
- emotional direction
- voice characteristics

## Other players
- allies
- opponents
- supporting characters
- relationships
- appearance
- clothing
- personality
- voice

## Assets
- weapons
- tools
- vehicles
- important props
- technology
- magical objects
- recurring objects

## Environment
- location
- architecture
- geography
- important objects
- lighting
- weather
- spatial anchors
- time period

Do not invent missing details without reason. When useful ask the user or propose several options.

---

# 3. PROMPT ARCHITECTURE

Use:

# MASTER VIDEO GENERATION PROMPT

## HEADER DATA

Context
Style
Character Definitions
Assets and Environment
Lighting when useful
Camera Rules
Animation and Motion
Audio when useful

## STORY BEATS

Each separate line is one cinematic beat.

Do not number beats unless numbering is useful for human discussion.

The STORY BEATS heading establishes the beat structure.

---

# 4. ONE LINE ONE BEAT

Default:

one line = one visual beat = one terminating full stop

A beat should contain one clear cinematic event or tightly connected physical action.

Do not split a continuous physical interaction into disconnected beats when doing so can break the action.

Example:

Bad:
Character A kicks Character B.
Character B dodges.

Preferred:
Character A kicks toward Character B who immediately dodges the incoming kick.

The attack and immediate reaction belong to the same beat.

---

# 5. PUNCTUATION MINIMALISM

Video prompts do not need literary grammar.

Optimize punctuation for machine interpretation.

## Full stops

Normally use one full stop at the end of each beat.

Avoid unnecessary full stops inside beats.

## Dialogue

Do not use full stops inside a spoken line when the same character is intended to continue speaking.

Preferred:
He says "What are you doing here get out I am busy"

Avoid:
He says "What are you doing here. Get out. I am busy."

A full stop inside dialogue may cause a video engine to interpret the following words as another speaker's line.

## Commas

Commas are optional.

Use them only when they materially improve clarity.

Compact character data may omit them.

## Semicolons

Avoid by default.

## Brackets

Avoid unless genuinely necessary.

Do not hard-code project-specific reference filenames such as image_0.png unless that exact filename is required.

Prefer:
Maintain the attached character reference.

## Colons

Colons are useful for structural headers:

Character Definitions:
Style:
Environment:
Camera Rules:
Story Beats:

They are not required inside ordinary beats.

---

# 6. CHARACTER LOCKING

For independently generated clips repeat essential character information.

Useful fields:

name
sex
age when relevant
height
physique
face
hair
skin
clothing
accessories
personality
demeanor
emotional direction
voice

Keep descriptions compact.

If a reference image is attached:

Maintain the exact character design clothing proportions and art style shown in the attached image.

Do not depend on a project-specific filename.

Define voice characteristics when a character speaks so vocal identity remains consistent.

---

# 7. ENVIRONMENT LOCKING

Define:

location
architecture
important objects
spatial anchors
persistent props
important geography

When geography matters use literal relationships.

Bad:
She looks at the balcony.

Good:
Her balcony is directly below the rooftop terrace on the same building facade.

Do not overload the prompt with irrelevant geography.

---

# 8. CAMERA AUTONOMY

Default:

Multiple dynamic cinematic camera angle shots for every story beat emphasizing action emotion expression reaction environment and spatial relationships. Engine determines shot composition dynamically.

Allow the engine to choose:

close-ups
medium shots
wide shots
tracking shots
POV shots
low angles
high angles
over-the-shoulder shots
macro details
environmental views
reaction shots

Do not manually force a camera angle for every beat when the angle is unimportant.

---

# 9. CAMERA ENFORCEMENT

Force a camera angle when the specific viewpoint is necessary to communicate the intended result.

Examples:

Low worm's-eye view emphasizing a tall character standing behind a shorter character.

Reverse over-the-shoulder view revealing a character positioned directly behind another character.

High drone view establishing the geography of several characters.

Macro closeup confirming a hand touching the back of another character's neck.

POV from the seated character showing the other character leaning toward him.

The camera should be used as a tool for confirming spatial relationships rather than merely decorating the prompt.

---

# 10. CRITICAL SPATIAL CONTINUITY RULE

## STYLE A — EXPLICIT POSITIONAL RE-ANCHORING

This is the preferred tested method.

Do NOT assume the engine will reliably carry character positioning from one beat into the next.

Every beat must independently establish any character position physical state orientation or spatial relationship that is important to the intended shot.

If a character's position matters to the beat say so directly in that beat.

Example:

Beat 1:
Both characters remain seated in their established positions on the bench.

Beat 2:
She leans forward toward him while remaining seated beside him.

Beat 3:
She slowly moves her lips away from his ear and settles back against the backrest while remaining seated beside him.

Beat 4:
He looks toward her and says "It is a nice name" while she remains seated beside him facing him.

Do not rely on a global instruction such as "remember the previous beat" to replace important positional context.

---

# 11. CONTINUITY TEST B — NOT THE PRIMARY METHOD

A header instruction such as:

Treat every story beat as the immediate continuation of the preceding beat and carry forward established character positions poses and relationships

may sometimes help.

However observed testing showed inconsistent results.

Example failure:
A character established as seated may be made to stand when the next beat says she leans toward another character.

Therefore:

## Do not use continuous-scene-state instructions as a substitute for explicit positional anchoring.

They may be included as a supplementary instruction but Style A remains the primary workflow.

---

# 12. POSITIONING CONTEXT

When positioning matters explicitly define:

- who is near the camera
- who is far from the camera
- who is in front
- who is behind
- who faces whom
- who approaches whom
- movement target
- relative height
- foreground/background relationship
- camera viewpoint
- resulting pose

Example:

Bad:
The tall vampire approaches the man from behind.

Better:
He is close to the camera taking notes while the tall vampire is farther from the camera behind him and walks toward him.

Behind view of the vampire approaching him from directly behind while he continues taking notes unaware of her presence.

Low worm's-eye view from near the man showing him in the foreground while her tall human-scale silhouette stands directly behind him looking down toward him.

---

# 13. SPATIAL REASONING PRINCIPLE

More spatial detail is not automatically better.

Add spatial detail when an incorrect inference would break the intended shot.

The objective is:

## CONTROLLED FREEDOM

Control:
- critical positions
- movement targets
- important interactions
- important reactions
- required outcomes
- difficult spatial relationships

Allow the engine freedom for:
- ordinary transitional movement
- minor repositioning
- connective choreography
- unimportant camera movement
- details that do not affect the intended result

---

# 14. SPATIAL REVEAL TECHNIQUE

When a scene depends on a difficult reveal, do not rely only on the movement instruction.

Instead establish the movement and then show the resulting spatial configuration from an appropriate camera.

Example:

She slowly turns her head and upper body to look behind herself.

Reverse over-the-shoulder view reveals the vampire standing directly behind him facing him.

She remains several steps behind his body on the same central axis looking directly down toward him.

Low worm's-eye angle from near his position shows her tall human-scale silhouette standing behind him looking down toward him.

He finally sees her clearly and freezes in shock.

This technique can reduce the need for a reference frame but cannot guarantee the same accuracy as an actual spatial reference image.

---

# 15. CHARACTER COUNT

Default maximum:

## Two characters per beat.

More than two active characters substantially increases the risk of identity confusion incorrect positioning anatomy glitches unwanted character movement interaction errors and lip-sync errors.

Use larger groups only occasionally.

An occasional distant drone or high environmental shot may show several characters standing or walking together when individual character accuracy is not important.

Do not make multi-character shots the normal beat structure.

---

# 16. DIALOGUE AND LIP SYNC

When a character speaks:

## Preferred
Dedicate the entire beat to the speaker whenever practical.

Example:
Closeup of the man as he asks "Who are you"

This reduces lip-sync ambiguity.

## Listener POV alternative

Use the listener's POV when useful.

The listener's mouth should remain outside the visible frame so the engine does not assign the dialogue to the wrong character.

Example:
POV from her seated position looking toward him as he asks "Do you speak English"

Do not show the listener's visible mouth during the speaker's dialogue.

## Speaking while another character remains present

Explicitly state the other character's position when their presence matters.

Example:
He says "It is a nice name" while she remains seated beside him facing him.

Do not assume the engine will preserve an unmentioned character.

---

# 17. VOICE CONSISTENCY

When a character speaks define their voice in the character data.

Useful descriptions:

soft feminine voice
deep restrained aristocratic voice
raspy elderly voice
calm controlled Japanese delivery
young confident feminine voice

Keep voice identity consistent unless the story intentionally changes it.

---

# 18. ACTION AND FIGHT CHOREOGRAPHY

Action beats should communicate visible cause and immediate reaction.

## Action plus reaction belongs together

Bad:
Character A punches Character B.
Character B blocks.

Preferred:
Character A punches toward Character B who immediately blocks the strike.

Examples:

Character A kicks toward Character B who immediately dodges the incoming kick.

Character A grabs Character B who immediately slips free.

Character A launches a fast combination of punches and kicks at Character B who professionally blocks and dodges while Character A maintains the advantage.

---

# 19. FIGHT CHOREOGRAPHY CONTROL LEVELS

Use three levels.

## Engine choreography

Character A throws professional punches and kicks at Character B who expertly blocks dodges and counters while Character A maintains the advantage.

Use when the exact choreography is unimportant.

## Guided choreography

Character A launches a fast combination of punches and kicks at Character B who blocks the first strikes dodges the next attack and immediately counters.

Use when the sequence has an intended structure but intermediate movement can be delegated.

## Locked choreography

Character A drives a right roundhouse kick toward Character B's torso who immediately ducks underneath the kick and counters with a fast body strike.

Use when a specific action must occur accurately.

Principle:

> Control the moments that matter. Give the engine freedom between them.

---

# 20. FIGHT SPATIAL CONTINUITY

For difficult fight choreography explicitly establish:

- starting positions
- distance
- facing direction
- attack target
- reaction
- resulting position

Do not rely on the engine to infer complex spatial relationships.

For grappling or close combat use positional beats where necessary:

Position → attack → block → counter → escape → resulting position

Keep the sequence between the relevant two characters whenever possible.

---

# 21. MOVEMENT DIRECTION

Avoid unnecessary directional instructions that create ambiguity.

Bad:
Character A turns around and walks away.

The engine may interpret the resulting direction incorrectly.

Better:
Character A is standing facing Character B and talking. Character A walks away while Character B watches.

Only specify the direction when the direction itself is important.

If direction matters:
Character A walks away from Character B toward the doorway.

The goal is to define the necessary relationship rather than over-control the movement.

---

# 22. NEGATIVE SPATIAL CONSTRAINTS

Use explicit negative clarification when the engine has a known tendency to misinterpret a visual trait.

Examples:

Very tall towering woman but proportionally human sized not giant.

Tall human-scale silhouette.

Do not make the character gigantic.

Do not switch the characters' left and right positions.

Do not use negative constraints mechanically. Add them when they solve a known generation problem.

---

# 23. EMOTIONAL BEATS

Emotion can be its own beat when visually important.

Examples:

His expression shifts from relaxed curiosity to slight nervousness.

Her curious expression slowly becomes an eerie smile.

His eyes widen in shock when he finally sees her.

Do not over-describe emotions that are not visually observable.

---

# 24. PHYSICAL STATE CHANGES

When a beat changes a character's physical state, explicitly describe both the important previous relationship and the new state.

Example:

She slowly moves her lips away from his ear and settles back against the backrest while remaining seated beside him.

Example:

He drops the notepad and pen as he recoils in alarm while she remains standing directly behind him.

This prevents the engine from inventing a disconnected transition.

---

# 25. REFERENCE IMAGE USE

When a reference image is attached:

Maintain the same character design proportions clothing art style and important spatial arrangement shown in the attached image.

Use the reference as a visual anchor.

Do not refer to image_0.png or another project-specific filename unless that exact filename is required.

For extremely difficult spatial configurations an actual generated reference frame may still be the strongest solution.

Prompt refinement should attempt to eliminate that extra step where practical but should not pretend textual prompting can guarantee image-level spatial accuracy.

---

# 26. CAMERA AS SPATIAL VERIFICATION

For difficult spatial scenes use successive camera angles to confirm geometry.

Example sequence:

Wide shot establishes both characters.

POV confirms who is approaching whom.

Over-the-shoulder shot confirms foreground and background.

Macro shot confirms physical contact.

Reaction closeup confirms emotional response.

Low angle confirms relative height.

Do not force all of these into every scene. Use them when the spatial relationship is important.

---

# 27. TALL CHARACTER CINEMATOGRAPHY

When a character is unusually tall but human scale use:

- low angles
- worm's-eye views
- distant full-body shots
- foreground/background depth
- over-the-shoulder height comparison

Avoid physically distorting the character to fit the frame.

Explicitly state "tall human-scale" when the engine may interpret unusual height as giant scale.

---

# 28. TRANSFORMATIONS

For transformation sequences preserve identity across the transformation.

Define:

- original identity
- transformation progression
- resulting identity
- resulting clothing
- resulting physique
- resulting emotional state

Do not unnecessarily break every anatomical change into separate beats.

Example:

Her bent back begins straightening as magical energy flows through her body.

Her aged body elongates becoming tall and extremely slender.

Her aged face transforms into a youthful refined face while her hair flows through the magical energy.

Her clothing transforms into a premium fitted halter neck dress as the transformation completes.

---

# 29. ANIMATION AND MOTION

Useful directives:

fluid character motion
stable anatomy
natural cloth and hair movement
realistic sitting physics
elegant controlled movement
fast action pacing
zero limb duplication

Avoid excessive technical animation instructions unless they solve a known problem.

---

# 30. STYLE LOCK

Clearly define:

- art style
- rendering style
- lighting
- color character when important
- cinematic mood

Repeat style only as much as necessary.

If the engine repeatedly violates the style use explicit negative constraints.

---

# 31. LIGHTING AND CINEMATOGRAPHY

Include lighting when it materially affects the scene.

Lens and depth of field are optional.

Do not mechanically specify lens values for every prompt.

Camera language should be driven by visual purpose:

Geography → high or drone view
Power → low angle
Emotion → closeup
Technique → profile or tracking
Spatial reveal → POV or over-the-shoulder

---

# 32. AUDIO

Add audio when useful:

ambient environment
footsteps
cloth movement
impacts
door sounds
breathing
music
tension drones
character voices

Dialogue and important sound effects should be associated with the correct beat.

Do not overload prompts with audio direction that does not improve the scene.

---

# 33. PROMPT LIGHTWEIGHTNESS

More context is not automatically better.

The objective is minimum sufficient context.

However spatial continuity is an exception.

Do not remove positional information merely to make the prompt shorter when the engine has demonstrated that it needs that information.

Preferred principle:

> Lightweight where possible, explicit where necessary.

---

# 34. EXAMPLES — POSITIONAL ANCHORING

## Example A — seated conversation

Bad:
She leans toward him.

Better:
She remains seated beside him and slowly leans forward toward him.

More controlled:
His POV low angle showing the seated vampire beside him as she slowly leans her tall human-scale body forward toward him.

## Example B — whisper

Bad:
She whispers into his ear.

Better:
She remains seated beside him and leans forward bringing her lips close to his ear as she whispers her name.

## Example C — leaving the ear

Bad:
He says "It is a nice name"

Better:
She slowly moves her lips away from his ear and settles back against the backrest while remaining seated beside him.

He looks toward her and says "It is a nice name" while she remains seated beside him facing him.

## Example D — approach from behind

Bad:
The vampire approaches him from behind.

Better:
He is close to the camera taking notes while the tall vampire is farther from the camera behind him and walks toward him.

Behind view of the vampire approaching him from directly behind while he continues taking notes unaware of her presence.

## Example E — reveal

Bad:
He turns around and sees her.

Better:
He slowly turns his head and upper body to look behind himself.

Reverse over-the-shoulder view reveals her standing directly behind him facing him.

She remains close behind his body looking directly down toward him.

He sees her clearly and freezes in shock.

## Example F — tall character

Bad:
She stands behind him looking down.

Better:
She stands directly behind him facing him with her tall slender human-scale body clearly visible above him looking down toward him.

Low worm's-eye view emphasizes her towering but human-scale silhouette behind him.

---

# 35. EXAMPLES — CAMERA POSITIONING

Example:
drone distant high orbiting camera both characters remain seated in their established positions on the bench having a calm conversation.

Example:
face closeup of the speaker showing subtle emotional change.

Example:
his POV low angle showing the tall vampire beside him slowly leaning toward him while remaining seated.

Example:
macro closeup of her lips close to his ear.

Example:
worm's-eye semi-side view showing her withdrawing from his ear and settling back against the bench.

These are examples of how camera language can enforce spatial meaning when required, not mandatory camera patterns.

---

# 36. EXAMPLES — ACTION

Bad:
Character A attacks Character B.
Character B reacts.

Better:
Character A throws a fast punch toward Character B who immediately blocks the strike.

Bad:
She turns around and walks away.

Better:
She faces him while speaking then walks away from him toward the doorway.

Bad:
He kicks her.
She dodges.

Better:
He launches a high kick toward her torso who immediately steps aside and avoids the kick.

---

# 37. EXAMPLES — DIALOGUE

Bad:
He says "Do you speak English?"

She replies "A little."

Better:
He looks toward her and asks "Do you speak English"

She looks at him with quiet curiosity and says in Japanese "Sukoshi dake"

If the speaker must continue:
He looks toward her and says "What are you doing here get out I am busy"

---

# 38. EXAMPLES — MULTIPLE CHARACTERS

Default:
Two characters maximum per beat.

Occasional exception:
High distant drone view showing the entire group walking through the environment.

Do not use crowded close or medium shots as the normal workflow.

---

# 39. EXAMPLES — ENGINE FREEDOM

When exact choreography is unimportant:

Character A throws professional punches and kicks at Character B who professionally blocks dodges and counters while Character A maintains the advantage.

When exact choreography matters:

Character A drives a kick toward Character B's torso who immediately ducks beneath it and counters.

Do not specify every intermediate movement unless it matters.

---

# 40. COMMON FAILURE MODES

## Characters change position
Cause:
The engine treats beats independently.

Fix:
Restate the required position inside the beat.

## Seated character stands
Cause:
The beat says "leans forward" without explicitly saying she remains seated.

Fix:
"She remains seated beside him and leans forward toward him."

## Character disappears
Cause:
The beat does not mention the character whose continued presence matters.

Fix:
Explicitly state that character remains present and positioned.

## Speaker talks alone
Cause:
The listener's presence was omitted.

Fix:
"She remains seated beside him while he says..."

## Wrong lip sync
Cause:
Multiple visible mouths during dialogue.

Fix:
Dedicate the beat to the speaker or use listener POV with the listener's mouth outside the frame.

## Wrong spatial reveal
Cause:
"Turns around and sees her" leaves too much geometry to inference.

Fix:
Use explicit resulting spatial configuration plus an appropriate camera viewpoint.

## Tall character becomes giant
Cause:
Unconstrained interpretation of unusual height.

Fix:
"Very tall towering but human-scale not giant."

## Fight reaction occurs too late
Cause:
Attack and reaction separated into different beats.

Fix:
Combine action and immediate reaction in one beat.

---

# 41. FINAL PROMPT QUALITY CHECK

Before returning a finished prompt:

- Is the user's intended story preserved?
- Are protagonist and players defined?
- Are important assets defined?
- Is the environment sufficiently defined?
- Is the visual style explicit?
- Are important spatial relationships explicit?
- Is each beat independently understandable where necessary?
- Have important character positions been restated?
- Is the maximum-two-character rule respected?
- Is dialogue assigned clearly to the correct speaker?
- Are dialogue lines free of internal full stops?
- Is voice defined when relevant?
- Is camera autonomy used by default?
- Are forced camera angles used when spatial accuracy requires them?
- Are attack and immediate reactions combined?
- Are unnecessary directional instructions removed?
- Are semicolons avoided?
- Are unnecessary brackets removed?
- Are project-specific reference filenames avoided?
- Are commas used only when useful?
- Has the prompt remained lightweight except where explicit spatial control is necessary?
- Have known engine failure modes been proactively addressed?

---

# 42. CORE PRINCIPLES

1. Write like a filmmaker.
2. Prompt like a storyteller.
3. Preserve the user's story.
4. Define the protagonist players assets and environment when needed.
5. Use dynamic camera autonomy by default.
6. Force camera angles when they communicate something essential.
7. Maximum two characters per beat by default.
8. Give the engine breathing space when ambiguity is harmless.
9. Take control when ambiguity can break the shot.
10. Treat every beat as potentially visually independent.
11. Explicitly re-anchor important character positions inside the beat.
12. Do not rely on a continuity header to preserve critical spatial state.
13. Use camera angles to verify difficult spatial relationships.
14. Keep immediate action and reaction together.
15. Keep dialogue as one uninterrupted speech unit.
16. Prefer lightweight syntax.
17. Use literal visual language.
18. The best prompt is not the longest prompt.
19. The best prompt contains the minimum information required to prevent the engine from making the wrong interpretation.

## FINAL PRINCIPLE

### Lightweight where possible. Explicit where necessary.
