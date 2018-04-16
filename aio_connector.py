import aiomysql
import asyncio
import timeit

template = """SELECT title, content, date, link from dummy_cryptonews 
              where MATCH(content) against ('+{0}' In Boolean Mode)"""


async def select(currency_name, pool):
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(template.format(currency_name))
            r = await cur.fetchall()
            format = '%Y-%m-%d %H:%M:%S'
            for ele in r:
                print(",".join([currency_name, ele[0], ele[1], ele[2].strftime(format), ele[3]]))


async def main(loop):
    pool = await aiomysql.create_pool(
        host='cs336.ckksjtjg2jto.us-east-2.rds.amazonaws.com',
        port=3306,
        user='student',
        password='cs336student',
        db='CryptoNews',
        loop=loop)

    currency_names = ["Adelphoi", "Ethereum", "Eos", "Equal"]
    tasks = [asyncio.ensure_future(select(currency, pool)) for currency in currency_names]
    return await asyncio.gather(*tasks)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
