"""GA4에서 방문 현황 숫자를 받아 stats/data.json으로 저장합니다.

GitHub Actions 배포 때 실행됩니다. 비밀값 GA_SA_KEY(서비스 계정 JSON)가 없으면
'연결 전' 상태의 파일만 만들고 끝납니다.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

PROPERTY_ID = os.environ.get("GA_PROPERTY_ID", "564804538")
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "stats", "data.json")
KST = timezone(timedelta(hours=9))


def write(payload):
    """숫자가 담긴 결과는 STATS_PASSWORD로 암호화해서만 저장합니다.

    비밀번호가 없으면 숫자는 저장하지 않고 'no_password' 상태만 남깁니다.
    (페이지 주소를 아는 누구도 숫자를 볼 수 없게)
    """
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    if payload.get("status") == "ok":
        pw = os.environ.get("STATS_PASSWORD", "")
        if not pw:
            payload = {"status": "no_password", "updated_at": payload.get("updated_at")}
        else:
            import base64
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.ciphers.aead import AESGCM
            from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
            it = 250000
            salt, iv = os.urandom(16), os.urandom(12)
            key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=it).derive(pw.encode("utf-8"))
            ct = AESGCM(key).encrypt(iv, json.dumps(payload, ensure_ascii=False).encode("utf-8"), None)
            b64 = lambda b: base64.b64encode(b).decode("ascii")
            payload = {"status": "locked", "enc": "aes-256-gcm/pbkdf2-sha256", "iter": it,
                       "salt": b64(salt), "iv": b64(iv), "ct": b64(ct),
                       "updated_at": payload.get("updated_at")}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)


def main():
    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    key = os.environ.get("GA_SA_KEY", "").strip()
    if not key:
        write({"status": "not_connected", "updated_at": now})
        print("GA_SA_KEY 비밀값이 없어 연결 전 상태로 저장했습니다.")
        return

    from google.analytics.data_v1beta import BetaAnalyticsDataClient
    from google.analytics.data_v1beta.types import (
        DateRange, Dimension, Metric, OrderBy, RunReportRequest,
    )
    from google.oauth2 import service_account

    creds = service_account.Credentials.from_service_account_info(
        json.loads(key), scopes=["https://www.googleapis.com/auth/analytics.readonly"]
    )
    client = BetaAnalyticsDataClient(credentials=creds)
    prop = f"properties/{PROPERTY_ID}"
    cur = DateRange(start_date="27daysAgo", end_date="today", name="cur")
    prev = DateRange(start_date="55daysAgo", end_date="28daysAgo", name="prev")

    def run(dims, mets, ranges=(cur,), order=None, limit=50):
        req = RunReportRequest(
            property=prop,
            dimensions=[Dimension(name=d) for d in dims],
            metrics=[Metric(name=m) for m in mets],
            date_ranges=list(ranges),
            limit=limit,
        )
        if order:
            req.order_bys = [OrderBy(metric=OrderBy.MetricOrderBy(metric_name=order), desc=True)]
        res = client.run_report(req)
        dh = [h.name for h in res.dimension_headers]
        mh = [h.name for h in res.metric_headers]
        rows = []
        for r in res.rows:
            row = {dh[i]: v.value for i, v in enumerate(r.dimension_values)}
            for i, v in enumerate(r.metric_values):
                row[mh[i]] = float(v.value) if v.value not in ("", None) else 0.0
            rows.append(row)
        return rows

    total_mets = ["activeUsers", "newUsers", "sessions", "screenPageViews",
                  "engagementRate", "averageSessionDuration"]
    # 날짜 범위가 둘이면 GA4가 dateRange 열을 자동으로 붙여 줌
    totals_rows = run([], total_mets, ranges=(cur, prev))
    totals = {"cur": {}, "prev": {}}
    for r in totals_rows:
        totals[r.pop("dateRange", "cur")] = r

    # 이벤트별 횟수 + 그 행동을 한 사람 수
    events_rows = run(["eventName"], ["eventCount", "totalUsers"], ranges=(cur, prev), limit=200)
    events = {"cur": {}, "prev": {}}
    event_users = {"cur": {}, "prev": {}}
    for r in events_rows:
        dr = r.get("dateRange", "cur")
        events[dr][r["eventName"]] = r["eventCount"]
        event_users[dr][r["eventName"]] = r["totalUsers"]

    def optional(fn):
        """추가 숫자는 실패해도 전체를 막지 않음 (예: 맞춤 측정기준 미등록)."""
        try:
            return fn()
        except Exception as e:  # noqa: BLE001
            print("추가 숫자 건너뜀:", str(e)[:120], file=sys.stderr)
            return None

    DM_EVENTS = {"dm_sheet_open", "dm_instagram_open", "dm_direct_open", "instagram_click", "consult_click", "blog_consult_click", "consult_submit"}

    def daily_events():
        out = {}
        for r in run(["date", "eventName"], ["eventCount"], limit=5000):
            if r["eventName"] in DM_EVENTS:
                out.setdefault(r["date"], {})[r["eventName"]] = r["eventCount"]
        return out

    def channel_events():
        rows = run(["sessionSourceMedium", "eventName"], ["eventCount"], limit=2000)
        return [r for r in rows if r["eventName"] in DM_EVENTS]

    def param(name):
        rows = run(["eventName", f"customEvent:{name}"], ["eventCount"], limit=200)
        return [r for r in rows if r.get(f"customEvent:{name}") not in ("", "(not set)", None)]

    payload = {
        "status": "ok",
        "updated_at": now,
        "period": {
            "cur": [(datetime.now(KST) - timedelta(days=27)).strftime("%Y-%m-%d"), datetime.now(KST).strftime("%Y-%m-%d")],
        },
        "totals": totals,
        "events": events,
        "event_users": event_users,
        "daily_events": optional(daily_events),
        "channel_events": optional(channel_events),
        # GA4에 맞춤 측정기준으로 등록돼 있을 때만 채워짐
        "params": {
            "cta_location": optional(lambda: param("cta_location")),
            "audience": optional(lambda: param("audience")),
            "stage": optional(lambda: param("stage")),
        },
        "daily":run(["date"], ["activeUsers"], limit=60),
        "channels": run(["sessionSourceMedium"], ["sessions"], order="sessions", limit=8),
        "devices": run(["deviceCategory"], ["activeUsers"], order="activeUsers", limit=5),
    }
    payload["daily"].sort(key=lambda r: r["date"])
    write(payload)
    print("저장 완료:", OUT)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # 배포 자체는 막지 않음
        write({"status": "error", "message": str(e)[:300],
               "updated_at": datetime.now(KST).strftime("%Y-%m-%d %H:%M")})
        print("GA4 불러오기 실패:", e, file=sys.stderr)
