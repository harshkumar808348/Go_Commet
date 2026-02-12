"""
Load simulation script for the Gaming Leaderboard API.

Continuously submits scores, fetches the leaderboard, and queries
random player ranks to simulate real user behaviour under load.

Usage:
    python simulate_load.py
"""

import random
import time

import requests

API_BASE_URL = "http://localhost:8000/api/leaderboard"


def submit_score(user_id: int):
    """POST a random score for the given user."""
    score = random.randint(100, 10000)
    try:
        resp = requests.post(
            f"{API_BASE_URL}/submit",
            json={"user_id": user_id, "score": score, "game_mode": random.choice(["solo", "team"])},
            timeout=10,
        )
        print(f"  ↑ submit  user={user_id}  score={score}  status={resp.status_code}")
    except requests.RequestException as e:
        print(f"  ✗ submit failed: {e}")


def get_top_players():
    """GET the top-10 leaderboard."""
    try:
        resp = requests.get(f"{API_BASE_URL}/top", timeout=10)
        data = resp.json()
        print(f"  ↓ top-10  entries={len(data.get('leaderboard', []))}")
        return data
    except requests.RequestException as e:
        print(f"  ✗ top-10 failed: {e}")
        return {}


def get_user_rank(user_id: int):
    """GET the rank of a specific user."""
    try:
        resp = requests.get(f"{API_BASE_URL}/rank/{user_id}", timeout=10)
        data = resp.json()
        print(f"  ↓ rank    user={user_id}  rank={data.get('rank', '?')}")
        return data
    except requests.RequestException as e:
        print(f"  ✗ rank failed: {e}")
        return {}


if __name__ == "__main__":
    print("🚀 Load simulation started — press Ctrl+C to stop\n")
    cycle = 0
    try:
        while True:
            cycle += 1
            user_id = random.randint(1, 1_000_000)
            print(f"── Cycle {cycle} ──")
            submit_score(user_id)
            get_top_players()
            get_user_rank(user_id)
            delay = random.uniform(0.5, 2)
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\n⏹ Simulation stopped")
