from disco.bot import Plugin
from flask import jsonify


class UptimePlugin(Plugin):
    
    @Plugin.route("/uptime")
    async def uptime(self):
        return jsonify({"success": True})
