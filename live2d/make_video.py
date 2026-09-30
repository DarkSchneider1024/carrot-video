# -*- coding: utf-8 -*-
"""Story JSON -> Live2D (Inochi2D-rig) animated MP4, Vyond-style.

    python live2d/make_video.py 小紅帽/story_live2d.json            # full pipeline
    python live2d/make_video.py 小紅帽/story_live2d.json --no-render   # TTS + timeline only
    python live2d/make_video.py 小紅帽/story_live2d.json --frames 0:90 # render a frame range (preview)

Steps
  1. TTS   : edge-tts, or Gemini TTS when a voice has "engine": "gemini" (key from C:\\GitRoot\\env.conf), per line (voice / rate / pitch per speaker), cached by text hash -> <story dir>/voice/
  2. lipsync: decode each clip, RMS per video frame -> mouth-open envelope (0..1)
  3. timeline: lines play one after another (gap between them); walks / gestures / looks attach to the line
               they are written on; camera keyframes are relative to each scene (at 0..1)
  4. render : headless Chromium (Playwright) loads live2d/player/render.html, which draws backgrounds +
              puppets with the WebGL stage; frames are piped to FFmpeg
  5. mux    : audio clips placed at their start times, subtitles (ASS, <= 16 chars per cue) burned in
Voices: Gemini 3.8 Flash TTS for "engine": "gemini" voices, edge-tts otherwise (see synth()).
"""
import argparse, asyncio, base64, hashlib, http.server, json, math, os, re, socketserver, subprocess, sys, threading, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))


# ------------------------------------------------------------------ 1. TTS
def gemini_key():
    """GEMINI_API_KEY / GOOGLE_API_KEY from the environment, else from env files.
    Accepts KEY=VALUE, KEY: VALUE, JSON, or a bare key; any value that looks like a Google key wins."""
    for k in ('GEMINI_API_KEY', 'GOOGLE_API_KEY'):
        if os.environ.get(k):
            return os.environ[k].strip()
    candidates = [
        os.environ.get('ENV_CONF'),
        os.path.join(ROOT, '.env'),
        r'C:\GitRoot\env.conf',
        r'C:\GitRoot\CarrotStudio\sweet-line-api\.env',
    ]
    for conf in candidates:
        if not conf or not os.path.exists(conf):
            continue
        raw = open(conf, encoding='utf-8-sig', errors='replace').read()
        m = re.findall(r'(?:AIza[0-9A-Za-z_\-]{30,}|AQ\.[0-9A-Za-z_\-]{40,})', raw)
        if m:
            named = re.findall(r'(?im)^\s*(?:export\s+)?"?([A-Z0-9_]*(?:GEMINI|GOOGLE)[A-Z0-9_]*)"?\s*[:=]\s*"?(AIza[0-9A-Za-z_\-]{30,}|AQ\.[0-9A-Za-z_\-]{40,})', raw)
            pref = [v for k, v in named if 'GEMINI' in k.upper()] + [v for k, v in named]
            return (pref or m)[0]
        found = {}
        for line in raw.splitlines():
            mm = re.match(r'\s*(?:export\s+)?"?([A-Za-z0-9_.\-]+)"?\s*[:=]\s*"?([^"\s,]+)', line)
            if mm:
                found[mm.group(1).upper()] = mm.group(2)
        for k, val in found.items():
            if ('GOOGLE' in k or 'GEMINI' in k) and 'KEY' in k and val:
                return val
    raise RuntimeError('no Google / Gemini API key found in environment or config files')


_GEMINI_LAST = 0.0


def synth_gemini(text, v, out_mp3, tries=6):
    """Gemini TTS (prebuilt voice + natural-language style prompt) -> 24 kHz PCM -> trimmed mp3"""
    import time, urllib.request, urllib.error
    model = v.get('model') or os.environ.get('GEMINI_TTS_MODEL', 'gemini-3.8-flash-tts')
    style = v.get('style', '')
    prompt = (f"Read ONLY the text under TRANSCRIPT aloud, in Taiwanese Mandarin. Never speak the notes.\n\n"
              f"### DIRECTOR'S NOTES\n{style}\n\n### TRANSCRIPT\n{text}") if style else text
    body = json.dumps({'contents': [{'parts': [{'text': prompt}]}],
                       'generationConfig': {'responseModalities': ['AUDIO'],
                                            'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': v['voice']}}}}},
                      ensure_ascii=False).encode('utf-8')
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    pcm, last = None, ''
    global _GEMINI_LAST
    for attempt in range(tries):
        gapsec = float(os.environ.get('GEMINI_MIN_GAP', '21'))    # free tier: 3 requests / minute
        wait = _GEMINI_LAST + gapsec - time.time()
        if wait > 0:
            time.sleep(wait)
        _GEMINI_LAST = time.time()
        req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json',
                                                              'x-goog-api-key': gemini_key()})
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                res = json.loads(r.read().decode('utf-8'))
            parts = res['candidates'][0]['content']['parts']
            inl = next(p['inlineData'] for p in parts if 'inlineData' in p)
            pcm = base64.b64decode(inl['data'])
            mime = inl.get('mimeType', '')
            print(f'  gemini audio: {mime}, {len(pcm)} bytes')
            m_rate = re.search(r'rate=(\d+)', mime)
            rate = int(m_rate.group(1)) if m_rate else 24000
            if not re.search(r'L16|pcm', mime, re.I) and mime:   # a container (wav / mp3 / ogg): let ffmpeg decode it
                tmp = out_mp3[:-4] + '.gem'
                open(tmp, 'wb').write(pcm)
                pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', tmp, '-ac', '1', '-ar', '24000', '-f', 's16le', '-'],
                                     capture_output=True, check=True).stdout
                os.remove(tmp); rate = 24000
        except urllib.error.HTTPError as e:
            last = e.read().decode('utf-8', 'replace')
            if e.code == 429 and re.search(r'PerDay|per day|daily', last, re.I):
                print(last, flush=True)
                raise RuntimeError('Gemini TTS daily quota used up (full error above)')
            if e.code in (429, 500, 502, 503, 504):
                m = re.search(r'"retryDelay":\s*"(\d+(?:\.\d+)?)s"', last)
                wait = float(m.group(1)) + 2 if m else min(60, 5 * 2 ** attempt)
                print(f'  gemini {e.code}, retry in {wait:.0f}s')
                time.sleep(wait)
                continue
            raise RuntimeError(f'Gemini TTS HTTP {e.code}: {last[:600]}')
        except (KeyError, IndexError, StopIteration) as e:
            last = f'no audio in response: {str(res)[:300]}'
            time.sleep(3)
            continue
        dur = len(pcm) / 2 / rate
        n = len(re.sub(r'[\s，。！？、；：…～「」*?!,.]', '', text))
        if dur < n * 0.14 and attempt < tries - 1:   # far too short -> words were skipped; ask again
            print(f'  gemini clip too short ({dur:.1f}s for {n} chars), retrying', flush=True)
            pcm = None
            continue
        if dur > n / 1.6 + 4:   # far too long -> probably also read the style prompt aloud; ask again
            print(f'  gemini clip too long ({dur:.1f}s for {n} chars), retrying')
            with wave.open(out_mp3[:-4] + f'_rejected{attempt}.wav', 'wb') as w:
                w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)
            pcm = None
            continue
        break
    if pcm is None:
        raise RuntimeError(f'Gemini TTS failed: {last[:600]}')
    wav = out_mp3[:-4] + '.wav'
    with wave.open(wav, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)
    trim = 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', wav, '-af', trim, '-ar', '24000', '-b:a', '128k', out_mp3], check=True)
    os.remove(wav)


def _gemini_request(prompt, voice, model, tries=4):
    """one Gemini TTS call -> (int16 mono pcm bytes, rate); same quota / retry handling as synth_gemini"""
    import time, urllib.request, urllib.error
    body = json.dumps({'contents': [{'parts': [{'text': prompt}]}],
                       'generationConfig': {'responseModalities': ['AUDIO'],
                                            'speechConfig': {'voiceConfig': {'prebuiltVoiceConfig': {'voiceName': voice}}}}},
                      ensure_ascii=False).encode('utf-8')
    url = f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent'
    global _GEMINI_LAST
    last = ''
    for attempt in range(tries):
        wait = _GEMINI_LAST + float(os.environ.get('GEMINI_MIN_GAP', '21')) - time.time()
        if wait > 0:
            time.sleep(wait)
        _GEMINI_LAST = time.time()
        req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json',
                                                              'x-goog-api-key': gemini_key()})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                res = json.loads(r.read().decode('utf-8'))
            parts = res['candidates'][0]['content']['parts']
            inl = next(p['inlineData'] for p in parts if 'inlineData' in p)
        except urllib.error.HTTPError as e:
            last = e.read().decode('utf-8', 'replace')
            if e.code == 429 and re.search(r'PerDay|per day|daily', last, re.I):
                print(last, flush=True)
                raise RuntimeError('Gemini TTS daily quota used up (full error above)')
            if e.code in (429, 500, 502, 503, 504):
                m = re.search(r'"retryDelay":\s*"(\d+(?:\.\d+)?)s"', last)
                wait = float(m.group(1)) + 2 if m else min(60, 5 * 2 ** attempt)
                print(f'  gemini {e.code}, retry in {wait:.0f}s', flush=True)
                time.sleep(wait)
                continue
            raise RuntimeError(f'Gemini TTS HTTP {e.code}: {last[:600]}')
        except (KeyError, IndexError, StopIteration):
            last = 'no audio in response'
            continue
        data, mime = base64.b64decode(inl['data']), inl.get('mimeType', '')
        m_rate = re.search(r'rate=(\d+)', mime)
        rate = int(m_rate.group(1)) if m_rate else 24000
        if mime and not re.search(r'L16|pcm', mime, re.I):
            data = subprocess.run(['ffmpeg', '-v', 'error', '-i', '-', '-ac', '1', '-ar', '24000', '-f', 's16le', '-'],
                                  input=data, capture_output=True, check=True).stdout
            rate = 24000
        print(f'  gemini audio: {mime}, {len(data)} bytes, {len(data) / 2 / rate:.1f}s', flush=True)
        return data, rate
    raise RuntimeError(f'Gemini TTS failed: {last[:600]}')


def _nchars(t):
    return max(1, len(re.sub(r'[\s，。！？、；：…～「」*?!,.]', '', t)))


def _split_batch(x, rate, texts):
    """cut one long take into len(texts) clips at the pauses closest to where each line should end
    (expected boundary = speech span * cumulative character share). Returns list of arrays or None."""
    n = len(texts)
    hop = rate // 100                                   # 10 ms frames
    f = len(x) // hop
    rms = np.sqrt(np.mean(x[:f * hop].reshape(f, hop) ** 2, axis=1) + 1e-12)
    loud = rms > max(np.percentile(rms, 95) * 0.04, 1e-4)
    idx = np.where(loud)[0]
    if len(idx) == 0:
        return None
    a, b = idx[0], idx[-1] + 1
    runs, i = [], a                                     # silent runs strictly inside the speech span
    while i < b:
        if not loud[i]:
            j = i
            while j < b and not loud[j]:
                j += 1
            if j - i >= 25:                             # >= 0.25 s
                runs.append((i, j))
            i = j
        else:
            i += 1
    if len(runs) < n - 1:
        return None
    w = np.cumsum([_nchars(t) for t in texts])
    exp = [a + (b - a) * w[k] / w[-1] for k in range(n - 1)]
    # DP: choose n-1 increasing runs, score = pause length (s) - 0.12 * |distance to expected| (s)
    R = len(runs)
    sc = lambda k, r: min(3.0, (runs[r][1] - runs[r][0]) / 100) - 0.12 * abs((runs[r][0] + runs[r][1]) / 2 - exp[k]) / 100
    NEG = -1e9
    best = [[NEG] * R for _ in range(n - 1)]
    back = [[-1] * R for _ in range(n - 1)]
    for r in range(R):
        best[0][r] = sc(0, r)
    for k in range(1, n - 1):
        run_best, run_arg = NEG, -1
        for r in range(R):
            if r - 1 >= 0 and best[k - 1][r - 1] > run_best:
                run_best, run_arg = best[k - 1][r - 1], r - 1
            if run_arg >= 0:
                best[k][r] = run_best + sc(k, r)
                back[k][r] = run_arg
    if n == 1:
        cuts = []
    else:
        r = int(np.argmax(best[n - 2]))
        if best[n - 2][r] <= NEG / 2:
            return None
        cuts = [r]
        for k in range(n - 2, 0, -1):
            r = back[k][r]
            cuts.append(r)
        cuts = cuts[::-1]
    edges = [a] + [(runs[r][0] + runs[r][1]) // 2 for r in cuts] + [b]
    segs = [x[edges[k] * hop:edges[k + 1] * hop] for k in range(n)]
    # sanity: every clip's speaking rate within 0.45x..2.2x of the take's average
    avg = (b - a) / 100 / w[-1]
    for s, t in zip(segs, texts):
        per = len(s) / rate / _nchars(t)
        if not (0.45 * avg <= per <= 2.2 * avg) or per < 0.14:
            print(f'  split check failed: {per:.2f}s/char vs avg {avg:.2f} for 「{t[:12]}…」', flush=True)
            return None
    return segs


def _save_clip(x, rate, out_mp3):
    wav = out_mp3[:-4] + '.wav'
    with wave.open(wav, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())
    trim = 'silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse'
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', wav, '-af', trim, '-ar', '24000', '-b:a', '128k', out_mp3], check=True)
    os.remove(wav)


def synth_gemini_batch(items, v, depth=0):
    """items: [(text, out_mp3)] all for one voice/style -> ONE request (free tier allows only ~10 requests a day),
    then split at the pauses. Falls back to halves (and finally single lines) if the take can't be split cleanly."""
    if len(items) == 1:
        return synth_gemini(items[0][0], v, items[0][1])
    model = v.get('model') or os.environ.get('GEMINI_TTS_MODEL', 'gemini-3.8-flash-tts')
    texts = [t for t, _ in items]
    prompt = (f"Read ONLY the {len(texts)} lines under TRANSCRIPT aloud, in order, in Taiwanese Mandarin. "
              f"Never speak the notes, numbers or separators. After EVERY line stop and stay completely silent "
              f"for about two seconds before starting the next line.\n\n"
              f"### DIRECTOR'S NOTES\n{v.get('style', '')}\n\n### TRANSCRIPT\n" + '\n\n'.join(texts))
    for attempt in range(2 if depth == 0 else 1):
        pcm, rate = _gemini_request(prompt, v['voice'], model)
        x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0
        segs = _split_batch(x, rate, texts)
        if segs:
            for s, (_, mp3) in zip(segs, items):
                _save_clip(s, rate, mp3)
            print(f'  batch of {len(items)} lines split OK', flush=True)
            return
        raw = items[0][1][:-4] + f'_batch_rejected{depth}_{attempt}.wav'
        with wave.open(raw, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(pcm)
        print(f'  could not split a batch of {len(items)} lines (kept {os.path.basename(raw)})', flush=True)
    h = len(items) // 2
    synth_gemini_batch(items[:h], v, depth + 1)
    synth_gemini_batch(items[h:], v, depth + 1)


def voice_file(vdir, si, bi, key):
    """cached clip for this exact line (speaker + voice settings + text); reused even if scenes were re-ordered"""
    mp3 = os.path.join(vdir, f's{si + 1}_{bi + 1}_{key}.mp3')
    if not (os.path.exists(mp3) and os.path.getsize(mp3) > 1000):
        import glob, shutil
        old = [f for f in glob.glob(os.path.join(vdir, f'*_{key}.mp3')) if os.path.getsize(f) > 1000]
        if old:
            shutil.copyfile(old[0], mp3)
    return mp3


def pre_synth_gemini(story, story_dir, max_lines=None, max_chars=None):
    """synthesise every missing Gemini line up front, grouped per speaker + style, several lines per request"""
    max_lines = max_lines or int(os.environ.get('GEMINI_BATCH_LINES', '10'))
    max_chars = max_chars or int(os.environ.get('GEMINI_BATCH_CHARS', '380'))
    vdir = os.path.join(story_dir, 'voice')
    groups = {}
    for si, sc in enumerate(story['scenes']):
        for bi, beat in enumerate(sc['beats']):
            who = beat['who']
            v = story['voices'][who]
            if beat.get('style'):
                v = {**v, 'style': beat['style']}
            if v.get('engine') != 'gemini':
                continue
            text = clean(beat['text'])
            key = hashlib.sha1(f"{who}|{v}|{text}".encode('utf-8')).hexdigest()[:10]
            mp3 = voice_file(vdir, si, bi, key)
            if os.path.exists(mp3) and os.path.getsize(mp3) > 1000:
                continue
            g = groups.setdefault(json.dumps(v, ensure_ascii=False, sort_keys=True), (v, []))
            g[1].append((text, mp3))
    todo = sum(len(g[1]) for g in groups.values())
    print(f'gemini: {todo} lines to synthesise in {len(groups)} voice groups', flush=True)
    for v, items in groups.values():
        chunk, n = [], 0
        for it in items:
            if chunk and (len(chunk) >= max_lines or n + len(it[0]) > max_chars):
                synth_gemini_batch(chunk, v); chunk, n = [], 0
            chunk.append(it); n += len(it[0])
        if chunk:
            synth_gemini_batch(chunk, v)


def synth(text, v, out_mp3):
    if os.path.exists(out_mp3) and os.path.getsize(out_mp3) > 1000:
        return
    if v.get('engine') == 'gemini':
        return synth_gemini(text, v, out_mp3)
    import edge_tts
    async def go():
        await edge_tts.Communicate(text, v['voice'], rate=v.get('rate', '+0%'), pitch=v.get('pitch', '+0Hz')).save(out_mp3)
    asyncio.run(go())


def decode(mp3, sr=16000):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', mp3, '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768.0


# ------------------------------------------------------------------ 2. lipsync
def mouth_envelope(samples, sr, fps):
    hop = sr // fps
    n = int(math.ceil(len(samples) / hop))
    rms = np.array([np.sqrt(np.mean(samples[i * hop:(i + 1) * hop] ** 2) + 1e-12) for i in range(n)])
    if rms.max() <= 0:
        return [0.0] * n
    ref = np.percentile(rms, 90) + 1e-6
    v = np.clip((rms / ref - 0.12) / 0.88, 0, 1) ** 0.8
    # attack fast, release a little slower -> less jitter, still snappy
    out, cur = [], 0.0
    for x in v:
        cur = x if x > cur else cur * 0.55 + x * 0.45
        out.append(round(float(cur), 3))
    return out


# ------------------------------------------------------------------ 3. timeline + subtitles
# ------------------------------------------------------------------ subtitles (繁中字幕業界慣例，參考 Netflix zh-Hant)
#  * 一條字幕一行、最多 16 字；只在「詞與詞之間」斷行（jieba 斷詞），《書名》「引號」內容不拆
#  * 太長的子句平均切成幾段（不會剩一兩個字的尾巴）；太短的子句併進同一條
#  * 標點：逗號、頓號、分號、冒號 → 全形空格；句號刪除；？！……～ 保留；行首行尾不留標點/空格
#  * 每條至少 0.8 秒；時間依字數比例分配
SUB_MAX = 16
SUB_WORDS = ['卡洛兒姐姐', '卡洛特', '小紅帽', '大野狼', '青蛙王子', '小青蛙', '小公主', '好朋友', '守信用', '金球']
_PAUSE = '，、；：,;:'
_STOP = '。.'
_KEEP_END = '？！?!…～~'
_jieba = None


def _words(text):
    global _jieba
    if _jieba is None:
        try:
            import jieba
            jieba.setLogLevel(60)
            for w in SUB_WORDS:
                jieba.add_word(w)
            _jieba = jieba
        except ImportError:
            _jieba = False
    toks = _jieba.lcut(text) if _jieba else list(text)
    out, depth = [], 0                                       # glue 《…》 / 「…」 into single unbreakable tokens
    for t in toks:
        if depth and out:
            out[-1] += t
        else:
            out.append(t)
        depth += sum(t.count(c) for c in '《「『') - sum(t.count(c) for c in '》」』')
        depth = max(depth, 0)
    return out


def _clauses(text):
    """[(clause text, trailing punctuation)]"""
    out, cur = [], ''
    for ch in text:
        if ch in _PAUSE + _STOP + _KEEP_END:
            if out and not cur.strip():
                out[-1] = (out[-1][0], out[-1][1] + ch)
            else:
                out.append((cur.strip(), ch))
            cur = ''
        else:
            cur += ch
    if cur.strip():
        out.append((cur.strip(), ''))
    return out


def _balanced(clause):
    """split a clause longer than SUB_MAX into k even pieces at word boundaries"""
    n = len(clause)
    if n <= SUB_MAX:
        return [clause]
    k = math.ceil(n / SUB_MAX)
    words = _words(clause)
    bounds, acc = [], 0
    for w in words[:-1]:
        acc += len(w)
        bounds.append(acc)
    cuts, prev = [], 0
    for i in range(1, k):
        target = n * i / k
        cand = [b for b in bounds if prev < b < n and b - prev <= SUB_MAX and n - b <= SUB_MAX * (k - i)]
        if not cand:
            cand = [b for b in bounds if b > prev] or [min(prev + SUB_MAX, n - 1)]
        b = min(cand, key=lambda x: abs(x - target))
        cuts.append(b); prev = b
    edges = [0] + cuts + [n]
    return [clause[a:b] for a, b in zip(edges, edges[1:]) if clause[a:b]]


def _punct(p):
    """how a clause's trailing punctuation is shown inside a subtitle"""
    shown = ''.join(c for c in p if c in _KEEP_END)
    return shown.replace('...', '…').replace('~', '～')


def sub_lines(text):
    events, cur = [], ''
    text = text.replace('——', '，').replace('—', '，')          # dash = a pause (break point)
    for body, p in _clauses(text):
        tail = _punct(p)
        for k, piece in enumerate(_balanced(body)):
            last = k == len(_balanced(body)) - 1
            piece = piece + (tail if last else '')
            sep = '' if not cur else ('' if cur.endswith(tuple(_KEEP_END)) else '　')
            if cur and len(cur) + len(sep) + len(piece) <= SUB_MAX:
                cur = cur + sep + piece
            else:
                if cur:
                    events.append(cur)
                cur = piece
            if last and (any(c in p for c in _STOP + _KEEP_END)) and len(cur) >= SUB_MAX // 2:
                events.append(cur); cur = ''                # sentence end closes a reasonably full subtitle
    if cur:
        events.append(cur)
    return [e.strip('　 ') for e in events if e.strip('　 ')]


def split_subs(text, t0, dur, max_chars=SUB_MAX, gap=0.12, min_dur=0.8):
    chunks = sub_lines(text)
    weight = [len(c.replace('　', '')) + (0.8 if '　' in c else 0) for c in chunks]
    total = sum(weight) or 1
    durs = [dur * w / total for w in weight]
    if len(durs) > 1:                                        # enforce the minimum on-screen time
        short = [i for i, d in enumerate(durs) if d < min_dur]
        need = sum(min_dur - durs[i] for i in short)
        pool = sum(durs[i] - min_dur for i in range(len(durs)) if i not in short)
        if short and pool > need:
            durs = [min_dur if i in short else d - (d - min_dur) * need / pool for i, d in enumerate(durs)]
    t, out = t0, []
    for c, d in zip(chunks, durs):
        out.append((t, t + max(0.3, d - gap), c))
        t += d
    return out


def clean(text):
    """script markup -> spoken / subtitle text"""
    return re.sub(r'\*\*', '', text).strip()


_METRICS = {}


def puppet_metrics(name, story_dir):
    """(feet, tall) in puppet units, measured from the puppet's own composite (lowest / highest opaque rows)"""
    if name not in _METRICS:
        from PIL import Image
        im = Image.open(os.path.join(story_dir, 'characters', name, 'psd_composite.png'))
        a = np.asarray(im)[..., 3]
        rows = np.where(a.max(1) > 20)[0]
        h = a.shape[0]
        _METRICS[name] = (float(rows[-1] - h / 2), float(rows[-1] - rows[0]))
    return _METRICS[name]


def synth_sfx(story_dir):
    """notification ding + a short Canon-style closing melody, synthesised (no downloaded audio)"""
    d = os.path.join(story_dir, 'voice')
    os.makedirs(d, exist_ok=True)
    sr = 44100

    def save(path, x):
        x = np.clip(x, -1, 1)
        with wave.open(path, 'wb') as w:
            w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
            w.writeframes((x * 32000).astype(np.int16).tobytes())

    ding = os.path.join(d, 'sfx_ding.wav')
    if not os.path.exists(ding):
        t = np.arange(int(sr * 0.55)) / sr
        x = np.zeros_like(t)
        for f0, st in ((1318.5, 0.0), (1760.0, 0.12)):
            m = t >= st
            tt = t[m] - st
            x[m] += 0.5 * np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * 9)
        save(ding, x)
    canon = os.path.join(d, 'bgm_canon.wav')
    if not os.path.exists(canon):
        # D A Bm F#m G D G A -- the Canon progression, arpeggiated plucks (public-domain composition, own synthesis)
        chords = [(62, 66, 69), (57, 61, 64), (59, 62, 66), (54, 57, 61), (55, 59, 62), (50, 54, 57), (55, 59, 62),
                  (57, 61, 64)]
        beat = 60 / 76
        total = beat * 2 * len(chords) * 2
        x = np.zeros(int(sr * (total + 2)))
        mid = lambda n: 440 * 2 ** ((n - 69) / 12)
        pos = 0.0
        for rep in range(2):
            for ch in chords:
                notes = [ch[0] - 12, ch[0], ch[1], ch[2], ch[1] + 12, ch[2], ch[1], ch[0] + 12]
                for k, n in enumerate(notes):
                    st = int((pos + k * beat / 4) * sr)
                    tt = np.arange(int(sr * 1.2)) / sr
                    f0 = mid(n)
                    tone = (np.sin(2 * np.pi * f0 * tt) + 0.35 * np.sin(4 * np.pi * f0 * tt) + 0.12 * np.sin(6 * np.pi * f0 * tt))
                    x[st:st + len(tt)] += 0.16 * tone * np.exp(-tt * 3.2)
                pos += beat * 2
        fade = np.ones_like(x)
        n = int(sr * 3)
        fade[-n:] = np.linspace(1, 0, n)
        save(canon, x * fade)
    return ding, canon


def build_timeline(story, story_dir):
    fps, gap = story['fps'], story.get('gap', 0.35)
    vdir = os.path.join(story_dir, 'voice')
    os.makedirs(vdir, exist_ok=True)
    ding, canon = synth_sfx(story_dir)
    pre_synth_gemini(story, story_dir)
    rel = lambda f: os.path.relpath(f, ROOT).replace('\\', '/')
    t = 0.3
    scenes, clips, subs = [], [], []
    for si, sc in enumerate(story['scenes']):
        s0 = t
        actors = {}
        for a in sc['actors']:
            cast = story['cast'][a.get('cast', a['id'])]
            puppet = a.get('puppet', cast['puppet'])
            side = a.get('side', cast.get('side'))
            feet, tall = puppet_metrics(puppet, story_dir)
            actors[a['id']] = {'id': a['id'], 'puppet': puppet, 'side': side, 'feet': feet, 'tall': tall,
                               'sideFeet': puppet_metrics(side, story_dir)[0] if side else None,
                               'height': a.get('height', cast['height']), 'x': a['x'], 'y': a['y'],
                               'look': a.get('look', 0.0), 'expr': a.get('expr'), 'walks': [], 'gestures': [],
                               'looks': [], 'nods': [], 'talk': [], 'rises': [], 'shakes': [], 'eats': [], 'fades': [],
                               'exprs': []}
            if a.get('flower'):
                actors[a['id']]['flower'] = True
            if a.get('hidden'):                  # starts invisible; a later "fade_in" makes it appear
                actors[a['id']]['fades'].append({'t': 1e9, 'dur': 0.6, 'in': True})
        overlays = []
        if sc.get('card'):
            overlays.append({'type': 'card', 't0': round(s0 + 0.2, 3), 't1': round(s0 + 4.0, 3), 'text': sc['card']})
        for bi, beat in enumerate(sc['beats']):
            who = beat['who']
            v = story['voices'][who]
            if beat.get('style'):                     # per-line delivery override (Gemini TTS)
                v = {**v, 'style': beat['style']}
            text = clean(beat['text'])
            key = hashlib.sha1(f"{who}|{v}|{text}".encode('utf-8')).hexdigest()[:10]
            mp3 = voice_file(vdir, si, bi, key)
            synth(text, v, mp3)
            samples = decode(mp3)
            dur = len(samples) / 16000
            clips.append({'file': rel(mp3), 'start': round(t, 3), 'dur': round(dur, 3)})
            subs += [(a_, b_, c_, v.get('label', who)) for a_, b_, c_ in split_subs(text, t, dur)]
            if who in actors:
                actors[who]['talk'].append({'t0': round(t, 3), 'env': mouth_envelope(samples, 16000, fps)})
            ui = beat.get('ui', {})
            if ui.get('ding'):
                clips.append({'file': rel(ding), 'start': round(max(0, t - 0.25), 3), 'dur': 0.55, 'vol': 0.7})
            if ui.get('chat_open'):
                overlays.append({'type': 'chat_open', 't': round(t, 3), 'title': ui['chat_open']})
            if ui.get('chat'):
                overlays.append({'type': 'chat', 't': round(t + 0.1, 3), 'from': ui.get('chat_from', who),
                                 'text': clean(ui['chat'] if isinstance(ui['chat'], str) else beat['text'])})
            if ui.get('chat_close'):
                overlays.append({'type': 'chat_close', 't': round(t, 3)})
            if ui.get('sfx'):
                at = round(t + ui.get('sfx_at', 0.0), 3)
                overlays.append({'type': 'sfx', 't': at, 'text': ui['sfx'], 'actor': ui.get('sfx_actor', who)})
                if ui.get('sfx_actor', who) in actors and ui.get('sfx_shake', True):
                    actors[ui.get('sfx_actor', who)]['shakes'].append({'t0': at, 't1': round(at + 0.8, 3)})
            if ui.get('papers'):
                overlays.append({'type': 'papers', 't0': round(t + 0.2, 3), 't1': round(t + dur + 0.2, 3), 'actor': who})
            if ui.get('story'):
                overlays.append({'type': 'story', 't0': round(t - 0.2, 3), 't1': round(t + dur + 1.2, 3),
                                 'text': clean(ui['story']), 'name': ui.get('story_name', '外婆')})
            if ui.get('bgm'):
                clips.append({'file': rel(canon), 'start': round(t, 3), 'dur': 30.0, 'vol': ui.get('bgm_vol', 0.35)})
            for d in beat.get('do', []):
                a = actors[d['id']]
                if 'walk_to' in d:
                    a['walks'].append({'t0': round(t + d.get('at', 0.0), 3),
                                       't1': round(t + d.get('at', 0.0) + dur * min(1.0, 0.95 / d.get('speed', 1.0)), 3),
                                       'to': d['walk_to']})
                if 'gesture' in d:
                    a['gestures'].append({'t0': round(t, 3), 't1': round(t + dur, 3), 'type': d['gesture']})
                if 'look' in d:
                    a['looks'].append({'t': round(t + d.get('at', 0.0), 3), 'v': d['look']})
                if d.get('nod'):
                    a['nods'].append({'t': round(t + 0.2, 3)})
                if 'rise_to' in d:
                    a['rises'].append({'t': round(t + d.get('at', 0.0), 3), 'to': d['rise_to']})
                if d.get('shake'):
                    a['shakes'].append({'t0': round(t, 3), 't1': round(t + min(dur, d.get('shake_dur', 1.0)), 3)})
                if d.get('eat'):
                    a['eats'].append({'t0': round(t, 3), 't1': round(t + dur, 3)})
                if d.get('fade_in'):                  # replaces the 'hidden' placeholder
                    a['fades'] = [f for f in a['fades'] if f['t'] < 1e8] + [
                        {'t': round(t + d.get('at', 0.0), 3), 'dur': d.get('fade_dur', 0.6), 'in': True}]
                if 'expr' in d:
                    a['exprs'].append({'t': round(t + d.get('at', 0.0), 3), 'v': d['expr']})
                if d.get('fade_out'):
                    a['fades'].append({'t': round(t + d.get('at', 0.0), 3), 'dur': d.get('fade_dur', 0.8)})
            t += dur + gap + beat.get('pause', 0.0)
        t += sc.get('tail', 0.5)
        if sc.get('title_card'):                  # story title shown over the whole scene (after the channel intro)
            overlays.append({'type': 'title', 't0': round(s0 + 0.3, 3), 't1': round(t + 0.2, 3), 'text': sc['title_card'], 'size': 220, 'y': 380})
        if sc.get('end_card'):
            overlays.append({'type': 'title', 't0': round(t - 3.0, 3), 't1': round(t + 0.2, 3), 'text': sc['end_card']})
        scenes.append({'bg': sc['bg'], 't0': round(s0, 3), 't1': round(t, 3), 'camera': sc['camera'],
                       'actors': list(actors.values()), 'overlays': overlays, 'light': sc.get('light'),
                       'props': sc.get('props', [])})
    return {'fps': fps, 'size': story['size'], 'duration': round(t + 0.2, 3), 'scenes': scenes, 'clips': clips,
            'subs': [{'t0': round(a, 3), 't1': round(b, 3), 'text': c, 'who': w} for a, b, c, w in subs]}


def write_ass(subs, path, size):
    W, H = size
    def ts(x):
        h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
        return f'{h}:{m:02d}:{s:05.2f}'
    lines = ['[Script Info]', 'ScriptType: v4.00+', f'PlayResX: {W}', f'PlayResY: {H}', '',
             '[V4+ Styles]',
             'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, '
             'Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, '
             'MarginR, MarginV, Encoding',
             'Style: Default,Microsoft JhengHei,58,&H00FFFFFF,&H00FFFFFF,&H00402A1E,&H64000000,1,0,0,0,100,100,1,0,1,4,1,2,60,60,60,1',
             '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text']
    for s in subs:
        lines.append(f"Dialogue: 0,{ts(s['t0'])},{ts(s['t1'])},Default,,0,0,0,,{s['text']}")
    with open(path, 'w', encoding='utf-8-sig') as f:
        f.write('\n'.join(lines) + '\n')


# ------------------------------------------------------------------ 4. render
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve(root):
    handler = lambda *a, **k: Quiet(*a, directory=root, **k)
    httpd = socketserver.ThreadingTCPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def render(timeline_rel, out_video, fps, n_frames, frame_range=None, size=(1920, 1080)):
    from playwright.sync_api import sync_playwright
    httpd = serve(ROOT)
    url = f'http://127.0.0.1:{httpd.server_address[1]}/live2d/player/render.html?timeline=/{timeline_rel}'
    f0, f1 = frame_range if isinstance(frame_range, tuple) else (0, n_frames)
    frames = frame_range if isinstance(frame_range, list) else range(f0, f1)
    if frame_range:
        os.makedirs(out_video, exist_ok=True)
        ff = None
    else:
        ff = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(fps), '-c:v', 'mjpeg',
                               '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'medium',
                               out_video], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        b = p.chromium.launch(channel=os.environ.get('RENDER_BROWSER', 'msedge') or None, args=['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
        page = b.new_page(viewport={'width': size[0], 'height': size[1]})
        page.on('console', lambda m: print('[page]', m.text) if m.type in ('error', 'warning') else None)
        page.goto(url)
        page.wait_for_function('window.stageReady === true', timeout=120000)
        for i in frames:
            data = page.evaluate(f'window.renderFrame({i})')
            jpg = base64.b64decode(data.split(',', 1)[1])
            if ff:
                ff.stdin.write(jpg)
            else:
                open(os.path.join(out_video, f'frame_{i:05d}.jpg'), 'wb').write(jpg)
            if i % 150 == 0:
                print(f'  frame {i}/{f1}')
        b.close()
    httpd.shutdown()
    if ff:
        ff.stdin.close()
        ff.wait()


def mux(video, timeline, ass, out_mp4):
    clips = timeline['clips']
    inputs, filters = ['-i', video], []
    for k, c in enumerate(clips):
        inputs += ['-i', os.path.join(ROOT, c['file'])]
        ms = int(round(c['start'] * 1000))
        vol = c.get('vol', 1.0)
        filters.append(f'[{k + 1}:a]aresample=44100,volume={vol},adelay={ms}|{ms}[a{k}]')
    mix = ''.join(f'[a{k}]' for k in range(len(clips)))
    filters.append(f'{mix}amix=inputs={len(clips)}:normalize=0,apad[aout]')
    ass_path = ass.replace('\\', '/').replace(':', '\\:')
    filters.append(f"[0:v]subtitles='{ass_path}'[vout]")
    cmd = ['ffmpeg', '-y', '-v', 'error', *inputs, '-filter_complex', ';'.join(filters), '-map', '[vout]', '-map', '[aout]',
           '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-c:a', 'aac', '-b:a', '192k', '-shortest', out_mp4]
    subprocess.run(cmd, check=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('story')
    ap.add_argument('--no-render', action='store_true')
    ap.add_argument('--frames', help='a:b  render only this frame range to <story dir>/_frames/')
    ap.add_argument('--remux', action='store_true',
                    help='reuse video/_video_silent*.mp4 from the last render: only rebuild subtitles + audio')
    a = ap.parse_args()
    story_path = os.path.abspath(a.story)
    story_dir = os.path.dirname(story_path)
    story = json.load(open(story_path, encoding='utf-8'))
    tl = build_timeline(story, story_dir)
    stem = os.path.splitext(os.path.basename(story_path))[0]
    suffix = '' if stem == 'story_live2d' else '_' + stem          # the pilot keeps its original file names
    tl_path = os.path.join(story_dir, f'timeline{suffix}.json')
    json.dump(tl, open(tl_path, 'w', encoding='utf-8'), ensure_ascii=False)
    ass = os.path.join(story_dir, f'subtitles{suffix}.ass')
    write_ass(tl['subs'], ass, story['size'])
    n = int(math.ceil(tl['duration'] * tl['fps']))
    print(f"timeline: {len(tl['scenes'])} scenes, {len(tl['clips'])} lines, {tl['duration']:.1f}s, {n} frames")
    if a.no_render:
        return
    rel = os.path.relpath(tl_path, ROOT).replace('\\', '/')
    if a.frames:
        if ',' in a.frames or a.frames.endswith('s'):          # "12.5s,40s,..." seconds, or "300,900" frame numbers
            fl = [int(round(float(x[:-1]) * tl['fps'])) if x.endswith('s') else int(x) for x in a.frames.split(',')]
            render(rel, os.path.join(story_dir, '_frames'), tl['fps'], n, fl, tuple(story['size']))
        else:
            f0, f1 = map(int, a.frames.split(':'))
            render(rel, os.path.join(story_dir, '_frames'), tl['fps'], n, (f0, f1), tuple(story['size']))
        return
    vdir = os.path.join(story_dir, 'video')
    os.makedirs(vdir, exist_ok=True)
    silent = os.path.join(vdir, f'_video_silent{suffix}.mp4')
    if not (a.remux and os.path.exists(silent)):
        render(rel, silent, tl['fps'], n, None, tuple(story['size']))
    out = os.path.join(vdir, story.get('output', 'little_red_riding_hood_live2d.mp4'))
    mux(silent, tl, ass, out)                     # the silent render is kept for --remux (mp4s are not in git)
    print('done ->', out)


if __name__ == '__main__':
    main()
