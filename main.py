import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta
import json

class PrivatBankAPI:
    BASE_URL = 'https://api.privatbank.ua/p24api/pubinfo?json&exchange&coursid=5'

    async def fetch_rates(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    response.raise_for_status()

class CurrencyRatesFetcher:
    def __init__(self, days):
        self.days = days
        self.api = PrivatBankAPI()

    async def get_rates(self):
        if self.days > 10:
            raise ValueError("Неможливо отримати ставки протягом більше 10 днів.")
        today = datetime.now()
        tasks = [self.api.fetch_rates() for _ in range(self.days)]
        results = await asyncio.gather(*tasks)
        return self.format_results(results)

    def format_results(self, results):
        rates = []
        for i, result in enumerate(results):
            date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
            rate_data = {
                date: {
                    'EUR': {
                        'sale': next(item for item in result if item["ccy"] == "EUR")["sale"],
                        'purchase': next(item for item in result if item["ccy"] == "EUR")["buy"]
                    },
                    'USD': {
                        'sale': next(item for item in result if item["ccy"] == "USD")["sale"],
                        'purchase': next(item for item in result if item["ccy"] == "USD")["buy"]
                    }
                }
            }
            rates.append(rate_data)
        return rates

async def main(days):
    fetcher = CurrencyRatesFetcher(days)
    try:
        rates = await fetcher.get_rates()
        print(json.dumps(rates, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Помилка: {e}")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Використання: python main.py <days>")
    else:
        try:
            days = int(sys.argv[1])
            asyncio.run(main(days))
        except ValueError:
            print("Введіть дійсну кількість днів.")
