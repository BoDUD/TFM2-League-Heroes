#!/usr/bin/env python3
"""Render League's spell VFX - the particle systems of a champion's skin bin, read from the local client - through
our game's camera, as true-colour frames (tools/lol/vfx_pixel.py turns them into effect frames).

    python tools/lol/vfx_render.py --list Lux [--grep Base_E]          # the skin's VFX systems
    python tools/lol/vfx_render.py --dump Lux Lux_Base_E_tar_nova      # one system's emitters, fields named
    python tools/lol/vfx_render.py --survey                            # every champion: the share of emitters drawn
    python tools/lol/vfx_pilot.py ...                                  # scenes of tools/lol/vfx_scenes.json -> frames

Reads (never writes) Champions/<Champ>.wad.client: data/characters/<champ>/skins/skin<N>.bin and the bins its PROP
header links (the character's own bin, the shared *_Multi_Skins_* bins), every VfxSystemDefinitionData in them,
their textures (.tex: DXT1 / DXT5 / BGRA8, pose_ref.read_tex) and static meshes (.scb). The renders show Riot's
art: keep them local, never commit them (like the pose renders and the extracted audio).

The particle model (what the emitter fields are taken to mean; League's own runtime is not public, every rule below
was read off the data and checked on the pilot spells' renders - Lux Q / E / R, Jinx W / R):
  - timing: an emitter starts `timeBeforeFirstEmission` after its system, emits for `lifetime` seconds (none: as
    long as the system lives) at `rate` particles a second, the first at once; `isSingleParticle` emits `rate`
    particles at once (a burst: the R beam's 45 streaks) and nothing after. A particle lives `particleLifetime` (none
    or <= 0: as long as its emitter); when its system is removed it lingers `particleLinger` at most. `disabled`
    emitters and ones whose `filtering` requires a skin keyword are left out.
  - values: Value* fields are a constant or keys over normalised time (birth* fields: the emitter's age over its
    lifetime; the others: the particle's age over its life), times a random factor per component drawn from the
    field's probability tables (keyTimes -> keyValues: the factor is the table read at a uniform random point).
  - frames: a standing system (an AoE, a hit, Lux R's beam) has local y up and z its facing; a flying missile's
    (Play frame "missile": Lux Q, Jinx W / R) has y its flight and z up - Lux Q's helix trails turn about y, Jinx R's
    rocket mesh (nose +y) rolls about y and squashes along it, its quads' local XY plane lies flat.
  - place: the system's origin + emitterPosition + the spawn shape (VfxShapeLegacy: emitOffset turned by the
    emitRotationAngles about the emitRotationAxes, which turn birthVelocity too; a plain-offset shape; sphere / box /
    cylinder: a random point in it). bindWeight 1 keeps a particle with its emitter (a missile's glow), 0 leaves it
    where it was born (a trail). Motion: birthVelocity + velocity(t), birthAcceleration + worldAcceleration (world
    axes), birthDrag / drag as an exponential damping per axis, birthOrbitalVelocity (rad/s about the emitter's axes).
    Child systems (childParticleSetDefinition, through the skin's resource resolver) ride on their parent particle.
  - look: birthScale0 x scale0(t) is the quad's full size in units (Lux R's ground strips 2000-3050 long fit its 3400
    beam only so) and a mesh's scale factor (per axis; a ground-layer mesh takes x for all axes); birthColor x
    color(t); birthRotation0 + rotation0(t) + spin; texture with flipbook (texDiv, numFrames, frameRate, startFrame,
    isRandomStartFrame), UV offset / scroll / scale / rotation, textureMult (a second texture multiplied in with its
    own UV transform: Lux's rainbow tints), particleColorTexture (a colour ramp read along the life),
    paletteDefinition (a channel of the texture picks a colour in one row of a palette texture), alphaErosion.
  - primitives: none = a camera-facing quad (isDirectionOriented: stretched along its motion); ArbitraryQuad = a quad
    turned in 3D (its plane is local XY; R = Ry Rx Rz of birthRotation0, so (90, y, 0) lays it on the ground; a
    ground-layer quad of a standing system left upright is laid down with its yaw); Mesh = a .scb mesh; Ray = a
    camera-facing strip from the particle out along its turned up axis; Beam = a strip from the emitter to the
    scene's target point (texture profile across in u); CameraTrail / ArbitraryTrail = a strip through the emitter's
    particles in emission order (a point every step whatever the rate; texture along in u). PlanarProjection,
    AttachedMesh, skinned meshes (.skn) and distortion emitters (heat haze) are not drawn; force fields, soft
    particles, reflections and unit-size scaling are ignored (`--survey` counts them).
  - blend: 1 = alpha, 0 and 4 = additive (src.rgb x src.a added: Lux_Base_E_Glow's grey RGB outside its ring and
    Lux_Q_Shape's white RGB need the alpha), 2 = screen, 3 = opaque. On transparency the canvas keeps light
    (additive) and matter (alpha) apart for the pixel pass.
  - isGroundLayer particles are drawn before the rest (under them), then by `pass`, then far to near.

Camera: world X right, Y up, Z toward the viewer. A standing system's local z (its facing: Lux R's beam) is world +X,
local y is Y, local x is -Z; a missile's local y is +X and z is Y. Screen x = X*s, screen y = ground_px +
(Z sin(pitch) - Y cos(pitch)) * s (game px from the frame's centre, which is the anchor the game draws a view at);
pitch 90 is straight down (the picture of a projectile, which the game turns to its flight); our ground ellipses (Lux
E) are about 0.57 as tall as wide: pitch 35. s is game px per League unit, chosen per scene: from the kit for areas
and lines (Lux E's 26.5 px radius is League's 310, Lux R's 340 px is its 3400), at sprite scale (0.15-0.2, our heroes'
size) for projectiles and hits. A scene's `warp` maps our tag's time to League's (Lux R's 1 s charge in our 0.47 s)
and a play's `speed` runs one system faster (Lux E's 5 s field in our 1 s).
"""
import argparse
import math
import os
import struct
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import anim_graph as AG  # noqa: E402
import pose_ref as P  # noqa: E402
from riot import Wad  # noqa: E402

LOL = r"D:\WeGameApps\lol"

# ----------------------------------------------------------------------------- bin names
# FNV-1a of the field and class names the VFX data uses (names found by hashing candidates against the bins).
VFX_FIELDS = """complexEmitterDefinitionData simpleEmitterDefinitionData particleName particlePath flags
visibilityRadius assetCategory emitterName rate particleLifetime lifetime isSingleParticle timeBeforeFirstEmission
particleLinger emitterLinger bindWeight birthColor color birthScale0 scale0 birthRotation0 rotation0 birthVelocity
velocity birthAcceleration birthDrag drag worldAcceleration texture texDiv frameRate numFrames startFrame
isRandomStartFrame blendMode primitive birthUvOffset birthUvScrollRate birthUvRotateRate uvScrollRate uvRotation
uvScale uvScrollClamp isUniformScale emitterPosition birthOrbitalVelocity birthRotationalVelocity0
rotationalVelocity0 disabled alphaRef particleColorTexture colorLookUpTypeX colorLookUpTypeY colorLookUpScales
colorLookUpOffsets particleIsLocalOrientation isLocalOrientation isDirectionOriented directionVelocityScale
directionVelocityMinScale childParticleSetDefinition fieldCollectionDefinition isGroundLayer pass importance
miscRenderFlags colorRenderFlags useNavmeshMask spawnShape flexShapeDefinition filtering keywordsRequired
keywordsExcluded paletteDefinition paletteTexture paletteCount paletteSelector textureMult uvScaleMult
birthUvOffsetMult birthUvScrollRateMult particleIntegratedUvScrollMult particleIntegratedUvRotateMult
emitterUvScrollRateMult texAddressModeMult texAddressModeBase particleUvScrollRate particleUvRotateRate
alphaErosionDefinition erosionDriveCurve erosionMapName erosionMapChannelMixer erosionSliceWidth erosionFeatherIn
erosionFeatherOut erosionMapAddressMode distortionDefinition distortion distortionMode normalMapTexture
reflectionDefinition softParticleParams beginIn deltaIn beginOut deltaOut emitOffset emitRotationAngles
emitRotationAxes radius height size keyTimes keyValues singleValue constantValue dynamics times values
probabilityTables mMesh mSimpleMeshName mMeshName mMeshSkeletonName mAnimationName mBeam mTrail mProjection mFading
mYRange mMode mCutoff mBirthTilingSize mSegments mSmoothingMode mMaxAddedPerFrame mLocalSpaceSourceOffset
mLocalSpaceTargetOffset childrenIdentifiers effectKey effectName boneToSpawnAt fieldNoiseDefinitions axisFraction
fieldAccelerationDefinitions fieldDragDefinitions fieldOrbitalDefinitions fieldAttractionDefinitions acceleration
isLocalSpace strength position frequency velocityDelta direction soundOnCreateDefault soundPersistentDefault
voiceOverOnCreateDefault voiceOverPersistentDefault overrideScaleCap materialOverrideDefinitions audio
scaleBirthScaleByBoundObjectSize scaleEmitOffsetByBoundObjectSize scaleEmitOffsetByBoundObjectRadius
isRotationEnabled offsetLifetimeScaling modulationFactor depthBiasFactors falloffTexture""".split()
VFX_CLASSES = """VfxSystemDefinitionData VfxEmitterDefinitionData ValueFloat ValueVector2 ValueVector3 ValueColor
IntegratedValueFloat IntegratedValueVector2 IntegratedValueVector3 VfxAnimatedFloatVariableData
VfxAnimatedVector2fVariableData VfxAnimatedVector3fVariableData VfxAnimatedColorVariableData VfxProbabilityTableData
VfxPrimitiveMesh VfxPrimitiveArbitraryQuad VfxPrimitiveCameraUnitQuad VfxPrimitiveRay VfxPrimitiveCameraTrail
VfxPrimitiveArbitraryTrail VfxPrimitiveBeam VfxPrimitivePlanarProjection VfxPrimitiveAttachedMesh
VfxPrimitiveCameraQuad VfxPrimitiveCameraSegmentBeam VfxMeshDefinitionData VfxSoftParticleDefinitionData
VfxFieldCollectionDefinitionData VfxFieldAccelerationDefinitionData VfxFieldDragDefinitionData
VfxFieldNoiseDefinitionData VfxFieldOrbitalDefinitionData VfxFieldAttractionDefinitionData VfxTrailDefinitionData
VfxBeamDefinitionData VfxDistortionDefinitionData VfxChildParticleSetDefinitionData VfxChildIdentifier
VfxAlphaErosionDefinitionData VfxShapeLegacy VfxShapeBox VfxShapeSphere VfxShapeCylinder VfxFlexShapeDefinitionData
VfxEmitterFiltering VfxPaletteDefinitionData VfxTextureMultDefinitionData VfxReflectionDefinitionData
VfxProjectionDefinitionData VfxEmitterAudio VfxMaterialOverrideDefinitionData""".split()
for _n in VFX_FIELDS + VFX_CLASSES:
    AG.NAMES[AG.fnv1a(_n)] = _n
# Unnamed so far: the spawn-shape class holding a plain emitOffset (0xee39916f, read as a fixed offset), the palette's
# channel mixer (0x143f06d1, which channel of the texture picks the palette colour) and a flag on trails / meshes
# (0x3c91cebd).
AG.NAMES[0xee39916f] = "VfxShapeOffset"
AG.NAMES[0x143f06d1] = "paletteChannel"


def parse_prop_keyed(b):
    """[(entry key, class, fields)] of a PROP bin (anim_graph.parse_prop without dropping the keys)."""
    r = AG.Reader(b)
    r.o = 4
    if b[:4] == b"PTCH":
        r.o = 20
    elif b[:4] != b"PROP":
        raise ValueError("not a PROP bin")
    version = r.u("I")
    if version >= 2:
        for _ in range(r.u("I")):
            r.string()
    types = [r.u("I") for _ in range(r.u("I"))]
    out = []
    for t in types:
        size = r.u("I")
        end = r.o + size
        key = r.u("I")
        fields = {}
        for _ in range(r.u("H")):
            name, ft = r.u("IB")
            fields[AG.NAMES.get(name, f"#{name:08x}")] = AG.value(r, ft)
        r.o = end
        out.append((key, AG.NAMES.get(t, f"#{t:08x}"), fields))
    return out


def prop_links(b):
    r = AG.Reader(b)
    r.o = 4 if b[:4] == b"PROP" else 20
    version = r.u("I")
    return [r.string() for _ in range(r.u("I"))] if version >= 2 else []


# ----------------------------------------------------------------------------- the client's files
class Vfx:
    """A champion's VFX systems (by name and by entry key), with its textures and meshes."""

    def __init__(self, champ, skin=0, lol=LOL):
        self.champ = champ
        self.wad = Wad(os.path.join(lol, "Game", "DATA", "FINAL", "Champions", f"{champ}.wad.client"))
        raw = self.wad.read_path(f"data/characters/{champ.lower()}/skins/skin{skin}.bin")
        entries = parse_prop_keyed(raw)
        for link in prop_links(raw):
            try:
                entries += parse_prop_keyed(self.wad.read_path(link))
            except KeyError:
                pass
        self.systems, self.by_key = {}, {}
        for key, cls, f in entries:
            if cls == "VfxSystemDefinitionData":
                self.systems[str(f.get("particleName", key))] = f
                self.by_key[key] = f
        # the skin's resource resolver (a map of keys -> system entries): child particles name systems through it
        self.resolver = {}
        for key, cls, f in entries:
            for v in f.values():
                if isinstance(v, list) and v and all(isinstance(x, tuple) and len(x) == 2 for x in v):
                    for a, b in v:
                        if isinstance(b, int) and b in self.by_key:
                            self.resolver[a] = self.by_key[b]
        self._tex, self._mesh = {}, {}

    def child(self, key):
        """the system a VfxChildIdentifier's effectKey names (through the resolver, else an entry key)."""
        return self.resolver.get(key) or self.by_key.get(key)

    def system(self, name):
        for n, f in self.systems.items():
            if n.lower() == name.lower():
                return f
        raise KeyError(f"{self.champ}: no VFX system {name}")

    def read(self, path):
        return self.wad.read_path(path.lower())

    def texture(self, path):
        """float32 RGBA [0, 1], (h, w, 4); None when the file is not in the WAD."""
        if not path:
            return None
        if path not in self._tex:
            try:
                im = P.read_tex(self.read(path))
                self._tex[path] = np.asarray(im.convert("RGBA"), np.float32) / 255.0
            except (KeyError, OSError, ValueError):
                self._tex[path] = None
        return self._tex[path]

    def mesh(self, path):
        """(vertices (n, 3), triangles (m, 3), uvs per triangle corner (m, 3, 2)) of a .scb; None if absent."""
        if path not in self._mesh:
            try:
                self._mesh[path] = read_scb(self.read(path))
            except (KeyError, ValueError, struct.error):
                self._mesh[path] = None
        return self._mesh[path]


def read_scb(b):
    """Riot's static mesh "r3d2Mesh" (3.x): vertices, faces with a material name and per-corner UVs."""
    if b[:8] != b"r3d2Mesh":
        raise ValueError("not an SCB")
    major, minor = struct.unpack_from("<HH", b, 8)
    vc, fc, _flags = struct.unpack_from("<III", b, 140)
    o = 176                                      # name (128) + counts + flags + bounding box (24)
    colours = 0
    if major == 3 and minor == 2:
        colours = struct.unpack_from("<I", b, o)[0]
        o += 4
    verts = np.frombuffer(b, "<f4", vc * 3, o).reshape(vc, 3).astype(np.float64)
    o += 12 * vc
    if colours == 1:
        o += 4 * vc
    o += 12                                      # central point
    tris = np.zeros((fc, 3), np.int64)
    uvs = np.zeros((fc, 3, 2))
    for i in range(fc):
        a, b_, c = struct.unpack_from("<3I", b, o)
        u = struct.unpack_from("<3f", b, o + 76)
        v = struct.unpack_from("<3f", b, o + 88)
        tris[i] = (a, b_, c)
        uvs[i, :, 0], uvs[i, :, 1] = u, v
        o += 100
    return verts, tris, uvs


# ----------------------------------------------------------------------------- values
def _vec(x, n):
    if x is None:
        return None
    a = np.atleast_1d(np.asarray(x, np.float64)).ravel()
    if len(a) < n:
        a = np.concatenate([a, np.zeros(n - len(a))])
    return a[:n]


class Curve:
    """A Value* / IntegratedValue* field (or a plain number / vector): a constant, or keys over normalised time,
    with probability tables giving a random factor per component."""

    def __init__(self, d, default):
        default = np.atleast_1d(np.asarray(default, np.float64))
        self.n = len(default)
        self.const = default.copy()
        self.times = None
        self.tables = []
        if d is None:
            return
        if not isinstance(d, dict):
            self.const = _vec(d, self.n)
            return
        if d.get("constantValue") is not None:
            self.const = _vec(d["constantValue"], self.n)
        dyn = d.get("dynamics")
        if isinstance(dyn, dict):
            t, v = dyn.get("times"), dyn.get("values")
            if t and v:
                self.times = np.asarray(t, np.float64)
                self.values = np.array([_vec(x, self.n) for x in v])
                order = np.argsort(self.times, kind="stable")
                self.times, self.values = self.times[order], self.values[order]
            for tab in dyn.get("probabilityTables") or []:
                tab = tab or {}
                kv = tab.get("keyValues")
                kt = tab.get("keyTimes")
                if kv:
                    kt = list(kt) if kt and len(kt) == len(kv) else list(np.linspace(0, 1, len(kv)))
                    self.tables.append((np.asarray(kt, np.float64), np.asarray(kv, np.float64)))
                elif tab.get("singleValue") is not None:
                    self.tables.append((np.zeros(1), np.asarray([tab["singleValue"]], np.float64)))
                else:
                    self.tables.append(None)

    def at(self, t):
        """the value at normalised time t (a number)."""
        if self.times is None:
            return self.const.copy()
        if len(self.times) == 1:
            return self.values[0].copy()
        return np.array([np.interp(t, self.times, self.values[:, i]) for i in range(self.n)])

    def factor(self, rng):
        f = np.ones(self.n)
        for i, tab in enumerate(self.tables[:self.n]):
            if tab is None:
                continue
            kt, kv = tab
            f[i] = kv[0] if len(kv) == 1 else np.interp(rng.random(), kt, kv)
        return f

    def birth(self, t, rng):
        return self.at(t) * self.factor(rng)

    @property
    def animated(self):
        return self.times is not None and len(self.times) > 1


def rot_matrix(deg):
    """Euler angles (degrees) about x, y, z -> R = Ry Rx Rz (a quad: turned in its plane, tilted, then spun)."""
    rx, ry, rz = np.radians(deg[:3])
    cx, sx, cy, sy, cz, sz = math.cos(rx), math.sin(rx), math.cos(ry), math.sin(ry), math.cos(rz), math.sin(rz)
    Rx = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]])
    Ry = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]])
    Rz = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]])
    return Ry @ Rx @ Rz


def axis_angle(axis, deg):
    a = np.asarray(axis, np.float64)
    n = np.linalg.norm(a)
    if n < 1e-9:
        return np.eye(3)
    x, y, z = a / n
    t = math.radians(deg)
    c, s, C = math.cos(t), math.sin(t), 1 - math.cos(t)
    return np.array([[c + x * x * C, x * y * C - z * s, x * z * C + y * s],
                     [y * x * C + z * s, c + y * y * C, y * z * C - x * s],
                     [z * x * C - y * s, z * y * C + x * s, c + z * z * C]])


# ----------------------------------------------------------------------------- emitters
BLEND_ADD, BLEND_ALPHA, BLEND_SCREEN, BLEND_OPAQUE = "add", "alpha", "screen", "opaque"
BLENDS = {0: BLEND_ADD, 1: BLEND_ALPHA, 2: BLEND_SCREEN, 3: BLEND_OPAQUE, 4: BLEND_ADD}
DRAWN = {"Billboard", "ArbitraryQuad", "Mesh", "Ray", "Beam", "CameraTrail", "ArbitraryTrail"}


class Emitter:
    def __init__(self, e, vfx):
        self.e = e
        self.name = str(e.get("emitterName", "?"))
        prim = e.get("primitive") or {}
        self.prim = str(prim.get("__class", "VfxPrimitiveCameraUnitQuad")).replace("VfxPrimitive", "")
        if self.prim in ("CameraUnitQuad", "CameraQuad"):
            self.prim = "Billboard"
        self.prim_data = prim
        self.single = bool(e.get("isSingleParticle"))
        self.rate = Curve(e.get("rate"), 0.0)
        self.life = e.get("lifetime")                              # None: as long as the system
        self.t0 = float(e.get("timeBeforeFirstEmission") or 0.0)
        self.plife = Curve(e.get("particleLifetime"), -1.0)
        self.linger = float(e.get("particleLinger") or 0.0)
        self.bind = Curve(e.get("bindWeight"), 0.0)
        self.ground = bool(e.get("isGroundLayer"))
        self.blend = BLENDS.get(int(e.get("blendMode") or 0), BLEND_ADD)
        self.pass_ = int(e.get("pass") or 0)
        self.uniform = bool(e.get("isUniformScale"))
        self.bscale = Curve(e.get("birthScale0"), (10.0, 10.0, 10.0))
        self.scale = Curve(e.get("scale0"), (1.0, 1.0, 1.0))
        self.bcolor = Curve(e.get("birthColor"), (1.0, 1.0, 1.0, 1.0))
        self.color = Curve(e.get("color"), (1.0, 1.0, 1.0, 1.0))
        self.bvel = Curve(e.get("birthVelocity"), (0.0, 0.0, 0.0))
        self.vel = Curve(e.get("velocity"), (0.0, 0.0, 0.0))
        self.bacc = Curve(e.get("birthAcceleration"), (0.0, 0.0, 0.0))
        self.wacc = Curve(e.get("worldAcceleration"), (0.0, 0.0, 0.0))
        self.bdrag = Curve(e.get("birthDrag"), (0.0, 0.0, 0.0))
        self.drag = Curve(e.get("drag"), (0.0, 0.0, 0.0))
        self.brot = Curve(e.get("birthRotation0"), (0.0, 0.0, 0.0))
        self.rot = Curve(e.get("rotation0"), (0.0, 0.0, 0.0))
        self.brotv = Curve(e.get("birthRotationalVelocity0"), (0.0, 0.0, 0.0))
        self.rotv = Curve(e.get("rotationalVelocity0"), (0.0, 0.0, 0.0))
        self.orbit = Curve(e.get("birthOrbitalVelocity"), (0.0, 0.0, 0.0))
        self.epos = Curve(e.get("emitterPosition"), (0.0, 0.0, 0.0))
        self.dir_oriented = bool(e.get("isDirectionOriented"))
        self.dir_scale = float(e.get("directionVelocityScale") or 0.0)
        self.dir_min = float(e.get("directionVelocityMinScale") or 0.0)
        self.shape = e.get("spawnShape") or {}
        # texture and its UVs
        self.tex = vfx.texture(e.get("texture"))
        td = e.get("texDiv")
        self.div = (max(1, int(round(td[0]))), max(1, int(round(td[1])))) if td else (1, 1)
        self.nframes = int(e.get("numFrames") or 0)
        self.frame_rate = float(e.get("frameRate") or 0.0)
        self.start_frame = int(e.get("startFrame") or 0)
        self.random_frame = bool(e.get("isRandomStartFrame"))
        self.uv_off = Curve(e.get("birthUvOffset"), (0.0, 0.0))
        self.uv_scroll = Curve(e.get("birthUvScrollRate"), (0.0, 0.0))
        self.uv_pscroll = Curve(e.get("particleUvScrollRate"), (0.0, 0.0))
        self.uv_scale = Curve(e.get("uvScale"), (1.0, 1.0))
        self.uv_rot = Curve(e.get("uvRotation"), 0.0)
        self.uv_clamp = bool(e.get("uvScrollClamp"))
        self.mult = None
        tm = e.get("textureMult")
        if isinstance(tm, dict) and vfx.texture(tm.get("textureMult")) is not None:
            self.mult = dict(tex=vfx.texture(tm.get("textureMult")),
                             scale=Curve(tm.get("uvScaleMult"), (1.0, 1.0)),
                             off=Curve(tm.get("birthUvOffsetMult"), (0.0, 0.0)),
                             scroll=Curve(tm.get("birthUvScrollRateMult"), (0.0, 0.0)),
                             pscroll=Curve(tm.get("particleIntegratedUvScrollMult"), (0.0, 0.0)),
                             escroll=_vec(tm.get("emitterUvScrollRateMult"), 2))
        self.ramp = vfx.texture(e.get("particleColorTexture"))
        self.ramp_scale = _vec(e.get("colorLookUpScales"), 2) if e.get("colorLookUpScales") else np.ones(2)
        self.ramp_off = _vec(e.get("colorLookUpOffsets"), 2) if e.get("colorLookUpOffsets") else np.zeros(2)
        self.ramp_type_y = int(e.get("colorLookUpTypeY") or 0)
        self.palette = None
        pd = e.get("paletteDefinition")
        if isinstance(pd, dict) and vfx.texture(pd.get("paletteTexture")) is not None:
            ch = _vec(pd.get("paletteChannel", {}).get("constantValue") if isinstance(pd.get("paletteChannel"), dict)
                      else None, 4)
            self.palette = dict(tex=vfx.texture(pd.get("paletteTexture")),
                                count=max(1, int(pd.get("paletteCount") or 1)),
                                sel=Curve(pd.get("paletteSelector"), (0.0, 0.0, 0.0)),
                                channel=ch if ch is not None and ch.any() else np.array([1.0, 0, 0, 0]))
        self.erosion = None
        er = e.get("alphaErosionDefinition")
        if isinstance(er, dict) and vfx.texture(er.get("erosionMapName")) is not None:
            ch = er.get("erosionMapChannelMixer")
            ch = (_vec(ch.get("constantValue"), 4) if isinstance(ch, dict) and ch.get("constantValue")
                  else np.array([0, 0, 0, 1.0]))
            self.erosion = dict(tex=vfx.texture(er.get("erosionMapName")),
                                drive=Curve(er.get("erosionDriveCurve"), 0.0),
                                width=float(er.get("erosionSliceWidth") or 0.1), channel=ch)
        self.children = []
        cp = e.get("childParticleSetDefinition")
        if isinstance(cp, dict) and not cp.get("boneToSpawnAt"):
            for ci in cp.get("childrenIdentifiers") or []:
                sysdef = vfx.child((ci or {}).get("effectKey"))
                if sysdef is not None:
                    self.children.append(sysdef)
        self.mesh = None
        if self.prim == "Mesh":
            md = prim.get("mMesh") or {}
            name = md.get("mSimpleMeshName")
            self.mesh = vfx.mesh(name) if name else None
        filt = e.get("filtering") or {}
        self.hidden = (bool(e.get("disabled")) or bool(filt.get("keywordsRequired")) or self.prim not in DRAWN
                       or e.get("distortionDefinition") is not None
                       or (self.tex is None and self.prim not in ("Mesh",))
                       or (self.prim == "Mesh" and self.mesh is None))
        # an emitter that draws nothing still runs when it carries children (a missile mesh's trail)
        self.skip = self.hidden and not (self.children and not e.get("disabled"))

    def plife_at(self, et, rng, emitter_life):
        pl = float(self.plife.birth(et, rng)[0])
        if pl <= 0:
            pl = emitter_life if emitter_life else 1e9
        return pl


class Particle:
    __slots__ = ("t_birth", "life", "pos", "vel", "acc", "drag", "scale", "color", "rot", "rotv", "orbit", "bind",
                 "origin", "frame", "uv0", "uvs", "multoff", "ramp_y", "pal_row", "et", "seq", "age_now")


class Play:
    """One system played in a scene: where it is (a function of time), which way it faces, until when."""

    def __init__(self, vfx, system, t_start=0.0, origin=(0, 0, 0), velocity=(0, 0, 0), forward=(1, 0, 0),
                 target=None, kill=None, seed=1, emitters=None, skip=(), speed=1.0, frame="standing"):
        self.vfx = vfx
        self.sysdef = vfx.system(system) if isinstance(system, str) else system
        self.name = str(self.sysdef.get("particleName"))
        self.t_start = t_start
        self.origin = np.asarray(origin, np.float64)
        self.velocity = np.asarray(velocity, np.float64)
        f = np.asarray(forward, np.float64)
        f = f / np.linalg.norm(f)
        up = np.array([0.0, 1.0, 0.0])
        side = np.cross(up, f)                      # local x
        self.frame = frame
        if frame == "missile":
            # a flying missile's system: local y is its flight, z is up (Lux Q's helix trails turn about y, Jinx R's
            # rocket mesh (nose +y) rolls about y, its quads' local XY plane lies flat)
            self.M = np.stack([side, f, up], 1)
        else:
            self.M = np.stack([side, up, f], 1)    # a standing system: y up, z its facing (Lux R's beam)
        self.target = None if target is None else np.asarray(target, np.float64)
        self.kill = kill                           # system time the system is removed (None: never)
        self.speed = speed                         # League seconds per scene second (5: a 5 s field in our 1 s)
        self.rng = np.random.default_rng(seed)
        ems = ((self.sysdef.get("complexEmitterDefinitionData") or [])
               + (self.sysdef.get("simpleEmitterDefinitionData") or []))
        self.emitters = []
        for e in ems:
            if not isinstance(e, dict):
                continue
            em = Emitter(e, vfx)
            if em.skip or em.name in skip or (emitters is not None and em.name not in emitters):
                continue
            self.emitters.append(em)

        self.parent = None                         # (play, particle) a child system rides on

    def pos_at(self, t):
        """the system's origin in world units at system time t."""
        if self.parent is not None:
            ppl, pp = self.parent
            age = pp.age_now if pp.age_now is not None else 0
            return pp.pos + (ppl.pos_at(pp.t_birth + age) if pp.bind >= 0.5 else 0)
        return self.origin + self.velocity * t


class Sim:
    """Steps every play of a scene in fixed time steps and keeps the live particles per emitter."""

    def __init__(self, plays, dt=1.0 / 120):
        self.plays = plays
        self.dt = dt
        self.t = 0.0
        self.state = {}
        for pi, pl in enumerate(plays):
            for ei, em in enumerate(pl.emitters):
                self.state[(pi, ei)] = dict(parts=[], acc=1.0, done=False, seq=0)   # the first particle at once

    def run_to(self, t_end):
        while self.t < t_end - 1e-9:
            self.step(min(self.dt, t_end - self.t))

    def step(self, dt):
        t1 = self.t + dt
        for pi, pl in enumerate(list(self.plays)):
            st = (t1 - pl.t_start) * pl.speed      # system time at the end of the step
            if st <= 0:
                continue
            sdt = min(dt * pl.speed, st)
            alive = pl.kill is None or st < pl.kill
            for ei, em in enumerate(pl.emitters):
                s = self.state[(pi, ei)]
                self._emit(pl, em, s, st - sdt, st, alive)
                self._update(pl, em, s, st, sdt, alive)
        self.t = t1

    # -- emission
    def _emit(self, pl, em, s, sa, sb, alive):
        if not alive or s["done"]:
            return
        start = em.t0
        life = float(em.life) if em.life is not None else None
        if sb < start:
            return
        if em.single:
            n = max(1, int(round(float(em.rate.at(0.0)[0])))) if em.e.get("rate") is not None else 1
            for _ in range(n):
                self._spawn(pl, em, s, start, 0.0, life)
            s["done"] = True
            return
        a0 = max(sa, start)
        a1 = sb if life is None else min(sb, start + life)
        if a1 <= a0:
            if life is not None and sb >= start + life:
                s["done"] = True
            return
        et = 0.0 if not life else (a0 - start) / life
        r = float(em.rate.birth(et, pl.rng)[0])
        if em.prim in ("CameraTrail", "ArbitraryTrail"):
            r = max(r, 120.0)          # a trail is a ribbon through the emitter's path: a point every step (Jinx W: 1)
        s["acc"] += max(0.0, r) * (a1 - a0)
        n = int(s["acc"])
        s["acc"] -= n
        for k in range(n):
            tb = a1 - (k + 0.5) / max(n, 1) * (a1 - a0)        # spread over the step (oldest first)
            et = 0.0 if not life else (tb - start) / life
            self._spawn(pl, em, s, tb, et, life)

    def _spawn(self, pl, em, s, tb, et, life):
        rng = pl.rng
        p = Particle()
        p.t_birth = tb
        p.et = et
        p.seq = s["seq"]
        s["seq"] += 1
        p.life = em.plife_at(et, rng, (life - (tb - em.t0)) if life else None)
        # spawn shape
        off = np.zeros(3)
        vel = em.bvel.birth(et, rng)
        sh = em.shape
        cls = sh.get("__class") if isinstance(sh, dict) else None
        if cls == "VfxShapeLegacy":
            off = Curve(sh.get("emitOffset"), (0.0, 0.0, 0.0)).birth(et, rng)
            angles = sh.get("emitRotationAngles") or []
            axes = sh.get("emitRotationAxes") or []
            R = np.eye(3)
            for ang, ax in zip(angles, axes):
                a = float(Curve(ang, 0.0).birth(et, rng)[0])
                R = axis_angle(ax, a) @ R
            off, vel = R @ off, R @ vel
        elif cls == "VfxShapeOffset":
            off = _vec(sh.get("emitOffset"), 3)
        elif cls == "VfxShapeSphere":
            r = float(sh.get("radius") or 0.0)
            d = rng.normal(size=3)
            d /= np.linalg.norm(d) + 1e-12
            off = d * r * (1.0 if (sh.get("flags") or 0) & 1 else rng.random() ** (1 / 3))
        elif cls == "VfxShapeBox":
            size = _vec(sh.get("size"), 3) if sh.get("size") is not None else np.zeros(3)
            off = (rng.random(3) - 0.5) * size
        elif cls == "VfxShapeCylinder":
            r = float(sh.get("radius") or 0.0)
            h = float(sh.get("height") or 0.0)
            a = rng.random() * 2 * math.pi
            rr = r if (sh.get("flags") or 0) & 1 else r * math.sqrt(rng.random())
            off = np.array([rr * math.cos(a), (rng.random() - 0.5) * h, rr * math.sin(a)])
        p.origin = em.epos.at(et)
        p.pos = p.origin + off                                  # local to the system
        p.vel = vel
        p.acc = em.bacc.birth(et, rng)
        p.drag = em.bdrag.birth(et, rng)
        sc = em.bscale.at(et)
        f = em.bscale.factor(rng)
        if em.uniform:
            sc = np.full(3, sc[0] * f[0])
        else:
            sc = sc * f
        p.scale = sc
        p.color = em.bcolor.birth(et, rng)
        p.rot = em.brot.birth(et, rng)
        p.rotv = em.brotv.birth(et, rng)
        p.orbit = em.orbit.birth(et, rng)
        p.bind = float(em.bind.at(et)[0])
        nf = em.nframes or 1
        p.frame = (em.start_frame + (int(rng.integers(0, nf)) if em.random_frame else 0))
        p.uv0 = em.uv_off.birth(et, rng)
        p.uvs = em.uv_scroll.birth(et, rng)
        p.multoff = em.mult["off"].birth(et, rng) if em.mult else np.zeros(2)
        p.ramp_y = rng.random()
        p.pal_row = em.palette["sel"].birth(et, rng)[0] if em.palette else 0.0
        p.age_now = 0.0
        # world placement: a particle not bound to its emitter keeps the place it was born at
        sys_pos = pl.pos_at(tb)
        p.pos = pl.M @ p.pos + (sys_pos if p.bind < 0.5 else 0)
        p.vel = pl.M @ p.vel
        p.acc = pl.M @ p.acc
        s["parts"].append(p)
        for sysdef in em.children:
            child = Play(pl.vfx, sysdef, t_start=pl.t_start + tb / pl.speed,
                         forward=pl.M[:, 1] if pl.frame == "missile" else pl.M[:, 2],
                         seed=int(rng.integers(1, 1 << 30)), speed=pl.speed, frame=pl.frame)
            child.parent = (pl, p)
            child.kill = p.life
            self.add(child)

    def add(self, play):
        self.plays.append(play)
        pi = len(self.plays) - 1
        for ei, _em in enumerate(play.emitters):
            self.state[(pi, ei)] = dict(parts=[], acc=1.0, done=False, seq=0)

    # -- motion
    def _update(self, pl, em, s, st, dt, alive):
        keep = []
        sys_end = pl.kill
        for p in s["parts"]:
            age = st - p.t_birth
            if age < 0:
                keep.append(p)
                continue
            lim = p.life
            if sys_end is not None and st >= sys_end and age > 0:
                # the system was removed: particles linger particleLinger at most
                lim = min(lim, (sys_end - p.t_birth) + em.linger)
            if age > lim:
                continue
            p.age_now = age
            t = min(1.0, age / max(p.life, 1e-6))
            drag = p.drag + em.drag.at(t)
            p.vel = p.vel * np.exp(-drag * dt) + (p.acc + em.wacc.at(t)) * dt     # worldAcceleration: world axes (Y up)
            v = p.vel + pl.M @ em.vel.at(t)
            p.pos = p.pos + v * dt
            if np.any(p.orbit):
                R = (axis_angle((1, 0, 0), math.degrees(p.orbit[0] * dt))
                     @ axis_angle((0, 1, 0), math.degrees(p.orbit[1] * dt))
                     @ axis_angle((0, 0, 1), math.degrees(p.orbit[2] * dt)))
                c = pl.M @ p.origin + (0 if p.bind >= 0.5 else pl.pos_at(p.t_birth))
                p.pos = c + (pl.M @ R @ pl.M.T) @ (p.pos - c)
            keep.append(p)
        s["parts"] = keep

    def snapshot(self):
        """[(play, emitter, particle, age, world position)] alive now."""
        out = []
        for pi, pl in enumerate(self.plays):
            st = (self.t - pl.t_start) * pl.speed
            for ei, em in enumerate(pl.emitters):
                if em.hidden:
                    continue
                for p in self.state[(pi, ei)]["parts"]:
                    age = st - p.t_birth
                    if age < 0:
                        continue
                    pos = p.pos + (pl.pos_at(st) if p.bind >= 0.5 else 0)
                    out.append((pl, em, p, age, pos))
        return out


# ----------------------------------------------------------------------------- drawing
class Camera:
    def __init__(self, s, pitch=35.0, ground_px=11.5, ppx=8, size=(64, 64), center=None):
        """s: game px per unit; ppx: canvas pixels per game px; size: canvas in game px (w, h); the anchor (the frame
        centre the game draws at) is at `center` (game px in the canvas, default its middle)."""
        self.s, self.pitch, self.ground_px, self.ppx = s, pitch, ground_px, ppx
        self.size = size
        # the anchor sits in the middle of a game pixel (k + 0.5): the 1x frame's centre pixel, the hd frame's centre
        self.center = center if center is not None else (size[0] // 2 + 0.5, size[1] // 2 + 0.5)
        self.sp, self.cp = math.sin(math.radians(pitch)), math.cos(math.radians(pitch))
        self.W, self.H = int(round(size[0] * ppx)), int(round(size[1] * ppx))
        # screen axes of the view direction (for camera-facing quads): right, up (screen), toward the viewer
        self.right = np.array([1.0, 0, 0])
        self.up = np.array([0.0, self.cp, -self.sp])
        self.view = np.array([0.0, self.sp, self.cp])

    def project(self, w):
        """world points (..., 3) -> canvas pixels (..., 2) and depth (toward the viewer)."""
        w = np.asarray(w, np.float64)
        gx = w[..., 0] * self.s
        gy = self.ground_px + (w[..., 2] * self.sp - w[..., 1] * self.cp) * self.s
        px = (gx + self.center[0]) * self.ppx
        py = (gy + self.center[1]) * self.ppx
        depth = w[..., 2] * self.cp + w[..., 1] * self.sp
        return np.stack([px, py], -1), depth


def sample(tex, u, v, wrap=True):
    """bilinear sample of an (h, w, 4) texture at UVs (arrays) -> (..., 4)."""
    h, w = tex.shape[:2]
    x = u * w - 0.5
    y = v * h - 0.5
    x0 = np.floor(x)
    y0 = np.floor(y)
    fx = (x - x0)[..., None]
    fy = (y - y0)[..., None]
    x0 = x0.astype(np.int64)
    y0 = y0.astype(np.int64)
    if wrap:
        xa, xb, ya, yb = x0 % w, (x0 + 1) % w, y0 % h, (y0 + 1) % h
    else:
        xa, xb = np.clip(x0, 0, w - 1), np.clip(x0 + 1, 0, w - 1)
        ya, yb = np.clip(y0, 0, h - 1), np.clip(y0 + 1, 0, h - 1)
    c = (tex[ya, xa] * (1 - fx) * (1 - fy) + tex[ya, xb] * fx * (1 - fy) + tex[yb, xa] * (1 - fx) * fy
         + tex[yb, xb] * fx * fy)
    return c


class Canvas:
    """Premultiplied float canvas. `bg` None renders on transparency and keeps two layers apart: matter (alpha-blended
    particles: smoke, debris, dark marks; premultiplied colour + coverage) and light (additive / screen particles: an
    unbounded RGB sum, dimmed by matter drawn over it); else everything on that colour (exact blending)."""

    def __init__(self, W, H, bg=None):
        self.W, self.H = W, H
        self.bg = bg
        if bg is None:
            self.c = np.zeros((H, W, 3), np.float32)
            self.a = np.zeros((H, W), np.float32)
            self.L = np.zeros((H, W, 3), np.float32)
        else:
            self.c = np.ones((H, W, 3), np.float32) * (np.asarray(bg[:3], np.float32) / 255.0)
            self.a = np.ones((H, W), np.float32)
            self.L = None

    def blend(self, y0, x0, mask, rgb, alpha, mode):
        """rgb (n, 3) straight colour and alpha (n,) at the pixels `mask` of the block at (y0, x0)."""
        hh, ww = mask.shape
        c = self.c[y0:y0 + hh, x0:x0 + ww]
        a = self.a[y0:y0 + hh, x0:x0 + ww]
        L = self.L[y0:y0 + hh, x0:x0 + ww] if self.L is not None else None
        if mode == BLEND_ADD:
            if L is not None:
                L[mask] += rgb * alpha[:, None]
            else:
                c[mask] += rgb * alpha[:, None]
        elif mode == BLEND_SCREEN:
            src = np.clip(rgb * alpha[:, None], 0, 1)
            if L is not None:
                L[mask] = L[mask] + src * (1 - np.clip(L[mask], 0, 1))
            else:
                c[mask] = 1 - (1 - np.clip(c[mask], 0, 1)) * (1 - src)
        else:
            if mode == BLEND_OPAQUE:
                alpha = (alpha > 0.5).astype(np.float32)
            c[mask] = c[mask] * (1 - alpha[:, None]) + rgb * alpha[:, None]
            a[mask] = a[mask] * (1 - alpha) + alpha
            if L is not None:
                L[mask] *= (1 - alpha[:, None])

    def rgba(self):
        """straight RGBA float (H, W, 4) in [0, 1] (on transparency: light read as alpha by its brightest channel)."""
        c = self.c
        if self.bg is None:
            c = c + self.L
            a = np.clip(np.maximum(self.a, c.max(-1)), 0, 1)
            c = np.minimum(c, a[..., None])
            out = np.zeros(c.shape[:2] + (4,), np.float32)
            nz = a > 1e-6
            out[nz, :3] = c[nz] / a[nz, None]
            out[..., 3] = a
            return np.clip(out, 0, 1)
        out = np.concatenate([np.clip(c, 0, 1), np.ones(c.shape[:2] + (1,), np.float32)], -1)
        return out

    def layers(self):
        """(matter: premultiplied RGBA float (H, W, 4), light: RGB float (H, W, 3)) - transparency renders only."""
        return np.concatenate([self.c, self.a[..., None]], -1), self.L.copy()


def _tex_lookup(em, p, age, t, u, v):
    """the particle's texture colour (..., 4) at its quad UVs u, v (0..1 across the quad)."""
    # UV transform: scale, rotation about the centre, offset + scroll (wrapped unless clamped)
    us = em.uv_scale.at(t)
    uu, vv = u * us[0], v * us[1]
    uvr = float(em.uv_rot.at(t)[0])
    if uvr:
        a = math.radians(uvr)
        ca, sa = math.cos(a), math.sin(a)
        cu, cv = uu - 0.5 * us[0], vv - 0.5 * us[1]
        uu, vv = cu * ca - cv * sa + 0.5 * us[0], cu * sa + cv * ca + 0.5 * us[1]
    sc = p.uvs * age + em.uv_pscroll.at(t) * age
    uu = uu + p.uv0[0] + sc[0]
    vv = vv + p.uv0[1] + sc[1]
    wrap = not em.uv_clamp and (np.any(sc) or np.any(p.uv0) or np.any(us != 1))
    cols, rows = em.div
    if cols * rows > 1:
        nf = em.nframes or cols * rows
        if em.frame_rate > 0:
            f = p.frame + int(age * em.frame_rate)
        elif em.nframes > 1 and not em.random_frame:
            f = p.frame + int(t * nf)
        else:
            f = p.frame
        f %= max(1, cols * rows)
        cx, cy = f % cols, f // cols
        uu = (cx + np.clip(uu % 1.0 if wrap else uu, 0, 1)) / cols
        vv = (cy + np.clip(vv % 1.0 if wrap else vv, 0, 1)) / rows
        texel = sample(em.tex, uu, vv, wrap=False)
    else:
        texel = sample(em.tex, uu, vv, wrap=wrap)
    if em.palette is not None:
        ch = em.palette["channel"]
        k = np.clip((texel * ch).sum(-1), 0, 1)
        pt = em.palette["tex"]
        row = (np.floor(p.pal_row) % em.palette["count"] + 0.5) / em.palette["count"]
        pal = sample(pt, k * 0.999, np.full_like(k, row), wrap=False)
        texel = np.concatenate([pal[..., :3], texel[..., 3:4]], -1)
    if em.mult is not None:
        m = em.mult
        ms = m["scale"].at(t)
        mu = u * ms[0] + p.multoff[0] + m["scroll"].at(t)[0] * age + m["pscroll"].at(t)[0] * age
        mv = v * ms[1] + p.multoff[1] + m["scroll"].at(t)[1] * age + m["pscroll"].at(t)[1] * age
        if m["escroll"] is not None:
            mu = mu + m["escroll"][0] * age
            mv = mv + m["escroll"][1] * age
        mt = sample(m["tex"], mu, mv, wrap=True)
        texel = texel * mt
    if em.erosion is not None:
        er = em.erosion
        level = float(er["drive"].at(t)[0])
        if level > 0:
            ev = np.clip((sample(er["tex"], u, v, wrap=True) * er["channel"]).sum(-1), 0, 1)
            texel = texel.copy()
            texel[..., 3] *= np.clip((ev - level) / max(er["width"], 1e-3) + 0.5, 0, 1)
    return texel


def particle_colour(em, p, age, t):
    col = p.color * em.color.at(t)
    if em.ramp is not None:
        x = t * em.ramp_scale[0] + em.ramp_off[0]
        y = (p.ramp_y if em.ramp_type_y == 3 else 0.5) * em.ramp_scale[1] + em.ramp_off[1]
        col = col * sample(em.ramp, np.array([x % 1.0 if x > 1 else x]), np.array([min(max(y, 0), 1)]), wrap=False)[0]
    return np.clip(col, 0, 8)


def draw_para(cv, cam, em, p, age, t, origin_px, e1, e2, col):
    """a textured parallelogram: canvas pixel = origin + u*e1 + v*e2, u, v in [0, 1]."""
    corners = np.array([origin_px, origin_px + e1, origin_px + e2, origin_px + e1 + e2])
    x0 = max(int(math.floor(corners[:, 0].min())), 0)
    x1 = min(int(math.ceil(corners[:, 0].max())), cv.W)
    y0 = max(int(math.floor(corners[:, 1].min())), 0)
    y1 = min(int(math.ceil(corners[:, 1].max())), cv.H)
    if x1 <= x0 or y1 <= y0:
        return
    det = e1[0] * e2[1] - e1[1] * e2[0]
    if abs(det) < 1e-6:
        return
    gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5 - origin_px[0], np.arange(y0, y1) + 0.5 - origin_px[1])
    u = (gx * e2[1] - gy * e2[0]) / det
    v = (e1[0] * gy - e1[1] * gx) / det
    m = (u >= 0) & (u < 1) & (v >= 0) & (v < 1)
    if not m.any():
        return
    texel = _tex_lookup(em, p, age, t, u[m], v[m])
    rgb = texel[:, :3] * col[:3]
    alpha = np.clip(texel[:, 3] * col[3], 0, 1)
    cv.blend(y0, x0, m, rgb, alpha, em.blend)


def draw_tris(cv, cam, em, p, age, t, pts, uvs, cols):
    """textured triangles: pts (n, 3, 2) canvas pixels, uvs (n, 3, 2), cols (n, 3, 4) per corner."""
    for k in range(len(pts)):
        tp = pts[k]
        x0 = max(int(math.floor(tp[:, 0].min())), 0)
        x1 = min(int(math.ceil(tp[:, 0].max())), cv.W)
        y0 = max(int(math.floor(tp[:, 1].min())), 0)
        y1 = min(int(math.ceil(tp[:, 1].max())), cv.H)
        if x1 <= x0 or y1 <= y0:
            continue
        (ax, ay), (bx, by), (cx, cy) = tp
        den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
        if abs(den) < 1e-9:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        l0 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
        l1 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
        l2 = 1 - l0 - l1
        m = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if not m.any():
            continue
        w0, w1, w2 = l0[m], l1[m], l2[m]
        uv = uvs[k]
        u = w0 * uv[0, 0] + w1 * uv[1, 0] + w2 * uv[2, 0]
        v = w0 * uv[0, 1] + w1 * uv[1, 1] + w2 * uv[2, 1]
        c = cols[k]
        col = w0[:, None] * c[0] + w1[:, None] * c[1] + w2[:, None] * c[2]
        if em.tex is not None:
            texel = _tex_lookup(em, p, age, t, u, v)
        else:
            texel = np.ones((len(u), 4), np.float32)
        rgb = texel[:, :3] * col[:, :3]
        alpha = np.clip(texel[:, 3] * col[:, 3], 0, 1)
        cv.blend(y0, x0, m, rgb, alpha, em.blend)


def draw_particle(cv, cam, pl, em, p, age, pos):
    t = min(1.0, age / max(p.life, 1e-6))
    col = particle_colour(em, p, age, t)
    if col[3] <= 1e-4:
        return
    sc = p.scale * em.scale.at(t)
    if em.uniform:
        sc = np.full(3, sc[0])
    rot = p.rot + p.rotv * age + em.rot.at(t)
    ppu = cam.s * cam.ppx                                    # canvas px per unit
    c_px, _ = cam.project(pos)
    if em.prim == "Billboard":
        w, h = sc[0] * ppu, sc[1] * ppu
        if em.dir_oriented:
            vel = p.vel
            v2 = cam.project(pos + vel * 0.01)[0] - c_px
            n = np.linalg.norm(v2)
            ang = math.atan2(v2[1], v2[0]) if n > 1e-9 else 0.0
            speed = np.linalg.norm(vel)
            h = h * max(em.dir_min, 1.0 + speed * em.dir_scale) if em.dir_scale else h
            ax = np.array([math.cos(ang), math.sin(ang)])          # along the motion: the quad's height
            ay = np.array([-ax[1], ax[0]])
            e1, e2 = ay * w, ax * h
        else:
            a = math.radians(rot[0])
            ca, sa = math.cos(a), math.sin(a)
            e1 = np.array([ca, sa]) * w
            e2 = np.array([-sa, ca]) * h
        draw_para(cv, cam, em, p, age, t, c_px - (e1 + e2) / 2, e1, e2, col)
    elif em.prim == "ArbitraryQuad":
        if em.ground and pl.frame != "missile" and abs(abs(rot[0]) - 90) > 1:
            # a ground-layer quad stood up ((0, 0, 90): the missiles' arch-shaped glows, Lux_Q_Shape / Jinx_R_Shape) is
            # laid on the ground with its yaw only: the arch's round end (the texture's top) then leads the flight
            rot = np.array([90.0, rot[1], 0.0])
        R = pl.M @ rot_matrix(rot)
        ex = R @ np.array([sc[0], 0, 0])
        ey = R @ np.array([0, -sc[1], 0])                         # texture v runs down the quad
        o = pos - ex / 2 - ey / 2
        o_px, _ = cam.project(o)
        e1 = cam.project(o + ex)[0] - o_px
        e2 = cam.project(o + ey)[0] - o_px
        draw_para(cv, cam, em, p, age, t, o_px, e1, e2, col)
    elif em.prim == "Ray":
        R = pl.M @ rot_matrix(rot)
        axis = R @ np.array([0, 1.0, 0])
        end = pos + axis * sc[1]
        a_px, _ = cam.project(pos)
        b_px, _ = cam.project(end)
        d = b_px - a_px
        n = np.linalg.norm(d)
        if n < 1e-6:
            return
        side = np.array([-d[1], d[0]]) / n * sc[0] * ppu
        draw_para(cv, cam, em, p, age, t, b_px - side / 2, side, a_px - b_px, col)   # tip (v 0) out, base (v 1) in
    elif em.prim == "Mesh":
        verts, tris, uvs = em.mesh
        if em.ground:
            # a ground-layer mesh (Lux Q's rune rings (9, 38, 38), Jinx R's ring (0.82, 0.5, 0.5)) takes x for all axes:
            # read per axis they are ellipses thousands of units long; Jinx R's shockwave (4, 4, 15), not on the
            # ground layer, needs its axes apart (it widens while it flattens)
            sc = np.full(3, sc[0])
        R = pl.M @ rot_matrix(rot)
        wv = (verts * sc) @ R.T + pos
        pts, depth = cam.project(wv)
        tp = pts[tris]
        order = np.argsort(depth[tris].mean(1))
        cols = np.broadcast_to(col, (len(tris), 3, 4))
        draw_tris(cv, cam, em, p, age, t, tp[order], uvs[order], cols[order])


def draw_strip(cv, cam, pl, em, pts_w, widths, cols, along, age_t, u_along=False):
    """a camera-facing strip through world points pts_w (n, 3): widths (n,), colours (n, 4) per point; the texture
    runs along it in v (a beam: its profile across in u) or, with u_along, in u (a trail: across in v)."""
    pts, _ = cam.project(pts_w)
    ppu = cam.s * cam.ppx
    n = len(pts)
    if n < 2:
        return
    d = np.gradient(pts, axis=0)
    ln = np.linalg.norm(d, axis=1, keepdims=True)
    d = d / np.maximum(ln, 1e-9)
    side = np.stack([-d[:, 1], d[:, 0]], 1) * (widths[:, None] * ppu / 2)
    left, right = pts - side, pts + side
    tris, tuv, tcol = [], [], []
    for i in range(n - 1):
        q = [left[i], right[i], right[i + 1], left[i + 1]]
        if u_along:
            quv = [(along[i], 0), (along[i], 1), (along[i + 1], 1), (along[i + 1], 0)]
        else:
            quv = [(0, along[i]), (1, along[i]), (1, along[i + 1]), (0, along[i + 1])]
        qc = [cols[i], cols[i], cols[i + 1], cols[i + 1]]
        for a, b, c in ((0, 1, 2), (0, 2, 3)):
            tris.append([q[a], q[b], q[c]])
            tuv.append([quv[a], quv[b], quv[c]])
            tcol.append([qc[a], qc[b], qc[c]])
    p, age, t = age_t
    draw_tris(cv, cam, em, p, age, t, np.array(tris), np.array(tuv, np.float64), np.array(tcol))


def render(sim, cam, bg=None, ground_only=None, layers=False):
    """the scene now -> straight RGBA float (H, W, 4); with `layers` (on transparency) -> Canvas.layers()."""
    cv = Canvas(cam.W, cam.H, bg)
    snap = sim.snapshot()
    groups = {}
    for pl, em, p, age, pos in snap:
        groups.setdefault((id(pl), id(em)), (pl, em, []))[2].append((p, age, pos))
    items = []
    for (pid, eid), (pl, em, parts) in groups.items():
        if ground_only is not None and em.ground != ground_only:
            continue
        depth = float(np.mean([cam.project(pos)[1] for _, _, pos in parts]))
        items.append((0 if em.ground else 1, em.pass_, depth, pl, em, parts))
    items.sort(key=lambda x: (x[0], x[1], x[2]))
    for _g, _ps, _d, pl, em, parts in items:
        if em.prim in ("CameraTrail", "ArbitraryTrail"):
            _draw_trail(cv, cam, pl, em, parts)
        elif em.prim == "Beam":
            for p, age, pos in parts:
                _draw_beam(cv, cam, pl, em, p, age, pos, sim)
        else:
            parts.sort(key=lambda x: cam.project(x[2])[1])
            for p, age, pos in parts:
                draw_particle(cv, cam, pl, em, p, age, pos)
    return cv.layers() if layers else cv.rgba()


def _draw_trail(cv, cam, pl, em, parts):
    if len(parts) < 2:
        return
    parts = sorted(parts, key=lambda x: x[0].seq)
    trail = em.prim_data.get("mTrail")
    tiling = trail.get("mBirthTilingSize") if isinstance(trail, dict) else None
    tile = float(Curve(tiling, (0.0, 0.0, 0.0)).at(0)[0]) if tiling is not None else 0.0
    pts = np.array([pos for _, _, pos in parts])
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))]
    us = seg / tile if tile > 0 else seg / max(seg[-1], 1e-6)
    widths, cols = [], []
    for p, age, pos in parts:
        t = min(1.0, age / max(p.life, 1e-6))
        sc = p.scale * em.scale.at(t)
        widths.append(sc[0])
        cols.append(particle_colour(em, p, age, t))
    p, age, _ = parts[-1]
    draw_strip(cv, cam, pl, em, pts, np.array(widths), np.array(cols), us, (p, age, min(1.0, age / max(p.life, 1e-6))),
               u_along=True)


def _draw_beam(cv, cam, pl, em, p, age, pos, sim):
    if pl.target is None:
        return
    bd = em.prim_data.get("mBeam") or {}
    src = bd.get("mLocalSpaceSourceOffset")
    tgt = bd.get("mLocalSpaceTargetOffset")
    src_off = _vec(src, 3) if src is not None else np.zeros(3)
    tgt_off = _vec(tgt, 3) if tgt is not None else np.zeros(3)
    a = pos + pl.M @ src_off
    b = pl.target + pl.M @ tgt_off
    segs = int(bd.get("mSegments") or 24)
    k = np.linspace(0, 1, max(2, segs) + 1)
    pts = a[None] + (b - a)[None] * k[:, None]
    t = min(1.0, age / max(p.life, 1e-6))
    sc = p.scale * em.scale.at(t)
    col = particle_colour(em, p, age, t)
    widths = np.full(len(k), sc[0])
    cols = np.repeat(col[None], len(k), 0)
    draw_strip(cv, cam, pl, em, pts, widths, cols, k, (p, age, t))


# ----------------------------------------------------------------------------- scenes
def build_plays(vfxs, scene):
    plays = []
    for i, ps in enumerate(scene["plays"]):
        vfx = vfxs[ps.get("champ", scene["champ"])]
        plays.append(Play(vfx, ps["system"], t_start=ps.get("t", 0.0), origin=ps.get("origin", (0, 0, 0)),
                          velocity=ps.get("velocity", (0, 0, 0)), forward=ps.get("forward", (1, 0, 0)),
                          target=ps.get("target"), kill=ps.get("kill"), seed=ps.get("seed", 7 + i),
                          emitters=ps.get("only"), skip=tuple(ps.get("skip", ())), speed=ps.get("speed", 1.0),
                          frame=ps.get("frame", "standing")))
    return plays


def warp_fn(scene):
    """our time -> League time: the scene's `warp` pairs [[ours, League], ...], linear between and past the ends."""
    w = scene.get("warp") or [[0.0, 0.0], [1.0, 1.0]]
    xs = np.array([a for a, _ in w], np.float64)
    ys = np.array([b for _, b in w], np.float64)

    def f(t):
        if t <= xs[0]:
            k = (ys[1] - ys[0]) / (xs[1] - xs[0]) if len(xs) > 1 else 1.0
            return ys[0] + (t - xs[0]) * k
        if t >= xs[-1]:
            k = (ys[-1] - ys[-2]) / (xs[-1] - xs[-2]) if len(xs) > 1 else 1.0
            return ys[-1] + (t - xs[-1]) * k
        return float(np.interp(t, xs, ys))
    return f


def scene_frames(scene, intervals, bg=None, ppx=8, vfxs=None, shutter=None, layers=False):
    """render a scene over our-time intervals [(t0, t1), ...] (a frame shows what happens while it is on screen:
    `shutter` samples spread over it and averaged; None: one every 1/60 s of League time, 3 to 16) -> list of
    straight RGBA float arrays (H, W, 4)."""
    if vfxs is None:
        vfxs = {}
    for ps in [scene] + scene["plays"]:
        c = ps.get("champ")
        if c and c not in vfxs:
            vfxs[c] = Vfx(c)
    plays = build_plays(vfxs, scene)
    cam_d = scene["camera"]
    sim = Sim(plays, dt=scene.get("dt", 1.0 / 120))
    warp = warp_fn(scene)
    follow = scene.get("follow")
    out = []
    for t0, t1 in intervals:
        n = shutter if shutter else min(16, max(3, int(math.ceil((warp(t1) - warp(t0)) * 60))))
        acc = None
        for j in range(n):
            t = warp(t0 + (j + 0.5) / n * (t1 - t0)) if n > 1 else warp(t0)
            sim.run_to(t)
            cam = Camera(cam_d["s"], cam_d.get("pitch", 35.0), cam_d.get("ground_px", 11.5), ppx, tuple(cam_d["size"]),
                         tuple(cam_d["center"]) if cam_d.get("center") else None)
            if follow is not None:
                pl = plays[follow]
                o = pl.pos_at((t - pl.t_start) * pl.speed)
                cam.center = (cam.center[0] - o[0] * cam.s, cam.center[1] - o[2] * cam.s * cam.sp)
            if layers:
                m, li = render(sim, cam, None, layers=True)
                acc = [m, li] if acc is None else [acc[0] + m, acc[1] + li]
                continue
            img = render(sim, cam, bg)
            pre = img.copy()
            pre[..., :3] *= pre[..., 3:4]
            acc = pre if acc is None else acc + pre
        if layers:
            out.append((acc[0] / n, acc[1] / n))      # (matter premultiplied RGBA, light RGB)
            continue
        acc /= n
        res = acc.copy()
        nz = res[..., 3] > 1e-6
        res[nz, :3] = acc[nz, :3] / acc[nz, 3:4]
        out.append(res)
    return out


def downsample(a, k):
    """box filter by an integer factor on a straight RGBA float image (premultiplied average)."""
    H, W = a.shape[:2]
    H2, W2 = H // k, W // k
    a = a[:H2 * k, :W2 * k]
    pre = a.copy()
    pre[..., :3] *= pre[..., 3:4]
    pre = pre.reshape(H2, k, W2, k, 4).mean((1, 3))
    out = pre.copy()
    nz = out[..., 3] > 1e-6
    out[nz, :3] = pre[nz, :3] / pre[nz, 3:4]
    return out


def to_image(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8), "RGBA")


# ----------------------------------------------------------------------------- survey
IGNORED = {   # emitter fields the renderer reads past (drawn without them)
    "fieldCollectionDefinition": "force fields (noise / attraction / orbit / drag)",
    "reflectionDefinition": "fresnel / cube-map reflection",
    "flexShapeDefinition": "spawn scaled by the unit's size",
    "scaleBirthScaleByBoundObjectSize": "scaled by the unit's size",
    "softParticleParams": "soft-particle depth fade",
    "falloffTexture": "falloff texture",
    "materialOverrideDefinitions": "material override (custom shader)",
}


def survey(lol=LOL, skin=0, log=print):
    """every champion's skin: how many of its emitters the renderer draws as they are, draws without some feature, or
    does not draw (and why)."""
    import collections
    import glob
    root = os.path.join(lol, "Game", "DATA", "FINAL", "Champions")
    tot = collections.Counter()
    why = collections.Counter()
    ign = collections.Counter()
    prims = collections.Counter()
    fails = []
    for path in sorted(glob.glob(os.path.join(root, "*.wad.client"))):
        champ = os.path.basename(path).split(".")[0]
        if "." in os.path.basename(path)[:-len(".wad.client")]:
            continue                                          # locale WADs
        try:
            v = Vfx(champ, skin, lol)
        except Exception as e:  # noqa: BLE001
            fails.append((champ, str(e)[:60]))
            continue
        tot["champions"] += 1
        for name, f in v.systems.items():
            tot["systems"] += 1
            for e in (f.get("complexEmitterDefinitionData") or []) + (f.get("simpleEmitterDefinitionData") or []):
                if not isinstance(e, dict):
                    continue
                tot["emitters"] += 1
                if e.get("disabled"):
                    tot["disabled"] += 1
                    continue
                filt = e.get("filtering") or {}
                if filt.get("keywordsRequired"):
                    tot["other skins (keywords)"] += 1
                    continue
                prim = str((e.get("primitive") or {}).get("__class", "VfxPrimitiveCameraUnitQuad"))
                prim = prim.replace("VfxPrimitive", "")
                if prim in ("CameraUnitQuad", "CameraQuad"):
                    prim = "Billboard"
                prims[prim] += 1
                tex = e.get("texture")
                if prim in ("PlanarProjection", "AttachedMesh"):
                    why[f"primitive {prim}"] += 1
                    continue
                if prim == "Mesh":
                    md = (e.get("primitive") or {}).get("mMesh") or {}
                    if not md.get("mSimpleMeshName"):
                        why["skinned mesh (.skn + animation)"] += 1
                        continue
                    if v.mesh(md["mSimpleMeshName"]) is None:
                        why["mesh file missing / unreadable"] += 1
                        continue
                if e.get("distortionDefinition") is not None:
                    why["distortion (screen refraction)"] += 1
                    continue
                if not tex and prim != "Mesh":
                    why["no texture (sound / empty / material)"] += 1
                    continue
                if tex and v.texture(tex) is None:
                    why["texture missing / undecodable"] += 1
                    continue
                if prim not in DRAWN and prim != "Billboard":
                    why[f"primitive {prim}"] += 1
                    continue
                miss = [k for k in IGNORED if e.get(k) is not None]
                if (e.get("childParticleSetDefinition") or {}).get("boneToSpawnAt"):
                    miss.append("childrenOnBones")
                if miss:
                    tot["drawn without a feature"] += 1
                    for k in miss:
                        ign[k] += 1
                else:
                    tot["drawn as read"] += 1
    return tot, why, ign, prims, fails


# ----------------------------------------------------------------------------- CLI
def _short(v, depth=0):
    if isinstance(v, dict):
        cls = v.get("__class", "")
        if cls.startswith("Value") or cls.startswith("IntegratedValue"):
            s = ""
            if v.get("constantValue") is not None:
                s += _fmt(v["constantValue"])
            d = v.get("dynamics") or {}
            if d.get("times"):
                s += "~{" + ",".join(f"{t:.2g}:{_fmt(x)}" for t, x in zip(d["times"], d["values"])) + "}"
            if d.get("probabilityTables"):
                s += "rand[" + ";".join(_fmt((p or {}).get("keyValues", "")) for p in d["probabilityTables"]) + "]"
            return s or "{}"
        if depth > 3:
            return cls
        return "{" + cls + " " + ", ".join(f"{k}={_short(x, depth + 1)}" for k, x in v.items() if k != "__class") + "}"
    if isinstance(v, list):
        return "[" + ", ".join(_short(x, depth + 1) for x in v) + "]"
    return _fmt(v)


def _fmt(x):
    if isinstance(x, float):
        return f"{x:.3g}"
    if isinstance(x, (list, tuple)):
        return "(" + ",".join(_fmt(y) for y in x) + ")"
    return str(x)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", metavar="CHAMP")
    ap.add_argument("--grep", default="")
    ap.add_argument("--dump", nargs=2, metavar=("CHAMP", "SYSTEM"))
    ap.add_argument("--lol", default=LOL)
    ap.add_argument("--survey", action="store_true", help="every champion's base skin: what share of emitters is drawn")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    if a.survey:
        tot, why, ign, prims, fails = survey(a.lol)
        live = tot["emitters"] - tot["disabled"] - tot["other skins (keywords)"]
        print(f"{tot['champions']} champions, {tot['systems']} systems, {tot['emitters']} emitters "
              f"({tot['disabled']} disabled, {tot['other skins (keywords)']} for other skins) -> {live} live")
        print(f"  drawn as read:            {tot['drawn as read']:6d}  {tot['drawn as read'] / max(live, 1):.1%}")
        nw = tot["drawn without a feature"]
        print(f"  drawn without a feature:  {nw:6d}  {nw / max(live, 1):.1%}")
        for k, n in ign.most_common():
            print(f"      {k:36s} {n:6d}  ({IGNORED.get(k, k)})")
        nd = sum(why.values())
        print(f"  not drawn:                {nd:6d}  {nd / max(live, 1):.1%}")
        for k, n in why.most_common():
            print(f"      {k:36s} {n:6d}")
        print("  primitives:", dict(prims.most_common()))
        if fails:
            print("  unreadable:", fails)
    if a.list:
        v = Vfx(a.list, lol=a.lol)
        for name, f in v.systems.items():
            if a.grep.lower() in name.lower():
                ems = (f.get("complexEmitterDefinitionData") or []) + (f.get("simpleEmitterDefinitionData") or [])
                print(f"{name}  ({len(ems)} emitters)")
    if a.dump:
        v = Vfx(a.dump[0], lol=a.lol)
        f = v.system(a.dump[1])
        for e in (f.get("complexEmitterDefinitionData") or []) + (f.get("simpleEmitterDefinitionData") or []):
            em = Emitter(e, v)
            print(f"- {em.name}: {em.prim} {os.path.basename(str(e.get('texture', '')))} blend={em.blend}"
                  f"{' SKIPPED' if em.skip else ''}")
            for k, x in e.items():
                if k not in ("__class", "emitterName"):
                    print(f"    {k} = {_short(x)}")


if __name__ == "__main__":
    main()
