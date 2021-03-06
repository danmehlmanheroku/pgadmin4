##########################################################################
#
# pgAdmin 4 - PostgreSQL Tools
#
# Copyright (C) 2013 - 2016, The pgAdmin Development Team
# This software is released under the PostgreSQL Licence
#
##########################################################################
"""Defines views for management of server groups"""

from abc import ABCMeta, abstractmethod
import json
from flask import request, render_template, make_response, jsonify
from flask.ext.babel import gettext
from flask.ext.security import current_user
from pgadmin.utils.ajax import make_json_response, \
    make_response as ajax_response
from pgadmin.browser import BrowserPluginModule
from pgadmin.utils.menu import MenuItem
from pgadmin.model import db, ServerGroup
from pgadmin.browser.utils import NodeView
import six

class ServerGroupModule(BrowserPluginModule):

    NODE_TYPE = "server-group"

    def get_nodes(self, *arg, **kwargs):
        """Return a JSON document listing the server groups for the user"""
        groups = ServerGroup.query.filter_by(user_id=current_user.id)
        for group in groups:
            yield self.generate_browser_node(
                    "%d" % (group.id), None,
                    group.name,
                    "icon-%s" % self.node_type,
                    True,
                    self.node_type
                    )

    @property
    def node_type(self):
        """
        node_type
        Node type for Server Group is server-group. It is defined by NODE_TYPE
        static attribute of the class.
        """
        return self.NODE_TYPE

    @property
    def script_load(self):
        """
        script_load
        Load the server-group javascript module on loading of browser module.
        """
        return None

    def register_preferences(self):
        """
        register_preferences
        Overrides the register_preferences PgAdminModule, because - we will not
        register any preference for server-group (specially the show_node
        preference.)
        """
        pass


class ServerGroupMenuItem(MenuItem):

    def __init__(self, **kwargs):
        kwargs.setdefault("type", ServerGroupModule.NODE_TYPE)
        super(ServerGroupMenuItem, self).__init__(**kwargs)

@six.add_metaclass(ABCMeta)
class ServerGroupPluginModule(BrowserPluginModule):
    """
    Base class for server group plugins.
    """


    @abstractmethod
    def get_nodes(self, *arg, **kwargs):
        pass


blueprint = ServerGroupModule(__name__, static_url_path='')


class ServerGroupView(NodeView):

    node_type = ServerGroupModule.NODE_TYPE
    parent_ids = []
    ids = [{'type': 'int', 'id': 'gid'}]

    def list(self):
        res = []

        for sg in ServerGroup.query.filter_by(
                user_id=current_user.id
                ).order_by(name):
            res.append({
                'id': sg.id,
                'name': sg.name
                })

        return ajax_response(response=res, status=200)

    def delete(self, gid):
        """Delete a server group node in the settings database"""

        # There can be only one record at most
        servergroup = ServerGroup.query.filter_by(
                user_id=current_user.id,
                id=gid)

        if servergroup is None:
            return make_json_response(
                    status=417,
                    success=0,
                    errormsg=gettext(
                        'The specified server group could not be found.'
                        )
                    )
        else:
            try:
                for sg in servergroup:
                    db.session.delete(sg)
                db.session.commit()
            except Exception as e:
                return make_json_response(
                        status=410, success=0, errormsg=e.message
                        )

        return make_json_response(result=request.form)

    def update(self, gid):
        """Update the server-group properties"""

        # There can be only one record at most
        servergroup = ServerGroup.query.filter_by(
                user_id=current_user.id,
                id=gid).first()

        data = request.form if request.form else json.loads(request.data.decode())

        if servergroup is None:
            return make_json_response(
                    status=417,
                    success=0,
                    errormsg=gettext(
                        'The specified server group could not be found.'
                        )
                    )
        else:
            try:
                if u'name' in data:
                    servergroup.name = data[u'name']
                db.session.commit()
            except Exception as e:
                return make_json_response(
                        status=410, success=0, errormsg=e.message
                        )

        return make_json_response(result=request.form)

    def properties(self, gid):
        """Update the server-group properties"""

        # There can be only one record at most
        sg = ServerGroup.query.filter_by(
                user_id=current_user.id,
                id=gid).first()

        if sg is None:
            return make_json_response(
                    status=417,
                    success=0,
                    errormsg=gettext(
                        'The specified server group could not be found.'
                        )
                    )
        else:
            return ajax_response(
                    response={'id': sg.id, 'name': sg.name},
                    status=200
                    )

    def create(self):
        data = request.form if request.form else json.loads(request.data.decode())
        if data[u'name'] != '':
            try:
                sg = ServerGroup(
                    user_id=current_user.id,
                    name=data[u'name'])
                db.session.add(sg)
                db.session.commit()

                data[u'id'] = sg.id
                data[u'name'] = sg.name

                return jsonify(
                        node=self.blueprint.generate_browser_node(
                            "%d" % (sg.id), None,
                            sg.name,
                            "icon-%s" % self.node_type,
                            True,
                            self.node_type
                            )
                        )
            except Exception as e:
                return make_json_response(
                        status=410,
                        success=0,
                        errormsg=e.message)

        else:
            return make_json_response(
                    status=417,
                    success=0,
                    errormsg=gettext('No server group name was specified'))

    def sql(self, gid):
        return make_json_response(status=422)

    def modified_sql(self, gid):
        return make_json_response(status=422)

    def statistics(self, gid):
        return make_json_response(status=422)

    def dependencies(self, gid):
        return make_json_response(status=422)

    def dependents(self, gid):
        return make_json_response(status=422)

    def module_js(self, **kwargs):
        """
        This property defines (if javascript) exists for this node.
        Override this property for your own logic.
        """
        return make_response(
                render_template("server_groups/server_groups.js"),
                200, {'Content-Type': 'application/x-javascript'}
                )

    def nodes(self, gid=None):
        """Return a JSON document listing the server groups for the user"""
        nodes = []

        if gid is None:
            groups = ServerGroup.query.filter_by(user_id=current_user.id)
        else:
            groups = ServerGroup.query.filter_by(user_id=current_user.id,
                    id=gid).first()

        for group in groups:
            nodes.append(
                    self.generate_browser_node(
                        "%d" % (group.id), None,
                        group.name,
                        "icon-%s" % self.node_type,
                        True,
                        self.node_type
                        )
                    )

        return make_json_response(data=nodes)

    def node(self, gid):
        return self.nodes(gid)


ServerGroupView.register_node_view(blueprint)
