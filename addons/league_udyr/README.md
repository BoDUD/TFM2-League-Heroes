# League Heroes: Udyr's stances (add-on)

Native add-on for **Udyr** in *League of Legends Heroes* (`league`). It replaces the main pack's Udyr with a copy
(`override/league_udyr.data_champion`, made by `make_override.py` from `tools/kit/build_udyr.py` with `native`) and adds
what the data cannot do:

- **Iron Mantle by health** (passive `league_udyr:mantle`): League's W is cast when Udyr is hurt. When his health falls
  under 50% (at most once every 12 s) he gets a shield of 70 + 40% attack for 4 s and his next two attacks heal him
  (the main pack's own healing attacks, `league_udyr_w2`); the jade shell shows while the shield holds. In the main pack
  his first ability every 12 s lays it instead.
- **Whole-body stances** (`src/view.rs`): in the Bear, Ram or Phoenix stance he also stands, runs, flinches and falls in
  that stance (`q_idle`, `e_run`, `r_dead` ...), the way league_gnar shows Mega Gnar. Without the add-on only his attacks
  and casts show the stance.

The numbers are the main pack's parameter table (`w_hp`, `w_icd`, `w_sh`, `w_sh_r`, `w_sh_t`, `w_t`); `make_override.py`
checks the main pack is built from the same table and the tests check the copy carries them.

Log: `%APPDATA%\TeamSamoyed\TeamfightManager2\data\league_udyr.log` (rewritten at every game start, the previous one kept
as `.prev.log`): `MANTLE` lines and the display handler's stance counts.

Build and test: `cargo test -p league_udyr`; it ships inside the `league_addons` bundle (`league_addons/assemble.py`).
