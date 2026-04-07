import asyncio
from ptero import PteroControl, Panel


SERVER_ID = "95635e32-7745-45ee-bae6-2ec458113233"



async def main():
    panel = Panel(
        id="main",
        base_url="http://65.109.37.23/api",
        client_key="ptlc_aZeCA68eaoswawPIhrhsWQAciWI5Fj0l5NTOhyJLkNA"
    )

    ptero = PteroControl([panel])

    # Get server details
    SERVER_ID = "95635e32-7745-45ee-bae6-2ec458113233"
    server = await ptero.get_server(SERVER_ID)

    # Get utilization (status, CPU, RAM, etc.)

    print(server.data["name"])
    print(server.data["status"])
    server.files

    # await server.restart()



asyncio.run(main())