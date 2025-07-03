from pycoingecko import CoinGeckoAPI
import requests
import os

def get_trending_ids():
    url = "https://api.coingecko.com/api/v3/search/trending"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to fetch trending coins: HTTP {response.status_code}")
        return set()
    data = response.json()
    coins = data.get("coins", [])
    trending_ids = set(item['item']['id'] for item in coins if 'item' in item)
    print(f"Fetched {len(trending_ids)} trending coin IDs.")
    return trending_ids

def get_top_liquid_trending_coins(trending_ids):
    cg = CoinGeckoAPI()
    page = 1
    per_page = 250  # max per page
    qualifying_coins = []

    while True:
        coins = cg.get_coins_markets(
            vs_currency='usd',
            order='market_cap_desc',
            per_page=per_page,
            page=page
        )
        if not coins:
            break

        for coin in coins:
            market_cap = coin.get('market_cap')
            volume = coin.get('total_volume')
            coin_id = coin.get('id')
            if market_cap and market_cap > 0 and volume and coin_id:
                ratio = volume / market_cap
                if ratio >= 0.2 and coin_id in trending_ids:
                    qualifying_coins.append({
                        'id': coin_id,
                        'symbol': coin['symbol'],
                        'name': coin['name'],
                        'market_cap': market_cap,
                        'volume': volume,
                        'ratio': ratio
                    })

        page += 1
        if page > 5:  # check first 1250 coins
            break

    qualifying_coins.sort(key=lambda c: c['ratio'], reverse=True)
    top_20 = qualifying_coins[:20]

    # Prepare and print results
    result_lines = []
    for i, coin in enumerate(top_20, start=1):
        line = (f"{i}. {coin['name']} ({coin['symbol'].upper()}): "
                f"Market Cap=${coin['market_cap']:,}, "
                f"Volume=${coin['volume']:,}, "
                f"Ratio={coin['ratio']:.2f}")
        print(line)
        result_lines.append(line)

    # Save results to Desktop
    desktop = os.path.join(os.path.expanduser('~'), 'Desktop')
    output_path = os.path.join(desktop, 'top_liquid_trending_coins.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(result_lines))

    print(f"\nResults saved to: {output_path}")

if __name__ == '__main__':
    trending_ids = get_trending_ids()
    get_top_liquid_trending_coins(trending_ids)
