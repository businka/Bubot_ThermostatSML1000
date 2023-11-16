from bubot.OcfResource.OcfResource import OcfResource


class OicRSwitchBinary(OcfResource):
    async def render_GET(self, request):
        await self.device.retrieve_switch()
        return await super().render_GET(request)

    async def render_POST_advanced(self, request, response):
        self.debug('post', request)
        payload = request.decode_payload()
        if 'value' in payload:
            await self.device.update_switch(payload['value'])
        return await super().render_POST_advanced(request, response)
