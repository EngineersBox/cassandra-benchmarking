mod logging;

extern crate serde;
extern crate ssh2;
extern crate flate2;
extern crate systemctl;
extern crate docker_api;
#[macro_use]
extern crate slog;
extern crate slog_term;
extern crate slog_async;
extern crate slog_json;
extern crate lazy_static;

pub(crate) use lazy_static::lazy_static;
use slog::Logger;

use crate::logging::logging::initialize_logging;

lazy_static!{
    static ref LOGGER: Logger = initialize_logging(String::from("Deployer"));
}

fn main() {
    info!(&crate::LOGGER, "Configured logger");
}
