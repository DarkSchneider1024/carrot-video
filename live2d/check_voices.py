# -*- coding: utf-8 -*-
"""配音檢查：把劇本每一句的配音快取轉寫成文字，跟劇本比對，抓出錯位 / 只剩笑聲 / 被截斷的句子。

Gemini TTS 為了省額度會把同一個聲音的多句台詞合成一次再依停頓切開（make_video.synth_gemini_batch），
切點偶爾會錯位：某句吞掉下一句、某句只剩笑聲。渲染前先跑這支，相似度低的句子刪掉快取重配（單句）。

    python live2d/check_voices.py 青蛙王子/story_frog.json [--min 0.6]

轉寫用 gemini-3.1-flash-lite（額度跟 TTS 模型分開算），每句間隔幾秒避免 429。
"""
import argparse, base64, difflib, hashlib, glob, json, os, re, subprocess, sys, time, urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import make_video as mv   # noqa: E402

MODEL = 'gemini-3.1-flash-lite'
PROMPT = '逐字轉寫這段中文語音（繁體字）。若有笑聲、嘆氣等非語言聲音，用（笑聲）等標在出現的位置。只輸出轉寫。'


def norm(s):
    s = re.sub(r'（[^）]*）|\([^)]*\)', '', s)
    s = s.replace('妳', '你').replace('牠', '他').replace('她', '他')
    return re.sub(r'[^\w]', '', s)


def transcribe(path, key):
    body = {'contents': [{'parts': [{'text': PROMPT}, {'inline_data': {
        'mime_type': 'audio/mp3', 'data': base64.b64encode(open(path, 'rb').read()).decode()}}]}]}
    for _ in range(5):
        try:
            req = urllib.request.Request(
                f'https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent',
                data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', 'x-goog-api-key': key})
            r = json.load(urllib.request.urlopen(req, timeout=120))
            return r['candidates'][0]['content']['parts'][0]['text'].strip()
        except Exception as e:                                    # 429 -> wait and retry
            err = e
            time.sleep(20)
    return f'ERR {err}'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('story')
    ap.add_argument('--min', type=float, default=0.6, help='similarity below this is flagged')
    a = ap.parse_args()
    story = json.load(open(a.story, encoding='utf-8'))
    vdir = os.path.join(os.path.dirname(a.story), 'voice')
    key = mv.gemini_key()
    bad = []
    for si, sc in enumerate(story['scenes']):
        for bi, b in enumerate(sc['beats']):
            v = story['voices'][b['who']]
            if b.get('style'):
                v = {**v, 'style': b['style']}
            text = mv.clean(b['text'])
            h = hashlib.sha1(f"{b['who']}|{v}|{text}".encode('utf-8')).hexdigest()[:10]
            files = [f for f in glob.glob(os.path.join(vdir, f'*_{h}.mp3'))]
            if not files:
                print(f'{si}-{bi} {b["who"]}: 沒有配音快取'); continue
            heard = transcribe(files[0], key)
            sim = difflib.SequenceMatcher(None, norm(text), norm(heard)).ratio()
            dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0',
                                        files[0]], capture_output=True, text=True).stdout)
            flag = '  <-- 檢查' if sim < a.min else ''
            print(f'{si}-{bi} {b["who"]:8s} {dur:4.1f}s 相似 {sim:.2f}{flag}\n      劇本 {text}\n      聽到 {heard}', flush=True)
            if flag:
                bad.append((si, bi, os.path.basename(files[0])))
            time.sleep(4)
    print('\n需要重配：' if bad else '\n全部通過')
    for si, bi, f in bad:
        print(f'  {si}-{bi}  {f}')


if __name__ == '__main__':
    main()
