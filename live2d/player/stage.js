// stage.js — Vyond-style stage for Inochi2D puppets: parallax backgrounds + several puppets + camera,
// driven by the timeline.json that live2d/make_video.py compiles.  Deterministic: frame i always looks the same
// (random blinks are seeded, springs are stepped at the video frame rate from the start of each scene).
import { loadINP, Puppet } from './inochi-lite.js';

const W = 1920, H = 1080;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const ease = (x) => { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); };
export const FEET = { red_hood: 996, wolf: 999, red_hood_side: 961, wolf_side: 971 };
const TURN_AT = 0.18, TURN_FADE = 0.16;   // walk start: head turns 30 deg first, then front -> profile cross-fade         // lowest opaque row of the puppet (puppet units, y down)
const TALL = { red_hood: 1901, wolf: 1886 };       // head top -> feet, puppet units

function rng(seed) {                                // mulberry32
  return () => { seed |= 0; seed = (seed + 0x6d2b79f5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
}

export class GL {                     // also used by the web demo (transparent canvas of any size)
  constructor(canvas, { alpha = false } = {}) {
    this.canvas = canvas;
    const gl = (this.gl = canvas.getContext('webgl2', { premultipliedAlpha: true, alpha, antialias: true,
      preserveDrawingBuffer: true }));
    const vs = `#version 300 es
      in vec2 aPos; in vec2 aUV; uniform vec4 uView; out vec2 vUV;
      void main(){ vUV=aUV; gl_Position=vec4(aPos.x*uView.x+uView.z, -(aPos.y*uView.y+uView.w), 0., 1.); }`;
    const fs = `#version 300 es
      precision mediump float; in vec2 vUV; uniform sampler2D uTex; uniform float uOpacity; out vec4 o;
      void main(){ o = texture(uTex, vUV) * uOpacity; }`;
    const sh = (t, s) => { const x = gl.createShader(t); gl.shaderSource(x, s); gl.compileShader(x);
      if (!gl.getShaderParameter(x, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(x)); return x; };
    const p = (this.prog = gl.createProgram());
    gl.attachShader(p, sh(gl.VERTEX_SHADER, vs)); gl.attachShader(p, sh(gl.FRAGMENT_SHADER, fs)); gl.linkProgram(p);
    this.loc = { pos: gl.getAttribLocation(p, 'aPos'), uv: gl.getAttribLocation(p, 'aUV'),
      view: gl.getUniformLocation(p, 'uView'), op: gl.getUniformLocation(p, 'uOpacity') };
    this.posBuf = gl.createBuffer(); this.uvBuf = gl.createBuffer(); this.idxBuf = gl.createBuffer();
    this.black = this.texture(Object.assign(document.createElement('canvas'), { width: 2, height: 2 }), '#000');
  }

  // upload premultiplied on the CPU (filtering straight alpha draws dark fringes)
  texture(src, fill) {
    const gl = this.gl, cv = document.createElement('canvas'), cx = cv.getContext('2d', { willReadFrequently: true });
    cv.width = src.width; cv.height = src.height;
    if (fill) { cx.fillStyle = fill; cx.fillRect(0, 0, cv.width, cv.height); } else cx.drawImage(src, 0, 0);
    const px = cx.getImageData(0, 0, cv.width, cv.height).data;
    for (let i = 0; i < px.length; i += 4) {
      const a = px[i + 3] / 255;
      px[i] = Math.round(px[i] * a); px[i + 1] = Math.round(px[i + 1] * a); px[i + 2] = Math.round(px[i + 2] * a);
    }
    const t = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, t);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
    gl.pixelStorei(gl.UNPACK_COLORSPACE_CONVERSION_WEBGL, gl.NONE);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, cv.width, cv.height, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array(px.buffer));
    gl.generateMipmap(gl.TEXTURE_2D);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    return t;
  }

  get w() { return this.canvas.width; }
  get h() { return this.canvas.height; }

  begin(clear = [0, 0, 0, 1]) {
    const gl = this.gl;
    gl.viewport(0, 0, this.w, this.h); gl.clearColor(...clear); gl.clear(gl.COLOR_BUFFER_BIT);
    gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA); gl.useProgram(this.prog);
  }

  // local px -> screen px = p * k + (ox, oy)
  mesh(pos, uvs, idx, tex, k, ox, oy, opacity = 1) {      // k: scale, or [kx, ky] (kx < 0 mirrors)
    const gl = this.gl, kx = Array.isArray(k) ? k[0] : k, ky = Array.isArray(k) ? k[1] : k, w = this.w, h = this.h;
    gl.uniform4f(this.loc.view, 2 * kx / w, 2 * ky / h, 2 * ox / w - 1, 2 * oy / h - 1);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.posBuf); gl.bufferData(gl.ARRAY_BUFFER, pos, gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.loc.pos); gl.vertexAttribPointer(this.loc.pos, 2, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ARRAY_BUFFER, this.uvBuf); gl.bufferData(gl.ARRAY_BUFFER, uvs, gl.DYNAMIC_DRAW);
    gl.enableVertexAttribArray(this.loc.uv); gl.vertexAttribPointer(this.loc.uv, 2, gl.FLOAT, false, 0, 0);
    gl.bindBuffer(gl.ELEMENT_ARRAY_BUFFER, this.idxBuf); gl.bufferData(gl.ELEMENT_ARRAY_BUFFER, idx, gl.DYNAMIC_DRAW);
    gl.bindTexture(gl.TEXTURE_2D, tex); gl.uniform1f(this.loc.op, opacity);
    gl.drawElements(gl.TRIANGLES, idx.length, gl.UNSIGNED_SHORT, 0);
  }

  // offscreen layer: draw a whole puppet, then composite it with one opacity (a cross-fade must not show
  // the puppet's inner layers through each other)
  layer(i) {
    const gl = this.gl;
    this.layers = this.layers || [];
    if (this.layers[i] && (this.layers[i].w !== this.w || this.layers[i].h !== this.h)) this.layers[i] = null;
    if (!this.layers[i]) {
      const tex = gl.createTexture();
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, this.w, this.h, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      const fb = gl.createFramebuffer();
      gl.bindFramebuffer(gl.FRAMEBUFFER, fb);
      gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, tex, 0);
      this.layers[i] = { fb, tex, w: this.w, h: this.h };
    }
    return this.layers[i];
  }

  toLayer(i, draw) {
    const gl = this.gl, L = this.layer(i);
    gl.bindFramebuffer(gl.FRAMEBUFFER, L.fb);
    gl.viewport(0, 0, this.w, this.h); gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
    draw();
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.viewport(0, 0, this.w, this.h);
  }

  showLayer(i, opacity) {                   // framebuffer textures are bottom-up: flip v
    const w = this.w, h = this.h;
    this.mesh(new Float32Array([0, 0, w, 0, w, h, 0, h]), new Float32Array([0, 1, 1, 1, 1, 0, 0, 0]),
      new Uint16Array([0, 1, 2, 0, 2, 3]), this.layer(i).tex, 1, 0, 0, opacity);
  }

  canvasTexture(cv, tex) {
    const gl = this.gl;
    if (!tex) {
      tex = gl.createTexture();
      gl.bindTexture(gl.TEXTURE_2D, tex);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    }
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, cv);
    gl.pixelStorei(gl.UNPACK_PREMULTIPLY_ALPHA_WEBGL, false);
    return tex;
  }

  quad(tex, w, h, k, ox, oy, opacity = 1) {
    this.mesh(new Float32Array([0, 0, w, 0, w, h, 0, h]), new Float32Array([0, 0, 1, 0, 1, 1, 0, 1]),
      new Uint16Array([0, 1, 2, 0, 2, 3]), tex, k, ox, oy, opacity);
  }

  // only: undefined = whole puppet; 'body' = parts not under the Head node; 'headBack' / 'headFront' = head
  // parts drawn behind / in front of the neck (back hair and the back of a hood must stay behind the body)
  puppet(p, texs, k, ox, oy, only) {
    if (only) {
      if (!p._headTagged) {
        for (const n of p.parts) { let q = n.parent, h = false; while (q) { if (q.name === 'Head') { h = true; break; } q = q.parent; } n.inHead = h; }
        p._headTagged = true;
      }
      const neck = p.parts.find((n) => n.name === '脖子');
      p._neckZ = neck ? neck.z : -Infinity;
    }
    const keep = (n) => !only || (only === 'body' ? !n.inHead
      : n.inHead && ((only === 'headBack') === (n.z > p._neckZ)));
    const order = [...p.parts].filter((n) => n.enabled && keep(n)).sort((a, b) => b.z - a.z);
    for (const n of order) {
      const m = n.mesh, M = n.world, nv = m.verts.length / 2;
      const pos = new Float32Array(nv * 2);
      for (let i = 0; i < nv; i++) {
        let x = m.verts[2 * i], y = m.verts[2 * i + 1];
        if (n.deform) { x += n.deform[2 * i]; y += n.deform[2 * i + 1]; }
        pos[2 * i] = M[0] * x + M[2] * y + M[4];
        pos[2 * i + 1] = M[1] * x + M[3] * y + M[5];
      }
      if (!m._uv) { m._uv = new Float32Array(m.uvs); m._idx = new Uint16Array(m.indices); }
      this.mesh(pos, m._uv, m._idx, texs[n.textures[0]], k, ox, oy, n.opacity ?? 1);
    }
  }
}

// ------------------------------------------------------------------------------------------------ actor
class Actor {
  constructor(spec, sceneT0, fps, puppet, side) {
    this.s = spec; this.t0 = sceneT0; this.fps = fps; this.p = puppet;
    this.side = side || null;                  // {p, joints}: profile puppet used while walking
    if (side) {
      const j = side.joints;
      this.Lt = j['Shin F'][1] - j['Thigh F'][1]; this.Ls = j['Foot F'][1] - j['Shin F'][1];
      this.sideFeet = spec.sideFeet ?? FEET[spec.side];
    }
    this.k = spec.height / (spec.tall || TALL[spec.puppet]);
    this.feet = spec.feet ?? FEET[spec.puppet];
    const r = rng([...spec.id].reduce((a, c) => a * 31 + c.charCodeAt(0), 7) + Math.round(sceneT0 * 10));
    this.blinks = []; for (let t = 0.8 + r() * 1.5; t < 400; t += 2.2 + r() * 3.2) this.blinks.push(t);
    this.reset();
  }

  reset() {
    this.st = { yaw: this.s.look, pitch: 0, roll: 0, armR: 0, armL: 0, bendR: 0, bendL: 0, wR: 0, wL: 0,
      vYaw: 0, hair: 0, hairV: 0, basket: 0, basketV: 0, phase: 0, x: this.s.x, prevX: this.s.x,
      sb: 0, sbV: 0, sh: 0, shV: 0, lastDir: 1 };
  }

  // 0 = front puppet, 1 = profile puppet; natural turn: nine-axis head turn first, then a short cross-fade
  sideWeight(t) {
    let w = 0;
    for (const s of this.s.walks) {
      const fin = clamp((t - (s.t0 + TURN_AT)) / TURN_FADE, 0, 1);
      const fout = clamp((s.t1 - t) / TURN_FADE, 0, 1);
      w = Math.max(w, Math.min(fin, fout));
    }
    return this.side ? w : 0;
  }

  // side puppet's Head:: Turn (1 = 70 deg half-profile, 0 = 90 deg profile): it arrives at 70 deg (matching the
  // front view's 30 deg as closely as one drawing can), then eases to 90 deg; the reverse before stopping
  turnAt(t) {
    let v = 0;
    for (const s of this.s.walks) {
      const a = s.t0 + TURN_AT + TURN_FADE, b = s.t1 - TURN_FADE;
      v = Math.max(v, t < s.t0 || t > s.t1 ? 0 : Math.max(1 - ease((t - a) / 0.3), 1 - ease((b - t) / 0.3)));
    }
    return v;
  }

  yAt(t) {                                    // rises (e.g. jumping out of bed): ease-out with a little overshoot
    let y = this.s.y;
    for (const r of this.s.rises || []) {
      if (t < r.t) break;
      const u = clamp((t - r.t) / 0.42, 0, 1), c = 1.9;
      const e = 1 + (c + 1) * (u - 1) ** 3 + c * (u - 1) ** 2;
      y = y + (r.to - y) * e;
    }
    return y;
  }

  within(list, t, pad = 0.15) {               // 0..1 envelope for [t0, t1] segments
    let w = 0;
    for (const e of list || []) w = Math.max(w, Math.min(ease((t - e.t0) / pad), ease((e.t1 - t) / pad)));
    return w;
  }

  xAt(t) {                                    // absolute time -> ground x (walks are eased segments)
    let x = this.s.x, walking = 0, dir = 0, active = false;
    for (const w of this.s.walks) {
      if (t <= w.t0) break;
      const from = x, u = clamp((t - w.t0) / (w.t1 - w.t0), 0, 1);
      // trapezoid velocity profile: 12% accel / decel ramps
      const r = 0.12, vm = 1 / (1 - r);
      const v = u < r ? vm * u * u / (2 * r) : u > 1 - r ? 1 - vm * (1 - u) * (1 - u) / (2 * r) : vm * (u - r / 2);
      x = from + (w.to - from) * v;
      if (u < 1) { walking = u < r ? u / r : u > 1 - r ? (1 - u) / r : 1; dir = Math.sign(w.to - from); active = true; }
    }
    return { x, walking, dir, active };
  }

  env(t) {
    for (const c of this.s.talk) {
      const i = Math.floor((t - c.t0) * this.fps);
      if (i >= 0 && i < c.env.length) return c.env[i];
    }
    return 0;
  }

  gesture(t) {                                 // -> {type, w} with ramped weight
    let best = null;
    for (const g of this.s.gestures) {
      const w = Math.min(ease((t - g.t0) / 0.35), ease((g.t1 + 0.4 - t) / 0.45));
      if (w > 0 && (!best || w > best.w)) best = { type: g.type, w, t: t - g.t0 };
    }
    return best;
  }

  lookAt(t) {
    let v = this.s.look;
    for (const l of this.s.looks) if (t >= l.t) v = l.v;
    return v;
  }

  // advance springs one frame and set puppet params
  step(t) {
    const dt = 1 / this.fps, st = this.st, p = this.p;
    const lt = t - this.t0;
    const { x, walking, dir, active } = this.xAt(t);
    st.prevX = st.x; st.x = x;
    if (dir) st.lastDir = dir;
    // half-cycle stride: with the side rig it is exactly what the legs cover (2 L sin A) -> feet do not slide
    const stride = this.side ? 2 * (this.Lt + this.Ls) * this.k * Math.sin(0.42) : 0.26 * this.s.height;
    st.phase += (Math.abs(st.x - st.prevX) / stride) * Math.PI;
    const ph = st.phase, wk = walking;
    const talk0 = this.env(t);
    const eat = this.within(this.s.eats, t, 0.2);
    const talk = Math.max(talk0, eat * (0.35 + 0.35 * Math.sin((t - this.t0) * 11)));
    const shake = this.within(this.s.shakes, t, 0.08);
    this.y = this.yAt(t);
    // fades in time order: the latest started fade decides (a later fade_in must not hide the actor before it);
    // an actor whose first fade is a fade_in starts invisible ("hidden")
    const fades = [...(this.s.fades || [])].sort((m, n) => m.t - n.t);
    this.opacity = fades.length && fades[0].in ? 0 : 1;
    for (const f of fades) {
      if (t < f.t) break;
      const u = clamp((t - f.t) / f.dur, 0, 1);
      this.opacity = f.in ? u : 1 - u;
    }
    const g = this.gesture(t);

    // targets
    let yaw = this.lookAt(t), pitch = 0, roll = 0;
    let armR = 0.05 * Math.sin(lt * 0.9 + 1), armL = -0.05 * Math.sin(lt * 0.8), bendR = 0.08, bendL = 0.08,
      wR = 0.1 * Math.sin(lt * 1.1), wL = 0.1 * Math.sin(lt * 1.3 + 2), bob = 0;
    if (active) yaw = st.lastDir * 1.0;          // turn the head the full 30 deg toward where she walks
    if (wk > 0) {
      armR += wk * 0.85 * Math.sin(ph); armL += -wk * 0.85 * Math.sin(ph);
      bendR += wk * 0.25; bendL += wk * 0.25;
      roll += wk * 0.06 * Math.sin(ph);
      bob = -wk * Math.abs(Math.cos(ph)) * 0.012 * this.s.height;
      pitch += wk * 0.08 * Math.cos(2 * ph);
    }
    if (g) {
      const w = g.w, T = g.t;
      switch (g.type) {
        case 'shy':
          bendR += w * 0.8; bendL += w * 0.8; armR -= w * 0.5; armL -= w * 0.5; roll += w * 0.35; pitch += w * 0.35;
          wR += w * 0.4 * Math.sin(T * 2.2); break;
        case 'explain':
          bendR += w * 0.75; armR += w * (0.35 + 0.25 * Math.sin(T * 2.6)); wR += w * 0.8 * Math.sin(T * 3.3);
          roll += w * 0.08 * Math.sin(T * 1.7); break;
        case 'sly':
          bendL += w * 0.85; wL += w * (0.6 + 0.3 * Math.sin(T * 4)); bendR += w * 0.5; roll -= w * 0.25; pitch += w * 0.2;
          break;
        case 'point':
          armR += w * 1.0; bendR -= w * 0.05; wR -= w * 0.6; roll += w * 0.1; break;
        case 'happy':
          bendR += w * 0.6; bendL += w * 0.6; armR += w * 0.6; armL += w * 0.6;
          roll += w * 0.18 * Math.sin(T * 5); bob -= w * Math.max(0, Math.sin(T * 9)) * 0.012 * this.s.height;
          wR += w * 0.6 * Math.sin(T * 8); wL -= w * 0.6 * Math.sin(T * 8); break;
      }
    }
    for (const n of this.s.nods) {
      const u = t - n.t;
      if (u > 0 && u < 0.9) pitch += 0.7 * Math.sin((u / 0.9) * Math.PI * 2) ** 2 * (u < 0.45 ? 1 : 0.6);
    }
    if (talk > 0) { pitch += 0.12 * talk * Math.sin(lt * 7); roll += 0.04 * Math.sin(lt * 2.3); }
    if (shake > 0) {                            // angry "蛤？！": fast head shake + little hop
      roll += 0.28 * shake * Math.sin(lt * 38); yaw += 0.14 * shake * Math.sin(lt * 27);
      bob -= shake * Math.abs(Math.sin(lt * 18)) * 0.012 * this.s.height;
    }

    // springs (critically-damped-ish exponential smoothing, arms a little laggy and asymmetric)
    const sm = (cur, tgt, rate) => cur + (tgt - cur) * (1 - Math.exp(-rate * dt));
    const prevYaw = st.yaw;
    st.yaw = sm(st.yaw, yaw, active ? 11 : 6); st.pitch = sm(st.pitch, pitch, 12); st.roll = sm(st.roll, roll, 6);
    st.armR = sm(st.armR, armR, wk > 0 ? 14 : 6.5); st.armL = sm(st.armL, armL, wk > 0 ? 14 : 5.5);
    st.bendR = sm(st.bendR, bendR, 7); st.bendL = sm(st.bendL, bendL, 6);
    st.wR = sm(st.wR, wR, 9); st.wL = sm(st.wL, wL, 8);
    // hair / basket / tail: driven pendulums
    const drive = -(st.yaw - prevYaw) / dt * 0.25 - wk * 0.15 * dir + wk * 0.25 * Math.sin(2 * ph);
    st.hairV += (-40 * (st.hair - drive) - 5 * st.hairV) * dt; st.hair += st.hairV * dt;
    const bd = (st.armR - armR) * 1.5 + wk * 0.4 * Math.sin(ph - 0.6);
    st.basketV += (-30 * (st.basket - bd) - 4 * st.basketV) * dt; st.basket += st.basketV * dt;

    // blink
    let blink = 0;
    for (const b of this.blinks) { const u = lt - b; if (u > -0.1 && u < 0.2) blink = Math.max(blink, 1 - Math.abs(u - 0.05) / 0.12); }
    blink = clamp(blink, 0, 1);
    let expr = this.s.expr;
    for (const e of this.s.exprs || []) if (t >= e.t) expr = e.v;      // expression changes over time
    if (expr === 'deadpan') blink = Math.max(blink, 0.36);             // 死魚眼: half-lidded
    if (expr === 'sleep') blink = 1;                                   // eyes shut (snoring)

    p.set('Head:: Yaw-Pitch', clamp(st.yaw, -1, 1), clamp(-st.pitch, -1, 1));
    p.set('Head:: Roll', clamp(st.roll, -1, 1));
    p.set('Eye:: Left:: Blink', blink); p.set('Eye:: Right:: Blink', blink);
    p.set('Mouth:: Open', clamp(talk * 1.1, 0, 1));
    p.set('Body:: Breath', 0.5 + 0.5 * Math.sin((lt / 3.4) * Math.PI * 2));
    p.set('Arm:: Right:: Swing', clamp(st.armR, -1, 1)); p.set('Arm:: Left:: Swing', clamp(st.armL, -1, 1));
    p.set('Arm:: Right:: Bend', clamp(st.bendR, 0, 1)); p.set('Arm:: Left:: Bend', clamp(st.bendL, 0, 1));
    p.set('Hand:: Right:: Wrist', clamp(st.wR, -1, 1)); p.set('Hand:: Left:: Wrist', clamp(st.wL, -1, 1));
    p.set('Leg:: Right:: Step', wk * Math.max(0, Math.sin(ph))); p.set('Leg:: Left:: Step', wk * Math.max(0, -Math.sin(ph)));
    p.set('Hair:: Sway', clamp(st.hair + 0.08 * Math.sin(lt * 1.4), -1, 1));
    p.set('Basket:: Swing', clamp(st.basket, -1, 1));
    p.set('Tail:: Sway', clamp(0.55 * Math.sin(lt * 2.1) + wk * 0.4 * Math.sin(ph * 2) + 0.4 * talk, -1, 1));
    p.set('Arm:: Left:: Raise', this.holdPhone ? 1 : 0);          // phone held up at chest height (flashlight)
    this.bob = bob;
    this.sideW = this.sideWeight(t);
    if (this.sideW > 0) this.stepSide(lt, ph, wk, talk, blink, dt);
  }

  // profile walk: joint angles in radians (+ = forward); body height follows the supporting leg
  stepSide(lt, ph, wk, talk, blink, dt) {
    const p = this.side.p, st = this.st, s = Math.sin(ph), c = Math.cos(ph), A = 0.42 * wk;
    const hipF = A * s, hipB = -A * s;
    const kneeF = wk * (0.06 + 0.8 * Math.max(0, c) ** 2), kneeB = wk * (0.06 + 0.8 * Math.max(0, -c) ** 2);
    const hF = this.Lt * Math.cos(hipF) + this.Ls * Math.cos(kneeF - hipF);
    const hB = this.Lt * Math.cos(hipB) + this.Ls * Math.cos(kneeB - hipB);
    this.sideDrop = (this.Lt + this.Ls - Math.max(hF, hB)) * this.k;
    const armF = -0.36 * wk * s, armB = 0.36 * wk * s;
    const elbF = 0.18 + 0.3 * wk * Math.max(0, -s), elbB = 0.18 + 0.3 * wk * Math.max(0, s);
    // basket / braid / tail: pendulums driven by the stride
    st.sbV += (-35 * (st.sb - 0.25 * wk * Math.sin(ph - 0.8)) - 4 * st.sbV) * dt; st.sb += st.sbV * dt;
    st.shV += (-30 * (st.sh - (-0.12 * wk + 0.08 * Math.sin(2 * ph))) - 4 * st.shV) * dt; st.sh += st.shV * dt;
    p.set('Leg:: Front:: Hip', hipF); p.set('Leg:: Front:: Knee', kneeF); p.set('Leg:: Front:: Foot', (kneeF - hipF) * 0.85);
    p.set('Leg:: Back:: Hip', hipB); p.set('Leg:: Back:: Knee', kneeB); p.set('Leg:: Back:: Foot', (kneeB - hipB) * 0.85);
    p.set('Arm:: Front:: Swing', armF); p.set('Arm:: Front:: Elbow', elbF);
    p.set('Arm:: Back:: Swing', armB); p.set('Arm:: Back:: Elbow', elbB);
    if (this.holdPhone) {                     // far arm lifted forward holding the phone (flashlight)
      p.set('Arm:: Back:: Swing', 1.0 + 0.05 * Math.sin(ph)); p.set('Arm:: Back:: Elbow', 1.3);
    }
    p.set('Basket:: Swing', clamp(-(armF + elbF) + st.sb, -1, 1));
    p.set('Hair:: Sway', clamp(st.sh, -1, 1));
    p.set('Tail:: Sway', clamp(0.25 * Math.sin(ph * 2) + 0.15 * Math.sin(lt * 2.1), -1, 1));
    p.set('Head:: Nod', -(0.025 * Math.sin(2 * ph) + 0.05 * talk * Math.sin(lt * 7)));
    p.set('Body:: Lean', -0.05 * wk);
    p.set('Eye:: Blink', blink);
    p.set('Head:: Turn', this.turnAt(this.t0 + lt));
    p.set('Mouth:: Open', clamp(talk * 1.1, 0, 1));
    p.set('Body:: Breath', 0.5 + 0.5 * Math.sin((lt / 3.4) * Math.PI * 2));
  }
}

// ------------------------------------------------------------------------------------------------ stage
export class Stage {
  constructor(canvas, timeline, bgs, base) {
    this.gl = new GL(canvas); this.tl = timeline; this.bgs = bgs; this.base = base;
    this.last = -2; this.sceneIdx = -1;
  }

  async load() {
    const img = (u) => new Promise((ok, bad) => { const i = new Image(); i.onload = () => ok(i); i.onerror = bad; i.src = u; });
    this.bgTex = {};
    for (const sc of new Set(this.tl.scenes.map((s) => s.bg))) {
      const m = this.bgs[sc];
      this.bgTex[sc] = { width: m.width, height: m.height,
        layers: await Promise.all(m.layers.map(async (l) => ({ ...l, tex: this.gl.texture(await img(`${this.base}/backgrounds/${l.file}`)) }))) };
    }
    this.puppets = {};
    // one Puppet instance per actor per scene would be wasteful; one per puppet id + its textures is enough
    // as long as each actor sets all of its params before its own update() (actors are drawn one by one).
    for (const id of new Set(this.tl.scenes.flatMap((s) => s.actors.map((a) => a.puppet)))) {
      const d = await loadINP(`${this.base}/characters/${id}/${id}.inp`);
      const p = new Puppet(d);
      this.puppets[id] = { p, tex: d.textures.map((b) => this.gl.texture(b)) };
    }
    for (const id of new Set(this.tl.scenes.flatMap((s) => s.actors.map((a) => a.side)).filter(Boolean))) {
      const d = await loadINP(`${this.base}/characters/${id}/${id}.inp`);
      const joints = await (await fetch(`${this.base}/characters/${id}/joints.json`)).json();
      this.puppets[id] = { p: new Puppet(d), tex: d.textures.map((b) => this.gl.texture(b)), joints };
    }
  }

  scene(t) {
    const S = this.tl.scenes;
    for (let i = 0; i < S.length; i++) if (t < S[i].t1 || i === S.length - 1) return i;
  }

  enterScene(i) {
    const sc = this.tl.scenes[i];
    this.sceneIdx = i;
    this.actors = sc.actors.map((a) => new Actor(a, sc.t0, this.tl.fps, this.puppets[a.puppet].p,
      a.side ? this.puppets[a.side] : null));
    for (const a of this.actors) a.holdPhone = !!(sc.light && sc.light.flashlight === a.s.id);
    // new scene -> new UI canvas + texture: a long render once kept showing the forest's flashlight overlay in the
    // next (unlit) scene, the reused canvas/texture handed back a stale image
    this.ui = null;
    if (this.uiTex) { this.gl.gl.deleteTexture(this.uiTex); this.uiTex = null; }
  }

  camera(sc, t) {
    const u = (t - sc.t0) / (sc.t1 - sc.t0), K = sc.camera;
    let a = K[0], b = K[K.length - 1];
    for (let i = 0; i < K.length - 1; i++) if (u >= K[i].at && u <= K[i + 1].at) { a = K[i]; b = K[i + 1]; }
    const w = b.at > a.at ? ease((u - a.at) / (b.at - a.at)) : 0;
    const L = (k) => a[k] + (b[k] - a[k]) * w;
    return { x: L('x'), y: L('y'), zoom: L('zoom') };
  }

  // render frame i (must be called in order for springs; out-of-order calls fast-forward from the scene start)
  frame(i) {
    const fps = this.tl.fps, t = i / fps;
    const si = this.scene(t), sc = this.tl.scenes[si];
    if (si !== this.sceneIdx || i !== this.last + 1) {
      this.enterScene(si);
      for (let j = Math.ceil(sc.t0 * fps); j < i; j++) for (const a of this.actors) a.step(j / fps);
    }
    this.last = i;
    for (const a of this.actors) a.step(t);

    const gl = this.gl, bg = this.bgTex[sc.bg], cam = this.camera(sc, t), z = cam.zoom;
    this.screen = {};
    const cy = clamp(cam.y, H / 2 / z, bg.height - H / 2 / z);
    const offX = (par) => clamp(cam.x * par + (bg.width / 2) * (1 - par), W / 2 / z, bg.width - W / 2 / z);
    gl.begin();
    const layer = (l) => gl.quad(l.tex, bg.width, bg.height, z, -offX(l.parallax) * z + W / 2, -cy * z + H / 2);
    for (const l of bg.layers) if (l.parallax <= 1 && !l.front) layer(l);
    const gx = offX(1);
    for (const a of [...this.actors].sort((m, n) => m.s.y - n.s.y)) {
      const k = a.k * z, sx = (a.st.x - gx) * z + W / 2, gy = ((a.y ?? a.s.y) - cy) * z + H / 2;
      this.screen[a.s.id] = { sx, gy, top: gy - a.s.height * z, h: a.s.height * z, dir: a.st.lastDir || 1 };
      const sw = a.sideW;
      const partPos = (p, name, kx, ky, ox, oy) => {
        const n = p.parts.find((q) => q.name === name);
        if (!n) return null;
        const v = n.mesh.verts, M = n.world; let x = 0, y = 0;
        for (let i = 0; i < v.length; i += 2) {
          const vx = v[i] + (n.deform ? n.deform[i] : 0), vy = v[i + 1] + (n.deform ? n.deform[i + 1] : 0);
          x += M[0] * vx + M[2] * vy + M[4]; y += M[1] * vx + M[3] * vy + M[5];
        }
        x /= v.length / 2; y /= v.length / 2;
        return [x * kx + ox, y * ky + oy];
      };
      const phoneAt = (p, kx, ox, oy) => {     // screen position of the phone layer (the flashlight source)
        const pos = partPos(p, '手機', kx, k, ox, oy);
        if (pos) this.screen[a.s.id].phone = pos;
      };
      const drawFront = (only) => {
        const P = this.puppets[a.s.puppet];
        a.p.update();
        const oy = gy + a.bob * z - a.feet * k;
        gl.puppet(a.p, P.tex, k, sx, oy, only);
        if (a.holdPhone && a.sideW < 0.5) phoneAt(a.p, k, sx, oy);
        const hPos = partPos(a.p, '手指_L', k, k, sx, oy) || partPos(a.p, '手掌_L', k, k, sx, oy);
        if (hPos) this.screen[a.s.id].handL = hPos;
        const hR = partPos(a.p, '手指_R', k, k, sx, oy) || partPos(a.p, '手掌_R', k, k, sx, oy);
        if (hR) this.screen[a.s.id].handR = hR;
      };
      const drawSide = (only) => {             // profile puppet, mirrored when walking left
        const P = this.puppets[a.s.side];
        P.p.update();
        const kx = a.st.lastDir < 0 ? -k : k, oy = gy - a.sideFeet * k + (a.sideDrop || 0) * z;
        gl.puppet(P.p, P.tex, [kx, k], sx, oy, only);
        if (a.holdPhone && a.sideW >= 0.5) phoneAt(P.p, kx, sx, oy);
        const hPos = partPos(P.p, '手_前', kx, k, sx, oy) || partPos(P.p, '籃子', kx, k, sx, oy) || partPos(P.p, 'Hand F', kx, k, sx, oy);
        if (hPos) this.screen[a.s.id].handL = hPos;
      };
      this.drawShadow(sx, gy, a.s.height * (0.2 + 0.06 * sw) * z, sw < 1 ? a.bob : 0);
      if (a.opacity <= 0.001) continue;
      if (a.opacity < 1) { gl.toLayer(2, () => (sw >= 0.5 ? drawSide() : drawFront())); gl.showLayer(2, a.opacity); }
      else if (sw <= 0) drawFront();
      else if (sw >= 1) drawSide();
      else {
        // cross-fade the BODIES as whole images (not layer by layer); the HEAD comes from exactly one puppet
        // (switches at the midpoint, full opacity) -- never two noses / two mouths on screen
        const head = sw < 0.5 ? drawFront : drawSide;
        head('headBack');                                   // back hair / hood back: behind the bodies
        gl.toLayer(0, () => drawFront('body')); gl.toLayer(1, () => drawSide('body'));
        gl.showLayer(0, 1 - sw); gl.showLayer(1, sw);
        head('headFront');
      }
    }
    for (const l of bg.layers) if (l.parallax > 1 || l.front) layer(l);      // foreground: quilt, table, bushes
    this.drawUI(sc, t, (x, y) => [(x - gx) * z + W / 2, (y - cy) * z + H / 2], z);
    // fade in/out at scene cuts
    const fin = ease((t - sc.t0) / 0.4), fout = ease((sc.t1 - t) / 0.4);
    const black = 1 - Math.min(si === 0 ? ease(t / 0.6) : fin, si === this.tl.scenes.length - 1 ? ease((sc.t1 - t) / 0.9) : fout);
    if (black > 0.001) gl.quad(gl.black, W, H, 1, 0, 0, black);
  }

  // ------------------------------------------------------------------------------------------ UI overlays
  drawUI(sc, t, toScreen, z) {
    const ov = sc.overlays || [], props = sc.props || [], light = sc.light;
    const hasFlower = this.actors.some((a) => a.s.flower);
    if (!ov.length && !props.length && !light && !hasFlower && !sc.ball) return;
    if (!this.ui) { this.ui = Object.assign(document.createElement('canvas'), { width: W, height: H }); this.uiCtx = this.ui.getContext('2d'); }
    const c = this.uiCtx;
    c.clearRect(0, 0, W, H);
    if (light) this.uiLight(c, light, t);
    for (const p of props) if (p.type === 'steam') this.uiSteam(c, toScreen(p.x, p.y), t, z);
    if (sc.ball) this.uiBall(c, sc.ball, t, toScreen, z);
    for (const a of this.actors) {
      if (a.s.flower && this.screen[a.s.id]) {
        const who = this.screen[a.s.id];
        const hPos = who.handL || [who.sx + (who.dir || 1) * who.h * 0.14, who.gy - who.h * 0.48];
        this.uiFlower(c, hPos, who.dir || 1, who.h, z, t);
      }
    }
    this.uiPanels = ov.filter((o) => o.type === 'story' && t >= o.t0 - 0.5 && t <= o.t1).map(() => [1300, 90, 1780, 940]);
    this.uiChat(c, ov, t);
    for (const o of ov) {
      if (o.type === 'card' && t >= o.t0 && t <= o.t1) this.uiCard(c, o, t);
      if (o.type === 'sfx' && t >= o.t && t <= o.t + 1.1) this.uiSfx(c, o, t);
      if (o.type === 'papers' && t >= o.t0 && t <= o.t1 + 0.3) this.uiPapers(c, o, t);
      if (o.type === 'story' && t >= o.t0 && t <= o.t1) this.uiStory(c, o, t);
      if (o.type === 'title' && t >= o.t0 && t <= o.t1) this.uiTitle(c, o, t);
    }
    this.uiTex = this.gl.canvasTexture(this.ui, this.uiTex);
    this.gl.quad(this.uiTex, W, H, 1, 0, 0, 1);
  }

  uiFlower(c, [hx, hy], dir, h, z, t) {
    c.save();
    c.lineCap = 'round';
    c.lineJoin = 'round';
    const s = (h / 760);
    const sway = Math.sin(t * 2.5) * 0.04;
    c.translate(hx, hy);
    c.rotate(sway);

    // 1. Stem (green stalk)
    c.beginPath();
    c.moveTo(-2 * s, 25 * s);
    c.quadraticCurveTo(0, 5 * s, 2 * s, -68 * s);
    c.strokeStyle = '#275e14';
    c.lineWidth = 3.6 * s;
    c.stroke();

    c.beginPath();
    c.moveTo(-2 * s, 25 * s);
    c.quadraticCurveTo(0, 5 * s, 2 * s, -68 * s);
    c.strokeStyle = '#439e22';
    c.lineWidth = 2.2 * s;
    c.stroke();

    // 2. Leaf Left (y = -25s)
    c.save();
    c.translate(0, -25 * s);
    c.rotate(-0.45);
    c.beginPath();
    c.moveTo(0, 0);
    c.quadraticCurveTo(-14 * s, -8 * s, -22 * s, -4 * s);
    c.quadraticCurveTo(-12 * s, 8 * s, 0, 0);
    c.fillStyle = '#48a825';
    c.fill();
    c.strokeStyle = '#275e14';
    c.lineWidth = 1.0 * s;
    c.stroke();
    c.beginPath();
    c.moveTo(0, 0);
    c.lineTo(-16 * s, -3 * s);
    c.strokeStyle = '#7fe655';
    c.lineWidth = 0.8 * s;
    c.stroke();
    c.restore();

    // 3. Leaf Right (y = -42s)
    c.save();
    c.translate(1 * s, -42 * s);
    c.rotate(0.5);
    c.beginPath();
    c.moveTo(0, 0);
    c.quadraticCurveTo(12 * s, -6 * s, 18 * s, -2 * s);
    c.quadraticCurveTo(10 * s, 7 * s, 0, 0);
    c.fillStyle = '#48a825';
    c.fill();
    c.strokeStyle = '#275e14';
    c.lineWidth = 1.0 * s;
    c.stroke();
    c.beginPath();
    c.moveTo(0, 0);
    c.lineTo(13 * s, -2 * s);
    c.strokeStyle = '#7fe655';
    c.lineWidth = 0.8 * s;
    c.stroke();
    c.restore();

    // 4. Wildflower Blossom
    const fx = 2 * s, fy = -70 * s;
    const nPetals = 5;
    const petalDist = 9 * s;
    const petalR = 12 * s;

    for (let i = 0; i < nPetals; i++) {
      const ang = i * (Math.PI * 2 / nPetals) - Math.PI / 2;
      const px = fx + Math.cos(ang) * petalDist;
      const py = fy + Math.sin(ang) * petalDist;
      c.beginPath();
      c.arc(px, py, petalR, 0, Math.PI * 2);
      c.fillStyle = '#b82346';
      c.fill();
    }

    for (let i = 0; i < nPetals; i++) {
      const ang = i * (Math.PI * 2 / nPetals) - Math.PI / 2;
      const px = fx + Math.cos(ang) * petalDist;
      const py = fy + Math.sin(ang) * petalDist;
      c.beginPath();
      c.arc(px, py, petalR - 1.2 * s, 0, Math.PI * 2);
      const grad = c.createRadialGradient(px - 2 * s, py - 2 * s, 2 * s, px, py, petalR);
      grad.addColorStop(0, '#ff9ebb');
      grad.addColorStop(0.7, '#ff547a');
      grad.addColorStop(1, '#db2c53');
      c.fillStyle = grad;
      c.fill();
    }

    // Pistil
    c.beginPath();
    c.arc(fx, fy, 8.5 * s, 0, Math.PI * 2);
    c.fillStyle = '#b8770b';
    c.fill();

    c.beginPath();
    c.arc(fx, fy, 7.5 * s, 0, Math.PI * 2);
    const cGrad = c.createRadialGradient(fx - 2 * s, fy - 2 * s, 1.5 * s, fx, fy, 7.5 * s);
    cGrad.addColorStop(0, '#fff494');
    cGrad.addColorStop(0.5, '#ffcc00');
    cGrad.addColorStop(1, '#e69900');
    c.fillStyle = cGrad;
    c.fill();

    c.beginPath();
    c.arc(fx - 2.5 * s, fy - 2.5 * s, 2.2 * s, 0, Math.PI * 2);
    c.fillStyle = 'rgba(255, 255, 255, 0.85)';
    c.fill();

    c.restore();
  }

  rr(c, x, y, w, h, r) { c.beginPath(); c.roundRect(x, y, w, h, r); }

  // pick the candidate box (top-left x,y) that covers the characters least; stays on screen, above the subtitles
  // anchor = the speaker's head: among spots that cover nobody, the closest one wins
  place(w, h, cands, anchor) {
    const boxes = Object.values(this.screen).map((s) => [s.sx - s.h * 0.2, s.top - s.h * 0.04, s.sx + s.h * 0.2, s.gy]);
    const panels = (this.uiPanels || []).map((b) => [...b, 0]);          // story card etc.: never cover them
    const M = 24, BOT = H - 150;
    for (let gy = 0; gy <= 4; gy++) for (let gx = 0; gx <= 12; gx++) cands.push([gx * (W - w) / 12, gy * (BOT - h) / 4]);
    let best = null, bestCost = Infinity;
    cands.forEach(([x, y], i) => {
      x = clamp(x, M, W - M - w); y = clamp(y, M, BOT - h);
      let cost = i * 1e-3;                                 // earlier candidates win ties
      if (anchor) cost += 6 * Math.hypot(x + w / 2 - anchor[0], y + h / 2 - anchor[1]);
      for (const [x0, y0, x1, y1] of panels) {
        const ox = Math.max(0, Math.min(x + w, x1) - Math.max(x, x0)), oy = Math.max(0, Math.min(y + h, y1) - Math.max(y, y0));
        cost += 4 * ox * oy;
      }
      for (const [x0, y0, x1, y1] of boxes) {
        const ox = Math.max(0, Math.min(x + w, x1) - Math.max(x, x0)), oy = Math.max(0, Math.min(y + h, y1) - Math.max(y, y0));
        const face = Math.max(0, Math.min(y + h, y0 + (y1 - y0) * 0.3) - Math.max(y, y0));   // heads count triple
        cost += ox * (oy + 2 * face);
      }
      if (cost < bestCost) { bestCost = cost; best = [x, y]; }
    });
    return best;
  }

  wrap(c, text, maxW) {                         // CJK-aware line wrapping
    const lines = []; let cur = '';
    for (const ch of text) {
      if (c.measureText(cur + ch).width > maxW && cur) { lines.push(cur); cur = ch; } else cur += ch;
    }
    if (cur) lines.push(cur);
    return lines;
  }

  uiLight(c, L, t) {                            // night: darkness with the phone-flashlight cone cut out
    if (!this.dark) { this.dark = Object.assign(document.createElement('canvas'), { width: W, height: H }); }
    const d = this.dark.getContext('2d');
    d.globalCompositeOperation = 'source-over';
    d.clearRect(0, 0, W, H);
    d.fillStyle = `rgba(6,10,30,${L.dark ?? 0.45})`;
    d.fillRect(0, 0, W, H);
    const who = L.flashlight && this.screen[L.flashlight];
    if (who) {
      const dir = who.dir, h = who.h;
      const [hx, hy] = who.phone || [who.sx + dir * h * 0.06, who.gy - h * 0.40];   // the phone in her hand
      const gx = who.sx + dir * h * 0.95, gy2 = who.gy - h * 0.02;         // lit patch on the ground ahead
      const beam = (ctx, a0, a1) => {                                        // cone from the hand to the ground
        const g = ctx.createLinearGradient(hx, hy, gx, gy2);
        g.addColorStop(0, `rgba(255,244,200,${a0})`); g.addColorStop(1, `rgba(255,244,200,${a1})`);
        ctx.fillStyle = g; ctx.beginPath();
        ctx.moveTo(hx, hy - h * 0.015); ctx.lineTo(gx + dir * h * 0.05, gy2 - h * 0.30);
        ctx.quadraticCurveTo(gx + dir * h * 0.42, gy2, gx + dir * h * 0.05, gy2 + h * 0.08);
        ctx.lineTo(hx, hy + h * 0.015); ctx.closePath(); ctx.fill();
      };
      d.globalCompositeOperation = 'destination-out';
      beam(d, 0.9, 0.75);
      d.save(); d.translate(gx, gy2); d.scale(1.8, 0.5);
      const g = d.createRadialGradient(0, 0, 10, 0, 0, h * 0.42);
      g.addColorStop(0, 'rgba(0,0,0,0.95)'); g.addColorStop(1, 'rgba(0,0,0,0)');
      d.fillStyle = g; d.beginPath(); d.arc(0, 0, h * 0.42, 0, Math.PI * 2); d.fill(); d.restore();
      const g2 = d.createRadialGradient(who.sx, who.gy - h * 0.5, 20, who.sx, who.gy - h * 0.5, h * 0.55);
      g2.addColorStop(0, 'rgba(0,0,0,0.6)'); g2.addColorStop(1, 'rgba(0,0,0,0)');
      d.fillStyle = g2; d.fillRect(0, 0, W, H);
      d.globalCompositeOperation = 'source-over';
      c.drawImage(this.dark, 0, 0);
      c.save(); c.globalCompositeOperation = 'lighter';
      beam(c, 0.22, 0.06);                                                   // visible beam glow
      c.translate(gx, gy2); c.scale(1.8, 0.5);
      const g3 = c.createRadialGradient(0, 0, 10, 0, 0, h * 0.4);
      g3.addColorStop(0, 'rgba(255,240,190,0.22)'); g3.addColorStop(1, 'rgba(255,240,190,0)');
      c.fillStyle = g3; c.beginPath(); c.arc(0, 0, h * 0.4, 0, Math.PI * 2); c.fill(); c.restore();
      c.fillStyle = 'rgba(255,255,240,0.9)'; c.beginPath(); c.arc(hx, hy, 5, 0, Math.PI * 2); c.fill();   // the phone light
    } else c.drawImage(this.dark, 0, 0);
  }

  // golden ball (青蛙王子): held in an actor's right hand, tossed up and caught, passed between two actors,
  // rolled into the well; it follows the hand every frame, so gestures move it too
  uiBall(c, B, t, toScreen, z) {
    const r = 26 * z;
    const hand = (id) => {
      const s = this.screen[id];
      return s && s.handR ? [s.handR[0], s.handR[1] - r * 0.55] : null;
    };
    const arc = (p, q, u, hgt) => [p[0] + (q[0] - p[0]) * u, p[1] + (q[1] - p[1]) * u - 4 * hgt * u * (1 - u)];
    let holder = B.holder, pos = null, visible = !!holder, spin = t * 2;
    for (const e of [...(B.events || [])].sort((m, n) => m.t0 - n.t0)) {
      if (t < e.t0) break;
      const live = t <= e.t1, u = (t - e.t0) / Math.max(0.01, e.t1 - e.t0);
      if (e.mode === 'hold') { holder = e.actor; visible = true; pos = null; }
      else if (e.mode === 'hide') { visible = false; pos = null; }
      else if (e.mode === 'toss' && live) {
        holder = e.actor; visible = true;
        const h = hand(e.actor), who = this.screen[e.actor];
        const T = 1.3, ph = ((t - e.t0) % T) / T;
        if (h && who) pos = [h[0], h[1] - 4 * who.h * 0.32 * ph * (1 - ph)];
        spin = t * 9;
      } else if (e.mode === 'pass' && live) {
        visible = true;
        const T = Math.min(1.6, e.t1 - e.t0), n = Math.floor((t - e.t0) / T), ph = ((t - e.t0) % T) / T;
        const [from, to] = n % 2 ? [e.to, e.actor] : [e.actor, e.to];
        const p = hand(from), q = hand(to), who = this.screen[e.actor];
        if (p && q && who) pos = arc(p, q, ph, who.h * 0.22);
        holder = ph > 0.5 ? to : from;
        spin = t * 9;
      } else if (e.mode === 'roll') {
        if (!live) { visible = false; pos = null; continue; }
        const p = hand(e.actor) || pos, q = toScreen(e.x, e.y);
        if (p) pos = arc(p, q, Math.min(1, u * 1.15), 120 * z);
        visible = true; spin = t * 12;
        if (u > 0.92) c.globalAlpha = Math.max(0, (1 - u) / 0.08);
      } else if (!live && e.mode === 'pass') {
        const T = Math.min(1.6, e.t1 - e.t0), n = Math.max(1, Math.round((e.t1 - e.t0) / T));
        holder = n % 2 ? e.to : e.actor; pos = null; visible = true;
      } else if (!live && e.mode === 'toss') { pos = null; }
    }
    if (!visible) { c.globalAlpha = 1; return; }
    const [x, y] = pos || hand(holder) || [NaN, NaN];
    if (!isFinite(x)) { c.globalAlpha = 1; return; }
    c.save();
    const glow = c.createRadialGradient(x, y, r * 0.6, x, y, r * 1.9);
    glow.addColorStop(0, 'rgba(255,215,90,0.45)'); glow.addColorStop(1, 'rgba(255,215,90,0)');
    c.fillStyle = glow; c.beginPath(); c.arc(x, y, r * 1.9, 0, Math.PI * 2); c.fill();
    const g = c.createRadialGradient(x - r * 0.35, y - r * 0.4, r * 0.1, x, y, r);
    g.addColorStop(0, '#fff6b0'); g.addColorStop(0.45, '#f7ca39'); g.addColorStop(1, '#b5860f');
    c.fillStyle = g; c.beginPath(); c.arc(x, y, r, 0, Math.PI * 2); c.fill();
    c.lineWidth = Math.max(1, r * 0.08); c.strokeStyle = '#6a4f08'; c.stroke();
    c.strokeStyle = 'rgba(255,255,255,0.55)'; c.lineWidth = r * 0.12;          // spinning band = motion cue
    c.beginPath(); c.ellipse(x, y, r * 0.85, r * 0.35, spin, 0, Math.PI * 2); c.stroke();
    c.fillStyle = '#ffffff'; c.beginPath(); c.arc(x - r * 0.35, y - r * 0.38, r * 0.22, 0, Math.PI * 2); c.fill();
    c.restore();
    c.globalAlpha = 1;
  }

  uiSteam(c, [x, y], t, z) {
    c.save(); c.lineCap = 'round';
    for (let k = 0; k < 3; k++) {
      const ph = (t * 0.6 + k / 3) % 1;
      c.strokeStyle = `rgba(255,255,255,${0.55 * Math.sin(Math.PI * ph)})`; c.lineWidth = 7 * z;
      c.beginPath();
      for (let i = 0; i <= 12; i++) {
        const u = i / 12, yy = y - (20 + ph * 120 + u * 90) * z;
        const xx = x + (k - 1) * 34 * z + Math.sin(u * 5 + t * 3 + k) * 12 * z;
        i ? c.lineTo(xx, yy) : c.moveTo(xx, yy);
      }
      c.stroke();
    }
    c.restore();
  }

  uiCard(c, o, t) {                             // time card, top-left
    const a = Math.min(ease((t - o.t0) / 0.3), ease((o.t1 - t) / 0.4));
    c.save(); c.globalAlpha = a; c.translate(-40 * (1 - a), 0);
    c.font = 'bold 44px "Microsoft JhengHei"';
    const w = c.measureText(o.text).width + 120;
    c.fillStyle = 'rgba(20,18,40,0.78)'; this.rr(c, 60, 60, w, 84, 42); c.fill();
    c.strokeStyle = '#ff5a5a'; c.lineWidth = 5; c.beginPath(); c.arc(106, 102, 20, 0, Math.PI * 2); c.stroke();
    c.beginPath(); c.moveTo(106, 102); c.lineTo(106, 90); c.moveTo(106, 102); c.lineTo(116, 106); c.stroke();
    c.fillStyle = '#fff'; c.textBaseline = 'middle'; c.fillText(o.text, 142, 104);
    c.restore();
  }

  uiChat(c, ov, t) {                            // phone chat panel (pink-brown bubbles = grandma)
    const open = ov.find((o) => o.type === 'chat_open' && o.t <= t);
    if (!open) return;
    const close = ov.find((o) => o.type === 'chat_close' && o.t <= t + 0.35 && o.t >= open.t);
    let a = ease((t - open.t) / 0.35);
    if (close) a = Math.min(a, ease((close.t + 0.35 - t) / 0.35));
    if (a <= 0) return;
    const X = 1230 + (1 - a) * 700, Y = 70, PW = 620, PH = 940;
    c.save();
    c.shadowColor = 'rgba(0,0,0,0.35)'; c.shadowBlur = 30;
    c.fillStyle = '#1d1b22'; this.rr(c, X - 14, Y - 14, PW + 28, PH + 28, 56); c.fill();
    c.shadowBlur = 0;
    c.fillStyle = '#f7efe9'; this.rr(c, X, Y, PW, PH, 44); c.fill();
    c.fillStyle = '#ecd9ce'; this.rr(c, X, Y, PW, 110, 44); c.fill(); c.fillRect(X, Y + 60, PW, 50);
    c.fillStyle = '#c9967f'; c.beginPath(); c.arc(X + 70, Y + 58, 30, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#fff'; c.font = 'bold 28px "Microsoft JhengHei"'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.fillText('婆', X + 70, Y + 59);
    c.textAlign = 'left'; c.fillStyle = '#4a3530'; c.font = 'bold 36px "Microsoft JhengHei"';
    c.fillText(open.title || '外婆', X + 116, Y + 58);
    // messages, newest at the bottom
    c.font = '34px "Microsoft JhengHei"';
    const msgs = ov.filter((o) => o.type === 'chat' && o.t <= t);
    let y = Y + PH - 36;
    c.save(); c.beginPath(); c.rect(X, Y + 112, PW, PH - 120); c.clip();
    for (let i = msgs.length - 1; i >= 0; i--) {
      const m = msgs[i], mine = m.from !== 'grandma';
      const lines = this.wrap(c, m.text, PW - 190);
      const bw = Math.max(...lines.map((l) => c.measureText(l).width)) + 48, bh = lines.length * 46 + 30;
      const pop = ease((t - m.t) / 0.2), sc = 0.6 + 0.4 * pop;
      y -= bh + 20;
      const bx = mine ? X + PW - 30 - bw : X + 30;
      c.save(); c.globalAlpha = pop;
      c.translate(mine ? bx + bw : bx, y + bh); c.scale(sc, sc); c.translate(-(mine ? bx + bw : bx), -(y + bh));
      c.fillStyle = mine ? '#ffffff' : '#e8c0ad';
      this.rr(c, bx, y, bw, bh, 26); c.fill();
      if (mine) { c.strokeStyle = '#d8cfc8'; c.lineWidth = 2; c.stroke(); }
      c.fillStyle = '#3a2a26'; c.textBaseline = 'top';
      lines.forEach((l, k) => c.fillText(l, bx + 24, y + 16 + k * 46));
      c.restore();
      if (y < Y + 120) break;
    }
    c.restore();
    c.restore();
  }

  uiSfx(c, o, t) {                              // comic pop text next to the speaker's head
    const who = this.screen[o.actor];
    const u = t - o.t, pop = u < 0.12 ? u / 0.12 * 1.25 : u < 0.25 ? 1.25 - (u - 0.12) / 0.13 * 0.25 : 1;
    const a = Math.min(1, (1.1 - u) / 0.25);
    c.save();
    c.font = '900 150px "Microsoft JhengHei"';
    const bw = c.measureText(o.text).width + 120, bh = 300;        // text + burst lines
    if (!o._pos || o._t !== o.t) {                                 // choose once per pop (no jumping around)
      const sx = who ? who.sx : W / 2, top = who ? who.top : 200, hh = who ? who.h : 600;
      o._pos = this.place(bw, bh, [[sx + hh * 0.2, top - 40], [sx - hh * 0.2 - bw, top - 40], [sx - bw / 2, top - bh - 10],
        [sx + hh * 0.2, top + hh * 0.3], [sx - hh * 0.2 - bw, top + hh * 0.3]], [sx, top + hh * 0.1]);
      o._t = o.t;
    }
    const x = o._pos[0] + bw / 2, y = o._pos[1] + bh / 2 + 30;
    c.globalAlpha = clamp(a, 0, 1);
    c.translate(x + Math.sin(u * 60) * 6 * (u < 0.4 ? 1 : 0), y); c.rotate(-0.12); c.scale(pop, pop);
    c.font = '900 150px "Microsoft JhengHei"'; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.lineJoin = 'round'; c.lineWidth = 18; c.strokeStyle = '#2a1a10'; c.strokeText(o.text, 0, 0);
    c.fillStyle = '#ffe14d'; c.fillText(o.text, 0, 0);
    for (let k = 0; k < 6; k++) {               // burst lines
      const ang = -Math.PI / 2 + (k - 2.5) * 0.35;
      c.strokeStyle = '#ffe14d'; c.lineWidth = 8; c.beginPath();
      c.moveTo(Math.cos(ang) * 170, Math.sin(ang) * 110 - 20); c.lineTo(Math.cos(ang) * 230, Math.sin(ang) * 150 - 20); c.stroke();
    }
    c.restore();
  }

  uiPapers(c, o, t) {                           // the wolf's stack of "screenshot" printouts
    const who = this.screen[o.actor];
    const a = Math.min(ease((t - o.t0) / 0.25), ease((o.t1 + 0.3 - t) / 0.3));
    const pw = 360, ph = 420;                                      // the stack of three sheets
    if (!o._pos) {
      const sx = who ? who.sx : W / 2, top = who ? who.top : 200, hh = who ? who.h : 600;
      o._pos = this.place(pw, ph, [[sx - hh * 0.22 - pw, top + hh * 0.15], [sx + hh * 0.22, top + hh * 0.15],
        [sx - hh * 0.22 - pw, top], [sx + hh * 0.22, top]], [sx, top + hh * 0.3]);
    }
    const [x0, y0] = o._pos;
    c.save(); c.globalAlpha = a;
    for (let k = 2; k >= 0; k--) {
      c.save();
      c.translate(x0 + k * 26, y0 + (1 - a) * 80 + k * 14); c.rotate(-0.1 + k * 0.07 + Math.sin(t * 6 + k) * 0.015);
      c.fillStyle = k ? '#efe6cf' : '#fbf6e8'; c.shadowColor = 'rgba(0,0,0,0.3)'; c.shadowBlur = 12;
      c.fillRect(0, 0, 300, 380); c.shadowBlur = 0;
      if (k === 0) {
        c.fillStyle = '#8a3b2a'; c.font = 'bold 30px "Microsoft JhengHei"'; c.fillText('對話紀錄截圖', 22, 48);
        c.font = '22px "Microsoft JhengHei"'; c.fillStyle = '#5a4a3a';
        const rows = ['03:12:05 踩斷樹枝', '03:12:07 分貝 62dB', '03:12:09 心跳 128', '03:12:11 無錄影 ?!', '03:12:14 請勿公審'];
        rows.forEach((r, i) => c.fillText(r, 24, 100 + i * 50));
        c.strokeStyle = '#d33'; c.lineWidth = 5; c.beginPath(); c.ellipse(150, 184, 130, 30, 0, 0, Math.PI * 2); c.stroke();
      }
      c.restore();
    }
    c.restore();
  }

  uiStory(c, o, t) {                            // social "story" post card
    const a = Math.min(ease((t - o.t0) / 0.3), ease((o.t1 - t) / 0.35));
    const X = 1300, Y = 90, PW = 480, PH = 850;
    c.save(); c.globalAlpha = a; c.translate(0, (1 - a) * 60);
    const g = c.createLinearGradient(X, Y, X + PW, Y + PH);
    g.addColorStop(0, '#f58529'); g.addColorStop(0.5, '#dd2a7b'); g.addColorStop(1, '#8134af');
    c.shadowColor = 'rgba(0,0,0,0.4)'; c.shadowBlur = 30; c.fillStyle = g; this.rr(c, X, Y, PW, PH, 30); c.fill(); c.shadowBlur = 0;
    c.fillStyle = 'rgba(255,255,255,0.35)'; this.rr(c, X + 24, Y + 20, PW - 48, 6, 3); c.fill();
    c.fillStyle = '#fff'; this.rr(c, X + 24, Y + 20, (PW - 48) * clamp((t - o.t0) / (o.t1 - o.t0), 0, 1), 6, 3); c.fill();
    c.fillStyle = '#e8c0ad'; c.beginPath(); c.arc(X + 60, Y + 72, 26, 0, Math.PI * 2); c.fill();
    c.fillStyle = '#fff'; c.font = 'bold 28px "Microsoft JhengHei"'; c.textBaseline = 'middle';
    c.fillText(`${o.name} · 1分鐘前`, X + 100, Y + 72);
    c.font = 'bold 44px "Microsoft JhengHei"'; c.textAlign = 'center';
    const lines = this.wrap(c, o.text, PW - 90);
    lines.forEach((l, k) => c.fillText(l, X + PW / 2, Y + PH / 2 - (lines.length - 1) * 30 + k * 60));
    c.font = '60px "Microsoft JhengHei"'; c.fillText('🍜', X + PW / 2, Y + PH - 150);
    c.restore();
  }

  uiTitle(c, o, t) {
    const a = Math.min(ease((t - o.t0) / 0.5), 1);
    c.save(); c.globalAlpha = a;
    const fs = o.size || 120, y = o.y || (H / 2 - 40);
    c.font = `900 ${fs}px "Microsoft JhengHei"`; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.lineWidth = fs * 0.12; c.strokeStyle = '#2a1a10'; c.strokeText(o.text, W / 2, y);
    c.fillStyle = '#fff4d6'; c.fillText(o.text, W / 2, y);
    c.restore();
  }

  shadowTex() {
    if (!this._sh) {
      const c = Object.assign(document.createElement('canvas'), { width: 128, height: 32 }), x = c.getContext('2d');
      const g = x.createRadialGradient(64, 16, 2, 64, 16, 64);
      g.addColorStop(0, 'rgba(40,30,20,0.42)'); g.addColorStop(1, 'rgba(40,30,20,0)');
      x.setTransform(1, 0, 0, 0.25, 0, 12); x.fillStyle = g; x.fillRect(0, 0, 128, 128);
      this._sh = this.gl.texture(c);
    }
    return this._sh;
  }

  drawShadow(sx, sy, w, bob) {
    const s = w / 128 * (1 + bob / 200);
    this.gl.quad(this.shadowTex(), 128, 32, s, sx - 64 * s, sy - 16 * s);
  }
}
