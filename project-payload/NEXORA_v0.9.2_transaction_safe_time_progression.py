#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

def replace_once(relative_path: str, old: str, new: str) -> None:
    path = root / relative_path
    source = path.read_text(encoding="utf-8")
    if new in source:
        return
    if old not in source:
        raise SystemExit(f"Expected source block not found in {relative_path}")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")

replace_once("scripts/game_state.gd", """func _apply_time_progress() -> void:
    var now := int(Time.get_unix_time_from_system())
    if last_energy_timestamp <= 0:
        last_energy_timestamp = now
        save_game()
        return
    var elapsed := maxi(0, now - last_energy_timestamp)
    var gained := int(elapsed / REGEN_SECONDS)
    if gained <= 0:
        return
    var previous_energy := energy
    energy = mini(MAX_ENERGY, energy + gained)
    if energy >= MAX_ENERGY:
        last_energy_timestamp = now
    else:
        last_energy_timestamp += gained * REGEN_SECONDS
    if energy != previous_energy:
        save_game()
        changed.emit()
""", """func _apply_time_progress() -> void:
    if save_recovery_blocked:
        return
    var now := int(Time.get_unix_time_from_system())
    if last_energy_timestamp <= 0:
        var initial_snapshot := _capture_save_snapshot()
        last_energy_timestamp = now
        if not save_game():
            _restore_save_snapshot(initial_snapshot)
        return
    var elapsed := maxi(0, now - last_energy_timestamp)
    var gained := int(elapsed / REGEN_SECONDS)
    if gained <= 0:
        return
    var snapshot := _capture_save_snapshot()
    var previous_energy := energy
    var previous_timestamp := last_energy_timestamp
    energy = mini(MAX_ENERGY, energy + gained)
    if energy >= MAX_ENERGY:
        last_energy_timestamp = now
    else:
        last_energy_timestamp += gained * REGEN_SECONDS
    if energy != previous_energy or last_energy_timestamp != previous_timestamp:
        if not save_game():
            _restore_save_snapshot(snapshot)
            return
        changed.emit()
""")

replace_once("scripts/game_state.gd", """func _reset_daily_if_needed() -> void:
    var today := _today()
    if last_reset_date == today:
        return
    daily_pull_count = 0
    daily_chest_count = 0
    daily_card_count = 0
    daily_completed_sets = 0
    arcade["daily_wins"] = 0
    arcade["spell_daily_casts"] = 0
    daily_missions_claimed.clear()
    claimed_daily = false
    last_reset_date = today
    save_game()
    changed.emit()
""", """func _reset_daily_if_needed() -> void:
    if save_recovery_blocked:
        return
    var today := _today()
    if last_reset_date == today:
        return
    var snapshot := _capture_save_snapshot()
    daily_pull_count = 0
    daily_chest_count = 0
    daily_card_count = 0
    daily_completed_sets = 0
    arcade["daily_wins"] = 0
    arcade["spell_daily_casts"] = 0
    daily_missions_claimed.clear()
    claimed_daily = false
    last_reset_date = today
    if not save_game():
        _restore_save_snapshot(snapshot)
        return
    changed.emit()
""")

replace_once("scripts/game_state.gd", """    if season_start_timestamp <= 0:
        season_start_timestamp = now
        season_number = maxi(1, season_number)
        season_points = 0
        season_claimed_tiers.clear()
        season_bonus_chest_claimed = false
        save_game()
        return true
""", """    if season_start_timestamp <= 0:
        var initial_snapshot := _capture_save_snapshot()
        season_start_timestamp = now
        season_number = maxi(1, season_number)
        season_points = 0
        season_claimed_tiers.clear()
        season_bonus_chest_claimed = false
        if not save_game():
            _restore_save_snapshot(initial_snapshot)
            return false
        return true
""")

replace_once("scripts/game_state.gd", """    var completed_seasons := int(elapsed / SEASON_DURATION_SECONDS)
    season_number += completed_seasons
    season_start_timestamp += completed_seasons * SEASON_DURATION_SECONDS
    season_points = 0
    season_claimed_tiers.clear()
    season_bonus_chest_claimed = false
    save_game()
    return true
""", """    var completed_seasons := int(elapsed / SEASON_DURATION_SECONDS)
    var snapshot := _capture_save_snapshot()
    season_number += completed_seasons
    season_start_timestamp += completed_seasons * SEASON_DURATION_SECONDS
    season_points = 0
    season_claimed_tiers.clear()
    season_bonus_chest_claimed = false
    if not save_game():
        _restore_save_snapshot(snapshot)
        return false
    return true
""")

insert_tests = """    # Time-based and calendar resets must also roll back when persistence fails.
    print("TEST_MARKER_8B: Energy regeneration, daily reset and season rollover roll back on save failure.")
    if not _clear_test_saves():
        _fail("Could not reset time-progress failure tests")
        return
    var time_failure_temp_absolute := ProjectSettings.globalize_path(TEMP_SAVE_PATH)
    var now_timestamp := int(Time.get_unix_time_from_system())

    var failed_energy_state = state_script.new()
    failed_energy_state.energy = 5
    failed_energy_state.last_energy_timestamp = now_timestamp - int(failed_energy_state.REGEN_SECONDS) * 2
    var previous_energy_timestamp: int = int(failed_energy_state.last_energy_timestamp)
    if DirAccess.make_dir_absolute(time_failure_temp_absolute) != OK:
        _fail("Could not create the save-path collision for energy regeneration test")
        return
    failed_energy_state._apply_time_progress()
    if failed_energy_state.energy != 5 or failed_energy_state.last_energy_timestamp != previous_energy_timestamp or not failed_energy_state.save_recovery_blocked:
        _fail("Failed energy-regeneration save retained uncommitted energy or timestamp")
        return
    failed_energy_state.free()
    if DirAccess.remove_absolute(time_failure_temp_absolute) != OK:
        _fail("Could not remove the temporary save-path collision after energy test")
        return

    var failed_daily_reset_state = state_script.new()
    failed_daily_reset_state.last_reset_date = "2000-01-01"
    failed_daily_reset_state.daily_pull_count = 4
    failed_daily_reset_state.daily_chest_count = 3
    failed_daily_reset_state.daily_card_count = 2
    failed_daily_reset_state.daily_completed_sets = 1
    failed_daily_reset_state.claimed_daily = true
    failed_daily_reset_state.daily_missions_claimed = {"pulls_10":true}
    failed_daily_reset_state.arcade["daily_wins"] = 2
    failed_daily_reset_state.arcade["spell_daily_casts"] = 3
    if DirAccess.make_dir_absolute(time_failure_temp_absolute) != OK:
        _fail("Could not create the save-path collision for daily reset test")
        return
    failed_daily_reset_state._reset_daily_if_needed()
    if failed_daily_reset_state.last_reset_date != "2000-01-01" or failed_daily_reset_state.daily_pull_count != 4 or failed_daily_reset_state.daily_chest_count != 3 or failed_daily_reset_state.daily_card_count != 2 or failed_daily_reset_state.daily_completed_sets != 1 or not failed_daily_reset_state.claimed_daily or not bool(failed_daily_reset_state.daily_missions_claimed.get("pulls_10", false)) or int(failed_daily_reset_state.arcade.get("daily_wins", 0)) != 2 or int(failed_daily_reset_state.arcade.get("spell_daily_casts", 0)) != 3 or not failed_daily_reset_state.save_recovery_blocked:
        _fail("Failed daily reset did not restore counters and claim history")
        return
    failed_daily_reset_state.free()
    if DirAccess.remove_absolute(time_failure_temp_absolute) != OK:
        _fail("Could not remove the temporary save-path collision after daily reset test")
        return

    var failed_season_rollover_state = state_script.new()
    failed_season_rollover_state.season_start_timestamp = now_timestamp - int(failed_season_rollover_state.SEASON_DURATION_SECONDS)
    failed_season_rollover_state.season_number = 3
    failed_season_rollover_state.season_points = 450
    failed_season_rollover_state.season_claimed_tiers = {"1":true,"2":true}
    failed_season_rollover_state.season_bonus_chest_claimed = true
    var previous_season_start: int = int(failed_season_rollover_state.season_start_timestamp)
    if DirAccess.make_dir_absolute(time_failure_temp_absolute) != OK:
        _fail("Could not create the save-path collision for season rollover test")
        return
    var rollover_succeeded: bool = failed_season_rollover_state._reset_season_if_needed(now_timestamp)
    if rollover_succeeded or failed_season_rollover_state.season_number != 3 or failed_season_rollover_state.season_start_timestamp != previous_season_start or failed_season_rollover_state.season_points != 450 or not bool(failed_season_rollover_state.season_claimed_tiers.get("1", false)) or not bool(failed_season_rollover_state.season_bonus_chest_claimed) or not failed_season_rollover_state.save_recovery_blocked:
        _fail("Failed season rollover discarded existing season progress")
        return
    failed_season_rollover_state.free()
    if DirAccess.remove_absolute(time_failure_temp_absolute) != OK:
        _fail("Could not remove the temporary save-path collision after season rollover test")
        return

    # A completed-set mission reports its own unavailable reason, not the ad-SDK reason.
"""
replace_once("tests/save_recovery_test.gd", """    # A completed-set mission reports its own unavailable reason, not the ad-SDK reason.
""", insert_tests)

replace_once("tests/save_recovery_test.gd", """    print("NEXORA tests passed: save recovery, v4/v5/v6/v7 migrations, unified Spell Bastion campaign, between-wave preparation, shared wave progression, combat upgrade locks, spell chaining, fortress upgrades, shield/core damage, and Cat Squadron removal, cosmetic shop pricing and persistence, cosmetic equipping/reset, pull pity, independent chest odds, legendary chest gem spending, season bonus chest claims, card sets, six active offline daily missions, 14-day season rollover, and published probabilities.")
""", """    print("NEXORA tests passed: save recovery, transactional rewards, energy regeneration rollback, daily reset rollback, season rollover rollback, v4/v5/v6/v7 migrations, unified Spell Bastion campaign, between-wave preparation, shared wave progression, combat upgrade locks, spell chaining, fortress upgrades, shield/core damage, and Cat Squadron removal, cosmetic shop pricing and persistence, cosmetic equipping/reset, pull pity, independent chest odds, legendary chest gem spending, season bonus chest claims, card sets, six active offline daily missions, 14-day season rollover, and published probabilities.")
""")

replace_once("project.godot", 'config/version="0.9.1"', 'config/version="0.9.2"')
replace_once("export_presets.cfg", 'export_path="build/NEXORA-Android-v0.9.1.apk"', 'export_path="build/NEXORA-Android-v0.9.2.apk"')
replace_once("export_presets.cfg", "version/code=17", "version/code=18")
replace_once("export_presets.cfg", 'version/name="0.9.1"', 'version/name="0.9.2"')

(root / "README.md").write_text("""# NEXORA — نيكسورا: عوالم متحدة | v0.9.2

NEXORA is a mobile-first, Arabic-first fantasy game with a local-first progression economy. This release hardens persistence for rewards, energy regeneration, daily resets and season rollover while retaining the existing summon, card collection, chest, mission, season, cosmetic shop and Spell Bastion campaign systems.

## Android build
- Godot: 4.3
- Package ID: com.nexora.worlds
- Display name: NEXORA
- Version: 0.9.2 (code 18)
- Architectures: ARMv7 and ARM64
- Internet permission: disabled

## Installation and save data
Progress is stored locally in the app sandbox with an atomic primary/temporary/backup save strategy. Failed state-changing saves now restore the in-memory values and block further progression until recovery. No cloud account is required for the current offline build.

## Safety
All rewards are virtual game items and currencies only. There are no cash prizes, betting, wagering or cash-out mechanics.
""", encoding="utf-8")

(root / "BUILD_STATUS.md").write_text("""# NEXORA v0.9.2 — Build Status

- Version: 0.9.2 / code 18
- Package ID: com.nexora.worlds
- Arabic-first UI and Android mobile viewport retained.
- Save-failure rollback now covers pulls, chests, mission claims, daily rewards, season rewards, energy regeneration, daily reset and season rollover.
- Added deterministic regression tests for failed energy, daily-reset and season-rollover writes.
- CI status is determined by the GitHub Actions run for this revision.
- No physical Android device installation test is claimed by CI.
- Release signing remains unconfigured; CI uses a temporary debug keystore.
""", encoding="utf-8")

(root / "CHANGELOG.md").write_text("""# Changelog

## 0.9.2 — Transaction-safe time progression
- Energy regeneration and energy timestamps roll back if the local save cannot be committed.
- Daily mission-counter resets restore their previous counters and claim history if persistence fails.
- Season initialization and rollover preserve the previous season state when persistence fails.
- Added deterministic regression tests for all three failure paths.
- Android version code 18.

## 0.9.1 — Transaction-safe local rewards
- Pulls, chests, daily missions, daily login and season reward claims roll back if the local save cannot be committed.
- Added deterministic save-failure regression coverage.
- Android version code 17.

## 0.9.0 — NEXORA: Worlds United
- Replaced Lucky Pull brand with NEXORA / نيكسورا: عوالم متحدة.
- Replaced the launcher icon and visual identity.
- Rebuilt the home experience as a world hub while retaining the earlier gameplay systems.
- Assigned Android package ID com.nexora.worlds.
- Version code 16.
""", encoding="utf-8")

(root / "APPLY_UPDATE.txt").write_text("""NEXORA v0.9.2 — Transaction-safe time progression

Godot 4.3 Android project. Package ID: com.nexora.worlds. Version code: 18.

This update preserves the existing local save schema and protects energy regeneration, daily resets and season rollover from uncommitted writes. If a save cannot be committed, in-memory state is restored and progression is blocked to protect existing data.
""", encoding="utf-8")

print("Applied NEXORA 0.9.2 transactional time-progression update.")
