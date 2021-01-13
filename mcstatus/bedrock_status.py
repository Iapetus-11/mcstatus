from time import perf_counter
# import asyncio_dgram
import socket
import struct


class BedrockServerStatus:
    request_status_data = b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x124Vx'

    def __init__(self, host, port=19132, timeout=3):
        self.host = host
        self.port = port
        self.timeout = timeout

    @staticmethod
    def parse_response(data: bytes, latency: int):
        data = data[1:]
        name_length = struct.unpack('>H', data[32:34])[0]
        data = data[34:34+name_length].decode().split(';')

        try:
            map_ = data[7]
            gamemode = data[8]
        except BaseException:
            map_ = None
            gamemode = None

        return BedrockStatusResponse(
            data[2],
            data[0],
            latency,
            data[4],
            data[5],
            data[1],
            map_,
            gamemode
        )

    def read_status(self):
        start = perf_counter()

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(self.timeout)

        s.sendto(self.request_status_data, (socket.gethostbyname(self.host), self.port))
        data, _ = s.recvfrom(2048)

        return self.parse_response(data, (perf_counter() - start))

    async def read_status_async(self):
        # start = perf_counter()
        #
        # try:
        #     stream = await asyncio_dgram.connect((self.host, self.port))
        #
        #     await stream.send(self.request_status_data)
        #     data, _ = await stream.recv()
        # finally:
        #     try:
        #         stream.close()
        #     except BaseException:
        #         pass
        #
        # return self.parse_response(data, (perf_counter() - start))

        raise NotImplementedError('Python 3.5 doesn\'t support asyncio-dgram...')


class BedrockStatusResponse:
    class Version:
        def __init__(self, protocol, brand):
            self.protocol = protocol
            self.brand = brand

    def __init__(self, protocol, brand, latency, players_online, players_max, motd, map_, gamemode):
        self.version = self.Version(protocol, brand)
        self.latency = latency
        self.players_online = players_online
        self.players_max = players_max
        self.motd = motd
        self.map = map_
        self.gamemode = gamemode
