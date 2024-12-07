from Components.NetworkComponent import NetworkComponent, SendTo, Rpc, NetworkManager


class NetworkTransform(NetworkComponent):
    def __init__(
            self,
            identifier: int,
            owner: int,
            sync_frequency: float = 0.015,
            sync_x: bool = True,
            sync_y: bool = True,
            sync_z: bool = False,
            sync_angle: bool = False,
            sync_scale: bool = False
    ):
        super().__init__(identifier, owner)
        self.sync_frequency = sync_frequency
        self.sync_x = sync_x
        self.sync_y = sync_y
        self.sync_z = sync_z
        self.sync_angle = sync_angle
        self.sync_scale = sync_scale

    def init(self):
        super().init()
        self.game.scheduler.add_generator(self.sync())

    def sync(self):
        if self.owner == NetworkManager.instance.id:
            while True:
                data = self.serialize()
                self.sync_transform(data)
                yield self.sync_frequency

    @Rpc(send_to=SendTo.NOT_ME, require_owner=True)
    def sync_transform(self, data: list[float]):
        self.deserialize(data)

    def serialize(self) -> list[float]:
        data: list[float] = []
        if self.sync_x:
            data.append(self.transform.x)
        if self.sync_y:
            data.append(self.transform.y)
        if self.sync_z:
            data.append(self.transform.z)
        if self.sync_angle:
            data.append(self.transform.angle)
        if self.sync_scale:
            data.append(self.transform.scale)

        return data

    def deserialize(self, data: list[float]):
        index = 0
        if self.sync_x:
            self.transform.x = data[index]
            index += 1
        if self.sync_y:
            self.transform.y = data[index]
            index += 1
        if self.sync_z:
            self.transform.z = data[index]
            index += 1
        if self.sync_angle:
            self.transform.angle = data[index]
            index += 1
        if self.sync_scale:
            self.transform.scale = data[index]
            index += 1
