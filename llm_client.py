"""
llm_client.py — unified LLM client for Groq and Ollama
Replaces ollama_client.py

Routes model keys to the right provider based on config.json:
  - "groq/..." prefix → Groq API
  - anything else → Ollama API
"""
import json
import time
import os
from pathlib import Path
from datetime import datetime
from threading import Lock

_lock = Lock()

def get_config():
    """Find config.json — search from script location upward"""
    search = Path(__file__).parent
    for _ in range(4):
        candidate = search / 'config.json'
        if candidate.exists():
            return json.loads(candidate.read_text())
        search = search.parent
    raise FileNotFoundError("config.json not found")

def call_llm(prompt, model_key='generate', num_predict=4096):
    """
    Unified LLM call — routes to Groq or Ollama based on config.
    
    model_key: key from config['models'] e.g. 'generate', 'expand', 'fast'
    """
    config = get_config()
    model = config['models'][model_key]

    if model.startswith('groq/'):
        return _call_groq(prompt, model, model_key, config)
    else:
        return _call_ollama(prompt, model, model_key, config, num_predict)

# Keep backward compat
def call_ollama(prompt, model_key='generate', num_predict=4096):
    return call_llm(prompt, model_key, num_predict)

# ── Groq ──────────────────────────────────────────────────────────────────────

def _call_groq(prompt, model_spec, model_key, config):
    """Call Groq API using openai-compatible endpoint"""
    try:
        from groq import Groq
    except ImportError:
        raise ImportError("pip install groq --break-system-packages")

    groq_config = config.get('groq', {})
    api_key = groq_config.get('api_key') or os.environ.get('GROQ_API_KEY')
    if not api_key or api_key == 'PASTE_YOUR_GROQ_KEY_HERE':
        raise ValueError("Groq API key not set in config.json groq.api_key or GROQ_API_KEY env var")

    # Strip "groq/" prefix to get actual model name
    model_name = model_spec.replace('groq/', '')

    client = Groq(api_key=api_key)
    started = datetime.now()
    t0 = time.time()

    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4096,
    )

    elapsed = time.time() - t0
    content = response.choices[0].message.content
    tokens_in = response.usage.prompt_tokens
    tokens_out = response.usage.completion_tokens
    tps = round(tokens_out / elapsed, 1) if elapsed > 0 else 0

    print(f"    ← {tokens_out} tokens in {elapsed:.1f}s ({tps} t/s) [groq/{model_name}]")

    _log_perf({
        "timestamp": started.isoformat(),
        "model_key": model_key,
        "model": model_name,
        "provider": "groq",
        "host": "api.groq.com",
        "prompt_chars": len(prompt),
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "duration_seconds": round(elapsed, 2),
        "tokens_per_second": tps
    })

    _track_groq_usage(tokens_in + tokens_out, config)
    return content

def _track_groq_usage(tokens_used, config):
    """Track daily Groq token usage"""
    usage_file = Path(__file__).parent.parent / 'data' / 'groq_usage.json'
    usage_file.parent.mkdir(exist_ok=True)

    today = datetime.now().strftime('%Y-%m-%d')

    try:
        usage = json.loads(usage_file.read_text()) if usage_file.exists() else {}
    except:
        usage = {}

    usage[today] = usage.get(today, 0) + tokens_used
    usage_file.write_text(json.dumps(usage, indent=2))

    budget = config.get('groq', {}).get('daily_token_budget', 100000)
    warn_at = config.get('groq', {}).get('warn_at_percent', 80)
    used_today = usage[today]
    pct = round(used_today / budget * 100, 1)

    if pct >= warn_at:
        print(f"    ⚠ Groq daily usage: {used_today:,}/{budget:,} tokens ({pct}%)")

# ── Ollama ────────────────────────────────────────────────────────────────────

def _call_ollama(prompt, model, model_key, config, num_predict):
    """Call Ollama API"""
    try:
        import ollama
    except ImportError:
        raise ImportError("pip install ollama --break-system-packages")

    hosts = config.get('ollama_hosts', {})
    host = hosts.get(model_key, config['ollama_host']) if isinstance(hosts, dict) else config['ollama_host']

    client = ollama.Client(host=host)
    started = datetime.now()
    t0 = time.time()

    response = client.chat(
        model=model,
        messages=[{'role': 'user', 'content': prompt}],
        options={"num_predict": num_predict, "num_ctx": 8192}
    )

    elapsed = time.time() - t0
    content = response.message.content
    tokens_in = response.prompt_eval_count or 0
    tokens_out = response.eval_count or 0
    tps = round(tokens_out / elapsed, 1) if elapsed > 0 else 0

    host_label = host.split('//')[1].split(':')[0]
    print(f"    ← {tokens_out} tokens in {elapsed:.1f}s ({tps} t/s) [{model}@{host_label}]")

    _log_perf({
        "timestamp": started.isoformat(),
        "model_key": model_key,
        "model": model,
        "provider": "ollama",
        "host": host,
        "prompt_chars": len(prompt),
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "duration_seconds": round(elapsed, 2),
        "tokens_per_second": tps
    })

    return content

# ── Shared ────────────────────────────────────────────────────────────────────

def _get_perf_path():
    """Get the perf.json path - course data directory if available"""
    current_dir = Path(__file__).parent
    
    config_path = current_dir / "config.json"
    if config_path.exists():
        try:
            config = json.loads(config_path.read_text())
            bb_path = config.get("bb_path")
            if bb_path:
                course_data = Path(bb_path).parent / "data"
                if course_data.exists():
                    return course_data / "perf.json"
        except:
            pass
    
    return current_dir / "data" / "perf.json"

def _log_perf(entry):
    with _lock:
        perf_file = _get_perf_path()
        perf_file.parent.mkdir(exist_ok=True)
        try:
            entries = json.loads(perf_file.read_text()) if perf_file.exists() else []
        except:
            entries = []
        entries.append(entry)
        perf_file.write_text(json.dumps(entries, indent=2))

def print_perf_report():
    perf_file = _get_perf_path()
    if not perf_file.exists():
        print("No performance data yet")
        return

    entries = json.loads(perf_file.read_text())
    if not entries:
        return

    print("\n" + "="*60)
    print("Performance Report")
    print("="*60)

    from collections import defaultdict
    by_provider = defaultdict(list)
    for e in entries:
        key = f"{e.get('provider','ollama')}:{e['model']}"
        by_provider[key].append(e)

    for key, group in sorted(by_provider.items()):
        avg_tps = round(sum(e['tokens_per_second'] for e in group) / len(group), 1)
        total_out = sum(e['tokens_out'] for e in group)
        total_dur = sum(e['duration_seconds'] for e in group)
        print(f"\n  {key}")
        print(f"    calls: {len(group)} | tokens: {total_out:,} | time: {total_dur:.0f}s | avg: {avg_tps} t/s")

    total_time = sum(e['duration_seconds'] for e in entries)
    total_tokens = sum(e['tokens_out'] for e in entries)
    groq_tokens = sum(e['tokens_out'] for e in entries if e.get('provider') == 'groq')

    print(f"\n  Total time:   {total_time:.0f}s ({total_time/60:.1f} min)")
    print(f"  Total tokens: {total_tokens:,}")
    if groq_tokens:
        print(f"  Groq tokens:  {groq_tokens:,}")
    print("="*60)

    # Groq budget status
    usage_file = Path(__file__).parent.parent / 'data' / 'groq_usage.json'
    if usage_file.exists():
        usage = json.loads(usage_file.read_text())
        today = datetime.now().strftime('%Y-%m-%d')
        used = usage.get(today, 0)
        try:
            config = get_config()
            budget = config.get('groq', {}).get('daily_token_budget', 100000)
            print(f"\n  Groq today:   {used:,}/{budget:,} tokens ({round(used/budget*100,1)}%)")
        except:
            pass
