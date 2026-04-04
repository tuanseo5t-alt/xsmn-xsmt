import sys
sys.path.insert(0, "src")
from datetime import date
import fetcher_xsmn

print("=== TEST XSMN HON NAY ===")
results = fetcher_xsmn.fetch_day(date.today())
print(f"So dai tim duoc: {len(results)}")
for r in results:
    print(f"  - {r['station']}: DB={r['special']}, Nhat={r['first']}")