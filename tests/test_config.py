import logging

from app.config import config
import pytest

logger = logging.getLogger(__name__)


@pytest.mark.order(1)
def test_env_variables_loaded():
    """Ensure critical environment variables are loaded from app.config."""
    assert config.get_secret_key() is not None, "SECRET_KEY is missing!"
    assert config.get_algorithm() is not None, "ALGORITHM is missing!"
    assert (
        config.get_access_token_expiry() is not None
    ), "ACCESS_TOKEN_EXPIRE_MINUTES is missing!"
    assert config.get_mongo_cluster() is not None, "MONGO_CLUSTER is missing!"
    assert (
        config.get_db_name() == "TEST_SKIN_DIAGNOSIS_DB"
    ), "DB_NAME is incorrect!"
    assert config.is_testing() is True, "TESTING mode is not enabled!"

    logger.info("Environment variables successfully loaded from app.config.")


@pytest.mark.order(2)
def test_default_values():
    """Ensure environment variables fallback to defaults when missing."""
    assert (
        config.get_access_token_expiry() == 10
    ), "Default ACCESS_TOKEN_EXPIRE_MINUTES is incorrect!"
    assert (
        config.get_bcrypt_salt_rounds() == 4
    ), "Default BCRYPT_SALT_ROUNDS is incorrect!"

    logger.info("Default values are correctly set.")


@pytest.mark.order(4)
def test_logging_enabled():
    """Check if logging is enabled in test mode."""
    assert config.is_logging_enabled() in [
        True,
        "TRUE",
        "true",
        "1",
    ], "Logging should be enabled in tests!"

    logger.info("Logging is enabled in test mode.")
