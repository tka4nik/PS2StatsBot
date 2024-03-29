import aiohttp
import asyncio
import time

from logger import GeneralLogger


def get_population_tasks(session, servers, url):
    tasks = [session.get(url.format(server_id)) for server_id in servers.keys()]
    return tasks


async def get_fisu_population_data(servers):
    async with aiohttp.ClientSession() as session:
        tasks = get_population_tasks(session, servers, "https://ps2.fisu.pw/api/population/?world={0}")
        responses = await asyncio.gather(*tasks)
        results = {}
        for response, server_id in zip(responses, servers):
            r = await response.json()
            results[server_id] = r['result'][0]['vs'] \
                                 + r['result'][0]['tr'] \
                                 + r['result'][0]['nc'] \
                                 + r['result'][0]['ns']
        return results


async def get_honu_population_data(servers):
    async with aiohttp.ClientSession() as session:
        tasks = get_population_tasks(session, servers, "https://wt2.honu.pw/api/population/{0}")
        responses = await asyncio.gather(*tasks)
        results = {}
        for response, server_id in zip(responses, servers):
            r = await response.json()
            results[server_id] = r['vs'] + r['tr'] + r['nc'] + r['ns']
        return results


async def get_voidwell_population_data(servers):
    async with aiohttp.ClientSession() as session:
        tasks = get_population_tasks(session, servers, "https://api.voidwell.com/ps2/worldstate/{0}?platform=pc")
        responses = await asyncio.gather(*tasks)
        results = {}
        for response, server_id in zip(responses, servers):
            r = await response.json()
            results[server_id] = r['onlineCharacters']
        return results


async def get_population_data(server, servers):
    logger = GeneralLogger()
    if server:
        tmp = {server: servers[server]}
        servers = tmp

    start_time = time.time()
    population_data = []

    try:
        population_data.append(await get_voidwell_population_data(servers))
    except aiohttp.ClientConnectorError:
        logger.LogError("ClientConnectionError: voidwell API is not responding", "%d/%m/%y;%H:%M:%S")
    try:
        population_data.append(await get_fisu_population_data(servers))
    except aiohttp.ClientConnectorError:
        logger.LogError("ClientConnectionError: fisu API is not responding", "%d/%m/%y;%H:%M:%S")
    try:
        population_data.append(await get_honu_population_data(servers))
    except aiohttp.ClientConnectorError:
        logger.LogError("ClientConnectionError: honu API is not responding", "%d/%m/%y;%H:%M:%S")

    print(population_data)

    results = {}
    for id in servers.keys():
        results[id] = 0
        for data in population_data:
            results[id] += data[id]
        results[id] /= len(population_data)
        results[id] = round(results[id])
    print("---Requests: %s seconds ---" % (time.time() - start_time))
    print(results)

    return results
