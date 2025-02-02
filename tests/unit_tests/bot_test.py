from unittest import mock

import pytest

from mmpy_bot import Bot, ExamplePlugin, Settings

from ..integration_tests.utils import TestPlugin


@pytest.fixture(scope="function")
def bot():
    bot = Bot(plugins=[ExamplePlugin()], settings=Settings(DEBUG=True))
    yield bot
    bot.stop()  # if the bot was started, stop it


class TestBot:
    @mock.patch("mmpy_bot.driver.Driver.login")
    def test_init(self, login):
        # Create some plugins and mock their initialize method so we can check calls
        plugins = [ExamplePlugin(), TestPlugin()]
        for plugin in plugins:
            plugin.initialize = mock.MagicMock()

        # Create a bot and verify that it gets initialized correctly
        bot = Bot(
            settings=Settings(MATTERMOST_URL="test_url.org", BOT_TOKEN="random_token"),
            plugins=plugins,
        )
        assert bot.driver.options["url"] == "test_url.org"
        assert bot.driver.options["token"] == "random_token"
        assert bot.plugins == plugins
        login.assert_called_once()

        # Verify that all of the passed plugins were initialized
        for plugin in plugins:
            assert plugin.initialize.called_once_with(bot.driver)

    @mock.patch("mmpy_bot.driver.Driver.init_websocket")
    @mock.patch.multiple("mmpy_bot.Plugin", on_start=mock.DEFAULT, on_stop=mock.DEFAULT)
    def test_run(self, init_websocket, bot, **mocks):
        bot.run()
        init_websocket.assert_called_once()

        for plugin in bot.plugins:
            plugin.on_start.assert_called_once()

        bot.stop()

        for plugin in bot.plugins:
            plugin.on_stop.assert_called_once()
