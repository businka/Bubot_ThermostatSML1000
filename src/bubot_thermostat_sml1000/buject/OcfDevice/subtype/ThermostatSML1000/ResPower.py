from bubot.OcfResource.OcfResource import OcfResource


class ResPower(OcfResource):
    async def on_get(self, request):
        await self.device.retrieve_switch()
        return await super().on_get(request)

    async def on_post(self, request, response):
        self.debug('post', request)
        payload = request.decode_payload()
        if 'value' in payload:
            await self.device.update_switch(payload['value'])
        return await super().on_post(request, response)
