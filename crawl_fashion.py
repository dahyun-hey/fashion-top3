"""
패션 플랫폼 TOP3 크롤러
- 무신사: REST API
- 지그재그: GraphQL API

크롤링 후 데이터가 내장된 index.html을 생성하여
GitHub Pages 등에 바로 배포 가능
"""

import json
import os
from datetime import datetime

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_HTML = os.path.join(SCRIPT_DIR, "index.html")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "ko-KR,ko;q=0.9",
}


def crawl_musinsa():
    """무신사 실시간 랭킹 TOP3"""
    print("[무신사] 크롤링 중...")
    url = "https://api.musinsa.com/api2/hm/web/v5/pans/ranking?storeCode=musinsa&subPan=product"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    data = r.json()

    items = []
    modules = data.get("data", {}).get("modules", [])
    for m in modules:
        if m.get("type") != "MULTICOLUMN":
            continue
        for entry in m.get("items", []):
            if entry.get("type") != "PRODUCT_COLUMN":
                continue
            info = entry.get("info", {})
            image_data = entry.get("image", {})
            product_id = entry.get("id", "")
            item = {
                "rank": image_data.get("rank", len(items) + 1),
                "brand": info.get("brandName", ""),
                "name": info.get("productName", ""),
                "price": info.get("finalPrice", 0),
                "discount": info.get("discountRatio", 0),
                "image": image_data.get("url", ""),
                "link": f"https://www.musinsa.com/products/{product_id}",
            }
            items.append(item)
            if len(items) >= 3:
                break
        if len(items) >= 3:
            break

    print(f"[무신사] {len(items)}개 상품 수집 완료")
    return items


def crawl_zigzag():
    """지그재그 베스트 TOP3"""
    print("[지그재그] 크롤링 중...")
    graphql_url = "https://api.zigzag.kr/api/2/graphql"

    query = """
    fragment UxGoodsCardItemPart on UxGoodsCardItem {
      type image_url product_url shop_name title discount_rate price final_price catalog_product_id ranking
    }
    query GetSearchResult($input: SearchResultInput!) {
      search_result(input: $input) {
        ui_item_list {
          __typename
          ... on UxGoodsCardItem { ...UxGoodsCardItemPart }
        }
      }
    }
    """

    variables = {"input": {"page_id": "best"}}
    gql_headers = {**HEADERS, "Content-Type": "application/json"}
    r = requests.post(
        graphql_url,
        headers=gql_headers,
        json={"query": query, "variables": variables},
        timeout=15,
    )
    r.raise_for_status()
    data = r.json()

    items = []
    ui_items = data.get("data", {}).get("search_result", {}).get("ui_item_list", [])
    for entry in ui_items:
        if entry.get("__typename") != "UxGoodsCardItem":
            continue
        catalog_id = entry.get("catalog_product_id", "")
        product_url = entry.get("product_url", "")
        web_url = f"https://zigzag.kr/catalog/products/{catalog_id}" if catalog_id else product_url

        item = {
            "rank": len(items) + 1,
            "brand": entry.get("shop_name", ""),
            "name": entry.get("title", ""),
            "price": entry.get("final_price", 0),
            "originalPrice": entry.get("price", 0),
            "discount": entry.get("discount_rate", 0),
            "image": entry.get("image_url", ""),
            "link": web_url,
        }
        items.append(item)
        if len(items) >= 3:
            break

    print(f"[지그재그] {len(items)}개 상품 수집 완료")
    return items


def generate_html(data):
    """크롤링 데이터를 내장한 단일 HTML 파일 생성"""
    data_json = json.dumps(data, ensure_ascii=False)

    html = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>패션 TOP3 - 무신사 / 지그재그 실시간 인기 순위</title>
<meta name="description" content="무신사, 지그재그 실시간 인기 TOP3 아이템을 한눈에!">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
  *{margin:0;padding:0;box-sizing:border-box}
  body{font-family:'Noto Sans KR',sans-serif;background:#f5f5f7;color:#1d1d1f;min-height:100vh}
  header{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 50%,#0f3460 100%);color:#fff;text-align:center;padding:28px 20px 22px;position:sticky;top:0;z-index:100;box-shadow:0 2px 20px rgba(0,0,0,.15)}
  header h1{font-size:26px;font-weight:900;letter-spacing:-.5px}
  header h1 span{color:#e94560}
  header p{font-size:13px;color:rgba(255,255,255,.6);margin-top:6px}
  #updateTime{font-size:12px;color:rgba(255,255,255,.45);margin-top:4px}
  .tab-bar{display:flex;background:#fff;border-bottom:1px solid #e0e0e0;position:sticky;top:96px;z-index:99}
  .tab{flex:1;text-align:center;padding:14px 0;font-size:15px;font-weight:700;cursor:pointer;transition:all .2s;border-bottom:3px solid transparent;color:#888}
  .tab:hover{color:#333}
  .tab.active{border-bottom-color:#e94560;color:#1d1d1f}
  .tab .dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px;vertical-align:middle}
  .content{max-width:600px;margin:0 auto;padding:16px}
  .platform-header{display:flex;align-items:center;gap:10px;margin-bottom:14px}
  .platform-logo{width:40px;height:40px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:18px;color:#fff}
  .platform-header h2{font-size:20px;font-weight:700}
  .badge{background:#e94560;color:#fff;font-size:11px;font-weight:700;padding:3px 8px;border-radius:10px;margin-left:auto}
  .item-card{background:#fff;border-radius:16px;padding:16px;margin-bottom:12px;display:flex;align-items:center;gap:14px;box-shadow:0 1px 4px rgba(0,0,0,.06);transition:transform .15s,box-shadow .15s;cursor:pointer;text-decoration:none;color:inherit}
  .item-card:hover{transform:translateY(-2px);box-shadow:0 4px 16px rgba(0,0,0,.1)}
  .rank{font-size:28px;font-weight:900;min-width:36px;text-align:center}
  .rank-1{color:#ffd700}.rank-2{color:#c0c0c0}.rank-3{color:#cd7f32}
  .item-thumb{width:80px;height:80px;border-radius:12px;overflow:hidden;flex-shrink:0;background:#f0f0f0}
  .item-thumb img{width:100%;height:100%;object-fit:cover}
  .item-info{flex:1;min-width:0}
  .item-brand{font-size:12px;color:#888;margin-bottom:3px}
  .item-name{font-size:14px;font-weight:500;line-height:1.4;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:6px}
  .item-price{font-size:18px;font-weight:900;color:#e94560}
  .item-original-price{font-size:12px;color:#bbb;text-decoration:line-through;margin-left:6px}
  .item-discount{font-size:13px;font-weight:700;color:#e94560;margin-right:4px}
  .go-link{flex-shrink:0;width:36px;height:36px;border-radius:50%;background:#f5f5f7;display:flex;align-items:center;justify-content:center;font-size:18px;color:#888;transition:background .2s}
  .item-card:hover .go-link{background:#e94560;color:#fff}
  .platform-group{margin-bottom:24px}
  .platform-group-title{font-size:16px;font-weight:700;margin-bottom:10px;padding-left:4px;display:flex;align-items:center;gap:8px}
  .platform-group-title .dot{width:10px;height:10px;border-radius:50%}
  .error-msg{background:#fff3cd;border:1px solid #ffc107;border-radius:12px;padding:16px;margin-bottom:16px;font-size:13px;color:#856404;text-align:center}
  footer{text-align:center;padding:30px 20px;color:#aaa;font-size:12px;line-height:1.8}
</style>
</head>
<body>
<header>
  <h1><span>REAL-TIME</span> TOP 3</h1>
  <p>무신사 / 지그재그 인기 아이템</p>
  <div id="updateTime"></div>
</header>
<div class="tab-bar">
  <div class="tab active" data-tab="all">전체</div>
  <div class="tab" data-tab="musinsa"><span class="dot" style="background:#000"></span>무신사</div>
  <div class="tab" data-tab="zigzag"><span class="dot" style="background:#f0308a"></span>지그재그</div>
</div>
<div class="content" id="content"></div>
<footer>패션 TOP3 &copy; 2026<br>데이터는 각 플랫폼 기준 인기 순위입니다</footer>
<script>
const DATA = ''' + data_json + ''';

let currentTab = 'all';

function fmt(n) { return n.toLocaleString() + '원'; }

function card(item, rank) {
  const img = item.image || '';
  const hasImg = img.startsWith('http');
  const op = item.originalPrice || 0;
  return `<a class="item-card" href="${item.link}" target="_blank" rel="noopener">
    <div class="rank rank-${rank}">${rank}</div>
    <div class="item-thumb">${hasImg ? `<img src="${img}" alt="${item.name}" loading="lazy" onerror="this.style.display='none'">` : ''}</div>
    <div class="item-info">
      <div class="item-brand">${item.brand}</div>
      <div class="item-name">${item.name}</div>
      <div>${item.discount ? `<span class="item-discount">${item.discount}%</span>` : ''}<span class="item-price">${fmt(item.price)}</span>${op && op > item.price ? `<span class="item-original-price">${fmt(op)}</span>` : ''}</div>
    </div>
    <div class="go-link">&rarr;</div>
  </a>`;
}

function render() {
  const el = document.getElementById('content');
  if (currentTab === 'all') {
    let h = '';
    for (const [k, p] of Object.entries(DATA.platforms)) {
      if (!p.items || !p.items.length) continue;
      h += `<div class="platform-group"><div class="platform-group-title"><span class="dot" style="background:${p.color}"></span>${p.name} TOP 3</div>${p.items.map((it, i) => card(it, i+1)).join('')}</div>`;
    }
    el.innerHTML = h;
  } else {
    const p = DATA.platforms[currentTab];
    if (!p) { el.innerHTML = '<div class="error-msg">데이터 없음</div>'; return; }
    let h = `<div class="platform-header"><div class="platform-logo" style="background:${p.color}">${p.name[0]}</div><h2>${p.name} TOP 3</h2><span class="badge">LIVE</span></div>`;
    if (!p.items || !p.items.length) h += '<div class="error-msg">데이터를 가져올 수 없습니다.</div>';
    else h += p.items.map((it, i) => card(it, i+1)).join('');
    el.innerHTML = h;
  }
}

document.querySelectorAll('.tab').forEach(t => {
  t.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(x => x.classList.remove('active'));
    t.classList.add('active');
    currentTab = t.dataset.tab;
    render();
  });
});

document.getElementById('updateTime').textContent = '업데이트: ' + DATA.updated_at;
render();
</script>
</body>
</html>'''
    return html


def main():
    print("=" * 50)
    print("패션 플랫폼 TOP3 크롤링 시작")
    print("=" * 50)

    result = {
        "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "platforms": {},
    }

    # 무신사
    try:
        result["platforms"]["musinsa"] = {
            "name": "무신사",
            "color": "#000000",
            "items": crawl_musinsa(),
        }
    except Exception as e:
        print(f"[무신사] 실패: {e}")
        result["platforms"]["musinsa"] = {"name": "무신사", "color": "#000000", "items": [], "error": str(e)}

    # 지그재그
    try:
        result["platforms"]["zigzag"] = {
            "name": "지그재그",
            "color": "#f0308a",
            "items": crawl_zigzag(),
        }
    except Exception as e:
        print(f"[지그재그] 실패: {e}")
        result["platforms"]["zigzag"] = {"name": "지그재그", "color": "#f0308a", "items": [], "error": str(e)}

    # HTML 생성
    html = generate_html(result)
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print()
    print("=" * 50)
    print(f"HTML 생성 완료: {OUTPUT_HTML}")
    print(f"업데이트 시간: {result['updated_at']}")
    for key, platform in result["platforms"].items():
        count = len(platform.get("items", []))
        print(f"  {platform['name']}: {count}개 상품")
    print("=" * 50)
    print()
    print("GitHub Pages 배포 방법:")
    print("  1. GitHub에 새 저장소 생성")
    print("  2. index.html을 push")
    print("  3. Settings > Pages > main 브랜치 선택 후 Save")
    print("  4. https://<유저명>.github.io/<저장소명>/ 에서 접속!")


if __name__ == "__main__":
    main()
