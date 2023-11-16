from bubot.OcfResource.OcfResource import OcfResource


class ResTemperatureExternal(OcfResource):
    async def on_get(self, request):
        await self.device.retrieve_temperature_external()
        return await super().on_get(request)

    def on_post(self, request, response):
        raise NotImplementedError

