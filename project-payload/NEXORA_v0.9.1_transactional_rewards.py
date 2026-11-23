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

replace_once("scripts/game_state.gd", "const SAVE_VERSION := 9\n", """const SAVE_VERSION := 9
const TRANSACTIONAL_SAVE_FIELDS := [
    "coins", "gems", "xp", "level", "energy", "starter_pulls",
    "normal_chests", "season_chests", "pity_counter", "total_pulls",
    "cards", "completed_sets", "unlocked_cosmetics", "owned_shop_cosmetics",
    "active_cosmetics", "claimed_daily", "daily_streak", "last_daily_date",
    "last_energy_timestamp", "daily_pull_count", "daily_chest_count",
    "daily_card_count", "daily_completed_sets", "daily_missions_claimed",
    "last_reset_date", "season_number", "season_start_timestamp", "season_points",
    "season_claimed_tiers", "season_bonus_chest_claimed", "arcade"
]
""")

replace_once("scripts/game_state.gd", "func claim_season_reward(tier: int) -> Dictionary:\n", """func _capture_save_snapshot() -> Dictionary:
    var snapshot: Dictionary = {}
    for field_name in TRANSACTIONAL_SAVE_FIELDS:
        var value: Variant = get(field_name)
        if typeof(value) == TYPE_DICTIONARY or typeof(value) == TYPE_ARRAY:
            snapshot[field_name] = value.duplicate(true)
        else:
            snapshot[field_name] = value
    return snapshot

func _restore_save_snapshot(snapshot: Dictionary) -> void:
    for field_name in snapshot.keys():
        set(str(field_name), snapshot[field_name])

func claim_season_reward(tier: int) -> Dictionary:
""")

replace_once("scripts/game_state.gd", "    var reward_data: Dictionary = info.reward\n    var amount := maxi(0, int(reward_data.get(\"amount\", 0)))\n", "    var snapshot := _capture_save_snapshot()\n    var reward_data: Dictionary = info.reward\n    var amount := maxi(0, int(reward_data.get(\"amount\", 0)))\n")
replace_once("scripts/game_state.gd", """    var reward := reward_data.duplicate(true)
    save_game()
    changed.emit()
    return {"ok":true,"reward":reward,"tier":tier}
""", """    var reward := reward_data.duplicate(true)
    if not save_game():
        _restore_save_snapshot(snapshot)
        return {"ok":false,"message":save_warning}
    changed.emit()
    return {"ok":true,"reward":reward,"tier":tier}
""")

replace_once("scripts/game_state.gd", """    if not can_pull():
        return {"ok":false, "message":"انتهت السحبات المتاحة حالياً"}
    if starter_pulls > 0:
""", """    if not can_pull():
        return {"ok":false, "message":"انتهت السحبات المتاحة حالياً"}
    _reset_season_if_needed()
    if save_recovery_blocked:
        return {"ok":false,"message":save_warning}
    var snapshot := _capture_save_snapshot()
    if starter_pulls > 0:
""")
replace_once("scripts/game_state.gd", """    _grant_xp(10)
    save_game()
    pull_result.emit(reward)
""", """    _grant_xp(10)
    if not save_game():
        _restore_save_snapshot(snapshot)
        return {"ok":false,"message":save_warning}
    pull_result.emit(reward)
""")

replace_once("scripts/game_state.gd", """    if save_recovery_blocked or claimed_daily:
        return false
    var today := _today()
""", """    if save_recovery_blocked or claimed_daily:
        return false
    _reset_season_if_needed()
    if save_recovery_blocked:
        return false
    var snapshot := _capture_save_snapshot()
    var today := _today()
""")
replace_once("scripts/game_state.gd", """    _add_season_points(10)
    save_game()
    changed.emit()
    return true
""", """    _add_season_points(10)
    if not save_game():
        _restore_save_snapshot(snapshot)
        return false
    changed.emit()
    return true
""")

replace_once("scripts/game_state.gd", """    if not bool(info.ready):
        return {"ok":false,"message":"أكمل المهمة أولاً لتحصل على المكافأة"}
    var reward: Dictionary = {}
""", """    if not bool(info.ready):
        return {"ok":false,"message":"أكمل المهمة أولاً لتحصل على المكافأة"}
    _reset_season_if_needed()
    if save_recovery_blocked:
        return {"ok":false,"message":save_warning}
    var snapshot := _capture_save_snapshot()
    var reward: Dictionary = {}
""")
replace_once("scripts/game_state.gd", """    daily_missions_claimed[mission_id] = true
    _add_season_points(10)
    save_game()
    changed.emit()
    return {"ok":true,"reward":reward}
""", """    daily_missions_claimed[mission_id] = true
    _add_season_points(10)
    if not save_game():
        _restore_save_snapshot(snapshot)
        return {"ok":false,"message":save_warning}
    changed.emit()
    return {"ok":true,"reward":reward}
""")

replace_once("scripts/game_state.gd", """    if coins < cost_coins or gems < cost_gems:
        return {"ok":false,"message":"العملة المطلوبة غير كافية"}

    if use_normal_inventory:
""", """    if coins < cost_coins or gems < cost_gems:
        return {"ok":false,"message":"العملة المطلوبة غير كافية"}
    _reset_season_if_needed()
    if save_recovery_blocked:
        return {"ok":false,"message":save_warning}
    var snapshot := _capture_save_snapshot()

    if use_normal_inventory:
""")
replace_once("scripts/game_state.gd", """    _add_season_points(5)
    _grant_xp(20)
    save_game()
    changed.emit()
    return {"ok":true,"reward":reward,"free":cost_coins == 0 and cost_gems == 0,"kind":kind}
""", """    _add_season_points(5)
    _grant_xp(20)
    if not save_game():
        _restore_save_snapshot(snapshot)
        return {"ok":false,"message":save_warning}
    changed.emit()
    return {"ok":true,"reward":reward,"free":cost_coins == 0 and cost_gems == 0,"kind":kind}
""")

test_block = """    chest_state.free()

    # Reward transactions must roll back in-memory state if the atomic save cannot be opened.
    print("TEST_MARKER_8A: Pull, chest, daily reward and mission claims roll back when persistence fails.")
    if not _clear_test_saves():
        _fail("Could not reset transactional save failure tests")
        return
    var failure_temp_absolute := ProjectSettings.globalize_path(TEMP_SAVE_PATH)
    var failed_pull_state = state_script.new()
    failed_pull_state.last_reset_date = Time.get_date_string_from_system()
    failed_pull_state.last_energy_timestamp = int(Time.get_unix_time_from_system())
    failed_pull_state.season_start_timestamp = int(Time.get_unix_time_from_system())
    failed_pull_state.starter_pulls = 1
    failed_pull_state.coins = 27
    failed_pull_state.pity_counter = 12
    if DirAccess.make_dir_absolute(failure_temp_absolute) != OK:
        _fail("Could not create the save-path collision used by the failure test")
        return
    var failed_pull: Dictionary = failed_pull_state.pull()
    if bool(failed_pull.get("ok", false)) or failed_pull_state.starter_pulls != 1 or failed_pull_state.total_pulls != 0 or failed_pull_state.pity_counter != 12 or failed_pull_state.coins != 27 or not failed_pull_state.save_recovery_blocked:
        _fail("Failed pull was reported or retained uncommitted reward state")
        return
    failed_pull_state.free()
    if DirAccess.remove_absolute(failure_temp_absolute) != OK:
        _fail("Could not remove the temporary save-path collision after pull test")
        return

    var failed_chest_state = state_script.new()
    failed_chest_state.last_reset_date = Time.get_date_string_from_system()
    failed_chest_state.last_energy_timestamp = int(Time.get_unix_time_from_system())
    failed_chest_state.season_start_timestamp = int(Time.get_unix_time_from_system())
    failed_chest_state.normal_chests = 1
    failed_chest_state.coins = 240
    failed_chest_state.daily_chest_count = 2
    if DirAccess.make_dir_absolute(failure_temp_absolute) != OK:
        _fail("Could not create the save-path collision for chest test")
        return
    var failed_chest: Dictionary = failed_chest_state.open_chest("normal")
    if bool(failed_chest.get("ok", false)) or failed_chest_state.normal_chests != 1 or failed_chest_state.coins != 240 or failed_chest_state.daily_chest_count != 2 or not failed_chest_state.save_recovery_blocked:
        _fail("Failed chest opening consumed inventory or retained an uncommitted reward")
        return
    failed_chest_state.free()
    if DirAccess.remove_absolute(failure_temp_absolute) != OK:
        _fail("Could not remove the temporary save-path collision after chest test")
        return

    var failed_mission_state = state_script.new()
    failed_mission_state.last_reset_date = Time.get_date_string_from_system()
    failed_mission_state.last_energy_timestamp = int(Time.get_unix_time_from_system())
    failed_mission_state.season_start_timestamp = int(Time.get_unix_time_from_system())
    failed_mission_state.daily_pull_count = 10
    failed_mission_state.coins = 15
    if DirAccess.make_dir_absolute(failure_temp_absolute) != OK:
        _fail("Could not create the save-path collision for mission test")
        return
    var failed_mission: Dictionary = failed_mission_state.claim_daily_mission("pulls_10")
    if bool(failed_mission.get("ok", false)) or bool(failed_mission_state.daily_missions_claimed.get("pulls_10", false)) or failed_mission_state.coins != 15 or not failed_mission_state.save_recovery_blocked:
        _fail("Failed mission claim was marked as collected without a durable save")
        return
    failed_mission_state.free()
    if DirAccess.remove_absolute(failure_temp_absolute) != OK:
        _fail("Could not remove the temporary save-path collision after mission test")
        return

    var failed_daily_state = state_script.new()
    failed_daily_state.last_reset_date = Time.get_date_string_from_system()
    failed_daily_state.last_energy_timestamp = int(Time.get_unix_time_from_system())
    failed_daily_state.season_start_timestamp = int(Time.get_unix_time_from_system())
    failed_daily_state.starter_pulls = 2
    failed_daily_state.normal_chests = 1
    if DirAccess.make_dir_absolute(failure_temp_absolute) != OK:
        _fail("Could not create the save-path collision for daily reward test")
        return
    var failed_daily_claim: bool = failed_daily_state.claim_daily_reward()
    if failed_daily_claim or failed_daily_state.claimed_daily or failed_daily_state.starter_pulls != 2 or failed_daily_state.normal_chests != 1 or not failed_daily_state.save_recovery_blocked:
        _fail("Failed daily reward claim was not rolled back")
        return
    failed_daily_state.free()
    if DirAccess.remove_absolute(failure_temp_absolute) != OK:
        _fail("Could not remove the temporary save-path collision after daily reward test")
        return

    var failed_season_state = state_script.new()
    failed_season_state.last_reset_date = Time.get_date_string_from_system()
    failed_season_state.last_energy_timestamp = int(Time.get_unix_time_from_system())
    failed_season_state.season_start_timestamp = int(Time.get_unix_time_from_system())
    failed_season_state.season_points = 100
    failed_season_state.coins = 9
    if DirAccess.make_dir_absolute(failure_temp_absolute) != OK:
        _fail("Could not create the save-path collision for season reward test")
        return
    var failed_season_claim: Dictionary = failed_season_state.claim_season_reward(1)
    if bool(failed_season_claim.get("ok", false)) or bool(failed_season_state.season_claimed_tiers.get("1", false)) or failed_season_state.coins != 9 or failed_season_state.season_points != 100 or not failed_season_state.save_recovery_blocked:
        _fail("Failed season reward claim was not rolled back")
        return
    failed_season_state.free()
    if DirAccess.remove_absolute(failure_temp_absolute) != OK:
        _fail("Could not remove the temporary save-path collision after season reward test")
        return

    # A completed-set mission reports its own unavailable reason, not the ad-SDK reason.
"""
replace_once("tests/save_recovery_test.gd", """    chest_state.free()

    # A completed-set mission reports its own unavailable reason, not the ad-SDK reason.
""", test_block)

replace_once("tests/save_recovery_test.gd", """func _clear_test_saves() -> bool:
    for path in [SAVE_PATH, BACKUP_SAVE_PATH, TEMP_SAVE_PATH]:
""", """func _clear_test_saves() -> bool:
    var temp_absolute := ProjectSettings.globalize_path(TEMP_SAVE_PATH)
    if DirAccess.dir_exists_absolute(temp_absolute):
        var directory_error := DirAccess.remove_absolute(temp_absolute)
        if directory_error != OK:
            return false
    for path in [SAVE_PATH, BACKUP_SAVE_PATH, TEMP_SAVE_PATH]:
""")

replace_once("scripts/main.gd", """    if state.claim_daily_reward():
        _show_message("وصلتك 5 سحبات إضافية وصندوق عادي مجاني. استمتع بجائزتك!")
    else:
        _show_message("تم استلام هدية اليوم بالفعل. عد غداً لهدية جديدة.")
""", """    if state.claim_daily_reward():
        _show_message("وصلتك 5 سحبات إضافية وصندوق عادي مجاني. استمتع بجائزتك!")
    elif state.save_recovery_blocked:
        _show_message(state.save_warning)
    else:
        _show_message("تم استلام هدية اليوم بالفعل. عد غداً لهدية جديدة.")
""")

replace_once("project.godot", 'config/version="0.9.0"', 'config/version="0.9.1"')
replace_once("export_presets.cfg", 'export_path="build/NEXORA-Android-v0.9.0.apk"', 'export_path="build/NEXORA-Android-v0.9.1.apk"')
replace_once("export_presets.cfg", "version/code=16", "version/code=17")
replace_once("export_presets.cfg", 'version/name="0.9.0"', 'version/name="0.9.1"')

(root / "README.md").write_text("""# NEXORA — نيكسورا: عوالم متحدة | v0.9.1

NEXORA is a mobile-first, Arabic-first fantasy game with a local-first progression economy. The current build keeps the existing summon, card collection, chest, daily mission, season, cosmetic shop and Spell Bastion campaign systems while strengthening reward persistence.

## Android build
- Godot: 4.3
- Package ID: com.nexora.worlds
- Display name: NEXORA
- Version: 0.9.1 (code 17)
- Architectures: ARMv7 and ARM64
- Internet permission: disabled

## Installation and save data
NEXORA installs alongside the previous Lucky Pull package. Progress is stored locally in the app sandbox with an atomic primary/temporary/backup save strategy. No cloud account is required for the current offline build.

## Safety
All rewards are virtual game items and currencies only. There are no cash prizes, betting, wagering or cash-out mechanics.
""", encoding="utf-8")

(root / "BUILD_STATUS.md").write_text("""# NEXORA v0.9.1 — Build Status

- Version: 0.9.1 / code 17
- Package ID: com.nexora.worlds
- Arabic-first UI and Android mobile viewport retained.
- Added rollback for pull, chest, daily mission, daily reward and season reward transactions when the local save cannot be committed.
- Added deterministic regression coverage that simulates a write failure by occupying the temporary-save path with a directory.
- Godot CI test, scene launch and Android export status: reported by the GitHub Actions run for this revision.
- No phone installation test has been performed for this version.
- Release signing remains unconfigured; CI uses a temporary debug keystore.
""", encoding="utf-8")

(root / "CHANGELOG.md").write_text("""# Changelog

## 0.9.1 — Transaction-safe local rewards
- Pulls now report failure and restore the pre-pull economy, energy, card inventory, pity and progression state when the local save cannot be committed.
- Chest openings roll back spent currency/inventory and uncommitted rewards on save failure.
- Daily mission, daily login and season reward claims no longer report success before a durable local save.
- Added deterministic save-failure regression tests for pulls, chests, missions and daily rewards.
- Android version code 17.

## 0.9.0 — NEXORA: Worlds United
- Replaced Lucky Pull brand with NEXORA / نيكسورا: عوالم متحدة.
- Replaced the launcher icon with a nexus artwork combining hero card, fortress, treasure and portal.
- Replaced the visual system with royal indigo, violet, cyan and gold.
- Rebuilt the home experience as a world hub with direct entry to all six modes.
- Unified labels and identity across hero summoning, card collection, tower defense, chests, missions, season and store.
- Assigned a new Android package ID so NEXORA installs alongside the previous game without removing it.
- Version code 16.

## 0.8.0
- Previous mobile-first redesign and unified Spell Bastion campaign.
""", encoding="utf-8")

(root / "APPLY_UPDATE.txt").write_text("""NEXORA v0.9.1 — Transaction-safe local rewards

This is a complete Godot 4.3 project. Open project.godot in Godot 4.3 and export the Android preset.

Package ID: com.nexora.worlds. Version code: 17. Existing Lucky Pull/NEXORA local data remains in its existing Android app sandbox; this update does not require cloud services.

Reward operations now roll back their in-memory changes and return a failure result if the atomic local save cannot be committed.
""", encoding="utf-8")

print("Applied NEXORA 0.9.1 transactional reward-save update.")
