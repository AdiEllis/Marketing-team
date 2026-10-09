"""Original background music, synthesized in code (zero cost, no licensing issues), synced to a reel's beat grid.

Usage:
  python3 -I studio/tools/compose.py spec.json out.wav

spec.json:
  {
    "duration": 15.0,          # seconds
    "bpm": 109.09,             # beat = 60/bpm
    "t0": 0.15,                # time of beat 0 (align beats to the edit's cuts)
    "chords": [["F3","A3","C4","E4"], ["C3","E3","G3","C4"], ...],   # one chord per bar (4 beats), cycles
    "melody": "musicbox",      # arpeggio voice: musicbox | piano
    "melody_mult": 4,          # arpeggio octave shift vs the chord voicing (4 = two octaves up, music-box register)
    "bass_gain": 0.35,
    "pad_from": 1.4,           # pad swells in at this time
    "ticks": true,             # soft clock tick on every beat
    "accents": [[4.0,"C5"], [4.55,"E5"]],   # bright bell hits on specific moments (door opens, reveals)
    "thumps": [10.05],         # soft low hits (doors closing, hard cuts)
    "whooshes": [7.65],        # short filtered-noise swells (whip pans)
    "end": 12.7,               # final chord here, then everything rings out and fades
    "lufs": -16
  }
Writes a 48 kHz stereo WAV. Mux with:
  ffmpeg -i reel.mp4 -i out.wav -c:v copy -c:a aac -b:a 192k -shortest reel_music.mp4
"""
import json
import sys
import wave

import numpy as np

SR = 48000
NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11, "Eb": 3, "Ab": 8}


def hz(n):
    name, octv = n[:-1], int(n[-1])
    return 440.0 * 2 ** ((NOTE[name] + 12 * (octv + 1) - 69) / 12)


def env(n, a, tau):
    t = np.arange(n) / SR
    e = np.exp(-t / tau)
    k = max(1, int(a * SR))
    e[:k] *= np.linspace(0, 1, k)
    return e


def tone(f, dur, partials, tau, a=0.004, detune=0.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for mult, amp, ptau in partials:
        s += amp * np.sin(2 * np.pi * f * mult * (1 + detune) * t) * np.exp(-t / (tau * ptau))
    return s * env(n, a, 1e9)


def musicbox(f, dur=2.5):
    return tone(f, dur, [(1, 1.0, 1.0), (2.0, 0.25, 0.6), (4.16, 0.12, 0.35), (6.3, 0.05, 0.2)], tau=0.9, a=0.002)


def piano(f, dur=3.0):
    return tone(f, dur, [(1, 1.0, 1.0), (2, 0.45, 0.7), (3, 0.2, 0.5), (4, 0.08, 0.35)], tau=1.4, a=0.006)


def bell(f, dur=3.0):
    return tone(f, dur, [(1, 1.0, 1.0), (2.76, 0.35, 0.5), (5.4, 0.18, 0.3), (8.93, 0.06, 0.2)], tau=1.1, a=0.001)


def pad(freqs, dur, attack=1.2):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for d in (-0.003, 0.003):
            s += np.sin(2 * np.pi * f * (1 + d) * t) + 0.25 * np.sin(2 * np.pi * 2 * f * (1 + d) * t)
    e = np.minimum(1, t / attack) * np.minimum(1, (dur - t) / 0.8).clip(0, 1)
    return s * e / (2 * len(freqs))


def noise_burst(dur, tau, seed, lp=0.15):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    x = rng.standard_normal(n)
    y = np.zeros(n)
    acc = 0.0
    for i in range(n):  # one-pole low-pass
        acc += lp * (x[i] - acc)
        y[i] = acc
    return y * env(n, 0.001, tau)


def reverb(x, seconds=1.4, mix=0.28, seed=7):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal(n) * np.exp(-t / (seconds / 4.5))
    ir = np.convolve(ir, np.ones(24) / 24, mode="same")  # darken the tail
    ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + n
    size = 1 << (m - 1).bit_length()
    wet = np.fft.irfft(np.fft.rfft(x, size) * np.fft.rfft(ir, size), size)[: len(x)]
    return (1 - mix) * x + mix * wet


def place(buf, sig, at, gain):
    i = int(at * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += gain * sig[: j - i]


def main():
    spec = json.load(open(sys.argv[1]))
    dur = spec["duration"]
    beat = 60.0 / spec["bpm"]
    t0 = spec.get("t0", 0.0)
    end = spec.get("end", dur)
    N = int((dur + 2) * SR)
    mel, low, padb, fx = (np.zeros(N) for _ in range(4))
    voice = musicbox if spec.get("melody", "musicbox") == "musicbox" else piano
    chords = spec["chords"]

    # arpeggio on eighth notes, bass on each bar, until the end chord
    k = 0
    while True:
        bt = t0 + k * beat
        if bt >= end - 1e-3:
            break
        bar = int(k // 4)
        ch = chords[bar % len(chords)]
        if k % 4 == 0:
            place(low, piano(hz(ch[0]) / 2, 3.0), bt, spec.get("bass_gain", 0.35))
        for h in (0, 1):
            note = ch[[1, 2, 3, 2][(k % 4)] if h == 0 else [3, 1, 2, 3][(k % 4)]]
            f = hz(note) * spec.get("melody_mult", 4)
            place(mel, voice(f), bt + h * beat / 2, 0.32 if h == 0 else 0.22)
        k += 1

    # pad under the body
    pf = spec.get("pad_from", 0.0)
    nb = int((end - pf) // (4 * beat)) + 1
    for b in range(nb):
        st = pf + b * 4 * beat
        bar = int(round((st - t0) / (4 * beat)))
        ch = chords[max(bar, 0) % len(chords)]
        place(padb, pad([hz(n) for n in ch[:3]], 4 * beat + 0.9, attack=0.9 if b else 1.4), st, 0.22)

    # end chord rings out
    ch = chords[0]
    place(low, piano(hz(ch[0]) / 2, 4.0), end, spec.get("bass_gain", 0.35))
    for i, n in enumerate(ch):
        place(mel, voice(hz(n) * spec.get("melody_mult", 4), 4.0), end + i * 0.07, 0.3)
    place(padb, pad([hz(n) for n in ch[:3]], dur - end + 0.5, attack=0.4), end, 0.22)

    for at, n in spec.get("accents", []):
        place(fx, bell(hz(n)), at, 0.42)
    for at in spec.get("thumps", []):
        th = tone(55.0, 1.2, [(1, 1.0, 1.0), (2, 0.3, 0.5)], tau=0.25, a=0.003)
        place(fx, th, at, 0.9)
        place(fx, noise_burst(0.25, 0.05, 3, 0.08), at, 0.25)
    if spec.get("ticks", True):
        k = 0
        while t0 + k * beat < end:
            place(fx, noise_burst(0.05, 0.008, 11 + k % 5, 0.6), t0 + k * beat, 0.05 if k % 4 else 0.08)
            k += 1
    for at in spec.get("whooshes", []):
        n = int(0.5 * SR)
        w = noise_burst(0.5, 1e9, 21, 0.05)
        e = np.sin(np.linspace(0, np.pi, n)) ** 2
        place(fx, w * e, at - 0.25, 0.5)

    mix = reverb(mel, 1.6, 0.32) + reverb(low, 1.2, 0.2) + padb + reverb(fx, 1.0, 0.18)
    mix = mix[: int(dur * SR)]
    fade = int(0.9 * SR)
    mix[-fade:] *= np.linspace(1, 0, fade) ** 1.5
    mix[: int(0.01 * SR)] *= np.linspace(0, 1, int(0.01 * SR))
    # crude loudness target via RMS (ffmpeg loudnorm can refine)
    rms = np.sqrt((mix ** 2).mean()) + 1e-9
    target = 10 ** ((spec.get("lufs", -16) + 3) / 20)
    mix *= target / rms
    peak = np.abs(mix).max()
    if peak > 0.95:
        mix *= 0.95 / peak
    # gentle stereo: tiny delay on the right channel
    d = int(0.012 * SR)
    left = mix
    right = np.concatenate([np.zeros(d), mix[:-d]]) * 0.92 + mix * 0.08
    st = (np.stack([left, right], 1) * 32767).astype(np.int16)
    with wave.open(sys.argv[2], "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(st.tobytes())


if __name__ == "__main__":
    main()
