"""
wireguard configuration adapter for the application
"""
# pylint: disable=logging-fstring-interpolation
import os
import logging
import tempfile

import wgconfig

import utils.config
import utils.log
import utils.generics
import utils.wireguard


class WgConfigAdapter(utils.generics.AsyncSubProcessMixin):
    """interface for the wireguatd configuration
    """
    _config: utils.config.ConfigUtil()
    _logger: logging.Logger
    _config_path: str
    _wg_interface_instance: "Type[models.WgInterfaceModel]"
    _wg_config: wgconfig.WGConfig

    def __init__(self, wg_interface: "Type[models.WgInterfaceModel]"):
        """Initialize the configuration adapter for the given interface

        :param interface_name: name of the wireguard interface that should be used
        :type interface_name: str
        :param wg_config_directory: path to the directory, where the wireguard config files are stored
        :type wg_config_directory: str
        """
        self._config = utils.config.ConfigUtil()
        self._logger = logging.getLogger("wg_adapter")
        self._wg_interface_instance = wg_interface

        self._config_path = os.path.join(self._config.wg_config_dir, f"{self._wg_interface_instance.intf_name}.conf")
        self._wg_config = wgconfig.WGConfig(self._config_path)

    def __str__(self):
        return f"Config Adapter {self._wg_interface_instance}"

    def __repr__(self):
        return f"<WgConfigAdapter {self._wg_interface_instance}>"

    def is_initialized(self) -> bool:
        """chek if the configuration already exists

        :return: [description]
        :rtype: bool
        """
        if os.path.exists(self._config_path):
            return True

        return False

    async def interface_exists(self) -> bool:
        """check if the interface exists on the system

        :return: [description]
        :rtype: bool
        """
        wg_json = await utils.wireguard.WgSystemInfoAdapter().get_wg_json()
        # WgSystemInfoAdapter returns a dictionary for interfaces that are configured
        # on interface level
        return self._wg_interface_instance.intf_name in wg_json.keys()

    async def interface_up(self) -> bool:
        """enable interface using wg-quick and the given configuration of the interface

        :return: True if successful, otherwise false
        :rtype: bool
        """
        if await self.interface_exists():
            return True

        wg_interface = self._wg_interface_instance.intf_name
        try:
            self._logger.info(f"try to create wireguard interface {wg_interface}...")
            out, err, success = await self._execute_subprocess(f"wg-quick up {self._config_path}")
            if not success:
                self._logger.error(f"failed to create wireguard interface {wg_interface}:\n{err}")
                return False

            self._logger.info(f"wireguard interface {wg_interface} created")

        except Exception as ex:
            self._logger.error(f"failed to run wg-quick up: {ex}")
            return False

        return True

    async def interface_down(self) -> bool:
        """disable interface using wg-quick and the given configuration of the interface

        :return: True if successful, otherwise false
        :rtype: bool
        """
        if not await self.interface_exists():
            return True

        wg_interface = self._wg_interface_instance.intf_name
        try:
            self._logger.info(f"try to remove wireguard interface {wg_interface}...")
            out, err, success = await self._execute_subprocess(f"wg-quick down {self._config_path}")
            if not success:
                self._logger.error(f"failed to remove wireguard interface {wg_interface}:\n{err}")
                return False

            self._logger.info(f"wireguard interface {wg_interface} removed")

        except Exception as ex:
            self._logger.error(f"failed to run wg-quick down: {ex}")
            return False

        return True

    async def init_config(self, force_overwrite: bool=False):
        """initialize wireguard configuration adapter with interface specific configuration settings

        :param force_overwrite: overwrite configuration file, defaults to False
        :type force_overwrite: bool, optional
        """
        # initialize configuration if not exists
        if self.is_initialized() or force_overwrite:
            # reset the file
            self._wg_config.initialize_file(f"# configuration managed by script - please don't change - {self._wg_interface_instance.description} ({self._wg_interface_instance.instance_id})")
            self._wg_config.add_attr(None, "PrivateKey", self._wg_interface_instance.private_key, append_as_line=False)
            self._wg_config.add_attr(None, "Address", self._wg_interface_instance.cidr_addresses, append_as_line=False)
            self._wg_config.add_attr(None, "ListenPort", self._wg_interface_instance.listen_port, append_as_line=False)
            self._wg_config.add_attr(None, "Table", self._wg_interface_instance.table.value, append_as_line=False)

            await self._wg_interface_instance.fetch_related("policy_rule_list")

            if self._wg_interface_instance.policy_rule_list:
                ipv4_rules = await self._wg_interface_instance.policy_rule_list.to_ipv4_iptables_list(intf_name="%i", drop_rule=False)
                ipv6_rules = await self._wg_interface_instance.policy_rule_list.to_ipv6_iptables_list(intf_name="%i", drop_rule=False)

                # add IPv4 policy if defined
                if len(ipv4_rules) != 0:
                    drop_ipv4_rules = await self._wg_interface_instance.policy_rule_list.to_ipv4_iptables_list(intf_name="%i", drop_rule=True)
                    self._wg_config.add_attr(
                        None,
                        "PostUp",
                        "; ".join(ipv4_rules),
                        append_as_line=True
                    )
                    self._wg_config.add_attr(
                        None,
                        "PostDown",
                        "; ".join(drop_ipv4_rules),
                        append_as_line=True
                    )

                # add IPv6 policy if defined
                if len(ipv6_rules) != 0:
                    drop_ipv6_rules = await self._wg_interface_instance.policy_rule_list.to_ipv6_iptables_list(intf_name="%i", drop_rule=True)
                    self._wg_config.add_attr(
                        None,
                        "PostUp",
                        "; ".join(ipv6_rules),
                        append_as_line=True
                    )
                    self._wg_config.add_attr(
                        None,
                        "PostDown",
                        "; ".join(drop_ipv6_rules),
                        append_as_line=True
                    )

            self._wg_config.write_file()

            # create interface if not existing or recreate with force_overwrite
            if force_overwrite:
                await self.interface_down()
                await self.interface_up()

            elif not await self.interface_exists():
                await self.interface_up()

            self._logger.info(f"interface configuration for {self._wg_interface_instance.intf_name} initialized")
            self._logger.debug(f"wireguard config created:\n{self._wg_config.interface}\n{self._wg_config.peers}")

        else:
            self._wg_config.read_file()
            self._logger.debug(f"interface configuration for {self._wg_interface_instance.intf_name} read from disk")
            self._logger.debug(f"wireguard config read from disk:\n{self._wg_config.interface}\n{self._wg_config.peers}")

    async def rebuild_peer_config(self) -> bool:
        """rebuild peer section in configuration

        :return: True if sync was successful, otherwise faile
        :rtype: bool
        """
        if not self.is_initialized():
            self._logger.warning("call sync peer without proper initialization, initial configuration...")
            self.init_config()

        await self._wg_interface_instance.fetch_related("peers")

        # drop existing entries
        for public_key in self._wg_config.peers.keys():
            self._wg_config.del_peer(public_key)

        # rebuild wireguard peer table
        try:
            for peer in self._wg_interface_instance.peers:
                # add a comment with some information about the peer to make the configuration more readable
                self._wg_config.add_peer(peer.public_key, f"# {peer.instance_id} / {peer.friendly_name} / {peer.description}")
                self._wg_config.add_attr(peer.public_key, "AllowedIPs", peer.cidr_routes)

                if peer.endpoint:
                    self._wg_config.add_attr(peer.public_key, "Endpoint", peer.endpoint)

                if peer.persistent_keepalives > 0:
                    self._wg_config.add_attr(peer.public_key, "PersistentKeepalive", peer.persistent_keepalives)

                if peer.preshared_key:
                    self._wg_config.add_attr(peer.public_key, "PresharedKey", peer.preshared_key)

            self._logger.debug(f"persist configuration files for {repr(self)}")
            self._wg_config.write_file()

        except Exception as ex:
            self._logger.error(f"unable to update peer list: {ex}")
            return False

        self._logger.debug(f"peer config for '{self._wg_interface_instance.intf_name}' updated")
        return True

    async def apply_config(self, recreate_interface: bool=False) -> bool:
        """apply new configuration to system

        :param recreate_interface: recreate the interface on system level (will disrupt the connectivity), defaults to False
        :type recreate_interface: bool, optional
        :return: True if apply was successful, otherwise faile
        :rtype: bool
        """
        wg_interface = self._wg_interface_instance.intf_name
        success_state = True
        interface_exists = await self.interface_exists()

        try:
            shell_command = f"wg-quick strip {self._config_path}"
            self._logger.debug(f"execute '{shell_command}'...")
            config, err, success = await self._execute_subprocess(shell_command)
            if not success:
                self._logger.fatal("unable to strip wireguard configuration file")
                return False

            # create temporary file with the config to apply sync
            with tempfile.NamedTemporaryFile(delete=not self._config.debug, suffix=".wgtempconf", dir=self._config.wg_tmp_dir) as tmp_file:
                # write configuration results to file
                self._logger.debug(f"write temporary wireguard configuration file to disk at {tmp_file.name}")
                tmp_file.write(config.encode("utf-8"))
                tmp_file.flush()

                # sync the wireguard configuration with the configuration file
                # this WON'T update the routing table (handled by another component)
                shell_command = f"wg syncconf {wg_interface} {tmp_file.name}"
                self._logger.debug(f"execute '{shell_command}'...")
                out, err, success = await self._execute_subprocess(shell_command)
                if not success:
                    if "Unable to modify interface: Operation not permitted" in err:
                        self._logger.fatal("unable to update network configuration, permission denied")

                    self._logger.error(f"unable to update configuration for interface {wg_interface}\n{err}")
                    success_state = False

                else:
                    self._logger.info(f"sync wireguard config file with interface {wg_interface}")

        except Exception as ex:
            self._logger.fatal(f"failed to apply the Wireguard configuration for interface {wg_interface} at system level: {str(ex)}", exc_info=True)
            return False

        if recreate_interface:
            self._logger.warning("apply config with recreate interface called")
            if interface_exists:
                await self.interface_down()
            await self.interface_up()

        else:
            if interface_exists:
                await self.interface_up()

        return success_state

    async def delete_config(self):
        """delete configuration file and clear interface
        """
        if await self.interface_exists():
            await self.interface_down()

        if os.path.exists(self._config_path):
            os.remove(self._config_path)
