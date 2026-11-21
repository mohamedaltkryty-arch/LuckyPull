# NEXORA — نيكسورا: عوالم متحدة

Android-first Arabic fantasy game built with Godot 4.3. The game is presented as one continuous **Core Journey**, not a collection of separate modes.

## Player navigation
- **الرئيسية** — Start or continue the current match.
- **المنزل** — Character progression and permanent weapon, armor and core upgrades.
- **البطاقات** — Luck-card draws, published odds and collection.
- **الصناديق** — Virtual-reward chests, with missions, free season and cosmetic shop.
- **الجذور** — Five branches and fifteen persistent progression nodes.

## Fairness and save data
- Current draw probabilities are shown before a draw.
- Root upgrades use fixed virtual-coin costs and prerequisite checks.
- All rewards are virtual; no betting or cash prizes.
- Local save files include a recovery backup and versioned migrations.
- The game works offline; no network permission is required for the current build.

## Android
- Godot 4.3
- Package: `com.nexora.worlds`
- Version target: 0.10.0 (version code 17)
- ARMv7 and ARM64
- Separate application data from the earlier Lucky Pull package.

## Not integrated yet
Google Play Games sign-in, cloud synchronization, Google Play Billing and AdMob are planned but are not included in this offline milestone.
