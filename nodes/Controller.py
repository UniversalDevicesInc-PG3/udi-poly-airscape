
from udi_interface import Node,LOGGER,Custom,LOG_HANDLER
import logging
from copy import deepcopy
from nodes import Airscape2
from node_funcs import *

class Controller(Node):
    def __init__(self, poly, primary, address, name):
        super(Controller, self).__init__(poly, primary, address, name)
        self.hb = 0
        self.airscape2       = None
        self.Notices         = Custom(poly, 'notices')
        self.Data            = Custom(poly, 'customdata')
        self.Parameters      = Custom(poly, 'customparams')
        self.Notices         = Custom(poly, 'notices')
        self.TypedParameters = Custom(poly, 'customtypedparams')
        self.TypedData       = Custom(poly, 'customtypeddata')
        poly.subscribe(poly.START,                  self.handler_start, address) 
        poly.subscribe(poly.POLL,                   self.handler_poll)
        poly.subscribe(poly.ADDNODEDONE,            self.handler_add_node_done)
        poly.subscribe(poly.CUSTOMTYPEDPARAMS,      self.handler_typed_params)
        poly.subscribe(poly.CUSTOMTYPEDDATA,        self.handler_typed_data)
        poly.subscribe(poly.CONFIGDONE,             self.handler_config_done)
        poly.subscribe(poly.LOGLEVEL,               self.handler_log_level)
        poly.ready()
        self.poly.addNode(self, conn_status='ST')

    def handler_start(self):
        #serverdata = self.poly._get_server_data()
        LOGGER.info(f"Started Airscape NodeServer {self.poly.serverdata['version']}")
        self.Notices.clear()
        self.heartbeat()
        self.set_params()
        self.discover("")

    def handler_config_done(self):
        LOGGER.debug(f'enter:')
        self.poly.addLogLevel('DEBUG_MODULES',9,'Debug + Modules')
        LOGGER.debug(f'exit')

    def handler_add_node_done(self, node):
        LOGGER.debug(f'node added {node}')

    def handler_poll(self, polltype):
        LOGGER.debug(f'polltype:{polltype}')
        if polltype == 'longPoll':
            self.heartbeat()

    def query(self):
        nodes = self.poly.getNodes()
        for node in nodes:
            if nodes[node].address != self.address:
                nodes[node].query()
        self.reportDrivers()

    def discover(self, command):
        if self.airscape2 is None or len(self.airscape2) == 0:
            LOGGER.info(f'No Airscape 2 Entries in config: {self.airscape2}')
            return
        for a2 in self.airscape2:
            self.poly.addNode(Airscape2(self, self.address, get_valid_node_name(a2['name']), 'Airscape {}'.format(a2['name']), a2))

    def delete(self):
        LOGGER.info('I am being deleted...')

    def heartbeat(self):
        LOGGER.debug(f'heartbeat hb={self.hb}')
        if self.hb == 0:
            self.reportCmd("DON",2)
            self.hb = 1
        else:
            self.reportCmd("DOF",2)
            self.hb = 0

    def set_params(self):
        self.TypedParameters.load( 
            [
                {
                    'name': 'airscape2',
                    'title': 'Airscape 2',
                    'desc': 'Airscape 2nd Generation Controller',
                    'isList': True,
                    'params': [
                        {
                            'name': 'name',
                            'title': "Name",
                            'isRequired': True,
                        },
                        {
                            'name': 'host',
                            'title': 'Host Name or IP Address',
                            'isRequired': True
                        },
                    ]
                },
            ], True)

    def handler_typed_params(self,params):
        LOGGER.debug(f'Loading typed params now {params}')
        return

    def handler_typed_data(self,params):
        LOGGER.debug(f'Loading typed data now {params}')
        self.Notices.clear()
        self.TypedData.load(params)
        LOGGER.debug(params)
        self.airscape2 = self.TypedData['airscape2']
        if self.airscape2 is None or len(self.airscape2) == 0:
            msg = 'Please add a Airscape 2 Fan in the configuration page'
            LOGGER.warning(msg)
            self.Notices['config'] = msg

    def handler_log_level(self,level):
        LOGGER.info(f'level={level}')
        if level['level'] < 10:
            LOGGER.info("Setting basic config to DEBUG...")
            LOG_HANDLER.set_basic_config(True,logging.DEBUG)
        else:
            LOGGER.info("Setting basic config to WARNING...")
            LOG_HANDLER.set_basic_config(True,logging.WARNING)

    def handler_log_level(self,level):
        LOGGER.info(f'level={level}')
        if level['level'] < 10:
            LOGGER.info("Setting basic config to DEBUG...")
            LOG_HANDLER.set_basic_config(True,logging.DEBUG)
        else:
            LOGGER.info("Setting basic config to WARNING...")
            LOG_HANDLER.set_basic_config(True,logging.WARNING)

    id = 'controller'
    commands = {
        'QUERY': query,
        'DISCOVER': discover,
    }
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 25},
    ]
