/* reel-kit.js — proven building blocks from the reels she loved (kids closet v8, white wall v2, warm wall, walnut v2,
   brand showreel v2.1). Building blocks, NOT a template: the idea, structure and signature move still change per project
   (content-log rotation). Copy into reel/assets/ (studio/tools/new_project.sh does it) and load after gsap.min.js.

   All helpers write into ONE paused GSAP timeline, animate only transform / opacity / filter / mask, deterministic.

   const tl = gsap.timeline({ paused: true });
   const K = RK.kit(tl);                       // bind the helpers to this timeline
   K.path("#sA", [[t, cx, cy, scale], ...]);   // continuous camera (Catmull-Rom, ease none) - one path per stage
   K.card("#t1", in, out);                     // word mask-reveal card (.t > .ln > span), right-to-left stagger
   K.blurOut("#LA", t, px) / K.blurIn("#LB", t, px)   // whip / dive-through: hand over INSIDE the blur
   K.dissolve("#LA", "#LB", t, dur)            // motion dissolve (both stages keep moving)
   K.flash("#flash", t)                        // warm light flash; swap stages at t, flash fades after
   K.maskFill("#lit", t, dur, {soft:15})       // real lit photo fills bottom->top over the unlit one (light moment)
   K.breathe("#bloom", [[t, opacity], ...])    // real-pixel bloom (screen) breathing
   K.cssDoor("#d1", sign, t, dur, {handover})  // kids-closet style door (face/back/shade/edge/bot/fs children)
   K.rig(RIG, names, prefixes) -> {door, drawer} // calibrated 3D rig (walnut v2): matrix3d per frame
   K.endCard(t)                                // living end card (#end, #endglow, #endin, img, .l1, .l2)
   K.done(duration)                            // pads the timeline and registers it as "main"
*/
(function () {
  const $ = id => document.getElementById(id.replace(/^#/, ""));
  const view = (cx, cy, s) => ({ scale: s, x: 540 - cx * s, y: 960 - cy * s });

  function homog(w, ht, q) {
    const src = [[0, 0], [w, 0], [w, ht], [0, ht]], A = [], b = [];
    for (let i = 0; i < 4; i++) {
      const [x, y] = src[i], [X, Y] = q[i];
      A.push([x, y, 1, 0, 0, 0, -x * X, -y * X]); b.push(X);
      A.push([0, 0, 0, x, y, 1, -x * Y, -y * Y]); b.push(Y);
    }
    for (let c = 0; c < 8; c++) {
      let p = c; for (let r = c + 1; r < 8; r++) if (Math.abs(A[r][c]) > Math.abs(A[p][c])) p = r;
      [A[c], A[p]] = [A[p], A[c]]; [b[c], b[p]] = [b[p], b[c]];
      for (let r = 0; r < 8; r++) if (r !== c) { const f = A[r][c] / A[c][c]; for (let k = c; k < 8; k++) A[r][k] -= f * A[c][k]; b[r] -= f * b[c]; }
    }
    const h = b.map((v, i) => v / A[i][i]); return [h[0], h[1], h[2], h[3], h[4], h[5], h[6], h[7], 1];
  }
  const m3d = H => `matrix3d(${H[0]},${H[3]},0,${H[6]},${H[1]},${H[4]},0,${H[7]},0,0,1,0,${H[2]},${H[5]},0,${H[8]})`;
  const put = (el, w, h, q) => { el.style.transform = m3d(homog(w, h, q)); };

  function kit(tl) {
    gsap.set(".st", { transformOrigin: "0 0" });
    gsap.set(".t span", { yPercent: 115 });

    // one camera path per stage: Catmull-Rom through (time, cx, cy, scale) keys -> continuous velocity, no stop-go
    function path(el, keys) {
      const P = { t: keys[0][0] };
      const at = t => {
        let i = 0; while (i < keys.length - 2 && t > keys[i + 1][0]) i++;
        const k0 = keys[Math.max(i - 1, 0)], k1 = keys[i], k2 = keys[i + 1], k3 = keys[Math.min(i + 2, keys.length - 1)];
        const u = Math.min(1, Math.max(0, (t - k1[0]) / (k2[0] - k1[0])));
        const cr = j => {
          const m1 = (k2[j] - k0[j]) / (k2[0] - k0[0] || 1) * (k2[0] - k1[0]);
          const m2 = (k3[j] - k1[j]) / (k3[0] - k1[0] || 1) * (k2[0] - k1[0]);
          const u2 = u * u, u3 = u2 * u;
          return (2 * u3 - 3 * u2 + 1) * k1[j] + (u3 - 2 * u2 + u) * m1 + (-2 * u3 + 3 * u2) * k2[j] + (u3 - u2) * m2;
        };
        return view(cr(1), cr(2), cr(3));
      };
      gsap.set(el, at(keys[0][0]));
      const T0 = keys[0][0], T1 = keys[keys.length - 1][0];
      tl.fromTo(P, { t: T0 }, { t: T1, duration: T1 - T0, ease: "none", immediateRender: false, onUpdate: () => gsap.set(el, at(P.t)) }, T0);
    }

    const card = (sel, at, out) => {
      tl.fromTo(sel + " span", { yPercent: 115 }, { yPercent: 0, duration: 0.45, stagger: 0.07, ease: "power3.out", immediateRender: false }, at);
      if (out) tl.to(sel + " span", { yPercent: -115, duration: 0.3, stagger: 0.04, ease: "power2.in" }, out);
    };

    const blurOut = (sel, t, px = 14, dur = 0.24) =>
      tl.fromTo(sel, { filter: "blur(0px)" }, { filter: `blur(${px}px)`, duration: dur, ease: "power2.in", immediateRender: false }, t - dur);
    const blurIn = (sel, t, px = 14, dur = 0.3) =>
      tl.fromTo(sel, { filter: `blur(${px}px)` }, { filter: "blur(0px)", duration: dur, ease: "power2.out", immediateRender: false }, t);
    // hard swap of layers at t (hidden inside a blur / flash peak)
    const swap = (from, to, t) => { tl.set(to, { opacity: 1 }, t); tl.set(from, { opacity: 0 }, t); };

    const dissolve = (from, to, t, dur = 0.45) => {
      tl.set(to, { opacity: 1 }, t);
      tl.fromTo(from, { opacity: 1 }, { opacity: 0, duration: dur, ease: "sine.inOut", immediateRender: false }, t);
    };

    // light flash: peaks at t (swap stages at t), then fades out
    const flash = (sel, t, peak = 0.85) => {
      tl.fromTo(sel, { opacity: 0 }, { opacity: peak, duration: 0.3, ease: "power2.in", immediateRender: false }, t - 0.3);
      tl.to(sel, { opacity: 0, duration: 0.6, ease: "power2.out" }, t);
    };

    // the REAL lit photo fills over the unlit one, bottom -> top (or any CSS direction)
    const maskFill = (sel, t, dur = 1.5, o = {}) => {
      const el = $(sel), soft = o.soft ?? 15, dir = o.dir ?? "to top", ease = o.ease ?? "power2.inOut";
      const s = { p: -20 };
      const apply = () => { const m = s.p >= 118 ? "none" : `linear-gradient(${dir},#000 ${s.p}%,transparent ${s.p + soft}%)`;
        el.style.webkitMaskImage = m; el.style.maskImage = m; };
      apply();
      tl.fromTo(s, { p: -20 }, { p: 120, duration: dur, ease, onUpdate: apply, immediateRender: false }, t);
    };

    const breathe = (sel, keys) => {
      gsap.set(sel, { opacity: keys[0][1] });
      for (let i = 1; i < keys.length; i++)
        tl.to(sel, { opacity: keys[i][1], duration: keys[i][0] - keys[i - 1][0], ease: "sine.inOut" }, keys[i - 1][0]);
    };

    // kids-closet door: rotateY on the real hinge side; children .shade .fs .bot (see reel-kit.css)
    const cssDoor = (id, sign, at, dur = 1.3, o = {}) => {
      tl.fromTo(id, { rotationY: 0 }, { rotationY: sign * (o.angle ?? 92), duration: dur, ease: "power2.inOut", immediateRender: false }, at);
      const on = { ".shade": 0.28, ".fs": 0.5, ".bot": 1 };
      for (const [el, val] of Object.entries(on))
        tl.fromTo(id + " " + el, { opacity: 0 }, { opacity: val, duration: el === ".bot" ? 0.12 : dur, ease: "power2.inOut", immediateRender: false }, at);
      if (o.handover) tl.set(id, { opacity: 0 }, at + dur);   // the real open photo underneath takes over
    };

    // calibrated 3D rig (walnut v2). RIG = output of doors_geom.py; elements: f_<n> k_<n> s_<n> ed_<n> in_<n> sh_<n>,
    // drawer: dr_front dr_cav dr_top dr_side. Before using: compare the rig's open state with the real open photo
    // (cmp_open); if the structure around the door differs, hand over to the real open photo inside a punch-in blur.
    function rig(RIG) {
      const Kf = RIG.K[0][0], Kcx = RIG.K[0][2], Kcy = RIG.K[1][2];
      const proj = P => { const c = [0, 1, 2].map(i => RIG.O[i] + P[0] * RIG.rx[i] + P[1] * RIG.ry[i] + P[2] * RIG.rz[i]);
        return [Kf * c[0] / c[2] + Kcx, Kf * c[1] / c[2] + Kcy]; };
      const add = (P, d) => [P[0] + d[0], P[1] + d[1], P[2] + d[2]];
      const T = RIG.thickness ?? 3.2;
      const area = q2 => { let a = 0; for (let i = 0; i < 4; i++) { const p = q2[i], r = q2[(i + 1) % 4]; a += p[0] * r[1] - r[0] * p[1]; } return a; };
      function door(name, phi) {
        const D = RIG.doors[name], P = D.P, hx = P[1][0];
        const rot = p => { const dx = p[0] - hx; return [hx + dx * Math.cos(phi), p[1], -dx * Math.sin(phi)]; };
        const R = P.map(rot), q = R.map(proj), n = [Math.sin(phi), 0, Math.cos(phi)];
        const f = $("f_" + name), k = $("k_" + name), s = $("s_" + name), e = $("ed_" + name);
        if (Math.sign(area(q)) === Math.sign(area(P.map(proj)))) {
          put(f, D.tw, D.th, q); f.style.opacity = 1; k.style.opacity = 0;
          put(s, D.tw, D.th, q); s.style.opacity = 0.22 * Math.sin(Math.min(phi, 1.4));
        } else {
          const qb = [q[1], q[0], q[3], q[2]];
          put(k, D.tw, D.th, qb); k.style.opacity = 1; f.style.opacity = 0;
          put(s, D.tw, D.th, qb); s.style.opacity = 0.12 * Math.max(0, 1 - phi / 1.9);
        }
        $("in_" + name).style.opacity = phi > 0.004 ? 1 : 0;
        const e0 = R[0], e3 = R[3], back = [-T * n[0], 0, -T * n[2]];
        put(e, 10, 100, [proj(e0), proj(add(e0, back)), proj(add(e3, back)), proj(e3)]);
        e.style.opacity = phi > 0.02 ? 1 : 0;
        put($("sh_" + name), 100, 100, P.map(proj));
        $("sh_" + name).style.opacity = phi < 0.004 ? 0 : 0.6 * Math.max(0, 1 - phi / 1.25);
      }
      function drawer(d) {
        const D = RIG.drawer, P = D.P, F = P.map(p => add(p, [0, 0, d])), on = Math.min(1, d / 10);
        put($("dr_front"), D.tw, D.th, F.map(proj));
        put($("dr_cav"), 100, 100, P.map(proj)); $("dr_cav").style.opacity = on;
        put($("dr_top"), 400, 120, [P[0], P[1], F[1], F[0]].map(proj)); $("dr_top").style.opacity = on;
        put($("dr_side"), 60, 160, [P[0], F[0], F[3], P[3]].map(proj)); $("dr_side").style.opacity = on;
      }
      const ST = {};
      const names = Object.keys(RIG.doors);
      names.forEach(n => (ST[n] = 0)); if (RIG.drawer) ST.drawer = 0;
      const upd = () => { names.forEach(n => door(n, ST[n])); if (RIG.drawer) drawer(ST.drawer); };
      upd();
      // open(name, at, dur): swings to the angle measured in the open photo (or pulls the drawer)
      const open = (name, at, dur = 1.4, ease = "power2.inOut") => {
        const to = name === "drawer" ? RIG.drawer.pull : RIG.doors[name].open * Math.PI / 180;
        tl.to(ST, { [name]: to, duration: dur, ease, onUpdate: upd }, at);
      };
      return { open, update: upd, proj };
    }

    const endCard = (t, hold = 3.0) => {
      gsap.set(["#end img", "#end .l1", "#end .l2"], { opacity: 0 });
      tl.fromTo("#end", { opacity: 0 }, { opacity: 1, duration: 0.5, ease: "sine.inOut", immediateRender: false }, t);
      tl.fromTo("#endglow", { opacity: 0, scale: 0.8 }, { opacity: 1, scale: 1.15, duration: hold, ease: "sine.out", immediateRender: false }, t);
      tl.fromTo("#end img", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.6, ease: "power2.out", immediateRender: false }, t + 0.3);
      tl.fromTo("#end .l1", { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.5, immediateRender: false }, t + 0.65);
      tl.fromTo("#end .l2", { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, immediateRender: false }, t + 1.0);
      tl.fromTo("#endin", { scale: 1 }, { scale: 1.06, duration: hold, ease: "none", immediateRender: false }, t);
    };

    const done = duration => {
      tl.set({}, {}, duration);
      window.__timelines = window.__timelines || {};
      window.__timelines["main"] = tl;
    };

    return { path, card, blurOut, blurIn, swap, dissolve, flash, maskFill, breathe, cssDoor, rig, endCard, done };
  }

  window.RK = { kit, view, homog, m3d, put };
})();
