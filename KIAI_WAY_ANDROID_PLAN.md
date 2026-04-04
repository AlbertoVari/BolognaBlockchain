# Kiai Way — Piano tecnico completo (Kotlin / Android)

## Obiettivo della V1 pubblicabile
Creare una prima versione **Android pubblicabile** di *Kiai Way* come **action arcade 2D rétro** (scope ridotto):
- 3 livelli
- 3 boss (1 per livello)
- 3 poteri Daimon
- loop semplice: entra, combatti, sopravvivi, boss, fine livello

---

## Stack e vincoli
- **Linguaggio:** Kotlin
- **IDE:** Android Studio
- **Architettura app:** Single-Activity
- **Gameplay/render:** `SurfaceView` con game loop dedicato
- **UI non gameplay:** Jetpack Compose (menu, HUD opzionale, settings)
- **Audio:** `SoundPool` (SFX) + `MediaPlayer` o ExoPlayer (BGM)
- **Build release:** Android App Bundle (`.aab`) firmato

---

## Struttura progetto consigliata

```text
app/
  src/main/java/com/kiaiway/
    MainActivity.kt
    core/
      GameLoop.kt
      Time.kt
      SceneManager.kt
      InputState.kt
      ObjectPool.kt
    render/
      GameSurfaceView.kt
      Sprite.kt
      SpriteSheet.kt
      Camera2D.kt
      RetroPalette.kt
      EffectsRenderer.kt
    gameplay/
      world/
        Level.kt
        SpawnSystem.kt
        Collision.kt
      entity/
        Entity.kt
        Actor.kt
        Player.kt
        Enemy.kt
        Boss.kt
        Daimon.kt
        Projectile.kt
        Effect.kt
      combat/
        Attack.kt
        Hitbox.kt
        Hurtbox.kt
        DamageSystem.kt
      ai/
        EnemyAI.kt
        BossPattern.kt
    scenes/
      TitleScene.kt
      LevelScene.kt
      BossScene.kt
      GameOverScene.kt
      VictoryScene.kt
    audio/
      AudioManager.kt
    ui/
      MainMenuScreen.kt
      SettingsScreen.kt
      PauseOverlay.kt
```

---

## Regole di design (scope control)
1. No open world
2. No loot system complesso
3. No albero RPG
4. Hitbox rettangolari
5. Animazioni corte (4–6 frame)
6. Sfondi statici o quasi statici
7. Solo 1 risoluzione logica interna (es. 320x180 upscaled)

---

## Gameplay loop della V1
1. Start livello
2. Ondate nemici base
3. Mini pausa + drop energia/potere
4. Boss con pattern leggibili
5. Vittoria livello / game over

### Input touch minimo
- **Sinistra:** joystick virtuale movimento
- **Destra:**
  - Attacco (tap)
  - Schivata (tap breve o swipe)
  - Potere Daimon (cooldown)

---

## Daimon semplificato (3 poteri)
1. **Colpo assistito**
   - Trigger: tap pulsante Daimon
   - Effetto: dash/spinta + danno frontale
   - Cooldown: 8s
2. **Scudo spirituale**
   - Effetto: riduzione danno per 2.5s
   - Cooldown: 12s
3. **Rallentamento del tempo**
   - Effetto: velocità nemici -40% per 2s
   - Cooldown: 15s

Implementazione: niente IA complessa autonoma. Il Daimon è un sistema di abilità con VFX dedicati.

---

## Entità minime e dati

## `Player`
- pos, vel, hp, stamina
- stato: idle/run/attack/hit/dead/dodge
- facing (left/right)

## `Enemy`
- tipo (melee/rush/ranged base)
- hp, speed, damage
- stato AI semplice: chase/attack/recover

## `Boss`
- hp alto
- fase 1 + fase 2 a soglia hp
- pattern a timer (niente behavior tree complesso)

## `Projectile` / `Effect`
- durata breve
- pooling per evitare allocazioni runtime

---

## Collisioni e combattimento
- AABB per corpo/hitbox
- Finestre attive attacco (active frames)
- i-frame in schivata del player (es. 200ms)
- knockback leggero
- hit-stop breve (es. 60ms) per impatto “arcade”

Pseudo-flow colpo:
1. player attiva animazione attack
2. in frame attivi, crea hitbox temporanea
3. collisione con hurtbox nemico
4. applica danno + knockback + VFX sangue
5. abilita cooldown/chain combo

---

## Scene management
- `TitleScene`
- `LevelScene`
- `BossScene`
- `GameOverScene`
- `VictoryScene`

`SceneManager` espone:
- `update(dt)`
- `render(canvas)`
- `onTouch(event)`
- `onEnter()` / `onExit()`

---

## Rendering rétro pratico
- Risoluzione interna fixed (es. 320x180 o 426x240)
- Upscale nearest-neighbor
- Palette limitata e LUT semplice
- Effetti pochi ma forti:
  - slash trail
  - blood splash 2D
  - flash bianco su hit
  - shake camera su finisher

---

## Audio design minimale
- 1 traccia BGM per livello
- 1 traccia boss
- SFX: spada, parata, grido kiai, danno, morte nemico
- Ducking volume durante urlo o attivazione potere Daimon

---

## Piano di sviluppo (30 giorni)

### Settimana 1 — Fondazione tecnica
- Setup progetto + Activity fullscreen immersive
- `GameSurfaceView` + thread loop stabile (60fps target)
- Input touch base
- Camera + render sprite statico

### Settimana 2 — Core combat
- Player movimento + attacco
- Nemico base melee
- Sistema collisioni
- Barra vita player/nemico

### Settimana 3 — Feel + contenuto
- Daimon potere #1
- VFX sangue/slash
- Audio manager con SFX/BGM
- Game over + restart

### Settimana 4 — Boss + release prep
- Boss livello 1 con 2 pattern
- Menu iniziale + pause
- Ottimizzazione draw allocations
- Build release signed + AAB interno test

---

## Backlog post-V1 (non bloccare rilascio)
- Daimon poteri #2 e #3 bilanciati
- 2° e 3° boss
- Sistema rank stage (S/A/B/C)
- Localizzazione EN/IT
- Controller support (facoltativo)

---

## Checklist pubblicazione Google Play (operativa)
1. Account Play Console attivo
2. App firmata (consigliato Play App Signing)
3. Upload `.aab`
4. Target API richiesto corrente
5. Privacy policy URL
6. Screenshot smartphone + icona 512x512 + feature graphic
7. Test interno/closed
8. Rollout graduale produzione

---

## Definition of Done V1
- 1 livello completo giocabile end-to-end
- 1 boss completo
- nessun crash in 20 run di test
- fps stabile su almeno 2 dispositivi Android medi
- pacchetto AAB pronto e validato in Play Console (internal test)

